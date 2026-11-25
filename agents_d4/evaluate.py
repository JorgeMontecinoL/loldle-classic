"""Partidas completas del Entregable 4: D3 original frente a D4 (Selector ajustado).

Mismo controlador, motor, prompts, presupuesto de llamadas y temperatura que el D3
(`results/d3/selection.json`); sólo cambia el adaptador que recibe cada rol. Cada
corrida se guarda bajo su propio identificador (`--run-id`) para no reanudar sobre
trazas antiguas.

    .venv-ft/bin/python -m agents_d4.evaluate --run-id test_v1 --split test --system d3
    .venv-ft/bin/python -m agents_d4.evaluate --run-id test_v1 --split test --system d4
    # adaptador descargado de Hugging Face en lugar del local:
    .venv-ft/bin/python -m agents_d4.evaluate --run-id hf_check --split test --system d4 --adapter /ruta/al/adaptador --targets Morgana,Ashe
"""
import argparse
import gzip
import json
from dataclasses import asdict
from datetime import datetime, timezone

from agents_d3.evaluate import atomic_json
from agents_d3.runtime import AgentConfig
from agents_d3.select import source_hashes
from .runtime import ROOT, SYSTEMS, build_system, describe


def frozen_d3():
    """El protocolo del D3 no puede haber cambiado: mismos prompts, controlador y límites."""
    selection = json.loads((ROOT / "results/d3/selection.json").read_text())
    if selection["source_hashes"] != source_hashes():
        raise ValueError("Los archivos del D3 cambiaron desde su selección; la comparación no sería la misma")
    if asdict(AgentConfig()) != selection["agent_config"]:
        raise ValueError("AgentConfig distinto del seleccionado en el D3")
    return selection


def evaluate(args):
    selection = frozen_d3()
    split = json.loads((ROOT / "finetune/data/split.json").read_text())
    targets = args.targets.split(",") if args.targets else split[args.split]
    if args.limit:
        targets = targets[:args.limit]
    agents, client = build_system(args.system, args.base_url, args.prompt, adapter_override=args.adapter,
                                  max_tokens=selection["max_tokens"])
    meta = {**agents.metadata(), **describe(args.system, client, args.prompt),
            "servers": {(str(k).replace(str(ROOT) + "/", "") if k else "base"): v for k, v in client.servers.items()}}
    meta.pop("adapter", None)
    meta.pop("adapter_sha256", None)
    name = f"{args.split}_{args.system}" + ("" if args.prompt == "d3" else f"_{args.prompt}")
    path = ROOT / "results/d4/runs" / args.run_id / f"{name}.json.gz"
    payload = {"variant": "full", "weights": args.system + ("" if args.prompt == "d3" else "+" + args.prompt),
               "system": args.system, "split": args.split, "run_id": args.run_id, "targets": targets,
               "config": meta, "started_at": datetime.now(timezone.utc).isoformat(), "records": [], "complete": False,
               "model_name": name, "params_b": 3.4}
    if path.exists():
        saved = json.loads(gzip.decompress(path.read_bytes()))
        if saved["config"] != meta or saved["targets"] != targets:
            raise ValueError(f"{path} existe con otra configuración: usa otro --run-id")
        payload = saved
    ns = agents.ns
    played = 0
    for i, target in enumerate(targets):
        if i < len(payload["records"]):
            continue
        if args.max_new is not None and played >= args.max_new:
            break
        played += 1
        client.calls_by_adapter = {}
        record = agents.play(target, i + 1)
        record["calls_by_adapter"] = client.calls_by_adapter
        payload["records"].append(record)
        payload["summary"] = ns["summarize"](payload["records"])
        payload["complete"] = len(payload["records"]) == len(targets)
        atomic_json(path, payload)
        calls = sum(e["kind"] == "model_call" for e in record["agent_trace"])
        print(f"{args.system} {i + 1}/{len(targets)} {target}: solved={record['solved']} attempts={record['attempts_used']} "
              f"calls={calls} stop={record['stop_reason']} adapters={record['calls_by_adapter']}", flush=True)
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", required=True)
    p.add_argument("--split", choices=("valid", "test", "train"), default="valid")
    p.add_argument("--system", choices=tuple(SYSTEMS), default="d4")
    p.add_argument("--prompt", choices=("d3", "amarillo"), default="d3")
    p.add_argument("--adapter", help="adaptador del Selector para d4 (checkpoint o descargado de Hugging Face)")
    p.add_argument("--targets", help="lista separada por comas, en lugar del split completo")
    p.add_argument("--limit", type=int)
    p.add_argument("--max-new", type=int, help="juega como mucho N partidas nuevas y sale (para alternar sistemas)")
    p.add_argument("--base-url", default="http://127.0.0.1:8083/v1")
    print(evaluate(p.parse_args()))


if __name__ == "__main__":
    main()
