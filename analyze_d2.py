"""Análisis del Entregable 2: baseline contra modelo ajustado, mismos objetivos.

Lee las corridas de results/d2/raw/ (producidas por run_benchmark.py en modo
de una variante), las compara con las mismas métricas del Entregable 1 y
agrega lo que el Entregable 2 exige: comparación pareada sobre los mismos 30
objetivos y los casos donde la solución todavía falla.

Genera:
    results/d2/summary.json   lo que muestra la app en vivo
    results/d2/summary.csv    una fila por variante
    results/d2/ANALISIS_D2.md informe

Uso (desde la raíz del repo):
    python3 analyze_d2.py
"""

import csv
import json
import random
import sys
from math import comb
from pathlib import Path
from statistics import mean

from analyze_results import FEEDBACK_FIELDS, WEIGHTS, add_baseline_stats, analyze
from run_benchmark import load_engine

sys.path.insert(0, str(Path(__file__).resolve().parent / "finetune"))
from make_data import state_line  # noqa: E402  (misma definición que el entrenamiento)

ROOT = Path(__file__).resolve().parent
D2 = ROOT / "results" / "d2"
RAW = D2 / "raw"
D1_REFERENCE = ROOT / "results" / "raw" / "ministral-3-3b-instruct-2512.json"
BASELINES = ROOT / "results" / "baselines.json"

