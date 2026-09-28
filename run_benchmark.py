"""Corrida por lotes de LoLdle Classic sobre varios modelos de LM Studio.

Reutiliza el motor del notebook (LoLdle_Classic.ipynb) ejecutando sus celdas de
código, de modo que el benchmark y el notebook comparten exactamente el mismo
roster, feedback, parser, checker de restricciones y métricas.

Uso:
    python3 run_benchmark.py              # corre todos los modelos pendientes
    python3 run_benchmark.py --games 5    # corrida corta de prueba
    python3 run_benchmark.py --force      # reejecuta modelos ya guardados

Modo de una variante (Entregable 2): evalúa un único servidor compatible con
OpenAI —por ejemplo mlx_lm.server con o sin adaptador LoRA— sobre los mismos
objetivos y con el mismo motor:
    python3 run_benchmark.py --label baseline --base-url http://127.0.0.1:8081/v1 \
        --api-model default_model --params 3.0 --out-dir results/d2/raw
    python3 run_benchmark.py --label lora --base-url http://127.0.0.1:8082/v1 \
        --api-model default_model --adapter finetune/adapters/final \
        --submit last-line --params 3.0 --out-dir results/d2/raw
(scripts/eval_d2.sh corre ambas, más la variante --submit state-tool.)
"""

import argparse
import io
import json
import time
import contextlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "LoLdle_Classic.ipynb"
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"

# Modelos open-weight <= 8B servidos por LM Studio.
MODELS = [
    ("exaone-3.5-2.4b-instruct", 2.4),
    ("qwen3.5-4b", 4.0),
    ("meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k", 3.2),
    ("microsoft_phi-4-mini-instruct", 3.8),
    ("ministral-3-3b-instruct-2512", 3.0),
    ("falcon3-7b-instruct", 7.0),
    ("josie-7b-v6.0-step2000", 7.6),
    ("josiefied-qwen2.5-7b-instruct-abliterated-v2", 7.6),
    ("qwen2.5-7b-instruct", 7.6),
    ("ministral-3-8b-instruct-2512", 8.0),
]

# Ajustes por modelo enviados al endpoint. qwen3.5-4b es un modelo de
# razonamiento: sin esto agota MAX_TOKENS en reasoning_content y devuelve
# content vacío en todos los intentos.
MODEL_EXTRA_BODY = {
    "qwen3.5-4b": {"reasoning_effort": "none"},
}

# Hiperparámetros compartidos por todas las corridas.
NUM_GAMES = 30
MAX_ATTEMPTS = 10
SEED = 777
TEMPERATURE = 0
MAX_TOKENS = 64
TIMEOUT_SECONDS = 900
API_RETRIES = 2


def load_engine():
    """Ejecuta las celdas de código del notebook en un namespace aislado."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "loldle_engine", "__file__": str(NOTEBOOK)}
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if "RUN_NOW" in source and "run_experiment()" in source:
            continue  # celda de ejecución del notebook
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(source, f"{NOTEBOOK.name}", "exec"), namespace)
    return namespace


def last_line(text):
    """Última línea no vacía: la jugada en el formato "compatibles + jugada"."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else text


STATE_SET_FIELDS = ("positions", "species", "regions")


def parse_state(ns, text):
    """Invierte la línea "Sé: ..." del formato de tres pasos.

    Devuelve {campo: valor requerido} y los límites de año que el MODELO dice
    conocer, o None si no escribió esa línea. Cada valor de atributo del roster
    pertenece a un único campo, así que la inversión no es ambigua.
    """
    owners = ns.setdefault("_value_owner", {})
    if not owners:
        for champion in ns["CHAMPIONS"].values():
            for field in ("gender", "resource", "range_type"):
                owners[champion[field]] = field
            for field in STATE_SET_FIELDS:
                for value in champion[field]:
                    owners[value] = field
    for line in (text or "").splitlines():
        head, _, body = line.partition(":")
        if head.strip().lower() != "sé":
            continue
        state = {"required": {}, "year": (None, None)}
        body = body.strip()
        if body in ("", "nada"):
            return state
        for token in (t.strip() for t in body.split("·")):
            if token.startswith(">") and token[1:].isdigit():
                state["year"] = (int(token[1:]) + 1, state["year"][1])
            elif token.startswith("<") and token[1:].isdigit():
                state["year"] = (state["year"][0], int(token[1:]) - 1)
            elif "-" in token and all(p.isdigit() for p in token.split("-", 1)):
                lo, hi = token.split("-", 1)
                state["year"] = (int(lo), int(hi))
            elif token.isdigit():
                state["year"] = (int(token), int(token))
            else:
                values = [v.strip() for v in token.split("+")]
                fields = {owners.get(v) for v in values}
                if len(fields) != 1 or None in fields:
                    continue  # valor que no existe en el roster: se ignora
                field = fields.pop()
                state["required"][field] = frozenset(values) if field in STATE_SET_FIELDS else values[0]
        return state
    return None


