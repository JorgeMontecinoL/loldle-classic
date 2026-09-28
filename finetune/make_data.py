"""Genera el dataset de fine-tuning a partir del motor del notebook.

Cada ejemplo es una conversación idéntica a la que el modelo ve en el pipeline
—mismo system prompt con el roster de 173 campeones, mismo mensaje inicial,
mismos mensajes de feedback— cortada en el turno en que el modelo debe proponer
un campeón. La etiqueta es un campeón compatible con TODAS las restricciones
reveladas hasta ese turno: exactamente la definición de salida correcta del
Entregable 1. El entrenamiento enseña la habilidad que el diagnóstico mostró
ausente (sostener las restricciones), no respuestas memorizadas.

Separación de datos:
    prueba   los 30 objetivos del Entregable 1 (SEED=777). Nunca aparecen como
             campeón secreto en entrenamiento ni en validación.
    valid    15 objetivos más, reservados para la pérdida de validación.
    train    los 128 objetivos restantes.

Tres formatos de salida:
    reasoned    (solución) tres líneas: lo confirmado hasta ahora, los
                campeones compatibles en orden del roster, y la jugada:
                    Sé: Female · Mana · Ranged · Ionia · 2011
                    Compatibles: Karma
                    Karma
                Al juego sólo llega la última línea. Todo el texto objetivo
                es determinista: lo calcula el mismo checker del Entregable 1.
    candidates  (alternativa descartada) sólo las dos últimas líneas. Aprendió
                el formato pero no a usar el feedback: su lista era casi la
                misma en partidas distintas.
    answer      (alternativa descartada) sólo el nombre, elegido al azar entre
                los compatibles. Con ~5 tokens supervisados por ejemplo de
                ~5.500 no aprendió la búsqueda y degradó al modelo.

Uso (desde la raíz del repo):
    python3 finetune/make_data.py                        # formato reasoned
    python3 finetune/make_data.py --format candidates    # alternativas descartadas
    python3 finetune/make_data.py --format answer
"""

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from run_benchmark import MAX_ATTEMPTS, NUM_GAMES, SEED, load_engine  # noqa: E402

DATA_DIR = ROOT / "finetune" / "data"
DATA_SEED = 2026
N_VALID_TARGETS = 15
TRAIN_EXAMPLES_PER_TARGET = 8
VALID_EXAMPLES_PER_TARGET = 4

# Cuántos intentos hay ya en el historial cuando el modelo debe responder.
# Un jugador consistente resuelve en ~3,3 intentos, así que se prioriza el
# tramo 1–4 sin dejar fuera historiales largos.
HISTORY_LENGTHS = list(range(1, MAX_ATTEMPTS))
HISTORY_WEIGHTS = [25, 25, 18, 12, 8, 5, 3, 2, 2]

# Probabilidad de que cada intento previo sea un campeón al azar en vez de uno
# compatible. Con ruido el historial se parece al de un modelo que ya violó
# restricciones, y el ejemplo enseña a recuperarse de ese estado.
NOISE_LEVELS = [0.0, 0.0, 0.25, 0.5, 1.0]


def split_targets(ns):
    ns["NUM_GAMES"] = NUM_GAMES
    ns["SEED"] = SEED
    test = ns["choose_targets"]()
    rest = [name for name in ns["NAMES"] if name not in set(test)]
    rng = random.Random(DATA_SEED)
    rng.shuffle(rest)
    return test, sorted(rest[N_VALID_TARGETS:]), sorted(rest[:N_VALID_TARGETS])


def feasible(ns, constraints, used):
    return [
        name for name in ns["NAMES"]
        if name not in used and not ns["constraint_violations"](name, constraints)
    ]


def sample_example(ns, target, rng):
    """Simula un historial y devuelve la conversación con su etiqueta."""
    constraints = ns["empty_constraints"]()
    history = []
    length = rng.choices(HISTORY_LENGTHS, weights=HISTORY_WEIGHTS)[0]
    noise = rng.choice(NOISE_LEVELS)

    for turn in range(1, length + 1):
        used = {event["guess"] for event in history}
        compatible = [n for n in feasible(ns, constraints, used) if n != target]
        if rng.random() < noise or not compatible:
            if not compatible and noise == 0.0:
                break  # sólo queda el objetivo: el siguiente turno lo cierra
            pool = [n for n in ns["NAMES"] if n not in used and n != target]
        else:
            pool = compatible
        guess = rng.choice(pool)
        event = ns["evaluate_attempt"](guess, target, history, constraints)
        event["turn"] = turn
        history.append(event)

    if not history:
        return None
    used = {event["guess"] for event in history}
    candidates = feasible(ns, constraints, used)
    assert target in candidates, "el objetivo siempre satisface sus propias restricciones"
    label = rng.choice(candidates)

    messages = ns["build_messages"](history)
    messages.append({"role": "assistant", "content": label})
    meta = {
        "target": target,
        "history": len(history),
        "noise": noise,
        "feasible": len(candidates),
        "label_is_target": label == target,
        "violations_in_history": sum(e["constraint_violation"] for e in history),
    }
    return {"messages": messages, "meta": meta}


