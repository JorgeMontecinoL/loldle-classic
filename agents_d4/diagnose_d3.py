"""Diagnóstico del Selector en las trazas de prueba del D3 (paginas/full).

Para cada partida detenida y cada llamada del Selector cuya página contenía al
secreto, muestra el estado que entregó Memoria, si el secreto cumplía ese estado,
el veredicto que escribió el Selector y si coincidía con el estado público real.

    .venv-ft/bin/python -m agents_d4.diagnose_d3 [--out results/d4/diagnostico_d3.json]
"""
import argparse
import gzip
import json
from pathlib import Path

from run_benchmark import load_engine
from agents_d3.state import observed_state, public_history, violations
from .selector_metrics import aggregate, score_page, selector_calls, state_for_rules

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "results/d3/raw/test_paginas_full.json.gz"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default=str(SOURCE))
    p.add_argument("--out", default="results/d4/diagnostico_d3.json")
    args = p.parse_args()
    ns = load_engine()
    roster = ns["CHAMPIONS"]
    data = json.loads(gzip.decompress(Path(args.source).read_bytes()))
    report = {"source": str(Path(args.source).relative_to(ROOT)), "games": [], "all_pages": None}
    all_scores = []
    for record in data["records"]:
        target = record["target"]
        turns_public = {}
        for i in range(len(record["trace"]) + 1):
            turns_public[i + 1] = public_history(ns, record["trace"][:i])
        game = {"target": target, "solved": record["solved"], "stop": record["stop_reason"], "pages": []}
        for call in selector_calls(record):
            score = score_page(call["payload"], call["content"], roster, target)
            all_scores.append(score)
            if not score["target_on_page"]:
                continue
            truth_state = observed_state(turns_public[call["turn"]])
            delivered = state_for_rules(call["payload"]["memory"])
            same = {k: delivered[k] for k in ("green", "gray", "yellow")} == {k: truth_state[k] for k in ("green", "gray", "yellow")} \
                and {k: v for k, v in delivered["year"].items() if v is not None} == {k: v for k, v in truth_state["year"].items() if v is not None}
            game["pages"].append({
                "turn": call["turn"], "call": call["call"], "page": call["payload"]["page"],
                "temperature": (call["sampling"] or {}).get("temperature"),
                "memory": call["payload"]["memory"], "years_allowed": call["payload"].get("years_allowed"),
                "memory_equals_public": same,
                "target_attrs": {k: (sorted(v) if isinstance(v, (set, frozenset)) else v) for k, v in roster[target].items()},
                "target_fits_memory": not violations(target, delivered, roster),
                "target_fits_public": not violations(target, truth_state, roster),
                "target_verdict": score["target_verdict"], "target_dropped": score["target_dropped"],
                "yellow_single_fields": score["yellow_single_fields"],
                "false_drop": score["false_drop"], "false_keep": score["false_keep"],
            })
        report["games"].append(game)
    report["all_pages"] = aggregate(all_scores)
    stopped = [g for g in report["games"] if g["stop"]]
    report["stopped"] = []
    for g in stopped:
        pages = g["pages"]
        drops = [x for x in pages if x["target_dropped"]]
        report["stopped"].append({
            "target": g["target"], "stop": g["stop"], "pages_with_target": len(pages),
            "target_fit_memory": sum(x["target_fits_memory"] for x in pages),
            "target_dropped": len(drops),
            "verdicts": sorted({x["target_verdict"] for x in drops if x["target_verdict"]}),
            "yellow_single": sorted({f for x in pages for f in x["yellow_single_fields"]}),
            "memory_equals_public_last": pages[-1]["memory_equals_public"] if pages else None,
        })
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(json.dumps(report["all_pages"], indent=1))
    for s in report["stopped"]:
        print(s)


if __name__ == "__main__":
    main()