def query_roster(ns, state, used):
    """La herramienta: campeones del roster que cumplen el estado declarado."""
    lo, hi = state["year"]
    out = []
    for name in ns["NAMES"]:
        if name in used:
            continue
        champion = ns["CHAMPIONS"][name]
        if any(champion[f] != v for f, v in state["required"].items()):
            continue
        year = champion["release_year"]
        if (lo is not None and year < lo) or (hi is not None and year > hi):
            continue
        out.append(name)
    return out


def build_runner(ns, model_name, api_model=None, base_url=None, extra_body=None,
                 submit="whole"):
    """Instala en el namespace un query_model instrumentado para este modelo.

    `api_model` es el valor que viaja en el campo "model" de la petición (por
    defecto el mismo nombre); `extra_body` se mezcla en el cuerpo, por ejemplo
    {"adapters": ...} para que mlx_lm.server aplique un adaptador LoRA.

    `submit` decide qué parte de la respuesta recibe el juego: "whole" (la
    respuesta entera, como en el Entregable 1) o "last-line" (sólo la última
    línea; el modelo ajustado escribe antes su estado y su lista). La
    respuesta completa queda siempre en la telemetría.

    "state-tool" es un análisis, no la solución: una herramienta ejecuta la
    línea "Sé:" que escribió el modelo contra el roster y juega el primer
    campeón que la cumple. El código nunca ve el feedback real; sirve para
    medir cuánto del fallo restante es la búsqueda y cuánto el estado.
    """
    if submit not in ("whole", "last-line", "state-tool"):
        raise ValueError(f"modo de envío desconocido: {submit}")
    ns["MODEL_NAME"] = model_name
    if base_url:
        ns["BASE_URL"] = base_url
    ns["MAX_ATTEMPTS"] = MAX_ATTEMPTS
    ns["NUM_GAMES"] = NUM_GAMES
    ns["SEED"] = SEED
    ns["TEMPERATURE"] = TEMPERATURE
    ns["MAX_TOKENS"] = MAX_TOKENS
    ns["TIMEOUT_SECONDS"] = TIMEOUT_SECONDS

    if extra_body is None:
        extra_body = MODEL_EXTRA_BODY.get(model_name, {})
    api_model = api_model or model_name
    telemetry = []

    def query_model(messages):
        body = {
            "model": api_model,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "stream": False,
            **extra_body,
        }
        last_error = None
        for attempt_index in range(API_RETRIES + 1):
            started = time.monotonic()
            try:
                payload = ns["_http_json"]("/chat/completions", body)
                choices = payload.get("choices")
                if not isinstance(choices, list) or not choices:
                    raise RuntimeError("La respuesta no contiene choices.")
                message = choices[0].get("message") or {}
                content = message.get("content")
                if not isinstance(content, str) or not content.strip():
                    finish = choices[0].get("finish_reason")
                    if message.get("reasoning_content"):
                        raise RuntimeError(
                            "content vacío: la generación se consumió en "
                            f"reasoning_content (finish_reason={finish!r})."
                        )
                    raise RuntimeError(
                        f"content vacío (finish_reason={finish!r})."
                    )
                usage = payload.get("usage") or {}
                submitted = last_line(content) if submit != "whole" else content
                if submit == "state-tool":
                    state = parse_state(ns, content)
                    if state is not None:
                        used = set()
                        for m in messages:
                            if m["role"] == "assistant":
                                name = ns["parse_response"](m["content"])["name"]
                                if name:
                                    used.add(name)
                        matches = query_roster(ns, state, used)
                        if matches:
                            submitted = matches[0]
                telemetry.append({
                    "latency_s": round(time.monotonic() - started, 3),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "retries": attempt_index,
                    "error": None,
                    "model_output": content,
                })
                return submitted
            except Exception as exc:  # reintenta errores de red y de generación
                last_error = exc
                elapsed = round(time.monotonic() - started, 3)
                if attempt_index == API_RETRIES:
                    telemetry.append({
                        "latency_s": elapsed,
                        "prompt_tokens": None,
                        "completion_tokens": None,
                        "retries": attempt_index,
                        "error": f"{type(exc).__name__}: {exc}",
                        "model_output": "",
                    })
                    # Se degrada a respuesta vacía: el motor la contabiliza como
                    # intento inválido en lugar de abortar toda la corrida.
                    return ""
                time.sleep(2)
        raise AssertionError(f"inalcanzable: {last_error}")

    ns["query_model"] = query_model
    ns["show_event"] = lambda event, game_number: None
    return telemetry


