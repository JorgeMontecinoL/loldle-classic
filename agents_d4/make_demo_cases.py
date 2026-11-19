"""Entradas reales e idénticas del Selector para la demo y el video (base vs D3 vs D4).

Toma, de la traza de prueba del D3, la primera llamada a temperatura 0 en la que el
Selector descartó al secreto de una partida detenida (Morgana, Ashe, Soraka, Thresh)
y una llamada sin amarillos como control. El secreto queda como metadato de la
interfaz; la entrada del Selector es exactamente la del D3.

    .venv-ft/bin/python -m agents_d4.make_demo_cases
"""
import gzip
import json
from pathlib import Path

from run_benchmark import load_engine
from .selector_metrics import score_page, selector_calls

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "results/d3/raw/test_paginas_full.json.gz"


def main():
    ns = load_engine()
    data = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    cases = []
    for target in ("Morgana", "Ashe", "Soraka", "Thresh"):
        record = next(r for r in data["records"] if r["target"] == target)
        for call in selector_calls(record):
            score = score_page(call["payload"], call["content"], ns["CHAMPIONS"], target)
            # El primer descarte del secreto atribuible a un amarillo (el fallo que se entrena).
            if call["sampling"]["temperature"] == 0 and score["target_dropped"] and score["target_verdict"] in call["payload"]["memory"].get("yellow", {}):
                yellow = call["payload"]["memory"].get("yellow")
                cases.append({"id": f"{target.lower()}-t{call['turn']}-p{call['payload']['page'].split('/')[0]}",
                              "label": f"{target} · turno {call['turn']} · página {call['payload']['page']} · amarillo {json.dumps(yellow, ensure_ascii=False)} (D3 lo descartó: «{score['target_verdict']}»)",
                              "target": target, "source": SOURCE, "turn": call["turn"], "d3_output": call["content"],
                              "payload": call["payload"]})
                break
    record = next(r for r in data["records"] if r["target"] == "Mordekaiser")
    call = next(c for c in selector_calls(record) if c["turn"] == 2 and c["payload"]["page"].startswith("5/"))
    cases.append({"id": "mordekaiser-t2-p5", "label": "Mordekaiser · turno 2 · página 5/7 · control sin amarillo difícil",
                  "target": "Mordekaiser", "source": SOURCE, "turn": 2, "d3_output": call["content"], "payload": call["payload"]})
    (ROOT / "results/d4/demo_cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=1))
    for c in cases:
        print(c["id"], "|", c["label"])


if __name__ == "__main__":
    main()
