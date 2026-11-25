"""Revisión de las etiquetas del dataset del Selector.

1. Re-verificación automática de TODOS los ejemplos con una implementación de las
   reglas escrita aparte (no reutiliza `agents_d3.state.violations`): cada fila marcada
   "ok" debe cumplir todo, y cada "x campo" debe fallar justo en ese campo. También
   comprueba que el secreto de la partida, si está en la página y no excluido, quede ok.
2. Muestra estratificada para revisión manual (results/d4/revision_manual/muestra.md),
   con casillas para registrar el veredicto del revisor.

    .venv-ft/bin/python -m agents_d4.review_data
"""
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "finetune/data/d4_selector"
OUT = ROOT / "results/d4/revision_manual"
SEED = 4242
SAMPLE = {"amarillo_dificil": 20, "amarillo": 8, "con_candidatos": 6, "vacia": 6}


def parse_rows(text):
    lines = text.strip().splitlines()
    header = lines[0].split("|")
    rows = {}
    for line in lines[1:]:
        cells = dict(zip(header, line.split("|")))
        rows[cells["name"]] = cells
    return header, rows


def values(cell):
    return {v.strip() for v in cell.split(",") if v.strip()}


def failing_fields(cells, memory, years, excluded):
    """Reglas del juego leídas de la página tal como la ve el Selector."""
    if cells["name"] in excluded:
        return ["excluded"]
    fails = []
    for field, want in (memory.get("green") or {}).items():
        if values(cells[field]) != set(want):
            fails.append(field)
    for field, banned in (memory.get("gray") or {}).items():
        if values(cells[field]) & set(banned):
            fails.append(field)
    for field, clauses in (memory.get("yellow") or {}).items():
        have = values(cells[field])
        if any(not (have & set(c)) or have == set(c) for c in clauses):
            fails.append(field)
    if years is not None and int(cells["release_year"]) not in years:
        fails.append("release_year")
    return fails


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", default=str(DATA))
    p.add_argument("--tag", default="", help="sufijo de los archivos de salida (p. ej. _r2)")
    p.add_argument("--no-sample", action="store_true", help="sólo la re-verificación automática")
    args = p.parse_args()
    data = Path(args.data)
    rows = [json.loads(l) for l in (data / "train.jsonl").read_text().splitlines()]
    meta = [json.loads(l) for l in (data / "train_meta.jsonl").read_text().splitlines()]
    problems, checked_rows = [], 0
    for ex, m in zip(rows, meta):
        payload = json.loads(ex["messages"][1]["content"])
        reply = json.loads(ex["messages"][2]["content"])
        _, page = parse_rows(payload["rows"])
        years = set(payload["years_allowed"]) if "years_allowed" in payload else None
        verdicts = {}
        for item in reply["revision"]:
            name, _, rest = item.rpartition(" ok") if item.endswith(" ok") else (item.rsplit(" x ", 1)[0], None, item.rsplit(" x ", 1)[1])
            verdicts[name] = "ok" if item.endswith(" ok") else rest
        if list(verdicts) != list(page):
            problems.append((m["i"], "orden o filas distintas a la página"))
        for name, cells in page.items():
            checked_rows += 1
            fails = failing_fields(cells, payload["memory"], years, set(payload["excluded"]))
            v = verdicts.get(name)
            if (v == "ok") != (not fails) or (v != "ok" and v not in fails):
                problems.append((m["i"], f"{name}: etiqueta {v}, reglas {fails}"))
        if set(reply["candidates"]) != {n for n, v in verdicts.items() if v == "ok"}:
            problems.append((m["i"], "candidates no coincide con los ok"))
        if m["target"] in page and m["target"] not in payload["excluded"] and verdicts.get(m["target"]) != "ok":
            problems.append((m["i"], f"el secreto {m['target']} no quedó ok"))
    OUT.mkdir(parents=True, exist_ok=True)
    auto = {"examples": len(rows), "rows_checked": checked_rows, "problems": problems[:50], "n_problems": len(problems)}
    (OUT / f"verificacion_automatica{args.tag}.json").write_text(json.dumps(auto, ensure_ascii=False, indent=1))
    print(f"{len(rows)} ejemplos, {checked_rows} filas re-verificadas, {len(problems)} discrepancias")
    if args.no_sample:
        return
    rng = random.Random(SEED)
    by_kind = {}
    for ex, m in zip(rows, meta):
        by_kind.setdefault(m["kind"], []).append((ex, m))
    sample = []
    for kind, n in SAMPLE.items():
        sample += rng.sample(by_kind.get(kind, []), min(n, len(by_kind.get(kind, []))))
    lines = ["# Muestra para revisión manual de etiquetas del Selector", "",
             f"{len(sample)} ejemplos de `finetune/data/d4_selector/train.jsonl`, estratificados por tipo "
             f"({', '.join(f'{k}: {v}' for k, v in SAMPLE.items())}), semilla {SEED}. Para cada fila marcada, el revisor "
             "comprueba a mano contra el estado (`memory`, `excluded`, `years_allowed`) si el veredicto es correcto y "
             "anota ✔ o ✘ en la columna Revisor. Las filas no marcadas se revisan sólo si el revisor lo decide.", ""]
    for ex, m in sample:
        payload = json.loads(ex["messages"][1]["content"])
        reply = json.loads(ex["messages"][2]["content"])
        lines += [f"## Ejemplo {m['i']} · {m['kind']} · página {m['page']} · secreto (sólo motor) {m['target']}", "",
                  "Estado: `" + json.dumps(payload["memory"], ensure_ascii=False) + "`  ",
                  f"Excluidos: {', '.join(payload['excluded']) or '—'} · years_allowed: {payload.get('years_allowed', '—')}", "",
                  "| Fila | Atributos | Etiqueta | Revisor |", "|---|---|---|---|"]
        _, page = parse_rows(payload["rows"])
        for item, (name, cells) in zip(reply["revision"], page.items()):
            attrs = " · ".join(cells[f] for f in cells if f != "name")
            lines.append(f"| {name} | {attrs} | {item} | |")
        lines += ["", f"candidates: {', '.join(reply['candidates']) or '(vacía)'}", ""]
    (OUT / "muestra.md").write_text("\n".join(lines) + "\n")
    print("muestra:", Counter(m["kind"] for _, m in sample), "→", (OUT / "muestra.md").relative_to(ROOT))


if __name__ == "__main__":
    main()
