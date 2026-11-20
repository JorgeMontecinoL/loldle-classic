"""Demo del Entregable 4: tablero estilo LoLdle Classic con el sistema real paso a paso.

    .venv-ft/bin/python -m agents_d4.app            # http://127.0.0.1:8767  (scripts/demo_d4.sh)

- «En vivo»: la interfaz llama al sistema real (servidor MLX + adaptadores del repositorio).
- «Reproducción de traza»: anima una traza guardada; no llama al modelo.
- «No disponible»: falta el adaptador o el servidor.
El secreto lo elige la interfaz y sólo lo usa el motor del juego (`AgentSystem.play`):
nunca entra en los mensajes de los agentes. Las partidas se ejecutan de a una (un
servidor, un adaptador por llamada), salvo el control por reglas.
"""
import argparse
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

from run_benchmark import build_runner
from agents_d3.analyze import read
from agents_d3.client import ModelClient
from agents_d3.evaluate import atomic_json, legacy_game
from agents_d3.runtime import AgentConfig, PAGE_MAX_TOKENS, PAGE_PREFIX, algorithmic_control, prompt_bundle
from agents_d3.state import jsonable
from .runtime import D3_ADAPTER, D4_ADAPTER, ROOT, SYSTEMS, build_system, dedicated_servers, describe
from .selector_metrics import score_page, truth_for_page, parse_selector

LOCK = threading.Lock()
SYSTEM_INFO = {
    "d4": {"label": "D4 · Selector con adaptador propio", "kind": "agents"},
    "d3": {"label": "D3 · tres agentes, LoRA común", "kind": "agents"},
    "d4_selector_base": {"label": "D3 con Selector base (sin LoRA)", "kind": "agents"},
    "d2_lora": {"label": "D2 · LoRA sin agentes", "kind": "legacy", "adapter": "finetune/adapters/final"},
    "direct": {"label": "D1 · prompting directo (base)", "kind": "legacy", "adapter": None},
    "control": {"label": "Control · filtro por reglas (sin LLM)", "kind": "control"},
}
CASES = ROOT / "results/d4/demo_cases.json"
TRACE_DIRS = [ROOT / "results/d4/runs", ROOT / "results/d3/raw"]
FRONTEND_FILES = {
    "/": ("arena.html", "text/html; charset=utf-8"),
    "/original": ("index.html", "text/html; charset=utf-8"),
    "/arena.css": ("arena.css", "text/css; charset=utf-8"),
    "/arena.js": ("arena.js", "text/javascript; charset=utf-8"),
    "/arcane.jpg": ("assets/arcane.jpg", "image/jpeg"),
    "/portraits.json": ("assets/portraits.json", "application/json"),
}
REPLAY_FILES = {
    "direct": "legacy/test_base_direct.json.gz",
    "d2_lora": "legacy/test_lora_d2_lora.json.gz",
    "d3": "test_d3.json.gz",
    "d4": "test_d4.json.gz",
}


