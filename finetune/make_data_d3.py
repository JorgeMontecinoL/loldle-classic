"""Dataset multirol del Entregable 3: un solo adaptador para Selector, Memoria y Verificador.

Cada ejemplo reproduce exactamente la entrada que un agente recibe en
agents_d3/runtime.py (mismo prompt de sistema, mismo JSON o la misma
conversación del D2) cortada en la respuesta que debe dar. Las etiquetas las
calcula el motor del notebook a partir de la evidencia pública, igual que en el
D2: el modelo aprende el procedimiento, y en la partida lo ejecuta él mismo.

    selector   Formato del D2 (Sé / Compatibles / jugada) con la nota del estado
               de Memoria en el último mensaje; parte de los ejemplos incluye un
               rechazo del Verificador y la jugada siguiente.
    memory     Estado JSON green/gray/yellow/year/used a partir de las pistas
               nuevas y el estado previo, o del historial completo ante una crítica.
    verifier   Llamada 1: pedir ver_atributos. Llamada 2: con la fila junto al
               estado, aprobar, devolver al Selector (rompe una pista que Memoria
               registra) o a Memoria (rompe una pista que Memoria omitió).

La partición es la del D2 (finetune/data/split.json): los 30 objetivos de
prueba nunca aparecen; los 15 de validación sólo en valid.jsonl, que mide la
pérdida y no se entrena.

    .venv-ft/bin/python finetune/make_data_d3.py
"""
import argparse
import copy
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "finetune"))

from run_benchmark import MAX_ATTEMPTS, load_engine  # noqa: E402
from make_data import _copy, candidates_reply, feasible, split_targets  # noqa: E402
from agents_d3.runtime import AgentConfig, AgentSystem, PAGE_PREFIX, years_allowed, PREFIX, prompt_bundle, public_clues, selector_templates, state_note  # noqa: E402
from agents_d3.state import empty_state, lookup, observed_state, public_history, violations  # noqa: E402

DATA_SEED = 3030


def compact(state):
    """El estado tal como Memoria lo entrega: sin límites de año nulos."""
    out = copy.deepcopy(state)
    out["year"] = {k: v for k, v in out["year"].items() if v is not None}
    # Como piden el prompt y sus ejemplos: todo valor verde es lista, también los escalares.
    out["green"] = {f: (v if isinstance(v, list) else [v]) for f, v in out["green"].items()}
    return out


# Separadores compactos: la respuesta debe continuar exactamente el prefill '{"action":"'.
def memory_reply(state):
    s = compact(state)
    return json.dumps({"action": "entregar_estado", "green": s["green"], "gray": s["gray"],
                       "yellow": s["yellow"], "year": s["year"], "used": s["used"]}, ensure_ascii=False, separators=(",", ":"))


def play(ns, target, rng, noise):
    """Historial jugado con la política del D2 (primer compatible), con ruido opcional."""
    constraints = ns["empty_constraints"]()
    history = []
    for turn in range(1, rng.randint(1, MAX_ATTEMPTS - 1) + 1):
        used = {e["guess"] for e in history}
        cands = feasible(ns, constraints, used)
        if rng.random() < noise:
            guess = rng.choice([n for n in ns["NAMES"] if n not in used and n != target])
        else:
            guess = cands[0]
        if guess == target:
            break
        event = ns["evaluate_attempt"](guess, target, history, constraints)
        event["turn"] = turn
        history.append(event)
    return history, constraints


def drop_clue(state, rng):
    """Estado de Memoria con una pista omitida: genera casos revisar_memoria."""
    state = copy.deepcopy(state)
    options = [("green", f) for f in state["green"]] + [("gray", f) for f in state["gray"]]
    options += [("yellow", f) for f in state["yellow"]] + [("year", k) for k, v in state["year"].items() if v is not None]
    if not options:
        return state, False
    key, field = rng.choice(options)
    if key == "year":
        state["year"][field] = None
    elif key == "gray" and len(state["gray"][field]) > 1:
        state["gray"][field] = state["gray"][field][1:]
    else:
        del state[key][field]
    return state, True


