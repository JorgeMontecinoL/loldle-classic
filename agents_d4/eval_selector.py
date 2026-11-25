"""Evaluación del Selector aislado: mismas páginas y estados, distintos pesos o prompts.

Cada línea del conjunto (`results/d4/selector_sets/*.jsonl`) es una entrada real del
Selector: el JSON que el controlador le envía (estado de Memoria, excluidos, página,
years_allowed) más metadatos para medir (secreto de la partida si existe, origen).
El modelo recibe sólo el JSON; los metadatos quedan en el evaluador.

    .venv-ft/bin/python -m agents_d4.eval_selector --set d3_test_trace --weights d4
    .venv-ft/bin/python -m agents_d4.eval_selector --set valid_generado --weights d3 --prompt amarillo
"""
import argparse
import json
import time
from pathlib import Path

from run_benchmark import load_engine
from agents_d3.client import ModelClient
from agents_d3.runtime import AgentConfig, PAGE_MAX_TOKENS, PAGE_PREFIX, prompt_bundle
from .runtime import D3_ADAPTER, D4_ADAPTER, ROOT, selector_prompt
from .selector_metrics import aggregate, score_page

WEIGHTS = {"base": None, "d3": D3_ADAPTER, "d4": D4_ADAPTER}
SETS = ROOT / "results/d4/selector_sets"


def run(args):
    ns = load_engine()
    roster = ns["CHAMPIONS"]
    system = selector_prompt(prompt_bundle(AgentConfig())["selector_paginas"], args.prompt)
    adapter = args.adapter or WEIGHTS[args.weights]
    adapter = str((ROOT / adapter).resolve()) if adapter else None
    client = ModelClient(args.base_url, adapter=adapter, max_tokens=PAGE_MAX_TOKENS)
    rows = [json.loads(line) for line in (SETS / f"{args.set}.jsonl").read_text().splitlines() if line.strip()]
    if args.only_yellow:
        # Sólo páginas cuyo estado trae alguna cláusula amarilla (la regla que falla en el D3).
        rows = [r for r in rows if (r["payload"].get("memory") or {}).get("yellow")]
    if args.limit:
        rows = rows[:args.limit]
    label = args.label or f"{args.weights}_{args.prompt}"
    out = ROOT / args.out / f"{args.set}__{label}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if out.exists():
        for line in out.read_text().splitlines():
            item = json.loads(line)
            done[item["id"]] = item
    with out.open("a") as stream:
        for row in rows:
            if row["id"] in done:
                continue
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": json.dumps(row["payload"], ensure_ascii=False)}]
            start = time.monotonic()
            sample = client.complete(messages, max_tokens=PAGE_MAX_TOKENS, prefix=PAGE_PREFIX, temperature=0)
            item = {"id": row["id"], "content": sample["content"], "latency_s": round(time.monotonic() - start, 3),
                    "finish_reason": sample.get("finish_reason"), "completion_tokens": (sample.get("usage") or {}).get("completion_tokens")}
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
            stream.flush()
            done[row["id"]] = item
            if len(done) % 25 == 0:
                print(f"{label} {args.set}: {len(done)}/{len(rows)}", flush=True)
    scores = []
    for row in rows:
        score = score_page(row["payload"], done[row["id"]]["content"], roster, row.get("target"))
        score.update(id=row["id"], kind=row.get("kind"))
        scores.append(score)
    summary = {"set": args.set + ("[amarillo]" if args.only_yellow else ""), "label": label, "weights": args.weights, "adapter": args.adapter or WEIGHTS[args.weights],
               "prompt": args.prompt, "n": len(rows), **aggregate(scores),
               "seconds": round(sum(done[r["id"]]["latency_s"] for r in rows), 1)}
    summary_path = out.with_name(out.stem + ("__amarillo" if args.only_yellow else "") + ".summary.json")
    summary_path.write_text(json.dumps({"summary": summary, "pages": scores}, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--set", required=True)
    p.add_argument("--weights", choices=tuple(WEIGHTS), default="d4")
    p.add_argument("--adapter", help="ruta de un adaptador (checkpoint o descargado), en lugar de --weights")
    p.add_argument("--prompt", choices=("d3", "amarillo"), default="d3")
    p.add_argument("--label")
    p.add_argument("--limit", type=int)
    p.add_argument("--only-yellow", action="store_true", help="sólo entradas con alguna cláusula amarilla")
    p.add_argument("--base-url", default="http://127.0.0.1:8083/v1")
    p.add_argument("--out", default="results/d4/selector_eval")
    run(p.parse_args())


if __name__ == "__main__":
    main()