def server_ok(base_url):
    try:
        with urlopen(base_url.rstrip("/") + "/models", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def availability(base_url):
    live = server_ok(base_url)
    out = {}
    for key, info in SYSTEM_INFO.items():
        needs = []
        if info["kind"] == "agents":
            needs = [p for p in SYSTEMS[key].values() if p]
        elif info.get("adapter"):
            needs = [info["adapter"]]
        missing = [p for p in needs if not (ROOT / p / "adapters.safetensors").exists()]
        if info["kind"] == "control":
            mode, why = "live", None
        elif missing:
            mode, why = "unavailable", "falta " + ", ".join(missing)
        elif not live:
            mode, why = "unavailable", "servidor MLX apagado en " + base_url
        else:
            mode, why = "live", None
        out[key] = {**info, "mode": mode, "why": why}
    return out


def traces():
    found = []
    for directory in TRACE_DIRS:
        for path in sorted(directory.rglob("*.json.gz")):
            found.append(path.relative_to(ROOT).as_posix())
    return found


def handler_for(args):
    from run_benchmark import load_engine
    ns = load_engine()
    split = json.loads((ROOT / "finetune/data/split.json").read_text())
    selector_system = prompt_bundle(AgentConfig())["selector_paginas"]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def json(self, payload, status=200):
            data = json.dumps(jsonable(payload), ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def stream_start(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            state = {"open": True}

            def send(event):
                if not state["open"]:
                    return
                try:
                    self.wfile.write(("data: " + json.dumps(jsonable(event), ensure_ascii=False) + "\n\n").encode())
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    state["open"] = False   # la partida termina y se guarda igual
            return send

        def do_GET(self):
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            if url.path in FRONTEND_FILES:
                filename, content_type = FRONTEND_FILES[url.path]
                path = Path(__file__).parent / filename
                if not path.is_file():
                    return self.json({"error": "Recurso no encontrado"}, 404)
                data = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif url.path == "/api/config":
                self.json({"names": ns["NAMES"], "split": split, "roster": ns["CHAMPIONS"],
                           "systems": availability(args.base_url), "traces": traces(),
                           "replays": {key: "results/d4/runs/test_v1/" + file
                                       for key, file in REPLAY_FILES.items()},
                           "model": "Ministral-3-3B-Instruct-2512 · MLX 4-bit",
                           "cases": json.loads(CASES.read_text()) if CASES.exists() else []})
            elif url.path == "/api/results":
                runs = sorted((ROOT / "results/d4").glob("summary_*.json"))
                self.json(json.loads(runs[-1].read_text()) if runs else {})
            elif url.path == "/api/trace":
                name = q.get("file", "")
                if name not in traces():
                    return self.json({"error": "Traza desconocida"}, 404)
                payload = read(ROOT / name)
                record = next((r for r in payload["records"] if r["target"] == q.get("target")), None)
                if record is None:
                    return self.json({"error": "Ese secreto no está en la traza"}, 404)
                self.json({"record": record, "label": payload.get("weights", "") + "/" + payload["variant"], "file": name})
            elif url.path == "/api/play":
                self.play(q)
            elif url.path == "/api/selector":
                self.selector(q)
            else:
                self.json({"error": "No encontrado"}, 404)

        def play(self, q):
            system, target = q.get("system", "d4"), q.get("target", "")
            info = availability(args.base_url).get(system)
            if target not in ns["CHAMPIONS"] or info is None:
                return self.json({"error": "Secreto o sistema inválidos"}, 400)
            if info["mode"] != "live":
                return self.json({"error": f"{info['label']}: no disponible ({info['why']})"}, 409)
            send = self.stream_start()
            uses_model = info["kind"] != "control"
            if uses_model and not LOCK.acquire(blocking=False):
                send({"kind": "queued"})
                LOCK.acquire()
            try:
                send({"kind": "start", "system": system, "label": info["label"], "mode": "live"})
                start = time.monotonic()
                if info["kind"] == "agents":
                    agents, client = build_system(system, args.base_url, observer=send)
                    record = agents.play(target)
                    config = describe(system, client, "d3")
                elif info["kind"] == "control":
                    record = algorithmic_control(ns, target)
                    for event in record["trace"]:
                        send({"kind": "game_feedback", "turn": event["turn"], "event": event})
                    config = {"algorithm": "primer compatible con todo el feedback público", "llm": False}
                else:
                    adapter = str(ROOT / info["adapter"]) if info.get("adapter") else None
                    legacy_ns = load_fresh()
                    telemetry = build_runner(legacy_ns, "default_model", base_url=args.base_url,
                                             extra_body={"adapters": adapter} if adapter else {},
                                             submit="last-line" if adapter else "whole")
                    original = legacy_ns["query_model"]

                    def request(messages, original=original):
                        send({"kind": "model_call", "agent": system, "messages": messages[-1:]})
                        return original(messages)

                    def show(event, game_number=None):
                        sample = telemetry[-1] if telemetry else {}
                        send({"kind": "model_output", "agent": system, "content": sample.get("model_output", ""),
                              "latency_s": sample.get("latency_s")})
                        send({"kind": "game_feedback", "turn": event.get("turn"), "event": event})
                    legacy_ns["query_model"], legacy_ns["show_event"] = request, show
                    record = legacy_game(legacy_ns, target, 1, telemetry)
                    config = {"adapter": info.get("adapter"), "max_tokens": 64, "protocol": system}
                record["wall_seconds"] = round(time.monotonic() - start, 2)
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                path = ROOT / "results/d4/app_runs" / f"{stamp}_{system}.json.gz"
                atomic_json(path, {"system": system, "config": config, "record": record})
                send({"kind": "finished", "record": {k: v for k, v in record.items() if k != "agent_trace"},
                      "calls": sum(e["kind"] == "model_call" for e in record.get("agent_trace", [])) or len(record["trace"]),
                      "saved": str(path.relative_to(ROOT))})
            except Exception as exc:
                send({"kind": "error", "error": f"{type(exc).__name__}: {exc}"})
            finally:
                if uses_model:
                    LOCK.release()

        def selector(self, q):
            """Una misma entrada del Selector con base, D3 o D4: la salida y su verificación por reglas."""
            cases = json.loads(CASES.read_text()) if CASES.exists() else []
            case = next((c for c in cases if c["id"] == q.get("case")), None)
            weights = q.get("weights", "d4")
            adapters = {"base": None, "d3": D3_ADAPTER, "d4": D4_ADAPTER}
            if case is None or weights not in adapters:
                return self.json({"error": "Caso o pesos inválidos"}, 400)
            if adapters[weights] and not (ROOT / adapters[weights] / "adapters.safetensors").exists():
                return self.json({"error": f"No disponible: falta {adapters[weights]}"}, 409)
            if not server_ok(args.base_url):
                return self.json({"error": "No disponible: servidor MLX apagado"}, 409)
            if not LOCK.acquire(blocking=False):
                return self.json({"error": "Hay una ejecución en curso"}, 409)
            try:
                adapter = str((ROOT / adapters[weights]).resolve()) if adapters[weights] else None
                url = dedicated_servers().get(adapter, args.base_url)   # un servidor por adaptador si está arriba
                client = ModelClient(url, adapter=adapter, max_tokens=PAGE_MAX_TOKENS)
                messages = [{"role": "system", "content": selector_system},
                            {"role": "user", "content": json.dumps(case["payload"], ensure_ascii=False)}]
                sample = client.complete(messages, max_tokens=PAGE_MAX_TOKENS, prefix=PAGE_PREFIX, temperature=0)
                verdicts, candidates, error = parse_selector(sample["content"])
                truth = truth_for_page(case["payload"], ns["CHAMPIONS"])
                score = score_page(case["payload"], sample["content"], ns["CHAMPIONS"], case.get("target"))
                self.json({"weights": weights, "content": sample["content"], "latency_s": sample["latency_s"],
                           "verdicts": verdicts, "candidates": candidates, "error": error,
                           "truth": {n: ("ok" if not v else v[0]) for n, v in truth.items()}, "score": score,
                           "messages": messages})
            except Exception as exc:
                self.json({"error": f"{type(exc).__name__}: {exc}"}, 500)
            finally:
                LOCK.release()

    def load_fresh():
        from run_benchmark import load_engine as fresh
        return fresh()

    return Handler


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8767)
    p.add_argument("--base-url", default="http://127.0.0.1:8083/v1")
    args = p.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(args))
    print(f"Demo D4: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
