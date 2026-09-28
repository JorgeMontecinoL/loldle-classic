"""Pipeline visual en vivo de LoLdle Classic (Entregable 2).

Juega la misma partida con dos variantes del modelo —el baseline de prompting
directo y el mismo modelo con el adaptador LoRA— y transmite al navegador cada
etapa del pipeline a medida que ocurre.

No hay salidas simuladas. Cada partida corre `play_game` del notebook
LoLdle_Classic.ipynb contra un servidor de modelo real; este archivo sólo se
engancha a los dos puntos de extensión que el notebook ya expone
(`query_model` y `show_event`) para emitir eventos. Cada partida queda
registrada en results/d2/app_runs/, así lo que se ve en pantalla es trazable.

Uso (desde la raíz del repo, con los servidores de modelo arriba):
    python3 pipeline_app/server.py                # http://127.0.0.1:8765
    python3 pipeline_app/server.py --pace 0       # sin espaciar las etapas
"""

import argparse
import json
import os
import random
import sys
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # el motor resuelve data/ respecto del directorio actual

from run_benchmark import SEED, NUM_GAMES, build_runner, load_engine, parse_state, query_roster  # noqa: E402

sys.path.insert(0, str(ROOT / "finetune"))
from make_data import state_line  # noqa: E402  (misma definición que el entrenamiento)

RUNS_DIR = ROOT / "results" / "d2" / "app_runs"
RESULTS_PATH = ROOT / "results" / "d2" / "summary.json"
ADAPTER = "finetune/adapters/final"

FIELDS = ("gender", "positions", "species", "resource", "range_type", "regions", "release_year")


def default_variants(args):
    return {
        "baseline": {
            "title": "Baseline",
            "subtitle": "Prompting directo",
            "model": "ministral-3-3b-instruct-2512",
            "weights": "MLX 4-bit · sin ajuste",
            "base_url": args.baseline_url,
            "api_model": args.baseline_model,
            "adapter": None,
            "submit": "whole",
        },
        "lora": {
            "title": "Solución",
            "subtitle": "Fine-tuning LoRA" if args.solution_mode == "last-line"
                        else "Fine-tuning LoRA + consulta al roster",
            "model": "ministral-3-3b-instruct-2512",
            "weights": "mismos pesos + adaptador LoRA",
            "base_url": args.lora_url,
            "api_model": args.lora_model,
            "adapter": args.adapter,
            "submit": args.solution_mode,
        },
    }


