"""Dataset del Entregable 4: sólo el rol Selector (búsqueda por páginas).

Cada ejemplo es exactamente la llamada que el controlador del D3 hace al Selector
(`agents_d3/runtime.py::_decide_paginas`): el mismo prompt de sistema, el mismo JSON
de entrada (`memory`, `excluded`, `page`, `rows`, `years_allowed`) y, como salida, el
JSON que continúa el prefill '{"action":"listar","revision":' con un veredicto por fila
y la lista de filas compatibles.

Etiquetas: se calculan con las reglas del juego (`agents_d3.state.violations`) sobre el
estado público reconstruido del historial (`observed_state`). No interviene ningún
modelo de lenguaje. El secreto sólo se usa para simular el feedback del juego al armar
el historial, como en el D2 y el D3; nunca entra en la entrada del Selector.

Diagnóstico que motiva el muestreo (results/d4/diagnostico_d3.json): en la prueba del
D3, con una cláusula amarilla de un solo valor en el estado, el Selector conservó sólo
13 de 58 filas compatibles, y en Morgana, Thresh, Ashe y Soraka descartó al secreto
por el campo amarillo. Por eso se sobrerrepresentan estados con amarillos y páginas
con filas que cumplen o rompen esas cláusulas, sin dejar fuera páginas comunes,
páginas sin candidatos y excluidos.

Partición: la del D2/D3 (`finetune/data/split.json`), por campeón secreto y antes de
generar historiales: 128 secretos de entrenamiento, 15 de validación, 30 de prueba.
Los conjuntos de evaluación del Selector (valid_generado, test_generado) se generan
con secretos de validación y prueba y semillas distintas.

    .venv-ft/bin/python finetune/make_data_d4.py
"""
import argparse
import copy
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "finetune"))

from run_benchmark import load_engine  # noqa: E402
from make_data import split_targets  # noqa: E402
from make_data_d3 import compact, play  # noqa: E402
from agents_d3.runtime import AgentConfig, AgentSystem, PAGE_PREFIX, prompt_bundle, years_allowed  # noqa: E402
from agents_d3.state import SETS, observed_state, public_history, violations  # noqa: E402

DATA_SEED = 4040
OUT = ROOT / "finetune/data/d4_selector"
SETS_DIR = ROOT / "results/d4/selector_sets"


def verdicts_for(names, state, excluded, roster):
    out, fits = [], []
    for n in names:
        if n in excluded:
            out.append(f"{n} x excluded")
            continue
        errs = violations(n, state, roster)
        if errs:
            out.append(f"{n} x {errs[0].split(':', 1)[0]}")
        else:
            out.append(f"{n} ok")
            fits.append(n)
    return out, fits


def yellow_kind(name, state, roster):
    """Cómo se relaciona una fila con las cláusulas amarillas del estado.
    'single_fit': cumple una cláusula de un valor teniendo más valores (el caso Morgana/Ashe/Soraka).
    'subset_fit': cumple siendo subconjunto estricto de la cláusula (el caso Thresh).
    'fit': cumple de otro modo. 'equal_fail' / 'disjoint_fail': rompe la cláusula."""
    kinds = set()
    attrs = roster[name]
    for field, clauses in state["yellow"].items():
        value = set(attrs[field]) if field in SETS else {attrs[field]}
        for clause in clauses:
            c = set(clause)
            if value == c:
                kinds.add("equal_fail")
            elif not value & c:
                kinds.add("disjoint_fail")
            elif len(c) == 1:
                kinds.add("single_fit")
            elif value < c:
                kinds.add("subset_fit")
            else:
                kinds.add("fit")
    return kinds


def render_memory(state, rng):
    """El estado como lo entrega Memoria: a veces con límites de año nulos, como en las trazas reales."""
    memory = compact(state)
    if rng.random() < 0.5:
        memory["year"] = {k: state["year"].get(k) for k in ("eq", "gt", "lt")}
    return memory


