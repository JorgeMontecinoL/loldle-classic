"""Evaluación reanudable de agentes y controles, sin sobrescribir resultados D1/D2."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import gzip
from pathlib import Path
import time

from run_benchmark import load_engine, build_runner
from .client import ModelClient
from .runtime import AgentConfig, AgentSystem, algorithmic_control
from .state import public_history, validate_move

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ("full", "no_examples", "no_previous_state", "no_revision", "direct", "d2_lora", "d2_tool", "algorithmic")


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    tmp.write_bytes(gzip.compress(encoded, mtime=0) if path.name.endswith('.gz') else encoded)
    tmp.replace(path)


def legacy_game(ns, target, index, telemetry):
    mark = len(telemetry)
    record = ns["play_game"](target, index)
    for event, sample in zip(record["trace"], telemetry[mark:]):
        event["model_output"] = sample.get("model_output")
        event["latency_s"] = sample.get("latency_s")
        event["api_error"] = sample.get("error")
        event["prompt_tokens"] = sample.get("prompt_tokens")
        event["completion_tokens"] = sample.get("completion_tokens")
        event["retries"] = sample.get("retries", 0)
    for i, event in enumerate(record["trace"]):
        errors = validate_move(event.get("guess"), public_history(ns, record["trace"][:i]), ns["CHAMPIONS"])["errors"]
        event["strict_violation"], event["strict_errors"] = bool(errors), errors
    return record


def evaluate(args):
    if args.split == 'test':
        from .select import source_hashes
        frozen = json.loads((ROOT / 'results/d3/selection.json').read_text())
        if frozen['source_hashes'] != source_hashes():
            raise ValueError('Protocolo modificado después de selección. Revalida antes de prueba.')
        if args.variant in ('full', 'no_examples', 'no_previous_state', 'no_revision'):
            if args.weights != frozen['selected_weights'] or args.max_tokens != frozen['max_tokens']:
                raise ValueError('Prueba requiere los pesos y presupuesto seleccionados en validación.')
            limits = frozen['agent_config']
            if (args.max_calls_per_turn, args.max_calls_per_game) != (limits['max_calls_per_turn'], limits['max_calls_per_game']):
                raise ValueError('Prueba requiere los límites seleccionados en validación.')
    split = json.loads((ROOT / "finetune/data/split.json").read_text())
    targets = split[args.split][:args.limit] if args.limit else split[args.split]
    config = AgentConfig(examples=args.variant != "no_examples", previous_state=args.variant != "no_previous_state",
                         revision=args.variant != "no_revision", max_calls_per_turn=args.max_calls_per_turn,
                         max_calls_per_game=args.max_calls_per_game)
    adapter = str((ROOT / "finetune/adapters/final").resolve()) if args.weights == "lora" else None
    if args.variant in ("d2_lora", "d2_tool"):
        adapter = str((ROOT / "finetune/adapters/final").resolve())
    if args.variant == "direct":
        adapter = None
    client = ModelClient(args.base_url, args.model, adapter, args.max_tokens)
    system = AgentSystem(client, config)
    meta = system.metadata()
    effective_weights = "lora" if adapter else "base"
    if args.variant == "algorithmic":
        effective_weights = "none"
        meta = {"algorithm": "first full-public-feedback-compatible", "llm": False}
    elif args.variant in ("direct", "d2_lora", "d2_tool"):
        meta = {"base_url": args.base_url, "model": args.model, "adapter": meta["adapter"],
                "adapter_sha256": meta["adapter_sha256"], "max_tokens_per_call": 64,
                "temperature": 0, "protocol": args.variant, "max_attempts": 10}
    filename = f"{args.split}_{effective_weights}_{args.variant}" + (f"_n{args.limit}" if args.limit else "") + ".json.gz"
    path = ROOT / args.out / filename
    payload = {"variant": args.variant, "weights": effective_weights, "split": args.split,
               "targets": targets, "config": meta, "started_at": datetime.now(timezone.utc).isoformat(),
               "records": [], "complete": False}
    payload['model_name'], payload['params_b'] = filename.split('.json')[0], 3.4
    if path.exists() and not args.force:
        saved = json.loads(gzip.decompress(path.read_bytes()))
        if saved["config"] != meta or saved["targets"] != targets:
            raise ValueError("Configuración/prompts distintos: usa otro --out o --force")
        payload = saved
    ns, telemetry = system.ns, []
    if args.variant in ("direct", "d2_lora", "d2_tool"):
        extra = {"adapters": adapter} if adapter else {}
        mode = {"direct": "whole", "d2_lora": "last-line", "d2_tool": "state-tool"}[args.variant]
        telemetry = build_runner(ns, args.model, api_model=args.model, base_url=args.base_url, extra_body=extra, submit=mode)
    for i, target in enumerate(targets):
        if i < len(payload["records"]):
            continue
        if args.variant == "algorithmic":
            record = algorithmic_control(ns, target, i + 1)
        elif args.variant in ("direct", "d2_lora", "d2_tool"):
            record = legacy_game(ns, target, i + 1, telemetry)
        else:
            record = system.play(target, i + 1)
        payload["records"].append(record)
        payload["summary"] = ns["summarize"](payload["records"])
        payload["complete"] = len(payload["records"]) == len(targets)
        atomic_json(path, payload)
        print(f"{args.weights}/{args.variant} {i + 1}/{len(targets)} {target}: "
              f"solved={record['solved']} attempts={record['attempts_used']} "
              f"calls={sum(e['kind']=='model_call' for e in record.get('agent_trace',[]))} "
              f"stop={record.get('stop_reason')}", flush=True)
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=("valid", "test", "train"), default="valid")
    p.add_argument("--weights", choices=("base", "lora"), default="base")
    p.add_argument("--variant", choices=VARIANTS, default="full")
    p.add_argument("--limit", type=int)
    p.add_argument("--base-url", default="http://127.0.0.1:8083/v1")
    p.add_argument("--model", default="default_model")
    p.add_argument("--max-tokens", type=int, default=768)
    p.add_argument("--max-calls-per-turn", type=int, default=18)
    p.add_argument("--max-calls-per-game", type=int, default=160)
    p.add_argument("--out", default="results/d3/dev")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    if args.limit is not None and args.limit < 1:
        p.error("--limit debe ser positivo")
    print(evaluate(args))


if __name__ == "__main__":
    main()
