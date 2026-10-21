"""Estado JSON y herramientas. Sólo reciben observaciones públicas, nunca el secreto.

El checker histórico del notebook ignora amarillos. Se conserva para las métricas
comparables; este módulo audita además su semántica exacta (intersección no vacía
y conjuntos distintos). No modifica el motor de los entregables anteriores.
"""
import copy

SCALARS = ("gender", "resource", "range_type")
SETS = ("positions", "species", "regions")
FIELDS = SCALARS + SETS


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def empty_state():
    return {"exact": {}, "forbidden": {}, "partial": {},
            "year": {"eq": None, "gt": None, "lt": None}, "used": []}


def public_history(ns, history):
    """Una frontera explícita: ni target, ni solved, ni restricciones del evaluador."""
    result = []
    for event in history:
        name = event.get("guess")
        result.append({"turn": event["turn"], "guess": name,
                       "attributes": jsonable(ns["CHAMPIONS"][name]) if name else None,
                       "feedback": event.get("feedback"),
                       "raw_response": event.get("raw_response"),
                       "repeated": bool(event.get("repeated"))})
    return result


def observed_state(history):
    """Reconstrucción determinista exclusiva de validar_jugada/control algorítmico.

Nunca se inyecta en Memoria ni se usa para arreglar su salida silenciosamente.
"""
    state = empty_state()
    for event in history:
        name, feedback = event.get("guess"), event.get("feedback")
        if name and name not in state["used"]:
            state["used"].append(name)
        if not name or not feedback:
            continue
        attrs = event["attributes"]
        for field in FIELDS:
            value = attrs[field]
            if feedback[field] == "green":
                state["exact"][field] = copy.deepcopy(value)
            elif feedback[field] == "gray":
                values = value if field in SETS else [value]
                state["forbidden"][field] = sorted(set(state["forbidden"].get(field, []) + values))
            elif feedback[field] == "yellow":
                entry = sorted(value)
                clauses = state["partial"].setdefault(field, [])
                if entry not in clauses:
                    clauses.append(entry)
        year, status = attrs["release_year"], feedback["release_year"]
        if status == "green":
            state["year"]["eq"] = year
        elif status == "higher":
            old = state["year"]["gt"]
            state["year"]["gt"] = year if old is None else max(old, year)
        elif status == "lower":
            old = state["year"]["lt"]
            state["year"]["lt"] = year if old is None else min(old, year)
    return state


def state_errors(state, roster):
    """Formato, vocabulario y consistencia interna; no deduce pistas faltantes."""
    if not isinstance(state, dict):
        return ["state debe ser un objeto"]
    errors = []
    if set(state) != {"exact", "forbidden", "partial", "year", "used"}:
        return ["state exige exactamente exact, forbidden, partial, year, used"]
    if not all(isinstance(state[k], dict) for k in ("exact", "forbidden", "partial", "year")):
        return ["exact, forbidden, partial, year deben ser objetos"]
    vocab = {f: {v for c in roster.values() for v in (c[f] if f in SETS else [c[f]])}
             for f in FIELDS}
    for field, value in state["exact"].items():
        if field not in FIELDS:
            errors.append(f"exact: atributo desconocido {field}")
            continue
        if field in SETS:
            if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
                errors.append(f"exact.{field} debe ser una lista no vacía")
                continue
            values = value
        else:
            if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
                values = value
            elif isinstance(value, str):
                values = [value]
            else:
                errors.append(f"exact.{field}: use a list containing exactly one string")
                continue
        if any(v not in vocab[field] for v in values):
            errors.append(f"exact.{field}: valor fuera del vocabulario")
    for field, values in state["forbidden"].items():
        if field not in FIELDS or not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            errors.append(f"forbidden.{field}: lista de textos inválida")
        elif any(v not in vocab[field] for v in values):
            errors.append(f"forbidden.{field}: valor fuera del vocabulario")
        else:
            required = state["exact"].get(field)
            required = required if isinstance(required, list) else [required]
            if all(isinstance(v, (str, type(None))) for v in required) and set(required) & set(values):
                errors.append(f"{field}: exact contiene un valor forbidden")
    for field, clauses in state["partial"].items():
        if field not in SETS or not isinstance(clauses, list):
            errors.append(f"partial.{field}: sólo atributos multivalor con listas de cláusulas")
        elif any(not isinstance(c, list) or not c or not all(isinstance(v, str) and v in vocab[field] for v in c) for c in clauses):
            errors.append(f"partial.{field}: cláusula inválida")
        else:
            denied = state['forbidden'].get(field, [])
            if isinstance(denied, list) and all(isinstance(v, str) for v in denied):
                for clause in clauses:
                    if set(clause) <= set(denied):
                        errors.append(f"partial.{field} requires overlap with {clause}, but all those values are forbidden. Yellow does NOT exclude its values.")
    year = state["year"]
    if set(year) - {"eq", "gt", "lt"} or any(v is not None and type(v) is not int for v in year.values()):
        errors.append("year accepts only eq, gt, lt with integer or null values; absent bounds mean unknown")
    else:
        eq, gt, lt = (year.get(k) for k in ("eq", "gt", "lt"))
        if gt is not None and lt is not None and gt + 1 >= lt:
            errors.append("year: intervalo entero vacío")
        if eq is not None and ((gt is not None and eq <= gt) or (lt is not None and eq >= lt)):
            errors.append("year: eq contradice los límites")
    if not isinstance(state["used"], list) or not all(isinstance(n, str) and n in roster for n in state["used"]):
        errors.append("used debe ser una lista de nombres exactos del roster")
    return errors


def violations(name, state, roster):
    if not isinstance(name, str) or name not in roster:
        return ["nombre fuera del roster"]
    attrs, errors = roster[name], []
    if name in state["used"]:
        errors.append("campeón ya utilizado")
    for field, value in state["exact"].items():
        expected = value[0] if field in SCALARS and isinstance(value, list) else value
        mismatch = set(attrs[field]) != set(value) if field in SETS else attrs[field] != expected
        if mismatch:
            errors.append(f"{field}: debe coincidir con {value}")
    for field, values in state["forbidden"].items():
        hits = set(attrs[field]) & set(values) if field in SETS else ({attrs[field]} & set(values))
        if hits:
            errors.append(f"{field}: valor descartado {sorted(hits)}")
    for field, clauses in state["partial"].items():
        for clause in clauses:
            value, partial = set(attrs[field]), set(clause)
            if not value & partial or value == partial:
                errors.append(f"{field}: debe compartir algo con {clause} sin ser igual")
    year = attrs["release_year"]
    for op, value in state["year"].items():
        if value is not None and ((op == "eq" and year != value) or (op == "gt" and year <= value) or (op == "lt" and year >= value)):
            errors.append(f"release_year: requiere {op} {value}")
    return errors


def query_roster(state, roster, limit=12):
    errors = state_errors(state, roster)
    if errors:
        return {"ok": False, "errors": errors, "candidates": [], "total": 0}
    candidates = [n for n in roster if not violations(n, state, roster)]
    return {"ok": True, "total": len(candidates), "candidates": candidates[:limit],
            "truncated": len(candidates) > limit}


def validate_move(name, history, roster):
    errors = violations(name, observed_state(history), roster)
    return {"ok": not errors, "candidate": name, "errors": errors,
            "source": "feedback público original; incluye amarillos"}