def page_rows(ns, history, rng, pages, system_prompt, focus):
    """Ejemplos de una partida: páginas elegidas según el diagnóstico.
    focus=True prioriza páginas con filas amarillas; si no, muestreo uniforme."""
    roster = ns["CHAMPIONS"]
    public = public_history(ns, history)
    state = observed_state(public)
    excluded = [e["guess"] for e in history]
    if history and rng.random() < 0.25:
        extra = [n for n in ns["NAMES"] if n not in excluded and not violations(n, state, roster)]
        excluded += rng.sample(extra, min(len(extra), rng.randint(1, 2)))
    memory = render_memory(state, rng)
    scored = []
    for k, (header, rows) in enumerate(pages):
        names = [r.split("|", 1)[0] for r in rows]
        verdicts, fits = verdicts_for(names, state, set(excluded), roster)
        kinds = Counter()
        for n in fits:
            # Filas compatibles que cumplen un amarillo difícil (el error observado en el D3).
            kinds.update(k_ for k_ in yellow_kind(n, state, roster) if k_.endswith("_fit"))
        for n in names:
            if n in excluded or n in fits:
                continue
            errs = violations(n, state, roster)
            if len(errs) == 1 and errs[0].split(":", 1)[0] in state["yellow"]:
                kinds["yellow_only_fail"] += 1   # casi compatible: sólo la rompe un amarillo
        scored.append((k, header, rows, names, verdicts, fits, kinds))
    hard = [s for s in scored if s[6]["single_fit"] or s[6]["subset_fit"]]
    yellow = [s for s in scored if s not in hard and (s[6]["yellow_only_fail"] or s[6]["fit"])]
    with_fit = [s for s in scored if s[5] and s not in hard and s not in yellow]
    empty = [s for s in scored if not s[5] and s not in yellow]
    if not history:
        chosen = rng.sample(scored, 1)
    elif focus:
        chosen = rng.sample(hard, min(2, len(hard))) + rng.sample(yellow, min(1, len(yellow)))
        chosen += rng.sample(with_fit, min(1, len(with_fit)))
        if rng.random() < 0.5 and empty:
            chosen += rng.sample(empty, 1)
    else:
        chosen = rng.sample(scored, min(2, len(scored)))
    out = []
    for k, header, rows, names, verdicts, fits, kinds in chosen:
        payload = {"your_role": "selector", "available_actions": ["listar"], "memory": memory, "excluded": excluded,
                   "page": f"{k + 1}/{len(pages)}", "rows": "\n".join([header] + rows)}
        allowed = years_allowed(state, roster)
        if allowed is not None:
            payload["years_allowed"] = allowed
        reply = json.dumps({"action": "listar", "revision": verdicts, "candidates": fits}, ensure_ascii=False, separators=(",", ":"))
        assert reply.startswith(PAGE_PREFIX)
        kind = ("amarillo_dificil" if kinds["single_fit"] or kinds["subset_fit"]
                else "amarillo" if kinds["yellow_only_fail"] or kinds["fit"]
                else "con_candidatos" if fits else "vacia")
        out.append({"payload": payload, "reply": reply, "kind": kind, "yellow": dict(sorted(kinds.items())), "fits": len(fits),
                    "history": [e["guess"] for e in history], "state_key": state_key(state)})
    return out


def hard_fields(name, state, roster):
    """Campos donde una fila compatible cumple un amarillo difícil (un valor, o subconjunto)."""
    out = set()
    attrs = roster[name]
    for field, clauses in state["yellow"].items():
        value = set(attrs[field]) if field in SETS else {attrs[field]}
        for clause in clauses:
            c = set(clause)
            if value & c and value != c and (len(c) == 1 or value < c):
                out.add(field)
    return out


def page_rows_r2(ns, history, rng, pages, plain):
    """Ronda 2: páginas con contraste en positions/regions/species.
    Cada página elegida tiene una fila compatible bajo un amarillo difícil y, si existe,
    filas que sólo rompen ese amarillo (iguales a la cláusula o sin intersección).
    plain=True: páginas comunes, para no olvidar el resto del formato."""
    roster = ns["CHAMPIONS"]
    state = observed_state(public_history(ns, history))
    excluded = [e["guess"] for e in history]
    if history and rng.random() < 0.2:
        extra = [n for n in ns["NAMES"] if n not in excluded and not violations(n, state, roster)]
        excluded += rng.sample(extra, min(len(extra), 1))
    memory = render_memory(state, rng)
    scored = []
    for k, (header, rows) in enumerate(pages):
        names = [r.split("|", 1)[0] for r in rows]
        verdicts, fits = verdicts_for(names, state, set(excluded), roster)
        fields = set().union(*[hard_fields(n, state, roster) for n in fits]) if fits else set()
        contrast = sum(1 for n in names if n not in excluded and n not in fits
                       and (lambda e: len(e) == 1 and e[0].split(":", 1)[0] in state["yellow"])(violations(n, state, roster)))
        scored.append((k, header, rows, verdicts, fits, fields, contrast))
    if plain:
        chosen = rng.sample(scored, min(2, len(scored)))
    else:
        hard = [s for s in scored if s[5]]
        hard.sort(key=lambda s: (-bool(s[5] & {"positions", "regions"}), -s[6], rng.random()))
        chosen = hard[:3]
    out = []
    for k, header, rows, verdicts, fits, fields, contrast in chosen:
        payload = {"your_role": "selector", "available_actions": ["listar"], "memory": memory, "excluded": excluded,
                   "page": f"{k + 1}/{len(pages)}", "rows": "\n".join([header] + rows)}
        allowed = years_allowed(state, roster)
        if allowed is not None:
            payload["years_allowed"] = allowed
        reply = json.dumps({"action": "listar", "revision": verdicts, "candidates": fits}, ensure_ascii=False, separators=(",", ":"))
        kind = "amarillo_dificil" if fields else ("con_candidatos" if fits else "vacia")
        out.append({"payload": payload, "reply": reply, "kind": kind,
                    "yellow": {"hard_fields": sorted(fields), "contrast_rows": contrast}, "fits": len(fits),
                    "history": [e["guess"] for e in history], "state_key": state_key(state)})
    return out