def selector_example(ns, history, constraints, rng, prompts, templates, state):
    used = {e["guess"] for e in history}
    messages = ns["build_messages"](history)
    note = state_note(compact(state))
    if note:
        messages[-1] = dict(messages[-1], content=messages[-1]["content"] + "\n" + templates["NOTE"].format(state=note))
    reply, cands = candidates_reply(ns, constraints, used, reasoned=True)
    kind = "plain"
    if rng.random() < 0.35 and cands:
        # Una propuesta previa devuelta por el Verificador: a veces errónea, a veces un falso rechazo.
        wrong = [n for n in ns["NAMES"] if n not in used and n not in cands and len(violations(n, state, ns["CHAMPIONS"])) <= 2]
        if rng.random() < 0.25 and len(cands) > 1:
            rejected, reason = cands[0], "it breaks a revealed clue"
            kind = "false_reject"
        elif wrong:
            rejected = rng.choice(wrong)
            reason = violations(rejected, state, ns["CHAMPIONS"])[0]
            kind = "reject"
        else:
            rejected = None
        if rejected:
            bad, _ = candidates_reply(ns, constraints, used, reasoned=True)
            bad = bad.rsplit("\n", 1)[0] + "\n" + rejected
            messages += [{"role": "assistant", "content": bad},
                         {"role": "user", "content": templates["REJECT"].format(candidate=rejected, reason=reason)}]
            reply, cands = candidates_reply(ns, constraints, used | {rejected}, reasoned=True)
    messages.append({"role": "assistant", "content": reply})
    return {"messages": messages, "meta": {"role": "selector", "kind": kind, "history": len(history)}}


def memory_example(ns, history, rng, prompts):
    public = public_history(ns, history)
    clues = public_clues(public)
    # Como en el runtime: el turno 1 recibe empty_state(); luego, el estado compacto que Memoria entregó.
    prev = compact(observed_state(public[:-1])) if public else empty_state()
    if rng.random() < 0.75:
        payload = {"your_role": "memory", "available_actions": ["entregar_estado", "validar_estado"],
                   "message": {"instruction": "Actualiza las restricciones y decide el siguiente paso."},
                   "new_clues": clues[-1:], "previous_state": prev}
        kind = "incremental"
    else:
        # Crítica del Verificador o del Selector: historial completo para reconstruir.
        payload = {"your_role": "memory", "available_actions": ["entregar_estado", "validar_estado"],
                   "message": {"reason": "The candidate breaks a revealed clue; recheck the clues.",
                               "candidate": public[-1]["guess"] if public else None, "rejected": []},
                   "history": clues, "previous_state": prev}
        kind = "criticism"
    messages = [{"role": "system", "content": prompts["memory"]},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                {"role": "assistant", "content": memory_reply(observed_state(public))}]
    return {"messages": messages, "meta": {"role": "memory", "kind": kind, "history": len(history)}}


