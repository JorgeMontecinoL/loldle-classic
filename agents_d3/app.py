"""Demo D3 real y visor de trazas guardadas. python -m agents_d3.app"""
import argparse
import json
import random
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from run_benchmark import load_engine, build_runner
from .analyze import read
from .client import ModelClient
from .evaluate import ADAPTERS, ROOT, SEARCH, atomic_json, legacy_game
from .runtime import AgentSystem, AgentConfig
from .state import jsonable

LOCK = threading.Lock()


def handler_for(args):
    ns = load_engine()
    split = json.loads((ROOT / 'finetune/data/split.json').read_text())

    class Handler(BaseHTTPRequestHandler):
        def json(self, payload, status=200):
            data = json.dumps(jsonable(payload), ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            if url.path == '/':
                data = (Path(__file__).parent / 'index.html').read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif url.path == '/api/config':
                self.json({'names': ns['NAMES'], 'split': split, 'weights': args.weights,
                           'roster': ns['CHAMPIONS'],
                           'model': 'Ministral-3-3B-Instruct-2512 · MLX 4-bit',
                           'runs': [p.name for p in sorted((ROOT / 'results/d3/raw').glob('*.json.gz'))]})
            elif url.path == '/api/results':
                p = ROOT / 'results/d3/summary.json'
                self.json(read(p) if p.exists() else {'rows': [], 'comparisons': {}})
            elif url.path == '/api/trace':
                name = query.get('file', [''])[0]
                directory = ROOT / 'results/d3/raw'
                allowed = {p.name: p for p in directory.glob('*.json.gz')}
                if name not in allowed:
                    return self.json({'error': 'Traza desconocida'}, 404)
                payload = read(allowed[name])
                record = next((r for r in payload['records'] if r['target'] == query.get('target', [''])[0]), None)
                self.json({'record': record, 'variant': payload['variant'], 'weights': payload['weights']})
            elif url.path == '/api/play':
                target = query.get('target', [''])[0]
                variant = query.get('variant', ['full'])[0]
                if target not in ns['CHAMPIONS'] or variant not in ('full', 'direct', 'd2_lora'):
                    return self.json({'error': 'Objetivo o variante inválidos'}, 400)
                if not LOCK.acquire(blocking=False):
                    return self.json({'error': 'Hay una partida en curso'}, 409)
                disconnected = False
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()

                def send(event):
                    nonlocal disconnected
                    if disconnected:
                        return
                    try:
                        self.wfile.write(('data: ' + json.dumps(jsonable(event), ensure_ascii=False) + '\n\n').encode())
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        # Se termina y registra la partida aunque el navegador se cierre.
                        disconnected = True

                try:
                    send({'kind': 'start', 'variant': variant, 'mode': 'live', 'target': target})
                    adapter = str(ROOT / ADAPTERS[args.weights]) if ADAPTERS[args.weights] else None
                    client = ModelClient(args.base_url, adapter=adapter)
                    system = AgentSystem(client, AgentConfig(search=SEARCH.get(args.weights, "d2")), observer=send)
                    if variant == 'full':
                        record = system.play(target)
                    else:
                        legacy_adapter = str(ROOT / 'finetune/adapters/final') if variant == 'd2_lora' else None
                        system = AgentSystem(ModelClient(args.base_url, adapter=legacy_adapter, max_tokens=64))
                        telemetry = build_runner(system.ns, 'default_model', base_url=args.base_url,
                            extra_body={'adapters': legacy_adapter} if legacy_adapter else {},
                            submit='last-line' if legacy_adapter else 'whole')
                        legacy_events = []
                        original_query = system.ns['query_model']
                        def request(messages):
                            event = {'kind': 'model_call', 'agent': variant, 'messages': messages}
                            legacy_events.append(event)
                            send(event)
                            return original_query(messages)
                        system.ns['query_model'] = request
                        def output(event):
                            sample = telemetry[-1] if telemetry else {}
                            response = {'kind': 'model_output', 'agent': variant, 'content': sample.get('model_output', '')}
                            feedback = {'kind': 'game_feedback', 'event': event}
                            legacy_events.extend([response, feedback])
                            send(response)
                            send(feedback)
                        system.ns['show_event'] = output
                        record = legacy_game(system.ns, target, 1, telemetry)
                        record['agent_trace'] = legacy_events
                    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    path = ROOT / 'results/d3/app_runs' / f'{stamp}_{variant}.json.gz'
                    atomic_json(path, {'variant': variant, 'config': system.metadata(), 'record': record})
                    send({'kind': 'finished', 'record': record, 'saved': str(path.relative_to(ROOT))})
                except Exception as exc:
                    send({'kind': 'error', 'error': f'{type(exc).__name__}: {exc}'})
                finally:
                    LOCK.release()
            else:
                self.json({'error': 'No encontrado'}, 404)

    return Handler


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=8766)
    p.add_argument('--base-url', default='http://127.0.0.1:8083/v1')
    p.add_argument('--weights', choices=tuple(ADAPTERS), default='base')
    args = p.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(args))
    print(f'Demo D3: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