SHOWN_CANDIDATES = 5          # nombres visibles en la línea de trabajo
NOISY_PER_TARGET = 4          # historiales con errores previos, por objetivo
OPENING_COPIES = 12           # el primer turno es idéntico para todo objetivo


STATE_FIELDS = ("gender", "positions", "species", "resource", "range_type", "regions")


def state_line(ns, constraints):
    """Lo confirmado hasta ahora: valores en verde y rango de año."""
    known = []
    for field in STATE_FIELDS:
        required = constraints[field]["required"]
        if required is not None:
            known.append(ns["_value_text"](required).replace(", ", "+"))
    year = constraints["release_year"]
    if year["exact"] is not None:
        known.append(str(year["exact"]))
    else:
        lo, hi = year["min_exclusive"], year["max_exclusive"]
        if lo is not None and hi is not None:
            known.append(f"{lo + 1}-{hi - 1}")
        elif lo is not None:
            known.append(f">{lo}")
        elif hi is not None:
            known.append(f"<{hi}")
    return "Sé: " + (" · ".join(known) if known else "nada")


def candidates_reply(ns, constraints, used, reasoned=False):
    """Respuesta objetivo: [estado,] línea de compatibles y, abajo, la jugada."""
    cands = feasible(ns, constraints, used)
    shown = cands[:SHOWN_CANDIDATES]
    line = "Compatibles: " + ", ".join(shown) + ("…" if len(cands) > len(shown) else "")
    reply = f"{line}\n{shown[0]}"
    if reasoned:
        reply = state_line(ns, constraints) + "\n" + reply
    return reply, cands


def candidates_example(ns, target, history, constraints, reasoned=False):
    used = {event["guess"] for event in history}
    reply, cands = candidates_reply(ns, constraints, used, reasoned)
    messages = ns["build_messages"](history)
    messages.append({"role": "assistant", "content": reply})
    return {"messages": messages, "meta": {
        "target": target,
        "history": len(history),
        "feasible": len(cands),
        "label_is_target": cands[0] == target,
        "violations_in_history": sum(e["constraint_violation"] for e in history),
    }}


def trajectory(ns, target, rng, noise, reasoned=False):
    """Juega con la política "primer compatible" (con ruido opcional) y
    devuelve un ejemplo por cada estado previo a acertar."""
    constraints = ns["empty_constraints"]()
    history, examples = [], []
    for turn in range(1, MAX_ATTEMPTS + 1):
        used = {event["guess"] for event in history}
        cands = feasible(ns, constraints, used)
        examples.append(candidates_example(ns, target, list(history), _copy(constraints), reasoned))
        if rng.random() < noise:
            pool = [n for n in ns["NAMES"] if n not in used and n != target]
            guess = rng.choice(pool)
        else:
            guess = cands[0]
        if guess == target:
            break
        event = ns["evaluate_attempt"](guess, target, history, constraints)
        event["turn"] = turn
        history.append(event)
    return examples


def _copy(constraints):
    return {
        field: {key: (set(value) if isinstance(value, set) else value)
                for key, value in item.items()}
        for field, item in constraints.items()
    }


def repeat_trajectory(ns, target, rng, reasoned=True):
    """Historial con repeticiones: el bucle que sufre el modelo con decodificación
    greedy. Repetir un campeón no aporta información, el estado no cambia y el
    modelo vuelve a proponer lo mismo. Se juegan 1-4 turnos con la política
    "primer compatible", se repite 1-3 veces una jugada anterior y se devuelve
    el estado resultante: su respuesta objetivo excluye todo lo ya jugado."""
    constraints = ns["empty_constraints"]()
    history = []
    for turn in range(1, rng.randint(1, 4) + 1):
        used = {event["guess"] for event in history}
        guess = feasible(ns, constraints, used)[0]
        if guess == target:
            break
        event = ns["evaluate_attempt"](guess, target, history, constraints)
        event["turn"] = turn
        history.append(event)
    if not history:
        return None
    for _ in range(rng.randint(1, 3)):
        if len(history) >= MAX_ATTEMPTS - 1:
            break
        previous = history[-1] if rng.random() < 0.7 else rng.choice(history)
        event = ns["evaluate_attempt"](previous["guess"], target, history, constraints)
        event["turn"] = len(history) + 1
        history.append(event)
    return candidates_example(ns, target, history, _copy(constraints), reasoned)