class Engine:
    """Un namespace del notebook por variante: cada una tiene su propio
    endpoint y su propio query_model, así las dos partidas corren en paralelo
    sin compartir estado."""

    def __init__(self, key, variant):
        self.key = key
        self.variant = variant
        self.ns = load_engine()
        extra_body = {}
        if variant["adapter"]:
            extra_body["adapters"] = str((ROOT / variant["adapter"]).resolve())
        self.telemetry = build_runner(
            self.ns,
            variant["model"],
            api_model=variant["api_model"],
            base_url=variant["base_url"],
            extra_body=extra_body,
            submit=variant["submit"],
        )
        self.query_model = self.ns["query_model"]
        self.lock = threading.Lock()

    # --- utilidades sobre el motor ---------------------------------------
    def feasible(self, constraints, used):
        check = self.ns["constraint_violations"]
        return [n for n in self.ns["NAMES"] if n not in used and not check(n, constraints)]

    def constraint_summary(self, constraints):
        value_text = self.ns["_value_text"]
        labels = self.ns["LABELS"]
        rows = []
        for field in FIELDS[:-1]:
            item = constraints[field]
            required = item["required"]
            rows.append({
                "field": field,
                "label": labels[field],
                "required": value_text(required) if required is not None else None,
                "forbidden": sorted(item["forbidden"]),
            })
        year = constraints["release_year"]
        if year["exact"] is not None:
            year_text = f"= {year['exact']}"
        else:
            parts = []
            if year["min_exclusive"] is not None:
                parts.append(f"> {year['min_exclusive']}")
            if year["max_exclusive"] is not None:
                parts.append(f"< {year['max_exclusive']}")
            year_text = " y ".join(parts) if parts else None
        rows.append({"field": "release_year", "label": labels["release_year"],
                     "required": year_text, "forbidden": []})
        return rows

    def reasoning(self, text, feasible, constraints):
        """Líneas de trabajo del modelo ajustado, verificadas contra el motor.

        "Sé: ..." se compara con el estado real (misma función que generó los
        datos de entrenamiento); cada nombre de "Compatibles: ..." se marca
        según si de verdad es compatible con todo lo revelado.
        """
        result = {"state": None, "true_state": None, "state_ok": None, "items": None, "more": False}
        for line in (text or "").splitlines():
            head, _, body = line.partition(":")
            key = head.strip().lower()
            if key == "sé" and result["state"] is None:
                result["state"] = body.strip()
                result["true_state"] = state_line(self.ns, constraints).partition(":")[2].strip()
                result["state_ok"] = result["state"] == result["true_state"]
            elif key == "compatibles" and body.strip() and result["items"] is None:
                items = [x.strip() for x in body.strip().rstrip("…").split(",") if x.strip()]
                out = []
                for item in items:
                    parsed = self.ns["parse_response"](item)
                    name = parsed["name"] if parsed["format_ok"] else None
                    out.append({"text": item, "known": name is not None,
                                "ok": name is not None and name in feasible})
                result["items"] = out
                result["more"] = body.strip().endswith("…")
        return result if (result["state"] is not None or result["items"]) else None

    def tiles(self, guess, feedback):
        champion = self.ns["CHAMPIONS"][guess]
        value_text = self.ns["_value_text"]
        return [
            {"field": f, "label": self.ns["LABELS"][f],
             "value": value_text(champion[f]), "status": feedback[f]}
            for f in FIELDS
        ]


class Game:
    """Estado de una partida en curso y emisión de eventos SSE."""

    def __init__(self, engine, target, pace, write):
        self.engine = engine
        self.target = target
        self.pace = pace
        self.write = write
        self.constraints = engine.ns["empty_constraints"]()
        self.used = []
        self.feasible_before = engine.ns["NAMES"]
        self.started = time.monotonic()

    def emit(self, kind, **data):
        data["t"] = round(time.monotonic() - self.started, 3)
        self.write(kind, data)

    def wait(self):
        if self.pace > 0:
            time.sleep(self.pace)

    # Punto de extensión 1 del notebook: la llamada al modelo.
    def query_model(self, messages):
        ns = self.engine.ns
        turn = (len(messages) - 2) // 2 + 1
        self.feasible_before = self.engine.feasible(self.constraints, set(self.used))
        last_user = messages[-1]["content"]
        self.emit(
            "prompt",
            turn=turn,
            max_attempts=ns["MAX_ATTEMPTS"],
            messages=len(messages),
            history_turns=turn - 1,
            roster=len(ns["NAMES"]),
            last_user=last_user,
            feasible=len(self.feasible_before),
            feasible_sample=self.feasible_before[:6],
        )
        self.wait()
        self.emit("model_call", turn=turn)
        mark = len(self.engine.telemetry)
        submitted = self.engine.query_model(messages)
        sample = self.engine.telemetry[-1] if len(self.engine.telemetry) > mark else {}
        full = sample.get("model_output") or submitted
        tool = None
        if self.engine.variant["submit"] == "state-tool":
            state = parse_state(ns, full)
            if state is not None:
                matches = query_roster(ns, state, set(self.used))
                tool = {"matches": len(matches), "sample": matches[:5], "submitted": submitted}
        self.emit(
            "model_output",
            turn=turn,
            raw=full,
            submitted=submitted,
            submit_mode=self.engine.variant["submit"],
            tool=tool,
            listed=self.engine.reasoning(full, set(self.feasible_before), self.constraints),
            feasible=len(self.feasible_before),
            latency_s=sample.get("latency_s"),
            prompt_tokens=sample.get("prompt_tokens"),
            completion_tokens=sample.get("completion_tokens"),
            error=sample.get("error"),
        )
        self.wait()
        return submitted

    # Punto de extensión 2 del notebook: después de evaluar cada intento.
    def show_event(self, event, game_number):
        turn = event["turn"]
        self.emit(
            "parse",
            turn=turn,
            guess=event["guess"],
            format_ok=event["format_ok"],
            invalid=event["invalid"],
            reason=event["reason"],
        )
        self.wait()
        inside = bool(event["guess"]) and event["guess"] in self.feasible_before
        self.emit(
            "verify",
            turn=turn,
            guess=event["guess"],
            invalid=event["invalid"],
            repeated=event["repeated"],
            violations=[
                {"label": self.engine.ns["LABELS"][v["attribute"]], "rule": v["rule"]}
                for v in event["violations"]
            ],
            inside_feasible=inside,
            feasible=len(self.feasible_before),
        )
        self.wait()
        if event["feedback"] is not None:
            self.engine.ns["update_constraints"](self.constraints, event["guess"], event["feedback"])
            self.used.append(event["guess"])
            after = self.engine.feasible(self.constraints, set(self.used))
            tiles = self.engine.tiles(event["guess"], event["feedback"])
        else:
            after = self.feasible_before
            tiles = None
        self.emit(
            "feedback",
            turn=turn,
            guess=event["guess"],
            raw=event["raw_response"],
            status=event["status"],
            tiles=tiles,
            solved=event["solved"],
            inside_feasible=inside,
            repeated=event["repeated"],
            feasible_after=len(after),
            constraints=self.engine.constraint_summary(self.constraints),
        )
        self.wait()