def generate_r2(ns, targets, rng, pages, states_per_target):
    rows = []
    for target in targets:
        made, tries = 0, 0
        while made < states_per_target and tries < 600:
            tries += 1
            history, _ = play(ns, target, rng, rng.choice([0.0, 0.25, 0.5, 0.75]))
            if not history:
                continue
            # Uno de cada 7 estados aceptados es «común» (≈14 %), decidido antes de muestrear.
            plain = made % 7 == 6
            chosen = page_rows_r2(ns, history, rng, pages, plain)
            if not plain:
                fields = set().union(*[set(r["yellow"]["hard_fields"]) for r in chosen]) if chosen else set()
                # Sobre todo positions y regions, donde falla el Selector del D3; species ya lo resuelve.
                if not fields or (not fields & {"positions", "regions"} and rng.random() < 0.7):
                    continue
            for row in chosen:
                row["target"] = target
                if row["payload"]["rows"].count("\n" + target + "|") and target not in row["payload"]["excluded"]:
                    assert f'"{target} ok"' in row["reply"], ("etiqueta inconsistente con el secreto", target)
                rows.append(row)
            made += 1
    return rows


def state_key(state):
    canon = {"green": {k: sorted(v) if isinstance(v, list) else [v] for k, v in state["green"].items()},
             "gray": {k: sorted(v) for k, v in state["gray"].items()},
             "yellow": {k: sorted(sorted(c) for c in v) for k, v in state["yellow"].items()},
             "year": {k: v for k, v in state["year"].items() if v is not None}}
    return hashlib.sha1(json.dumps(canon, sort_keys=True).encode()).hexdigest()[:12]


def generate(ns, targets, rng, pages, system_prompt, states_per_target, yellow_bias=0.6):
    """Para cada secreto, varios historiales jugados con la política del D2 y ruido.
    Con prob. yellow_bias el historial debe dejar alguna página con un amarillo difícil."""
    rows = []
    for target in targets:
        made, tries = 0, 0
        while made < states_per_target and tries < 400:
            tries += 1
            history, _ = play(ns, target, rng, rng.choice([0.0, 0.25, 0.5, 0.5]))
            if rng.random() < 0.05:
                history = []
            want_yellow = rng.random() < yellow_bias
            chosen = page_rows(ns, history, rng, pages, system_prompt, focus=bool(history))
            # Con prob. yellow_bias se exige una página con una fila compatible bajo un amarillo difícil.
            if history and want_yellow and not any(r["kind"] == "amarillo_dificil" for r in chosen):
                continue
            for row in chosen:
                row["target"] = target
                # El secreto, si está en la página y no excluido, debe quedar como compatible.
                if row["payload"]["rows"].count("\n" + target + "|") and target not in row["payload"]["excluded"]:
                    assert f'"{target} ok"' in row["reply"], ("etiqueta inconsistente con el secreto", target)
                rows.append(row)
            made += 1
    return rows


def write_training(rows, path, system_prompt):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            messages = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(row["payload"], ensure_ascii=False)},
                        {"role": "assistant", "content": row["reply"]}]
            stream.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")


def write_meta(rows, path):
    with path.open("w", encoding="utf-8") as stream:
        for i, row in enumerate(rows):
            stream.write(json.dumps({"i": i, "target": row["target"], "kind": row["kind"], "yellow": row["yellow"],
                                     "fits": row["fits"], "page": row["payload"]["page"], "history": row["history"],
                                     "state_key": row["state_key"]}, ensure_ascii=False) + "\n")


def write_set(rows, name):
    SETS_DIR.mkdir(parents=True, exist_ok=True)
    with (SETS_DIR / f"{name}.jsonl").open("w", encoding="utf-8") as stream:
        for i, row in enumerate(rows):
            stream.write(json.dumps({"id": f"{name}-{i:04d}", "target": row["target"], "kind": row["kind"],
                                     "state_key": row["state_key"], "payload": row["payload"]}, ensure_ascii=False) + "\n")


