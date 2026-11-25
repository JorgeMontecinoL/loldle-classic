"""Conjuntos del Selector tomados de trazas reales del D3 (entradas que el sistema produjo).

    d3_valid_trace  llamadas del Selector en la validación del D3 (15 secretos de validación)
    d3_test_trace   llamadas del Selector en la prueba del D3 (30 secretos de prueba)

Se conserva cada entrada distinta una vez (los reintentos muestreados repiten la entrada).
El secreto de la partida queda como metadato para medir si el Selector lo descarta;
el modelo nunca lo recibe.

    .venv-ft/bin/python -m agents_d4.make_sets
"""
import gzip
import hashlib
import json
from pathlib import Path

from .selector_metrics import selector_calls

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {"d3_valid_trace": "results/d3/dev/valid_paginas_full.json.gz",
           "d3_test_trace": "results/d3/raw/test_paginas_full.json.gz"}
OUT = ROOT / "results/d4/selector_sets"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        data = json.loads(gzip.decompress((ROOT / source).read_bytes()))
        seen, rows = set(), []
        for record in data["records"]:
            for call in selector_calls(record):
                key = hashlib.sha1(json.dumps(call["payload"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                rows.append({"id": f"{name}-{len(rows):04d}", "target": record["target"], "kind": "traza",
                             "turn": call["turn"], "d3_output": call["content"] if call["sampling"]["temperature"] == 0 else None,
                             "source": source, "payload": call["payload"]})
        with (OUT / f"{name}.jsonl").open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(name, len(rows), "entradas distintas de", source)


if __name__ == "__main__":
    main()