def run_game(engine, target, pace, write, draw_seed=None):
    game = Game(engine, target, pace, write)
    ns = engine.ns
    ns["query_model"] = game.query_model
    ns["show_event"] = game.show_event
    started_at = datetime.now()
    try:
        game.emit("start", target=target, variant=engine.key)
        record = ns["play_game"](target, 1)
    finally:
        ns["query_model"] = engine.query_model
    summary = {
        "solved": record["solved"],
        "attempts": record["attempts_used"],
        "violations": sum(e["constraint_violation"] for e in record["trace"]),
        "invalid": sum(e["invalid"] for e in record["trace"]),
        "repeated": sum(e["repeated"] for e in record["trace"]),
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = started_at.strftime("%Y%m%d-%H%M%S")
    safe_target = "".join(c for c in target if c.isalnum())
    log_path = RUNS_DIR / f"{stamp}_{engine.key}_{safe_target}.json"
    log_path.write_text(json.dumps({
        "variant": engine.key,
        "config": engine.variant,
        "target": target,
        "draw_seed": draw_seed,
        "pace_s": pace,
        "started_at": started_at.isoformat(timespec="seconds"),
        "summary": summary,
        "record": record,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    game.emit("end", log=str(log_path.relative_to(ROOT)), **summary)


def probe(variant):
    """¿Responde el servidor de modelo de esta variante?"""
    url = variant["base_url"].rstrip("/") + "/models"
    try:
        with urlopen(Request(url, headers={"Authorization": "Bearer lm-studio"}), timeout=2) as r:
            return r.status == 200
    except (URLError, OSError, ValueError):
        return False


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        server_version = "LoLdlePipeline/1.0"

        def log_message(self, fmt, *args):  # silencio: la consola queda limpia para grabar
            pass

        def send_json(self, payload, status=HTTPStatus.OK):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(url.query).items()}
            route = url.path
            if route in ("/", "/index.html"):
                return self.send_file(APP_DIR / "index.html", "text/html; charset=utf-8")
            if route == "/api/config":
                return self.send_json(self.config())
            if route == "/api/health":
                return self.send_json({k: probe(v) for k, v in state["variants"].items()})
            if route == "/api/draw":
                return self.send_json(self.draw())
            if route == "/api/results":
                data = None
                if RESULTS_PATH.exists():
                    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
                return self.send_json({"results": data})
            if route == "/api/play":
                return self.play(query)
            self.send_json({"error": "ruta desconocida"}, HTTPStatus.NOT_FOUND)

        def send_file(self, path, content_type):
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def config(self):
            ns = next(iter(state["engines"].values())).ns
            split = {}
            split_path = ROOT / "finetune" / "data" / "split.json"
            if split_path.exists():
                raw = json.loads(split_path.read_text(encoding="utf-8"))
                split = {"valid": raw.get("valid", []), "train": raw.get("train", [])}
            return {
                "variants": state["variants"],
                "test_targets": state["targets"],
                "split": split,
                "roster": list(ns["NAMES"]),
                "max_attempts": ns["MAX_ATTEMPTS"],
                "pace": state["pace"],
                "seed": SEED,
            }

        def draw(self):
            seed = time.time_ns() % 10_000_000
            target = random.Random(seed).choice(state["targets"])
            return {"target": target, "seed": seed, "pool": len(state["targets"])}

        def play(self, query):
            key = query.get("variant")
            target = query.get("target")
            engine = state["engines"].get(key)
            if engine is None or target not in state["roster"]:
                return self.send_json({"error": "variante o campeón inválido"}, HTTPStatus.BAD_REQUEST)
            if not engine.lock.acquire(blocking=False):
                return self.send_json({"error": "ya hay una partida en curso"}, HTTPStatus.CONFLICT)
            try:
                pace = float(query.get("pace", state["pace"]))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "keep-alive")
                self.end_headers()

                def write(kind, data):
                    chunk = f"event: {kind}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                    self.wfile.write(chunk.encode("utf-8"))
                    self.wfile.flush()

                draw_seed = query.get("seed")
                run_game(engine, target, max(0.0, min(pace, 3.0)), write, draw_seed)
            except (BrokenPipeError, ConnectionResetError):
                pass  # el navegador cerró la pestaña a mitad de partida
            finally:
                engine.lock.release()

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--pace", type=float, default=0.55,
                        help="segundos entre etapas en pantalla (las llamadas al modelo son reales)")
    parser.add_argument("--baseline-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--baseline-model", default="default_model")
    parser.add_argument("--lora-url", default="http://127.0.0.1:8082/v1")
    parser.add_argument("--lora-model", default="default_model")
    parser.add_argument("--adapter", default=ADAPTER)
    parser.add_argument("--solution-mode", choices=("last-line", "state-tool"), default="last-line",
                        help="last-line: el juego recibe la jugada del modelo (fine-tuning puro); "
                             "state-tool: una herramienta ejecuta la línea «Sé:» del modelo contra el roster")
    args = parser.parse_args()

    variants = default_variants(args)
    engines = {key: Engine(key, v) for key, v in variants.items()}
    ns = engines["baseline"].ns
    ns["NUM_GAMES"] = NUM_GAMES
    ns["SEED"] = SEED
    state = {
        "variants": variants,
        "engines": engines,
        "targets": ns["choose_targets"](),   # los 30 objetivos de prueba (SEED=777)
        "roster": set(ns["NAMES"]),
        "pace": args.pace,
    }

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(state))
    server.daemon_threads = True
    print(f"Pipeline en vivo: http://127.0.0.1:{args.port}")
    for key, v in variants.items():
        status = "arriba" if probe(v) else "SIN RESPUESTA"
        adapter = f" + {v['adapter']}" if v["adapter"] else ""
        print(f"  {key:<9} {v['base_url']}{adapter}  [{status}]")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\ndetenido")


if __name__ == "__main__":
    main()