def describe(rows):
    kinds = Counter(r["kind"] for r in rows)
    single = sum(bool(r["yellow"].get("single_fit")) for r in rows)
    subset = sum(bool(r["yellow"].get("subset_fit")) for r in rows)
    return {"examples": len(rows), "targets": len({r["target"] for r in rows}), "kinds": dict(kinds),
            "pages_with_single_value_yellow_fit": single, "pages_with_subset_yellow_fit": subset,
            "fit_rows": sum(r["fits"] for r in rows), "empty_pages": sum(r["fits"] == 0 for r in rows),
            "distinct_states": len({r["state_key"] for r in rows})}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--states", type=int, default=12, help="historiales por secreto de entrenamiento")
    p.add_argument("--ronda", type=int, default=1, choices=(1, 2),
                   help="2: páginas con contraste de amarillos en positions/regions (ronda 2)")
    args = p.parse_args()
    ns = load_engine()
    test, train_t, valid_t = split_targets(ns)
    saved = json.loads((ROOT / "finetune/data/split.json").read_text())
    assert (test, train_t, valid_t) == (saved["test"], saved["train"], saved["valid"]), "la partición cambió"
    assert not (set(train_t) & (set(valid_t) | set(test))), "secretos compartidos entre particiones"
    system_prompt = prompt_bundle(AgentConfig())["selector_paginas"]
    pages = AgentSystem.roster_pages(type("S", (), {"ns": ns})())
    if args.ronda == 2:
        out = ROOT / "finetune/data/d4_selector_r2"
        train = generate_r2(ns, train_t, random.Random(DATA_SEED + 20), pages, args.states)
        random.Random(DATA_SEED + 29).shuffle(train)
        write_training(train, out / "train.jsonl", system_prompt)
        # Misma validación de pérdida que la ronda 1, para comparar curvas.
        (out / "valid.jsonl").write_text((OUT / "valid.jsonl").read_text())
        write_meta(train, out / "train_meta.jsonl")
        fields = Counter(f for r in train for f in r["yellow"]["hard_fields"])
        report = {"seed": DATA_SEED + 20, "ronda": 2, "examples": len(train), "targets": len({r["target"] for r in train}),
                  "kinds": dict(Counter(r["kind"] for r in train)), "pages_by_hard_field": dict(fields),
                  "pages_with_contrast_rows": sum(r["yellow"]["contrast_rows"] > 0 for r in train),
                  "distinct_states": len({r["state_key"] for r in train}), "valid": "copia de d4_selector/valid.jsonl",
                  "target_overlap": {"train∩valid": len(set(train_t) & set(valid_t)), "train∩test": len(set(train_t) & set(test))}}
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return
    train = generate(ns, train_t, random.Random(DATA_SEED), pages, system_prompt, args.states)
    valid = generate(ns, valid_t, random.Random(DATA_SEED + 1), pages, system_prompt, 4)
    random.Random(DATA_SEED + 9).shuffle(train)
    write_training(train, OUT / "train.jsonl", system_prompt)
    write_training(valid, OUT / "valid.jsonl", system_prompt)
    write_meta(train, OUT / "train_meta.jsonl")
    write_meta(valid, OUT / "valid_meta.jsonl")
    # Conjuntos de evaluación del Selector (no se entrenan): secretos de validación y de prueba.
    valid_set = generate(ns, valid_t, random.Random(DATA_SEED + 2), pages, system_prompt, 4)
    test_set = generate(ns, test, random.Random(DATA_SEED + 3), pages, system_prompt, 3)
    write_set(valid_set, "valid_generado")
    write_set(test_set, "test_generado")
    train_states = {r["state_key"] for r in train}
    report = {"seed": DATA_SEED, "source": "historiales simulados con el motor del notebook (política del D2 + ruido)",
              "labeling": "reglas del juego sobre el estado público (agents_d3.state.violations); sin modelo de lenguaje",
              "split": {"train_targets": len(train_t), "valid_targets": len(valid_t), "test_targets": len(test)},
              "train": describe(train), "valid": describe(valid),
              "valid_generado": describe(valid_set), "test_generado": describe(test_set),
              "state_overlap_with_train": {
                  "valid": sum(r["state_key"] in train_states for r in valid),
                  "valid_generado": sum(r["state_key"] in train_states for r in valid_set),
                  "test_generado": sum(r["state_key"] in train_states for r in test_set)},
              "target_overlap": {"train∩valid": len(set(train_t) & set(valid_t)), "train∩test": len(set(train_t) & set(test))}}
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