def run_model(ns, model_name, params_b, num_games, targets, serving=None):
    serving = serving or {}
    telemetry = build_runner(
        ns,
        model_name,
        api_model=serving.get("api_model"),
        base_url=serving.get("base_url"),
        extra_body=serving.get("extra_body"),
        submit=serving.get("submit", "whole"),
    )
    started_at = datetime.now(timezone.utc)
    wall_start = time.monotonic()
    records = []
    for game_number, target in enumerate(targets, start=1):
        mark = len(telemetry)
        record = ns["play_game"](target, game_number)
        for event, sample in zip(record["trace"], telemetry[mark:]):
            event["latency_s"] = sample["latency_s"]
            event["prompt_tokens"] = sample["prompt_tokens"]
            event["completion_tokens"] = sample["completion_tokens"]
            event["api_error"] = sample["error"]
            event["model_output"] = sample.get("model_output")
        records.append(record)
        status = "OK " if record["solved"] else "-- "
        print(
            f"  [{model_name}] partida {game_number:>2}/{num_games} {status}"
            f" objetivo={target:<14} intentos={record['attempts_used']}"
            f" t={time.monotonic() - wall_start:6.0f}s",
            flush=True,
        )

    latencies = [s["latency_s"] for s in telemetry if s["error"] is None]
    return {
        "model_name": model_name,
        "params_b": params_b,
        "started_at": started_at.isoformat(),
        "wall_seconds": round(time.monotonic() - wall_start, 1),
        "config": {
            "num_games": num_games,
            "max_attempts": MAX_ATTEMPTS,
            "seed": SEED,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "extra_body": serving.get("extra_body", MODEL_EXTRA_BODY.get(model_name, {})),
            "base_url": ns["BASE_URL"],
            "api_model": serving.get("api_model") or model_name,
            "submit": serving.get("submit", "whole"),
        },
        "targets": targets,
        "records": records,
        "summary": ns["summarize"](records),
        "violations": ns["violation_rows"](records),
        "api_calls": len(telemetry),
        "api_errors": sum(1 for s in telemetry if s["error"]),
        "mean_latency_s": round(sum(latencies) / len(latencies), 3) if latencies else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=NUM_GAMES)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--models", nargs="*", default=None)
    single = parser.add_argument_group("una variante (Entregable 2)")
    single.add_argument("--label", help="nombre con el que se guarda la corrida")
    single.add_argument("--base-url", help="endpoint compatible con OpenAI")
    single.add_argument("--api-model", help='campo "model" de la petición')
    single.add_argument("--adapter", help="ruta de un adaptador LoRA para mlx_lm.server")
    single.add_argument("--params", type=float, default=None, help="parámetros en miles de millones")
    single.add_argument("--out-dir", default=None, help="carpeta de salida (por defecto results/raw)")
    single.add_argument("--submit", choices=("whole", "last-line", "state-tool"), default="whole",
                        help='qué recibe el juego: la respuesta entera, su última línea, o (análisis) '
                             'el primer campeón que cumple la línea "Sé:" del modelo')
    single.add_argument("--targets-json", default=None,
                        help="JSON con listas de objetivos (p. ej. finetune/data/split.json)")
    single.add_argument("--targets-key", default="valid",
                        help="clave de la lista a jugar dentro de --targets-json")
    args = parser.parse_args()

    raw_dir = (ROOT / args.out_dir) if args.out_dir else RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    ns = load_engine()

    ns["NUM_GAMES"] = args.games
    ns["SEED"] = SEED
    if args.targets_json:
        targets = json.loads((ROOT / args.targets_json).read_text(encoding="utf-8"))[args.targets_key]
        args.games = len(targets)
        print(f"Roster: {len(ns['CHAMPIONS'])} campeones")
        print(f"Objetivos ({args.targets_json}:{args.targets_key}, n={len(targets)}): {', '.join(targets)}\n")
    else:
        targets = ns["choose_targets"]()
        print(f"Roster: {len(ns['CHAMPIONS'])} campeones")
        print(f"Objetivos (SEED={SEED}, n={len(targets)}): {', '.join(targets)}\n")

    if args.label:
        extra_body = {}
        if args.adapter:
            extra_body["adapters"] = str((ROOT / args.adapter).resolve())
        serving = {
            "base_url": args.base_url,
            "api_model": args.api_model,
            "extra_body": extra_body,
            "submit": args.submit,
        }
        selected = [(args.label, args.params, serving)]
    else:
        selected = [
            (name, params, None) for name, params in MODELS
            if args.models is None or name in args.models
        ]

    for index, (model_name, params_b, serving) in enumerate(selected, start=1):
        out_path = raw_dir / f"{model_name}.json"
        if out_path.exists() and not args.force:
            print(f"[{index}/{len(selected)}] {model_name}: ya existe, se omite")
            continue
        print(f"[{index}/{len(selected)}] {model_name} ({params_b}B)", flush=True)
        result = run_model(ns, model_name, params_b, args.games, targets, serving)
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        s = result["summary"]
        print(
            f"  -> resueltas {s['solved_games']}/{s['games']}"
            f" | inválidos {s['invalid_count']}/{s['attempts']}"
            f" | violaciones {s['constraint_violation_count']}"
            f" | {result['wall_seconds']:.0f}s"
            f" | guardado en {out_path.relative_to(ROOT)}\n",
            flush=True,
        )


if __name__ == "__main__":
    main()
