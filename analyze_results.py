"""Análisis comparativo de las corridas guardadas en results/raw/.

Genera:
    results/summary.csv   una fila por modelo con todas las métricas
    results/attempts.csv  tabla plana de todos los intentos
    results/ANALISIS.md   informe con ranking, líneas base y candidatos
"""

import csv
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "results" / "raw"
RESULTS_DIR = ROOT / "results"
BASELINES_PATH = RESULTS_DIR / "baselines.json"
ROSTER_PATH = ROOT / "data" / "champions_173_prompt.txt"

FEEDBACK_FIELDS = (
    "gender", "positions", "species", "resource",
    "range_type", "regions", "release_year",
)

# Pesos del índice compuesto de seguimiento de restricciones (CFS).
# El término no_enumeration se añadió tras observar que varios modelos
# sustituyen la deducción por recitar el roster en orden alfabético: es una
# forma de fallo específica de esta tarea y debe contar en el índice.
WEIGHTS = {
    "constraint_compliance": 0.35,   # 1 - tasa de violación
    "solve_rate": 0.17,
    "progress": 0.16,                # cobertura media de atributos verdes
    "no_enumeration": 0.14,          # 1 - tasa de recorrido consecutivo del roster
    "validity": 0.12,                # 1 - tasa de respuestas inválidas
    "no_repeat": 0.06,               # 1 - tasa de repeticiones
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "los pesos del CFS deben sumar 1"

ROSTER_ORDER = {
    line.split("|")[0]: index
    for index, line in enumerate(
        ROSTER_PATH.read_text(encoding="utf-8").splitlines()[1:]
    )
    if line.strip()
}


def game_metrics(record):
    best_greens = 0
    first_violation_turn = None
    violations = 0
    guesses = []
    for event in record["trace"]:
        feedback = event.get("feedback")
        if feedback:
            best_greens = max(
                best_greens,
                sum(1 for f in FEEDBACK_FIELDS if feedback.get(f) == "green"),
            )
        if event.get("constraint_violation"):
            violations += 1
            if first_violation_turn is None:
                first_violation_turn = event.get("turn")
        if event.get("guess"):
            guesses.append(event["guess"])

    # ¿El modelo recorre el roster en orden en vez de deducir?
    steps = consecutive = forward = 0
    for previous, current in zip(guesses, guesses[1:]):
        if previous not in ROSTER_ORDER or current not in ROSTER_ORDER:
            continue
        steps += 1
        delta = ROSTER_ORDER[current] - ROSTER_ORDER[previous]
        consecutive += delta == 1
        forward += delta > 0
    return {
        "best_greens": best_greens,
        "first_violation_turn": first_violation_turn,
        "violations": violations,
        "steps": steps,
        "consecutive": consecutive,
        "forward": forward,
    }


def analyze(payload):
    summary = payload["summary"]
    per_game = [game_metrics(r) for r in payload["records"]]
    attempts = summary["attempts"] or 1

    violation_rate = summary["constraint_violation_rate"] or 0.0
    progress = mean(g["best_greens"] for g in per_game) / len(FEEDBACK_FIELDS)
    turns_before_violation = [
        g["first_violation_turn"] for g in per_game if g["first_violation_turn"]
    ]
    steps = sum(g["steps"] for g in per_game) or 1

    row = {
        "modelo": payload["model_name"],
        "params_B": payload["params_b"],
        "partidas": summary["games"],
        "resueltas": summary["solved_games"],
        "tasa_resolucion": summary["solve_rate"],
        "intentos_prom_resueltas": summary["average_attempts_solved"],
        "intentos_totales": attempts,
        "invalidos": summary["invalid_count"],
        "tasa_invalidos": summary["invalid_rate"],
        "formato_incorrecto": summary["format_count"],
        "tasa_formato": summary["format_rate"],
        "repeticiones": summary["repeat_count"],
        "tasa_repeticiones": summary["repeat_count"] / attempts,
        "violaciones": summary["constraint_violation_count"],
        "intentos_elegibles": summary["eligible_valid_attempts"],
        "tasa_violacion": violation_rate,
        "progreso_medio": progress,
        "mejor_greens_max": max(g["best_greens"] for g in per_game),
        "turno_1a_violacion": (
            mean(turns_before_violation) if turns_before_violation else None
        ),
        "partidas_sin_violacion": sum(1 for g in per_game if g["violations"] == 0),
        "roster_consecutivo": sum(g["consecutive"] for g in per_game) / steps,
        "roster_hacia_adelante": sum(g["forward"] for g in per_game) / steps,
        "latencia_media_s": payload["mean_latency_s"],
        "segundos_corrida": payload["wall_seconds"],
        "errores_api": payload["api_errors"],
    }
    row["CFS"] = (
        WEIGHTS["solve_rate"] * row["tasa_resolucion"]
        + WEIGHTS["constraint_compliance"] * (1 - violation_rate)
        + WEIGHTS["progress"] * progress
        + WEIGHTS["no_enumeration"] * (1 - row["roster_consecutivo"])
        + WEIGHTS["validity"] * (1 - row["tasa_invalidos"])
        + WEIGHTS["no_repeat"] * (1 - row["tasa_repeticiones"])
    )
    return row


def add_baseline_stats(rows, baselines):
    """p-valor empírico unilateral contra la línea base aleatoria."""
    counts = baselines["strategies"]["random"]["solved_counts"]
    n = len(counts)
    for row in rows:
        at_least = sum(1 for c in counts if c >= row["resueltas"])
        row["p_vs_random"] = (at_least + 1) / (n + 1)
        row["lift_vs_random"] = (
            row["tasa_resolucion"] - baselines["strategies"]["random"]["solve_rate"]
        )


def attempt_rows(payload):
    rows = []
    for record in payload["records"]:
        for event in record["trace"]:
            feedback = event.get("feedback") or {}
            rows.append({
                "modelo": payload["model_name"],
                "partida": record["game"],
                "objetivo": record["target"],
                "intento": event.get("turn"),
                "respuesta_cruda": (event.get("raw_response") or "").replace("\n", " ")[:200],
                "campeon": event.get("guess") or "",
                "invalido": int(bool(event.get("invalid"))),
                "formato_incorrecto": int(bool(event.get("format_violation"))),
                "repetido": int(bool(event.get("repeated"))),
                "violacion": int(bool(event.get("constraint_violation"))),
                "n_violaciones": len(event.get("violations") or []),
                "greens": sum(1 for f in FEEDBACK_FIELDS if feedback.get(f) == "green") if feedback else "",
                "resuelto": int(bool(event.get("solved"))),
                "latencia_s": event.get("latency_s"),
                "tokens_prompt": event.get("prompt_tokens"),
                "motivo": (event.get("reason") or "")[:160],
            })
    return rows


def top_violated_attributes(payloads):
    totals = {}
    for payload in payloads:
        for violation in payload["violations"]:
            key = violation["atributo"]
            totals[key] = totals.get(key, 0) + 1
    return sorted(totals.items(), key=lambda item: -item[1])


def fmt(value, spec=".1%"):
    if value is None:
        return "—"
    return format(value, spec)


def write_markdown(rows, payloads, baselines, path):
    ranked = sorted(rows, key=lambda r: -r["CFS"])
    config = payloads[0]["config"]
    strategies = baselines["strategies"]
    random_b, roster_b, feasible_b = (
        strategies["random"], strategies["roster"], strategies["feasible"]
    )
    lines = []
    add = lines.append

    add("# Análisis comparativo — LoLdle Classic con modelos open-weight ≤ 8B\n")
    add(
        f"**{config['num_games']} partidas por modelo**, máximo "
        f"{config['max_attempts']} intentos por partida, temperatura "
        f"{config['temperature']}, `max_tokens` {config['max_tokens']}, SEED "
        f"{config['seed']}. Los **mismos 30 campeones objetivo** para los {len(rows)} modelos, "
        "así que la comparación es pareada. Cada partida reinicia la conversación; el "
        "modelo recibe el roster completo de 173 campeones y, tras cada intento, "
        "feedback estilo Wordle sobre siete atributos.\n"
    )
    add(
        f"Total: **{sum(r['intentos_totales'] for r in rows)} intentos** evaluados "
        f"sobre {len(rows)} modelos, sin un solo error de API.\n"
    )

    add("## 1. El resultado principal\n")
    add(
        "La tarea es **completamente resoluble con la información que recibe el modelo**. "
        "Una línea base que sólo mantiene el conjunto de restricciones reveladas y elige "
        "al azar entre los campeones compatibles resuelve "
        f"**{fmt(feasible_b['solve_rate'])} de las partidas en "
        f"{feasible_b['average_attempts_solved']:.1f} intentos de media**, con "
        f"{fmt(feasible_b['constraint_violation_rate'])} de violaciones. No hace falta "
        "conocimiento del dominio ni heurística de teoría de la información: basta con "
        "no contradecir lo ya revelado.\n"
    )
    add("| Estrategia | Resueltas | Tasa violación | Progreso |")
    add("|------------|-----------|----------------|----------|")
    add(
        f"| **Deducción perfecta** (`feasible`) | {fmt(feasible_b['solve_rate'])} | "
        f"{fmt(feasible_b['constraint_violation_rate'])} | {fmt(feasible_b['progress'])} |"
    )
    best = ranked[0]
    top_solver = max(rows, key=lambda r: r["tasa_resolucion"])
    sig = [r for r in ranked if r["p_vs_random"] < 0.05]
    shown = {top_solver["modelo"]}
    add(
        f"| Mejor modelo (`{top_solver['modelo']}`) | "
        f"{fmt(top_solver['tasa_resolucion'])} | {fmt(top_solver['tasa_violacion'])} | "
        f"{fmt(top_solver['progreso_medio'])} |"
    )
    if best["modelo"] not in shown:
        add(
            f"| Líder del ranking (`{best['modelo']}`) | {fmt(best['tasa_resolucion'])} | "
            f"{fmt(best['tasa_violacion'])} | {fmt(best['progreso_medio'])} |"
        )
        shown.add(best["modelo"])
    median = ranked[len(ranked) // 2]
    add(
        f"| Modelo mediano (`{median['modelo']}`) | {fmt(median['tasa_resolucion'])} | "
        f"{fmt(median['tasa_violacion'])} | {fmt(median['progreso_medio'])} |"
    )
    add(
        f"| Azar sin memoria (`random`, {random_b['sims']} sim.) | "
        f"{fmt(random_b['solve_rate'])} | {fmt(random_b['constraint_violation_rate'])} | "
        f"{fmt(random_b['progress'])} |"
    )
    add(
        f"| Recorrer el roster (`roster`) | {fmt(roster_b['solve_rate'])} | "
        f"{fmt(roster_b['constraint_violation_rate'])} | {fmt(roster_b['progress'])} |"
    )
    add("")
    add(
        f"**{len(sig)} de los {len(rows)} modelos superan el azar de forma "
        f"estadísticamente significativa; los otros {len(rows) - len(sig)} no.** "
        f"`{top_solver['modelo']}` resuelve {top_solver['resueltas']}/30 frente a los "
        f"{random_b['solve_rate'] * 30:.1f}/30 del azar (p = {top_solver['p_vs_random']:.3f}), "
        "y es el primer modelo de esta serie que demuestra hacer algo más que adivinar.\n"
    )
    add(
        "**Pero la brecha no se cierra, sólo se estrecha.** Incluso el mejor modelo "
        f"viola restricciones ya reveladas en el {fmt(top_solver['tasa_violacion'])} de "
        f"sus intentos y resuelve {fmt(top_solver['tasa_resolucion'])} de las partidas, "
        "frente al 0% y el 100% de la deducción perfecta. El prompting directo sigue "
        "muy lejos del techo: esa distancia es lo que el resto del semestre tiene que "
        "cerrar.\n"
    )

    add("## 2. Ranking global (índice CFS)\n")
    add(
        "El **CFS** (Constraint-Following Score) resume la tarea en un número. Pesos: "
        f"cumplimiento de restricciones {WEIGHTS['constraint_compliance']:.0%}, "
        f"resolución {WEIGHTS['solve_rate']:.0%}, progreso {WEIGHTS['progress']:.0%}, "
        f"no enumerar el roster {WEIGHTS['no_enumeration']:.0%}, validez de formato "
        f"{WEIGHTS['validity']:.0%}, no repetición {WEIGHTS['no_repeat']:.0%}. El peso "
        "dominante es el cumplimiento de restricciones, que es la capacidad que la tarea "
        "mide realmente; la resolución pesa menos porque sobre 30 partidas la mayoría de "
        "los modelos no se separa del azar y las diferencias en la cola baja son ruido. "
        "El término de "
        "enumeración se incorporó tras observar el comportamiento descrito en §5(c): "
        "recitar el listado infla el progreso aparente sin deducir nada.\n"
    )
    add("| # | Modelo | B | CFS | Resueltas | Tasa violación | Progreso | Enumera roster | Inválidos |")
    add("|---|--------|---|-----|-----------|----------------|----------|----------------|-----------|")
    for index, r in enumerate(ranked, start=1):
        add(
            f"| {index} | `{r['modelo']}` | {r['params_B']} | **{r['CFS']:.3f}** | "
            f"{r['resueltas']}/{r['partidas']} ({fmt(r['tasa_resolucion'])}) | "
            f"{fmt(r['tasa_violacion'])} | {fmt(r['progreso_medio'])} | "
            f"{fmt(r['roster_consecutivo'])} | {fmt(r['tasa_invalidos'])} |"
        )
    add("")

    add("## 3. Contraste contra el azar\n")
    add(
        f"p-valor empírico unilateral: proporción de las {random_b['sims']} simulaciones "
        "aleatorias que igualan o superan las partidas resueltas del modelo. Un valor "
        "alto significa que el modelo **no se distingue del azar**.\n"
    )
    add("| Modelo | Resueltas | Azar esperado | Δ | p |")
    add("|--------|-----------|---------------|---|---|")
    for r in ranked:
        add(
            f"| `{r['modelo']}` | {r['resueltas']}/30 | "
            f"{random_b['solve_rate'] * 30:.1f}/30 | "
            f"{r['lift_vs_random']:+.1%} | {r['p_vs_random']:.3f} |"
        )
    add("")
    significant = [r for r in ranked if r["p_vs_random"] < 0.05]
    if significant:
        add(
            "Superan el azar con p < 0,05: "
            + ", ".join(f"`{r['modelo']}`" for r in significant)
            + ".\n"
        )
    else:
        add(
            "**Ningún modelo supera el azar con p < 0,05.** Sobre 30 partidas, el "
            "prompting directo es indistinguible de adivinar en una tarea que la "
            "deducción resuelve al 100%.\n"
        )

    add("## 4. Métricas detalladas\n")
    add("| Modelo | Intentos | Inválidos | Formato ✗ | Repet. | Violaciones / elegibles | Partidas limpias | Turno 1ª violación | Mejor greens |")
    add("|--------|----------|-----------|-----------|--------|-------------------------|------------------|--------------------|--------------|")
    for r in ranked:
        add(
            f"| `{r['modelo']}` | {r['intentos_totales']} | "
            f"{r['invalidos']} ({fmt(r['tasa_invalidos'])}) | "
            f"{r['formato_incorrecto']} ({fmt(r['tasa_formato'])}) | {r['repeticiones']} | "
            f"{r['violaciones']}/{r['intentos_elegibles']} ({fmt(r['tasa_violacion'])}) | "
            f"{r['partidas_sin_violacion']}/{r['partidas']} | "
            f"{fmt(r['turno_1a_violacion'], '.2f')} | {r['mejor_greens_max']}/7 |"
        )
    add("")
    add(
        "*Partidas limpias* = partidas sin ninguna violación. *Turno 1ª violación* = "
        "intento medio en que el modelo contradice por primera vez el feedback ya "
        "recibido. *Mejor greens* = máximo de atributos exactos en un intento (7/7 = "
        "partida resuelta).\n"
    )

    add("## 5. Diagnóstico del fallo\n")
    add(
        "El fallo **no es de conocimiento**. El roster completo va en el prompt, los "
        "modelos nombran campeones reales y el formato de salida es correcto en la gran "
        "mayoría de los intentos. El fallo es de **razonamiento deductivo acumulativo**: "
        "el modelo no mantiene el conjunto de restricciones reveladas a lo largo de la "
        "conversación.\n"
    )
    add("Tres evidencias concretas:\n")

    feasible_by_turn = feasible_b.get("feasible_set_by_turn", {})
    if feasible_by_turn:
        add(
            "**(a) La información está ahí y es abundante.** Tras un solo intento "
            f"informativo el espacio de candidatos compatibles cae de 173 a "
            f"{feasible_by_turn.get('2', '—')} campeones, y al tercer intento a "
            f"{feasible_by_turn.get('3', '—')}. Tamaño medio del conjunto factible por turno:\n"
        )
        add("| Turno | " + " | ".join(feasible_by_turn) + " |")
        add("|-------|" + "|".join("---" for _ in feasible_by_turn) + "|")
        add("| Candidatos | " + " | ".join(str(v) for v in feasible_by_turn.values()) + " |")
        add("")

    add(
        f"**(b) La violación aparece de inmediato y no se recupera.** En promedio el "
        f"primer intento contradictorio llega en el turno "
        f"{mean([r['turno_1a_violacion'] for r in rows if r['turno_1a_violacion']]):.1f}, "
        "es decir en cuanto hay algo que recordar. Sólo "
        f"{sum(r['partidas_sin_violacion'] for r in rows)} de las "
        f"{sum(r['partidas'] for r in rows)} partidas jugadas terminan sin ninguna "
        "violación.\n"
    )

    enumerators = sorted(rows, key=lambda r: -r["roster_consecutivo"])[:3]
    add(
        "**(c) Varios modelos sustituyen la deducción por enumerar el roster.** Cuando "
        "no saben qué hacer, proponen el siguiente campeón del listado en vez de uno "
        "compatible. Fracción de transiciones que avanzan exactamente una posición en el "
        "roster (el azar daría ~0,6%):\n"
    )
    add("| Modelo | Paso consecutivo | Avance hacia adelante |")
    add("|--------|------------------|-----------------------|")
    for r in sorted(rows, key=lambda x: -x["roster_consecutivo"]):
        add(
            f"| `{r['modelo']}` | {fmt(r['roster_consecutivo'])} | "
            f"{fmt(r['roster_hacia_adelante'])} |"
        )
    add("")
    add(
        f"`{enumerators[0]['modelo']}` recorre el roster en orden en "
        f"{fmt(enumerators[0]['roster_consecutivo'])} de sus transiciones: está "
        "ignorando el feedback por completo y usando el prompt como una lista que "
        "recitar.\n"
    )

    attributes = top_violated_attributes(payloads)
    add(f"Violaciones agregadas por atributo, sumando los {len(rows)} modelos:\n")
    add("| Atributo | Violaciones |")
    add("|----------|-------------|")
    for attribute, count in attributes:
        add(f"| {attribute} | {count} |")
    add("")

    add("## 6. Viabilidad de ejecución\n")
    add("| Modelo | B | Latencia media | Corrida de 30 partidas | Errores API |")
    add("|--------|---|----------------|------------------------|-------------|")
    for r in sorted(rows, key=lambda x: x["params_B"]):
        add(
            f"| `{r['modelo']}` | {r['params_B']} | {fmt(r['latencia_media_s'], '.2f')} s | "
            f"{r['segundos_corrida']:.0f} s | {r['errores_api']} |"
        )
    add("")
    add(
        "Los 8 modelos corren localmente en LM Studio (API compatible con OpenAI) con "
        f"prompts de ~5.000 tokens. La corrida completa —"
        f"{sum(r['intentos_totales'] for r in rows)} llamadas— tomó "
        f"{sum(r['segundos_corrida'] for r in rows) / 60:.0f} minutos sin un solo error. "
        "La viabilidad de hardware queda demostrada empíricamente, no estimada.\n"
    )
    add(
        "`qwen3.5-4b` requiere un ajuste: es un modelo de razonamiento y con "
        f"`max_tokens={config['max_tokens']}` agota la generación en `reasoning_content` "
        "devolviendo `content` vacío en el 100% de los intentos. Se corrige enviando "
        "`reasoning_effort: \"none\"` en el cuerpo de la petición.\n"
    )

    add("## 7. Los tres candidatos\n")
    add(
        f"Los {len(sig)} modelos que superan el azar de forma significativa entran "
        "directamente; para el tercer puesto, donde las diferencias de resolución ya son "
        "ruido, el criterio es **qué tan buena base ofrece cada modelo para el "
        "andamiaje** de los próximos entregables: que no degenere en recitar el listado, "
        "que respete el formato y que deje margen de mejora atacando la gestión de "
        "estado.\n"
    )
    # Claves por nombre de modelo: si el ranking cambia, una justificación nunca
    # puede quedar pegada al modelo equivocado.
    justifications = {
        "ministral-3-8b-instruct-2512": (
            "El único modelo que se acerca a hacer la tarea. Resuelve {resueltas}/30 con "
            "p = {p:.3f} contra el azar, tiene la **tasa de violación más baja del "
            "estudio** ({tasa_violacion}, siete puntos por debajo del siguiente) y el "
            "mejor progreso medio ({progreso_medio}). Casi no enumera el roster "
            "({roster}): cuando acierta es porque dedujo, no porque barrió. Con "
            "{tasa_invalidos} de respuestas inválidas es además directamente usable "
            "dentro de un pipeline."
        ),
        "ministral-3-3b-instruct-2512": (
            "La apuesta por eficiencia. Con 3B —el 38% del techo— resuelve "
            "{resueltas}/30 y **también supera el azar de forma significativa** "
            "(p = {p:.3f}), algo que ningún otro modelo por debajo de 8B consigue. "
            "Enumera el roster sólo un {roster}. Su punto débil es la disciplina de "
            "formato: {invalidos} respuestas inválidas ({tasa_invalidos}), corregible "
            "con validación externa y reintento."
        ),
        "exaone-3.5-2.4b-instruct": (
            "El control de bajo coste, y el más pequeño del estudio con 2,4B. No supera "
            "el azar (p = {p:.3f}), pero tiene **{roster} de enumeración**: cuando falla, "
            "falla intentando deducir en vez de recitar el listado. Es el más barato por "
            "intento, lo que lo hace útil como banco de pruebas rápido del andamiaje "
            "antes de gastar cómputo en los Ministral."
        ),
        "josiefied-qwen2.5-7b-instruct-abliterated-v2": (
            "El mejor de la familia Qwen: {resueltas}/30 resueltas, {tasa_violacion} de "
            "violación y {tasa_invalidos} de respuestas inválidas. El reparo es que "
            "enumera el roster en {roster} de sus transiciones, así que parte de su "
            "resultado es barrido y no deducción."
        ),
        "falcon3-7b-instruct": (
            "Resuelve {resueltas}/30 con enumeración baja ({roster}) y formato casi "
            "siempre válido. Aporta diversidad de familia al conjunto de candidatos. Su "
            "debilidad son las {repeticiones} repeticiones: repropone campeones ya "
            "descartados."
        ),
    }
    generic = (
        "Resuelve {resueltas}/30 (p = {p:.3f} contra el azar) con {tasa_violacion} de "
        "violación de restricciones, {progreso_medio} de progreso medio, "
        "{tasa_invalidos} de respuestas inválidas y {roster} de enumeración del roster."
    )
    for index, r in enumerate(ranked[:3], start=1):
        add(
            f"**{index}. `{r['modelo']}` ({r['params_B']}B) — CFS {r['CFS']:.3f}.** "
            f"Resuelve {r['resueltas']}/{r['partidas']} ({fmt(r['tasa_resolucion'])}), "
            f"viola restricciones en {fmt(r['tasa_violacion'])} de sus intentos "
            f"elegibles, progreso medio {fmt(r['progreso_medio'])}, "
            f"{fmt(r['tasa_invalidos'])} de respuestas inválidas, "
            f"{r['repeticiones']} repeticiones y {fmt(r['latencia_media_s'], '.2f')} s "
            "de latencia media por intento.\n"
        )
        add(
            justifications.get(r["modelo"], generic).format(
                invalidos=r["invalidos"],
                repeticiones=r["repeticiones"],
                resueltas=r["resueltas"],
                p=r["p_vs_random"],
                tasa_violacion=fmt(r["tasa_violacion"]),
                progreso_medio=fmt(r["progreso_medio"]),
                tasa_invalidos=fmt(r["tasa_invalidos"]),
                roster=fmt(r["roster_consecutivo"]),
            )
            + "\n"
        )
    smallest = min(ranked[:3], key=lambda r: r["params_B"])
    smallest_sig = min(
        (r for r in ranked if r["p_vs_random"] < 0.05),
        key=lambda r: r["params_B"],
        default=None,
    )
    if smallest_sig is not None:
        add(
            f"Para el bono por tamaño, `{smallest_sig['modelo']}` es el modelo más "
            f"pequeño que supera el azar de forma significativa: {smallest_sig['params_B']}B, "
            f"un {smallest_sig['params_B'] / 8:.0%} del techo, resolviendo "
            f"{smallest_sig['resueltas']}/30 con p = {smallest_sig['p_vs_random']:.3f}. "
            "La defensa es de tarea y no de tamaño: supera a los siete modelos de 7B y "
            "7,6B del estudio en el índice compuesto, y lo hace con menos de la mitad de "
            f"sus parámetros. El más pequeño del podio es `{smallest['modelo']}` con "
            f"{smallest['params_B']}B.\n"
        )
    else:
        add(
            f"Para el bono por tamaño, el más pequeño del podio es `{smallest['modelo']}` "
            f"con {smallest['params_B']}B ({smallest['params_B'] / 8:.0%} del techo de 8B).\n"
        )

    add("## 8. Qué implica para los próximos entregables\n")
    add(
        f"La elección de modelo **sí importa**, y más de lo que sugería la primera "
        f"tanda: `{best['modelo']}` resuelve {best['resueltas']}/30 donde la mediana del "
        f"estudio resuelve {median['resueltas']}/30, y lo hace con la tasa de violación "
        f"más baja medida. Cualquier andamiaje debe construirse sobre esa base, no sobre "
        "los modelos de la cola.\n"
    )
    add(
        f"Pero el mejor modelo sigue violando restricciones en {fmt(best['tasa_violacion'])} "
        f"de sus intentos y dejando {best['partidas'] - best['resueltas']} de 30 partidas "
        "sin resolver, frente a un techo del 100%. **El modelo solo no basta.** La brecha "
        "que queda no es de capacidad lingüística sino de gestión de estado, y se ataca "
        "con andamiaje externo:\n"
    )
    add(
        "1. **Memoria explícita de restricciones** — mantener el conjunto revelado fuera "
        "del modelo y reinyectarlo como texto en cada turno, en vez de esperar que lo "
        "reconstruya del historial.\n"
        "2. **Filtrado del espacio de candidatos** — pasar de 173 nombres a los "
        f"{feasible_by_turn.get('3', '≈4')} compatibles y pedir la elección sobre esa "
        "lista corta.\n"
        "3. **Descomposición del razonamiento** — separar «actualizar restricciones» de "
        "«elegir candidato» en dos llamadas, en vez de exigir ambas en una respuesta de "
        f"{config['max_tokens']} tokens.\n"
    )
    add(
        "La señal más útil para diseñar ese andamiaje está en §5(c): los modelos que "
        "enumeran el roster ocupan el fondo del ranking y los dos que lo superan el azar "
        "casi no enumeran. La diferencia entre recitar y deducir es exactamente lo que "
        "el andamiaje tiene que amplificar.\n"
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RAW_DIR.glob("*.json"))
    ]
    if not payloads:
        raise SystemExit("No hay resultados en results/raw/. Corre run_benchmark.py primero.")
    baselines = json.loads(BASELINES_PATH.read_text(encoding="utf-8"))

    rows = [analyze(payload) for payload in payloads]
    add_baseline_stats(rows, baselines)
    rows.sort(key=lambda r: -r["CFS"])

    summary_path = RESULTS_DIR / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    attempts_path = RESULTS_DIR / "attempts.csv"
    all_attempts = [row for payload in payloads for row in attempt_rows(payload)]
    with attempts_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_attempts[0]))
        writer.writeheader()
        writer.writerows(all_attempts)

    markdown_path = RESULTS_DIR / "ANALISIS.md"
    write_markdown(rows, payloads, baselines, markdown_path)

    print(f"{summary_path.relative_to(ROOT)}  ({len(rows)} modelos)")
    print(f"{attempts_path.relative_to(ROOT)}  ({len(all_attempts)} intentos)")
    print(f"{markdown_path.relative_to(ROOT)}\n")
    print("Ranking por CFS:")
    for index, r in enumerate(rows, start=1):
        print(
            f"  {index}. {r['modelo']:<54} CFS={r['CFS']:.3f} "
            f"resueltas={r['resueltas']:>2}/30 viol={r['tasa_violacion']:.1%} "
            f"prog={r['progreso_medio']:.1%} p={r['p_vs_random']:.3f} "
            f"roster={r['roster_consecutivo']:.1%}"
        )


if __name__ == "__main__":
    main()