def build_candidates(ns, targets, rng, noisy_per_target, openings, reasoned=False,
                     repeats_per_target=0):
    rows, opening = [], None
    for target in targets:
        clean = trajectory(ns, target, rng, noise=0.0, reasoned=reasoned)
        opening = clean[0]
        rows.extend(clean[1:])           # el primer turno se agrega aparte
        for _ in range(noisy_per_target):
            noisy = trajectory(ns, target, rng, noise=rng.choice(NOISE_LEVELS[2:]), reasoned=reasoned)
            rows.append(rng.choice(noisy[1:] or noisy))
        for _ in range(repeats_per_target):
            example = repeat_trajectory(ns, target, rng, reasoned)
            if example is not None:
                rows.append(example)
    rows.extend([opening] * openings)
    rng.shuffle(rows)
    return rows


def build(ns, targets, per_target, rng):
    rows = []
    for target in targets:
        made = 0
        while made < per_target:
            example = sample_example(ns, target, rng)
            if example is not None:
                rows.append(example)
                made += 1
    rng.shuffle(rows)
    return rows


def write(rows, path):
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def describe(name, rows):
    feas = Counter(min(r["meta"]["feasible"], 13) for r in rows)
    hist = Counter(r["meta"]["history"] for r in rows)
    closing = sum(r["meta"]["label_is_target"] for r in rows)
    noisy = sum(r["meta"]["violations_in_history"] > 0 for r in rows)
    print(f"{name}: {len(rows)} ejemplos · {len({r['meta']['target'] for r in rows})} objetivos")
    print(f"  la etiqueta es el objetivo (cierre de partida): {closing} ({closing / len(rows):.0%})")
    print(f"  historial con al menos una violación previa:   {noisy} ({noisy / len(rows):.0%})")
    print("  intentos previos:  " + "  ".join(f"{k}:{hist[k]}" for k in sorted(hist)))
    print("  candidatos compatibles: " + "  ".join(
        f"{'13+' if k == 13 else k}:{feas[k]}" for k in sorted(feas)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("reasoned", "candidates", "answer"), default="reasoned")
    parser.add_argument("--sample-seed", type=int, default=DATA_SEED,
                        help="semilla de las trayectorias; la partición prueba/validación/"
                             "entrenamiento usa siempre DATA_SEED y no cambia")
    parser.add_argument("--noisy-per-target", type=int, default=NOISY_PER_TARGET)
    parser.add_argument("--repeats-per-target", type=int, default=0,
                        help="historiales con repeticiones (enseñan a salir del bucle greedy)")
    parser.add_argument("--out", default=None, help="subcarpeta de salida (por defecto, el formato)")
    args = parser.parse_args()

    ns = load_engine()
    test, train_targets, valid_targets = split_targets(ns)
    assert not set(test) & set(train_targets) and not set(test) & set(valid_targets)
    assert not set(train_targets) & set(valid_targets)

    rng = random.Random(args.sample_seed)
    if args.format == "answer":
        train = build(ns, train_targets, TRAIN_EXAMPLES_PER_TARGET, rng)
        valid = build(ns, valid_targets, VALID_EXAMPLES_PER_TARGET, rng)
    else:
        reasoned = args.format == "reasoned"
        train = build_candidates(ns, train_targets, rng, args.noisy_per_target, OPENING_COPIES, reasoned,
                                 repeats_per_target=args.repeats_per_target)
        valid = build_candidates(ns, valid_targets, rng, 2, 2, reasoned)

    out_dir = DATA_DIR / (args.out or args.format)
    out_dir.mkdir(parents=True, exist_ok=True)
    write(train, out_dir / "train.jsonl")
    write(valid, out_dir / "valid.jsonl")
    (DATA_DIR / "split.json").write_text(json.dumps({
        "data_seed": DATA_SEED,
        "test_targets_seed": SEED,
        "test": test,
        "valid": valid_targets,
        "train": train_targets,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    describe("train", train)
    describe("valid", valid)
    print(f"\nprueba reservada: {len(test)} objetivos del Entregable 1 (SEED={SEED})")
    print(f"escrito en {out_dir.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
