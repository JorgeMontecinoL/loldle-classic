"""Métricas del Selector por página, a partir de las trazas reales del sistema.

Cada llamada del Selector recibe un JSON con el estado de Memoria (`memory`), los
nombres excluidos, una página del roster y, si hay límites de año, `years_allowed`.
Aquí se reconstruye esa entrada desde la traza, se calcula con las reglas del juego
(`agents_d3.state.violations`) qué filas cumplen ese mismo estado y se compara con
lo que el modelo escribió. El comprobador sólo se usa para etiquetar y medir: nunca
participa en la partida.
"""
import json

from agents_d3.client import parse_action
from agents_d3.state import violations


def row_names(rows_text):
    return [line.split("|", 1)[0] for line in rows_text.strip().splitlines()[1:]]


def state_for_rules(memory):
    """El estado de Memoria con las claves que espera `violations` (year con eq/gt/lt)."""
    memory = memory or {}
    year = {k: (memory.get("year") or {}).get(k) for k in ("eq", "gt", "lt")}
    return {"green": memory.get("green") or {}, "gray": memory.get("gray") or {},
            "yellow": memory.get("yellow") or {}, "year": year, "used": memory.get("used") or []}


def truth_for_page(payload, roster):
    """Veredicto correcto de cada fila según el estado entregado y los excluidos."""
    state = state_for_rules(payload.get("memory"))
    excluded = set(payload.get("excluded") or [])
    out = {}
    for name in row_names(payload["rows"]):
        if name in excluded:
            out[name] = ["excluded"]
        else:
            out[name] = [e.split(":", 1)[0] for e in violations(name, state, roster)]
    return out


def parse_selector(content):
    """(revision por nombre, candidatos, error de protocolo o None)."""
    try:
        decision = parse_action(content)
    except (ValueError, json.JSONDecodeError) as exc:
        return {}, [], f"json: {exc}"
    if decision.get("action") != "listar" or not isinstance(decision.get("candidates"), list):
        return {}, [], "acción o candidatos inválidos"
    verdicts = {}
    for item in decision.get("revision") or []:
        if not isinstance(item, str):
            continue
        if item.endswith(" ok"):
            verdicts[item[:-3]] = "ok"
        elif " x " in item:
            name, field = item.rsplit(" x ", 1)
            verdicts[name] = field.strip()
    return verdicts, [c for c in decision["candidates"] if isinstance(c, str)], None


def selector_calls(record):
    """Pares (entrada, salida) de cada llamada del Selector en una partida."""
    pending = None
    for event in record.get("agent_trace", []):
        if event["kind"] == "model_call" and event.get("agent") == "selector":
            pending = event
        elif event["kind"] == "model_output" and event.get("agent") == "selector" and pending is not None:
            payload = json.loads(pending["messages"][-1]["content"])
            yield {"turn": pending["turn"], "call": pending["call"], "sampling": pending.get("sampling"),
                   "system": pending["messages"][0]["content"], "payload": payload, "content": event["content"]}
            pending = None


def yellow_single(payload):
    """Campos con alguna cláusula amarilla de un solo valor en el estado de la entrada."""
    yellow = (payload.get("memory") or {}).get("yellow") or {}
    return sorted(f for f, clauses in yellow.items() if any(isinstance(c, list) and len(c) == 1 for c in clauses))


def score_page(payload, content, roster, target=None):
    """Compara una salida del Selector con la verdad de su página."""
    truth = truth_for_page(payload, roster)
    names = list(truth)
    fits = [n for n in names if not truth[n]]
    verdicts, candidates, error = parse_selector(content)
    listed = [c for c in candidates if c in truth]
    listed_set = set(listed)
    yellow_fields = {f for f in ((payload.get("memory") or {}).get("yellow") or {})}
    # Filas compatibles descartadas y la razón escrita: un campo amarillo indica error de amarillo.
    false_drop = [n for n in fits if n not in listed_set]
    false_keep = [n for n in listed if truth[n]]
    yellow_errors = [n for n in false_drop if verdicts.get(n) in yellow_fields]
    yellow_errors += [n for n in false_keep if any(f in yellow_fields for f in truth[n])]
    single = yellow_single(payload)
    yellow_single_errors = [n for n in false_drop if verdicts.get(n) in single]
    target_on_page = target in truth if target else False
    return {
        "page": payload.get("page"), "rows": len(names), "fits": len(fits), "listed": len(listed),
        "true_pos": len([n for n in listed if not truth[n]]), "false_drop": false_drop, "false_keep": false_keep,
        "protocol_error": error, "out_of_page": [c for c in candidates if c not in truth],
        "revision_rows": len(verdicts), "revision_complete": set(verdicts) >= set(names),
        "yellow_errors": sorted(set(yellow_errors)), "yellow_single_fields": single,
        "yellow_single_errors": yellow_single_errors,
        "target_on_page": target_on_page,
        "target_fits": bool(target_on_page and not truth[target]),
        "target_dropped": bool(target_on_page and not truth[target] and target not in listed_set),
        "target_verdict": verdicts.get(target) if target_on_page else None,
    }


def aggregate(scores):
    """Totales con denominadores explícitos."""
    fits = sum(s["fits"] for s in scores)
    listed = sum(s["listed"] for s in scores)
    tp = sum(s["true_pos"] for s in scores)
    target_cases = [s for s in scores if s["target_fits"]]
    yellow_cases = [s for s in scores if s["yellow_single_fields"]]
    yellow_fits = sum(s["fits"] for s in yellow_cases)
    yellow_tp = sum(s["true_pos"] for s in yellow_cases)
    return {
        "pages": len(scores),
        "fits": fits, "listed": listed, "true_pos": tp,
        "recall": tp / fits if fits else None,
        "precision": tp / listed if listed else None,
        "exact_pages": sum(not s["false_drop"] and not s["false_keep"] and not s["protocol_error"] for s in scores),
        "protocol_errors": sum(bool(s["protocol_error"]) for s in scores),
        "false_drops": sum(len(s["false_drop"]) for s in scores),
        "false_keeps": sum(len(s["false_keep"]) for s in scores),
        "yellow_errors": sum(len(s["yellow_errors"]) for s in scores),
        "target_pages": len(target_cases),
        "target_dropped": sum(s["target_dropped"] for s in target_cases),
        "yellow_single_pages": len(yellow_cases),
        "yellow_single_recall": yellow_tp / yellow_fits if yellow_fits else None,
        "yellow_single_fits": yellow_fits,
        "yellow_single_errors": sum(len(s["yellow_single_errors"]) for s in yellow_cases),
        "empty_pages": sum(s["fits"] == 0 for s in scores),
        "empty_pages_clean": sum(s["fits"] == 0 and s["listed"] == 0 and not s["protocol_error"] for s in scores),
    }
