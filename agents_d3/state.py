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
    return {"green": {}, "gray": {}, "yellow": {},
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
                state["green"][field] = copy.deepcopy(value)
            elif feedback[field] == "gray":
                values = value if field in SETS else [value]
                state["gray"][field] = sorted(set(state["gray"].get(field, []) + values))
            elif feedback[field] == "yellow":
                entry = sorted(value)
                clauses = state["yellow"].setdefault(field, [])
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


def normalize_state(state, roster=None):
    """Tolerancia de formato sin agregar evidencia: quita listas vacías y aplana
    cláusulas escritas como listas de listas de un valor ([["Top"],["Mid"]] -> ["Top","Mid"])."""
    if not isinstance(state, dict):
        return state
    state = copy.deepcopy(state)
    for key in ("green", "gray", "yellow", "year"):
        if key not in state:
            state[key] = {}
    state.setdefault("used", [])
    vocab = {f: {v for c in roster.values() for v in (c[f] if f in SETS else [c[f]])} for f in FIELDS} if roster else None

    def tokens(value, field=None):
        # Notación del formato D2 que arrastra el adaptador: "Sé: X", "A+B" y "X · Y" en una sola cadena.
        if isinstance(value, str):
            value = value.split(":", 1)[1] if value.lower().startswith("sé:") else value
            parts = [v.strip() for v in value.replace("·", "+").split("+") if v.strip()]
            if "·" in value and vocab and field in vocab:
                # Sólo descarta piezas de otros campos (p. ej. "Male · Darkin" en species); nunca agrega.
                parts = [v for v in parts if v in vocab[field]] or parts
            return parts if len(parts) > 1 else (parts[0] if parts else "")
        if isinstance(value, list):
            flat = []
            for v in value:
                t = tokens(v, field)
                flat.extend(t) if isinstance(t, list) and not isinstance(v, list) else flat.append(t)
            return flat
        return value

    for key in ("green", "gray", "yellow"):
        section = state.get(key)
        if not isinstance(section, dict):
            continue
        for field in list(section):
            value = section[field] = tokens(section[field], field)
            if key == "yellow" and isinstance(value, list) and value and all(isinstance(v, str) for v in value):
                value = [value]
            if key == "yellow" and isinstance(value, list):
                clauses = []
                for clause in value:
                    if isinstance(clause, list) and clause and all(isinstance(v, list) and len(v) == 1 for v in clause):
                        clause = [v[0] for v in clause]
                    if clause != []:
                        clauses.append(clause)
                section[field] = value = clauses
            if value in ([], "", None):
                del section[field]
    # Verde en el año es coincidencia exacta: green.release_year=X equivale a year.eq=X si no lo contradice.
    green_year = state["green"].get("release_year") if isinstance(state["green"], dict) else None
    if isinstance(green_year, list) and len(green_year) == 1:
        green_year = green_year[0]
    if isinstance(green_year, (int, str)) and str(green_year).strip().isdigit() and isinstance(state["year"], dict):
        if state["year"].get("eq") in (None, int(green_year)):
            state["year"]["eq"] = int(green_year)
            del state["green"]["release_year"]
    if isinstance(state["year"], dict):
        for op, value in list(state["year"].items()):
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if isinstance(value, str) and value.strip().isdigit():
                value = int(value)
            state["year"][op] = value
    return state


def state_errors(state, roster):
    """Formato, vocabulario y consistencia interna; no deduce pistas faltantes."""
    if not isinstance(state, dict):
        return ["state debe ser un objeto"]
    errors = []
    if set(state) != {"green", "gray", "yellow", "year", "used"}:
        return ["state requires exactly green, gray, yellow, year, used"]
    if not all(isinstance(state[k], dict) for k in ("green", "gray", "yellow", "year")):
        return ["green, gray, yellow, year must be objects"]
    vocab = {f: {v for c in roster.values() for v in (c[f] if f in SETS else [c[f]])}
             for f in FIELDS}
    for key in ("green", "gray"):
        if "release_year" in state[key]:
            errors.append(f"{key}.release_year: release_year never goes in {key}; write bounds in year, e.g. year={{\"gt\":2013}}")
    for field, value in state["green"].items():
        if field == "release_year":
            continue
        if field not in FIELDS:
            errors.append(f"green: atributo desconocido {field}")
            continue
        if field in SETS:
            if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
                errors.append(f"green.{field} debe ser una lista no vacía")
                continue
            values = value
        else:
            if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
                values = value
            elif isinstance(value, str):
                values = [value]
            else:
                errors.append(f"green.{field}: use a list containing exactly one string")
                continue
        if any(v not in vocab[field] for v in values):
            errors.append(f"green.{field}: valor fuera del vocabulario")
    for field, values in state["gray"].items():
        if field == "release_year":
            continue
        if field not in FIELDS or not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            errors.append(f"gray.{field}: lista de textos inválida")
        elif any(v not in vocab[field] for v in values):
            errors.append(f"gray.{field}: valor fuera del vocabulario")
        else:
            required = state["green"].get(field)
            required = required if isinstance(required, list) else [required]
            if all(isinstance(v, (str, type(None))) for v in required) and set(required) & set(values):
                errors.append(f"{field}: green contains a value that is also gray")
    for field, clauses in state["yellow"].items():
        if field == "release_year":
            errors.append("yellow.release_year: release_year never goes in yellow; write bounds in year, e.g. year={\"lt\":2013}")
        elif field not in SETS or not isinstance(clauses, list):
            errors.append(f"yellow.{field}: sólo atributos multivalor con listas de cláusulas")
        elif any(not isinstance(c, list) or not c or not all(isinstance(v, str) and v in vocab[field] for v in c) for c in clauses):
            errors.append(f"yellow.{field}: got {clauses}; each clause must be a flat LIST of known values, e.g. yellow.{field}=[[\"Middle\",\"Top\"]]")
        else:
            denied = state['gray'].get(field, [])
            if isinstance(denied, list) and all(isinstance(v, str) for v in denied):
                for clause in clauses:
                    if set(clause) <= set(denied):
                        errors.append(f"yellow.{field} requires overlap with {clause}, but all those values are in gray. Yellow values never go in gray.")
    year = state["year"]
    if set(year) - {"eq", "gt", "lt"} or any(v is not None and type(v) is not int for v in year.values()):
        errors.append("year accepts only eq, gt, lt with integer or null values; absent bounds mean unknown")
    else:
        eq, gt, lt = (year.get(k) for k in ("eq", "gt", "lt"))
        if gt is not None and lt is not None and gt + 1 >= lt:
            errors.append(f"year: gt {gt} and lt {lt} leave no possible year; higher feedback gives gt (newer than that guess), lower gives lt (older). Recheck each release_year clue")
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
        errors.append("already guessed: never repeat a used champion")
    for field, value in state["green"].items():
        expected = value[0] if field in SCALARS and isinstance(value, list) else value
        mismatch = set(attrs[field]) != set(value) if field in SETS else attrs[field] != expected
        if mismatch:
            errors.append(f"{field}: a green clue requires exactly {value}; candidate has {attrs[field]}")
    for field, values in state["gray"].items():
        hits = set(attrs[field]) & set(values) if field in SETS else ({attrs[field]} & set(values))
        if hits:
            errors.append(f"{field}: {sorted(hits)} got a gray clue, so it is forbidden")
    for field, clauses in state["yellow"].items():
        for clause in clauses:
            value, partial = set(attrs[field]), set(clause)
            if not value & partial or value == partial:
                errors.append(f"{field}: a yellow clue requires sharing some value with {clause} without being equal")
    year = attrs["release_year"]
    for op, value in state["year"].items():
        if value is not None and ((op == "eq" and year != value) or (op == "gt" and year <= value) or (op == "lt" and year >= value)):
            errors.append(f"release_year: public feedback requires year {op} {value}")
    return errors


def query_roster(state, roster, limit=12):
    """Filtro determinista: sólo para el control algorítmico, nunca para los agentes."""
    errors = state_errors(state, roster)
    if errors:
        return {"ok": False, "errors": errors, "candidates": [], "total": 0}
    candidates = [n for n in roster if not violations(n, state, roster)]
    return {"ok": True, "total": len(candidates), "candidates": candidates[:limit],
            "truncated": len(candidates) > limit}


def lookup(name, roster, state=None):
    """ver_atributos: la fila del roster de un nombre, como consultar la wiki.

    Con el estado de Memoria, coloca cada entrada junto al valor del mismo campo de la fila.
    Sólo yuxtapone: no compara ni marca coincidencias; el verificador juzga cada línea."""
    if name not in roster:
        return {"candidate": name, "found": False, "attributes": None}
    attrs = jsonable(roster[name])
    result = {"candidate": name, "found": True, "attributes": attrs}
    if isinstance(state, dict):
        lines = []
        for key in ("green", "gray", "yellow"):
            for field, value in (state.get(key) or {}).items():
                if field in attrs:
                    lines.append({"memory": f"{key} {field} {value}", "candidate_" + field: attrs[field]})
        for op, value in (state.get("year") or {}).items():
            if value is not None:
                lines.append({"memory": f"year {op} {value}", "candidate_release_year": attrs["release_year"]})
        lines.append({"memory": f"used {state.get('used', [])}", "candidate_name": name})
        result["side_by_side"] = lines
    return result


def validate_move(name, history, roster):
    """Sólo para métricas (violación estricta); los agentes no la reciben."""
    errors = violations(name, observed_state(history), roster)
    return {"ok": not errors, "candidate": name, "errors": errors,
            "source": "feedback público original; incluye amarillos"}