def verifier_examples(ns, history, rng, prompts):
    roster = ns["CHAMPIONS"]
    public = public_history(ns, history)
    clues = public_clues(public)
    truth = observed_state(public)
    used = [e["guess"] for e in public]
    memory, dropped = drop_clue(truth, rng) if rng.random() < 0.3 else (copy.deepcopy(truth), False)
    ok = [n for n in roster if not violations(n, truth, roster)]
    near = [n for n in roster if n not in used and 1 <= len(violations(n, truth, roster)) <= 2]
    if dropped:
        # Un candidato que cumple el estado incompleto pero rompe la pista omitida.
        missed = [n for n in roster if not violations(n, memory, roster) and violations(n, truth, roster)]
        candidate = rng.choice(missed) if missed else rng.choice(ok)
    else:
        r = rng.random()
        candidate = rng.choice(ok) if r < 0.5 or not near else (rng.choice(used) if r < 0.6 and used else rng.choice(near))
    payload = {"your_role": "verifier",
               "available_actions": ["aprobar", "revisar_memoria", "revisar_selector", "stop", "ver_atributos"],
               "candidate": candidate, "history": clues, "memory": compact(memory),
               "message": {"instruction": "Revisa la propuesta contra cada pista y decide."}}
    first = [{"role": "system", "content": prompts["verifier"]},
             {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
    tool = '{"action":"ver_atributos"}'
    full_errors = violations(candidate, truth, roster)
    memory_errors = violations(candidate, memory, roster)
    if not full_errors:
        decision = {"action": "aprobar", "reason": "Every line holds against the revealed clues."}
    elif memory_errors:
        decision = {"action": "revisar_selector", "reason": f"{candidate}: {memory_errors[0]}"}
    else:
        decision = {"action": "revisar_memoria", "reason": f"Memory missed a clue: {full_errors[0]}"}
    second = first + [{"role": "assistant", "content": tool},
                      {"role": "user", "content": json.dumps({"your_role": "verifier", "message": lookup(candidate, roster, compact(memory)),
                                                              "candidate": candidate}, ensure_ascii=False)},
                      {"role": "assistant", "content": json.dumps(decision, ensure_ascii=False, separators=(",", ":"))}]
    out = [{"messages": second, "meta": {"role": "verifier", "kind": decision["action"], "history": len(history)}}]
    if rng.random() < 0.3:
        out.append({"messages": first + [{"role": "assistant", "content": tool}],
                    "meta": {"role": "verifier", "kind": "ver_atributos", "history": len(history)}})
    return out


def rejection_chain_example(ns, history, constraints, rng, templates, state):
    """Ronda 2: el fallo observado en validación. El Selector arma una lista
    Compatibles equivocada, su primera jugada es rechazada y, por decodificación
    greedy, vuelve a proponer lo mismo. La etiqueta, tras 1-3 rechazos, es la
    jugada correcta sin los nombres rechazados."""
    roster = ns["CHAMPIONS"]
    used = {e["guess"] for e in history}
    near = [n for n in ns["NAMES"] if n not in used and len(violations(n, state, roster)) == 1]
    if not near:
        return None
    reply_ok, cands = candidates_reply(ns, constraints, used, reasoned=True)
    sure = reply_ok.splitlines()[0]
    messages = ns["build_messages"](history)
    note = state_note(compact(state))
    if note:
        messages[-1] = dict(messages[-1], content=messages[-1]["content"] + "\n" + templates["NOTE"].format(state=note))
    rejected = []
    for step in range(rng.randint(1, 3)):
        # Repite la jugada anterior (el bucle greedy) o cae en otro casi compatible.
        pick = rejected[-1] if rejected and rng.random() < 0.6 else rng.choice([n for n in near if n not in rejected] or near)
        shown = sorted({pick, *rng.sample(near, min(3, len(near))), *cands[:2]}, key=ns["NAMES"].index)[:5]
        bad = f"{sure}\nCompatibles: {', '.join(shown)}…\n{pick}"
        messages += [{"role": "assistant", "content": bad},
                     {"role": "user", "content": templates["REJECT"].format(
                         candidate=pick, reason=f"{pick}: {violations(pick, state, roster)[0]}")}]
        if pick not in rejected:
            rejected.append(pick)
    reply, _ = candidates_reply(ns, constraints, used | set(rejected), reasoned=True)
    messages.append({"role": "assistant", "content": reply})
    return {"messages": messages, "meta": {"role": "selector", "kind": "reject_chain", "history": len(history)}}


def build_round2(ns, targets, rng, prompts, templates, chains, others):
    rows = []
    for target in targets:
        made = 0
        while made < chains:
            history, constraints = play(ns, target, rng, rng.choice([0.0, 0.0, 0.25]))
            state = observed_state(public_history(ns, history))
            row = rejection_chain_example(ns, history, constraints, rng, templates, state) if history else None
            if row:
                rows.append(row)
                made += 1
    # Repaso de los otros roles para no olvidarlos.
    for target in rng.sample(targets, min(others, len(targets))):
        history, constraints = play(ns, target, rng, 0.0)
        state = observed_state(public_history(ns, history))
        rows.append(selector_example(ns, history, constraints, rng, prompts, templates, state))
        rows.append(memory_example(ns, history, rng, prompts))
        rows.extend(verifier_examples(ns, history, rng, prompts))
    rng.shuffle(rows)
    return rows


def page_examples(ns, history, rng, prompts, pages):
    """v4: una página del roster y la lista exacta de filas que cumplen el estado de Memoria.
    Se toman las páginas con al menos una fila que cumple y una página sin ninguna."""
    roster = ns["CHAMPIONS"]
    state = compact(observed_state(public_history(ns, history)))
    excluded = [e["guess"] for e in history]
    if history and rng.random() < 0.25:
        # A veces también hay propuestas ya rechazadas en el turno.
        extra = [n for n in ns["NAMES"] if n not in excluded and not violations(n, state, roster)]
        excluded += rng.sample(extra, min(len(extra), rng.randint(1, 2)))
    rows_out, empty = [], []
    for k, (header, rows) in enumerate(pages):
        names = [r.split("|", 1)[0] for r in rows]
        fit = [n for n in names if n not in excluded and not violations(n, state, roster)]
        # Veredicto por fila (razonamiento estructurado): "ok" o el primer campo que falla.
        verdicts = []
        for n in names:
            if n in excluded:
                verdicts.append(f"{n} x excluded")
            else:
                errs = violations(n, state, roster)
                verdicts.append(f"{n} ok" if not errs else f"{n} x {errs[0].split(':', 1)[0]}")
        payload = {"your_role": "selector", "available_actions": ["listar"], "memory": state, "excluded": excluded,
                   "page": f"{k + 1}/{len(pages)}", "rows": "\n".join([header] + rows)}
        allowed = years_allowed(state, roster)
        if allowed is not None:
            payload["years_allowed"] = allowed
        reply = json.dumps({"action": "listar", "revision": verdicts, "candidates": fit}, ensure_ascii=False, separators=(",", ":"))
        row = {"messages": [{"role": "system", "content": prompts["selector_paginas"]},
                            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                            {"role": "assistant", "content": reply}],
               "meta": {"role": "selector_pagina", "kind": "con_candidatos" if fit else "vacia", "history": len(history)}}
        (rows_out if fit else empty).append(row)
    if not history:
        rows_out = rng.sample(rows_out, 2)   # turno 1: todas las filas cumplen; basta con dos páginas
    elif len(rows_out) > 4:
        rows_out = rng.sample(rows_out, 4)
    return rows_out + rng.sample(empty, min(1, len(empty)))


def build_paginas(ns, targets, rng, prompts, states, replay):
    pages = AgentSystem.roster_pages(type("S", (), {"ns": ns})())
    rows = []
    for target in targets:
        for _ in range(states):
            history, _ = play(ns, target, rng, rng.choice([0.0, 0.0, 0.25, 0.5]))
            if rng.random() < 0.1:
                history = []
            rows.extend(page_examples(ns, history, rng, prompts, pages))
    # Repaso de Memoria y Verificador para conservar esos roles.
    for target in [rng.choice(targets) for _ in range(replay)]:
        history, _ = play(ns, target, rng, rng.choice([0.0, 0.25]))
        rows.append(memory_example(ns, history, rng, prompts))
        rows.extend(verifier_examples(ns, history, rng, prompts))
    rng.shuffle(rows)
    return rows


def build(ns, targets, rng, prompts, templates, per_target):
    rows = []
    for target in targets:
        for _ in range(per_target["selector"]):
            history, constraints = play(ns, target, rng, rng.choice([0.0, 0.0, 0.25, 0.5]))
            state = observed_state(public_history(ns, history))
            rows.append(selector_example(ns, history, constraints, rng, prompts, templates, state))
        for _ in range(per_target["memory"]):
            history, _ = play(ns, target, rng, rng.choice([0.0, 0.25, 0.5]))
            rows.append(memory_example(ns, history, rng, prompts))
        for _ in range(per_target["verifier"]):
            history, _ = play(ns, target, rng, rng.choice([0.0, 0.25]))
            rows.extend(verifier_examples(ns, history, rng, prompts))
    rng.shuffle(rows)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    parser.add_argument("--round2", action="store_true",
                        help="cadenas de rechazos del Selector (el bucle observado en validación) + repaso")
    parser.add_argument("--paginas", action="store_true",
                        help="v4: Selector que busca por páginas del roster + repaso de Memoria y Verificador")
    parser.add_argument("--repaso", type=int, default=100, help="partidas de repaso de Memoria y Verificador (--paginas)")
    parser.add_argument("--semilla", type=int, default=0, help="desplazamiento de la semilla de muestreo (--paginas)")
    args = parser.parse_args()
    args.out = args.out or ("d3_paginas" if args.paginas else "d3_multirol_r2" if args.round2 else "d3_multirol")
    ns = load_engine()
    test, train_targets, valid_targets = split_targets(ns)
    saved = json.loads((ROOT / "finetune/data/split.json").read_text())
    assert (test, train_targets, valid_targets) == (saved["test"], saved["train"], saved["valid"]), "la partición cambió"
    prompts = prompt_bundle(AgentConfig())
    prompts["selector"] = ns["SYSTEM_PROMPT"]
    templates = selector_templates(prompts["selector_turn"])
    assert PREFIX["memory"] == '{"action":"' and PREFIX["verifier"] == '{"action":"', "las etiquetas JSON empiezan como el prefill"
    assert PAGE_PREFIX == '{"action":"listar","revision":', "las etiquetas de página empiezan como el prefill"
    if args.paginas:
        rng = random.Random(DATA_SEED + 2 + args.semilla)
        train = build_paginas(ns, train_targets, rng, prompts, states=6, replay=args.repaso)
        valid = build_paginas(ns, valid_targets, rng, prompts, states=1, replay=6)
    elif args.round2:
        rng = random.Random(DATA_SEED + 1)
        train = build_round2(ns, train_targets, rng, prompts, templates, chains=2, others=64)
        valid = build_round2(ns, valid_targets, rng, prompts, templates, chains=1, others=5)
    else:
        rng = random.Random(DATA_SEED)
        train = build(ns, train_targets, rng, prompts, templates, {"selector": 3, "memory": 5, "verifier": 4})
        valid = build(ns, valid_targets, rng, prompts, templates, {"selector": 1, "memory": 1, "verifier": 1})
    out_dir = ROOT / "finetune/data" / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train", train), ("valid", valid)):
        with (out_dir / f"{name}.jsonl").open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps({"messages": row["messages"]}, ensure_ascii=False) + "\n")
        kinds = Counter((r["meta"]["role"], r["meta"]["kind"]) for r in rows)
        print(f"{name}: {len(rows)} ejemplos · " + " · ".join(f"{a}/{b}:{n}" for (a, b), n in sorted(kinds.items())))
    print(f"escrito en {out_dir.relative_to(ROOT)}/ · prueba y validación fuera de train: "
          f"{not (set(test) | set(valid_targets)) & set(train_targets)}")


if __name__ == "__main__":
    main()