LABELS = {
    "gguf_d1": ("Baseline del Entregable 1 · GGUF Q4_K_M en LM Studio", "E1 · GGUF"),
    "baseline": ("Baseline · MLX 4-bit, prompting directo", "Baseline"),
    "lora": ("Solución · fine-tuning LoRA (el juego recibe la jugada del modelo)", "LoRA"),
    "lora_tool": ("Variante · fine-tuning LoRA + consulta al roster con el «Sé» del modelo", "LoRA+herr."),
}
SOLUTIONS = ("lora", "lora_tool")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def exact_mcnemar(b, c):
    """p bilateral de McNemar exacto sobre los pares discordantes."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def per_game(payload):
    """Métricas por partida, indexadas por objetivo."""
    games = {}
    for record in payload["records"]:
        trace = record["trace"]
        eligible = [e for e in trace if e["eligible"] and not e["invalid"]]
        games[record["target"]] = {
            "solved": record["solved"],
            "attempts": record["attempts_used"],
            "violations": sum(e["constraint_violation"] for e in trace),
            "eligible": len(eligible),
            "invalid": sum(e["invalid"] for e in trace),
            "repeated": sum(e["repeated"] for e in trace),
            "best_greens": max(
                (sum(1 for f in FEEDBACK_FIELDS if (e.get("feedback") or {}).get(f) == "green")
                 for e in trace), default=0),
            "guesses": [e.get("guess") or f"«{(e.get('raw_response') or '')[:30]}»" for e in trace],
        }
    return games


def list_quality(ns, payload):
    """Calidad de la línea "Compatibles: ..." que escribe el modelo ajustado.

    Reconstruye, turno a turno, el conjunto compatible real con el mismo
    checker del Entregable 1 y lo compara con la lista del modelo.
    """
    listed_total = listed_ok = unknown = turns = first_ok = first_exact = 0
    state_turns = state_ok = 0
    for record in payload["records"]:
        constraints = ns["empty_constraints"]()
        used = set()
        for event in record["trace"]:
            feasible = [n for n in ns["NAMES"]
                        if n not in used and not ns["constraint_violations"](n, constraints)]
            text = event.get("model_output") or ""
            names = None
            for line in text.splitlines():
                head, _, body = line.partition(":")
                key = head.strip().lower()
                if key == "sé":
                    state_turns += 1
                    truth = state_line(ns, constraints).partition(":")[2].strip()
                    state_ok += body.strip() == truth
                elif key == "compatibles" and names is None:
                    names = [x.strip() for x in body.strip().rstrip("…").split(",") if x.strip()]
            if names:
                turns += 1
                resolved = []
                for item in names:
                    parsed = ns["parse_response"](item)
                    resolved.append(parsed["name"] if parsed["format_ok"] else None)
                listed_total += len(resolved)
                listed_ok += sum(1 for n in resolved if n in feasible)
                unknown += sum(1 for n in resolved if n is None)
                first_ok += resolved[0] in feasible
                first_exact += bool(feasible) and resolved[0] == feasible[0]
            if event.get("feedback") is not None:
                ns["update_constraints"](constraints, event["guess"], event["feedback"])
            if event.get("guess"):
                used.add(event["guess"])
    if not turns:
        return None
    return {
        "state_accuracy": state_ok / state_turns if state_turns else None,
        "turns_with_list": turns,
        "listed_precision": listed_ok / listed_total if listed_total else None,
        "listed_unknown": unknown,
        "first_listed_compatible": first_ok / turns,
        "first_listed_is_policy": first_exact / turns,
    }


DEV = D2 / "dev"
# Estrategias evaluadas en los 15 objetivos de validación, en orden de exploración.
STRATEGIES = [
    ("val_base", "Baseline · prompting directo"),
    ("val_base_oracle_state", "Diagnóstico · baseline + resumen perfecto de lo revelado en el prompt"),
    ("val_answer240", "FT «sólo nombre» (detenido en la iteración 240)"),
    ("val_cand100", "FT «compatibles + jugada» (iteración 100; detenido en ~140)"),
    ("val_reas100", "FT tres pasos · ronda 1, iteración 100"),
    ("val_reas300", "FT tres pasos · ronda 1, iteración 300"),
    ("val_reas500", "FT tres pasos · ronda 1, iteración 500"),
    ("val_reas700", "FT tres pasos · ronda 1, iteración 700"),
    ("val_r2_200", "FT tres pasos · ronda 2 (con repeticiones), iteración 200"),
    ("val_r2_400", "FT tres pasos · ronda 2 (con repeticiones), iteración 400"),
    ("val_r2_800", "FT tres pasos · ronda 2 (con repeticiones), iteración 800"),
    ("val_reas300_tool", "FT + herramienta · ronda 1, iteración 300"),
    ("val_reas500_tool", "FT + herramienta · ronda 1, iteración 500"),
    ("val_reas700_tool", "FT + herramienta · ronda 1, iteración 700"),
    ("val_r2_400_tool", "FT + herramienta · ronda 2, iteración 400"),
    ("val_r2_800_tool", "FT + herramienta · ronda 2, iteración 800"),
]


def strategy_rows(ns):
    rows = []
    for stem, label in STRATEGIES:
        path = DEV / f"{stem}.json"
        if not path.exists():
            continue
        payload = load(path)
        events = [e for r in payload["records"] for e in r["trace"]]
        eligible = [e for e in events if e["eligible"] and not e["invalid"]]
        q = list_quality(ns, payload)
        rows.append({
            "label": label,
            "solved": sum(r["solved"] for r in payload["records"]),
            "games": len(payload["records"]),
            "violation": (sum(e["constraint_violation"] for e in events) / len(eligible)) if eligible else None,
            "repeat": (sum(e["repeated"] for e in events) / len(eligible)) if eligible else None,
            "invalid": sum(e["invalid"] for e in events) / len(events),
            "state": q["state_accuracy"] if q else None,
        })
    return rows


def bootstrap_diff(games_a, games_b, targets, reps=5000, seed=2026):
    """IC 95 % de la diferencia de tasa de violación (b - a), remuestreando objetivos."""
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        sample = [rng.choice(targets) for _ in targets]
        def rate(games):
            v = sum(games[t]["violations"] for t in sample)
            e = sum(games[t]["eligible"] for t in sample)
            return v / e if e else 0.0
        diffs.append(rate(games_b) - rate(games_a))
    diffs.sort()
    return diffs[int(0.025 * reps)], diffs[int(0.975 * reps)]


def fmt(v, spec=".1%"):
    return "—" if v is None else format(v, spec)


def main():
    baselines = load(BASELINES)
    payloads = {}
    if D1_REFERENCE.exists():
        payloads["gguf_d1"] = load(D1_REFERENCE)
    for key in ("baseline",) + SOLUTIONS:
        path = RAW / f"{key}.json"
        if path.exists():
            payloads[key] = load(path)
    if "baseline" not in payloads:
        raise SystemExit("Falta results/d2/raw/baseline.json: corre la evaluación del baseline.")

    targets = payloads["baseline"]["targets"]
    for key, p in payloads.items():
        assert p["targets"] == targets, f"{key} no usa los mismos objetivos"

    rows = {}
    for key, payload in payloads.items():
        row = analyze(payload)
        rows[key] = row
    add_baseline_stats(list(rows.values()), baselines)

    games = {key: per_game(p) for key, p in payloads.items()}
    ns = load_engine()
    lists = {key: list_quality(ns, p) for key, p in payloads.items()}

    comparisons = {}
    for key in SOLUTIONS:
        if key not in payloads:
            continue
        base, sol = games["baseline"], games[key]
        only_sol = [t for t in targets if sol[t]["solved"] and not base[t]["solved"]]
        only_base = [t for t in targets if base[t]["solved"] and not sol[t]["solved"]]
        both = [t for t in targets if base[t]["solved"] and sol[t]["solved"]]
        lo, hi = bootstrap_diff(base, sol, targets)
        comparisons[key] = {
            "only_solution": only_sol,
            "only_baseline": only_base,
            "both": both,
            "mcnemar_p": exact_mcnemar(len(only_sol), len(only_base)),
            "violation_diff_ci95": [lo, hi],
        }

    # ---------------- summary.json (app) ----------------
    variants = []
    for key in ("gguf_d1", "baseline") + SOLUTIONS:
        if key not in rows:
            continue
        r = rows[key]
        variants.append({
            "key": key,
            "label": LABELS[key][0],
            "short": LABELS[key][1],
            "solved": int(r["resueltas"]),
            "games": int(r["partidas"]),
            "solve_rate": r["tasa_resolucion"],
            "violation_rate": r["tasa_violacion"],
            "compatible_rate": 1 - r["tasa_violacion"],
            "invalid_rate": r["tasa_invalidos"],
            "avg_attempts_solved": r["intentos_prom_resueltas"],
            "progress": r["progreso_medio"],
            "enumeration": r["roster_consecutivo"],
            "cfs": r["CFS"],
            "p_vs_random": r["p_vs_random"],
            "latency_s": r["latencia_media_s"],
            "list": lists.get(key),
        })
    failures = {key: [t for t in targets if not games[key][t]["solved"]]
                for key in SOLUTIONS if key in games}
    summary = {
        "targets": len(targets),
        "caption": (
            f"{len(targets)} objetivos de prueba reservados (SEED=777), los mismos del "
            "Entregable 1; cada variante juega las mismas partidas con el mismo motor, "
            "prompt y criterio de corrección."
        ),
        "variants": variants,
        "comparisons": comparisons,
        "failures": failures,
    }
    D2.mkdir(parents=True, exist_ok=True)
    (D2 / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    with (D2 / "summary.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["variante"] + list(next(iter(rows.values())).keys())
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for key, r in rows.items():
            writer.writerow({"variante": key, **r})

    # ---------------- informe ----------------
    lines = ["# Entregable 2 — baseline contra fine-tuning LoRA\n"]
    lines.append(
        f"**Entradas:** los {len(targets)} objetivos de prueba del Entregable 1 "
        "(SEED=777), reservados: ninguno aparece como campeón secreto en los datos de "
        "entrenamiento. **Criterio:** el mismo del Entregable 1 — salida correcta = nombre "
        "exacto de un campeón del roster que no contradice ninguna restricción revelada ni "
        "repite un intento previo. Máximo 10 intentos, temperatura 0, `max_tokens` 64.\n"
    )
    lines.append("| Variante | Resueltas | Violación | Compatibles | Inválidos | Intentos medios (resueltas) | Progreso | Enumera roster | CFS | p vs azar |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for v in variants:
        lines.append(
            f"| {v['label']} | {v['solved']}/{v['games']} ({fmt(v['solve_rate'])}) | "
            f"{fmt(v['violation_rate'])} | {fmt(v['compatible_rate'])} | {fmt(v['invalid_rate'])} | "
            f"{fmt(v['avg_attempts_solved'], '.2f')} | {fmt(v['progress'])} | "
            f"{fmt(v['enumeration'])} | {v['cfs']:.3f} | {v['p_vs_random']:.3f} |"
        )
    lines.append("")
    lines.append(
        f"CFS con los pesos del Entregable 1: " + ", ".join(f"{k} {w:.0%}" for k, w in WEIGHTS.items()) + ".\n"
    )
    strat = strategy_rows(ns)
    if strat:
        lines.append("## Estrategias evaluadas (validación: 15 objetivos reservados)\n")
        lines.append(
            "Los puntos de control y las alternativas se eligieron sólo con estos 15 "
            "objetivos; los 30 de prueba se usaron una única vez, con el modelo elegido.\n"
        )
        lines.append("| Estrategia | Resueltas | Violación | Repeticiones | Inválidos | Estado «Sé» exacto |")
        lines.append("|---|---|---|---|---|---|")
        for r in strat:
            lines.append(
                f"| {r['label']} | {r['solved']}/{r['games']} | {fmt(r['violation'])} | "
                f"{fmt(r['repeat'])} | {fmt(r['invalid'])} | {fmt(r['state'])} |"
            )
        lines.append("")
    quality = [(v, v["list"]) for v in variants if v.get("list")]
    if quality:
        lines.append("## La lista de compatibles que escribe el modelo\n")
        lines.append("| Variante | Estado «Sé» exacto | Turnos con lista | Nombres listados compatibles | Nombres inexistentes | Primer nombre compatible | Primer nombre = política |")
        lines.append("|---|---|---|---|---|---|---|")
        for v, q in quality:
            lines.append(
                f"| {v['label']} | {fmt(q['state_accuracy'])} | {q['turns_with_list']} | {fmt(q['listed_precision'])} | "
                f"{q['listed_unknown']} | {fmt(q['first_listed_compatible'])} | "
                f"{fmt(q['first_listed_is_policy'])} |"
            )
        lines.append("")
        lines.append(
            "*Primer nombre = política*: el primer nombre de la lista es exactamente el primer "
            "campeón compatible en orden del roster, que es lo que se entrenó a jugar.\n"
        )
    for key, cmp in comparisons.items():
        lines.append(f"## Comparación pareada · {LABELS[key][0]} contra el baseline MLX\n")
        lines.append(
            f"- Resueltas sólo por la solución: **{len(cmp['only_solution'])}** "
            f"({', '.join(cmp['only_solution']) or '—'})\n"
            f"- Resueltas sólo por el baseline: **{len(cmp['only_baseline'])}** "
            f"({', '.join(cmp['only_baseline']) or '—'})\n"
            f"- Resueltas por ambos: {len(cmp['both'])}\n"
            f"- McNemar exacto sobre los pares discordantes: p = {cmp['mcnemar_p']:.4g}\n"
            f"- Diferencia en tasa de violación (solución − baseline), IC 95 % bootstrap por "
            f"objetivo: [{cmp['violation_diff_ci95'][0]:+.1%}, {cmp['violation_diff_ci95'][1]:+.1%}]\n"
        )
    for key, fails in failures.items():
        if not fails:
            continue
        lines.append(f"## Dónde falla · {LABELS[key][0]}\n")
        lines.append("| Objetivo | Intentos | Violaciones | Inválidos | Repeticiones | Mejor verdes | Propuestas |")
        lines.append("|---|---|---|---|---|---|---|")
        for t in fails:
            g = games[key][t]
            lines.append(
                f"| {t} | {g['attempts']} | {g['violations']}/{g['eligible']} | {g['invalid']} | "
                f"{g['repeated']} | {g['best_greens']}/7 | {' → '.join(g['guesses'])} |"
            )
        lines.append("")
    (D2 / "ANALISIS_D2.md").write_text("\n".join(lines), encoding="utf-8")

    for v in variants:
        print(f"{v['short']:<9} resueltas {v['solved']:>2}/{v['games']}  violación {v['violation_rate']:.1%}  "
              f"inválidos {v['invalid_rate']:.1%}  CFS {v['cfs']:.3f}  p_azar {v['p_vs_random']:.3f}")
    for key, cmp in comparisons.items():
        print(f"pareado {key}: sólo solución {len(cmp['only_solution'])} · sólo baseline "
              f"{len(cmp['only_baseline'])} · McNemar p={cmp['mcnemar_p']:.4g}")
    print("results/d2/summary.json · summary.csv · ANALISIS_D2.md")


if __name__ == "__main__":
    main()
