"""Líneas base sin LLM para dar marco a los resultados de los modelos.

Tres referencias sobre los mismos 30 objetivos y el mismo motor:

    random    elige un campeón no usado al azar (ignora todo el feedback)
    feasible  elige al azar entre los campeones que satisfacen TODAS las
              restricciones reveladas (deducción perfecta, sin heurística extra)
    roster    recorre el roster en orden alfabético (Aatrox, Ahri, Akali, ...)

`feasible` demuestra que la tarea es resoluble con las mismas restricciones que
recibe el modelo; `random` y `roster` fijan el suelo.
"""

import json
import random
from pathlib import Path
from statistics import mean

from run_benchmark import load_engine, NUM_GAMES, MAX_ATTEMPTS, SEED

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "results" / "baselines.json"
N_SIMS = 200

FEEDBACK_FIELDS = (
    "gender", "positions", "species", "resource",
    "range_type", "regions", "release_year",
)


def play(ns, target, strategy, rng):
    names = list(ns["NAMES"])
    constraints = ns["empty_constraints"]()
    history = []
    used = []
    feasible_sizes = []
    for turn in range(1, MAX_ATTEMPTS + 1):
        if strategy == "random":
            pool = [n for n in names if n not in used] or names
            guess = rng.choice(pool)
        elif strategy == "roster":
            pool = [n for n in names if n not in used] or names
            guess = pool[0]
        elif strategy == "feasible":
            pool = [
                n for n in names
                if n not in used and not ns["constraint_violations"](n, constraints)
            ]
            feasible_sizes.append(len(pool))
            if not pool:
                pool = [n for n in names if n not in used] or names
            guess = rng.choice(pool)
        else:
            raise ValueError(strategy)

        used.append(guess)
        event = ns["evaluate_attempt"](guess, target, history, constraints)
        event["turn"] = turn
        history.append(event)
        if event["solved"]:
            break
    return {
        "target": target,
        "solved": bool(history and history[-1]["solved"]),
        "attempts_used": len(history),
        "trace": history,
        "feasible_sizes": feasible_sizes,
    }


def metrics(records):
    events = [e for r in records for e in r["trace"]]
    attempts = len(events) or 1
    eligible = sum(e["eligible"] and not e["invalid"] for e in events)
    violations = sum(e["constraint_violation"] for e in events)
    solved = [r for r in records if r["solved"]]
    best_greens = []
    for r in records:
        best = 0
        for e in r["trace"]:
            fb = e.get("feedback")
            if fb:
                best = max(best, sum(1 for f in FEEDBACK_FIELDS if fb.get(f) == "green"))
        best_greens.append(best)
    return {
        "games": len(records),
        "solved_games": len(solved),
        "solve_rate": len(solved) / len(records),
        "attempts": attempts,
        "constraint_violation_count": violations,
        "eligible_valid_attempts": eligible,
        "constraint_violation_rate": violations / eligible if eligible else None,
        "progress": mean(best_greens) / len(FEEDBACK_FIELDS),
        "average_attempts_solved": (
            mean(r["attempts_used"] for r in solved) if solved else None
        ),
    }


def main():
    ns = load_engine()
    ns["NUM_GAMES"] = NUM_GAMES
    ns["SEED"] = SEED
    targets = ns["choose_targets"]()

    output = {"n_sims": N_SIMS, "targets": targets, "strategies": {}}
    for strategy in ("random", "roster", "feasible"):
        sims = []
        feasible_by_turn = {}
        n = 1 if strategy == "roster" else N_SIMS  # roster es determinista
        for sim in range(n):
            rng = random.Random(1000 + sim)
            records = [play(ns, t, strategy, rng) for t in targets]
            sims.append(metrics(records))
            if strategy == "feasible":
                for r in records:
                    for turn, size in enumerate(r["feasible_sizes"], start=1):
                        feasible_by_turn.setdefault(turn, []).append(size)
        aggregated = {
            "solve_rate": mean(s["solve_rate"] for s in sims),
            "solve_rate_min": min(s["solve_rate"] for s in sims),
            "solve_rate_max": max(s["solve_rate"] for s in sims),
            "constraint_violation_rate": mean(
                s["constraint_violation_rate"] for s in sims
                if s["constraint_violation_rate"] is not None
            ),
            "progress": mean(s["progress"] for s in sims),
            "average_attempts_solved": mean(
                s["average_attempts_solved"] for s in sims
                if s["average_attempts_solved"] is not None
            ) if any(s["average_attempts_solved"] is not None for s in sims) else None,
            "sims": n,
            "solved_counts": [s["solved_games"] for s in sims],
        }
        if feasible_by_turn:
            aggregated["feasible_set_by_turn"] = {
                str(turn): round(mean(sizes), 1)
                for turn, sizes in sorted(feasible_by_turn.items())
            }
        output["strategies"][strategy] = aggregated
        print(
            f"{strategy:<9} resueltas={aggregated['solve_rate']:.1%} "
            f"violación={aggregated['constraint_violation_rate']:.1%} "
            f"progreso={aggregated['progress']:.1%} (n={n})"
        )

    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {OUT_PATH.relative_to(ROOT)}")
    fs = output["strategies"]["feasible"].get("feasible_set_by_turn", {})
    if fs:
        print("Tamaño medio del conjunto factible por turno:", fs)


if __name__ == "__main__":
    main()
