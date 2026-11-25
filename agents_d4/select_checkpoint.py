"""Elige el adaptador del Selector usando sólo validación y lo copia a finetune/adapters/d4_selector/.

Regla (fijada antes de ver los resultados de los candidatos): mayor número de páginas
exactas en la unión de `d3_valid_trace[amarillo]` y `valid_generado[amarillo]`; desempate
por más filas compatibles conservadas en páginas con amarillo de un valor y, después, el
candidato posterior en la lista. Registro: `results/d4/checkpoint_selection.json`.

    .venv-ft/bin/python -m agents_d4.select_checkpoint --candidates r1_1000=finetune/adapters/d4_selector_ckpts/r1_1000 ...
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINAL = ROOT / "finetune/adapters/d4_selector"
SETS = ("d3_valid_trace", "valid_generado")


def load(label):
    total = {"exact": 0, "pages": 0, "ys_tp": 0, "ys_fits": 0, "tp": 0, "fits": 0, "target_dropped": 0, "target_pages": 0, "protocol": 0}
    for s in SETS:
        summary = json.loads((ROOT / f"results/d4/selector_eval/{s}__{label}__amarillo.summary.json").read_text())["summary"]
        total["exact"] += summary["exact_pages"]
        total["pages"] += summary["pages"]
        total["tp"] += summary["true_pos"]
        total["fits"] += summary["fits"]
        total["target_dropped"] += summary["target_dropped"]
        total["target_pages"] += summary["target_pages"]
        total["protocol"] += summary["protocol_errors"]
        total["ys_fits"] += summary["yellow_single_fits"]
        total["ys_tp"] += round((summary["yellow_single_recall"] or 0) * summary["yellow_single_fits"])
    return total


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidates", nargs="+", required=True, help="nombre=carpeta del adaptador")
    p.add_argument("--reference", default="d3_d3", help="etiqueta del Selector D3 en validación, sólo para el registro")
    args = p.parse_args()
    rows = []
    for order, item in enumerate(args.candidates):
        name, path = item.split("=", 1)
        rows.append({"candidate": name, "path": path, "order": order, **load(f"ckpt_{name}")})
    best = max(rows, key=lambda r: (r["exact"], r["ys_tp"], r["order"]))
    FINAL.mkdir(parents=True, exist_ok=True)
    src = ROOT / best["path"]
    shutil.copy(src / "adapters.safetensors", FINAL / "adapters.safetensors")
    shutil.copy(src / "adapter_config.json", FINAL / "adapter_config.json")
    digest = hashlib.sha256((FINAL / "adapters.safetensors").read_bytes()).hexdigest()
    record = {"rule": " ".join(__doc__.split("\n\n")[1].split()), "candidates": rows, "selected": best["candidate"],
              "source": best["path"], "adapter_sha256": digest, "reference_d3_valid": load(args.reference),
              "selected_at": datetime.now(timezone.utc).isoformat(), "test_used_for_selection": False}
    (ROOT / "results/d4/checkpoint_selection.json").write_text(json.dumps(record, ensure_ascii=False, indent=1))
    print(json.dumps(record, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
