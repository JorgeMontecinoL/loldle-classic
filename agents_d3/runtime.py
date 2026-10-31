"""Máquina de estados dirigida por acciones del modelo, con ciclos acotados."""
import copy
import hashlib
import json
import time
from importlib.metadata import version
from dataclasses import asdict, dataclass
from pathlib import Path

from run_benchmark import load_engine, last_line
from .client import parse_action
from .state import empty_state, jsonable, lookup, normalize_state, public_history, state_errors, validate_move
from .state import query_roster, observed_state

PROMPTS = Path(__file__).resolve().parent / "prompts"
ROLES = ("memory", "selector", "verifier")
JSON_ROLES = ("memory", "verifier")
SELECTOR_MAX_TOKENS = 128
# Prefill de salida estructurada: los roles JSON empiezan su respuesta con estas llaves.
PREFIX = {"memory": '{"action":"', "verifier": '{"action":"'}
# Búsqueda por páginas (v4): el Selector revisa el roster de a PAGE_SIZE filas y lista las que cumplen el estado.
PAGE_SIZE = 25
PAGE_PREFIX = '{"action":"listar","revision":'
PAGE_MAX_TOKENS = 400
ALLOWED = {
    "memory": {"validar_estado", "entregar_estado"},
    "selector": {"proponer", "listar"},
    "verifier": {"ver_atributos", "aprobar", "revisar_selector", "revisar_memoria", "stop"},
}


def years_allowed(state, roster):
    """Los años que permite el estado escrito por Memoria (eq/gt/lt), dentro del rango del roster.
    Reformatea el estado del agente; no consulta la evidencia. None si no hay límites."""
    year = (state or {}).get("year") or {}
    if all(year.get(k) is None for k in ("eq", "gt", "lt")):
        return None
    years = sorted({c["release_year"] for c in roster.values()})
    return [y for y in range(years[0], years[-1] + 1)
            if (year.get("eq") is None or y == year["eq"]) and (year.get("gt") is None or y > year["gt"])
            and (year.get("lt") is None or y < year["lt"])]


def public_clues(public):
    """Cada valor unido a su color público; el año con la lectura literal de su flecha."""
    arrow = {"green": "=", "higher": ">", "lower": "<"}
    return [{"turn": e['turn'], "guess": e['guess'],
             "clues": [{"field": f, "value": (v if isinstance(v, list) else [v]), "feedback": e['feedback'][f]}
                       for f, v in (e['attributes'] or {}).items() if f not in ('name', 'release_year')] if e['feedback'] else [],
             "release_year": ({"value": e['attributes']['release_year'], "feedback": e['feedback']['release_year'],
                               "means": f"answer year {arrow[e['feedback']['release_year']]} {e['attributes']['release_year']}"}
                              if e['feedback'] else None)}
            for e in public]


@dataclass
class AgentConfig:
    examples: bool = True
    previous_state: bool = True
    revision: bool = True
    max_calls_per_turn: int = 60
    max_calls_per_game: int = 160
    max_attempts: int = 10
    search: str = "paginas"       # "paginas" (v4) o "d2" (v3: Selector en el formato del D2)
    max_rejections: int = 3       # rechazos del Verificador por turno; luego sólo aprueba o para
    retry_temperature: float = 0.6  # reintentos de Memoria tras un error: muestreo con semilla fija
    search_temperature: float = 0.7  # búsquedas repetidas tras una búsqueda vacía: muestreo con semilla fija
    search_retries: int = 3          # pasadas muestreadas por el roster antes de devolver el trabajo a Memoria


def prompt_bundle(config):
    """Memoria y Verificador: prompts JSON propios. Selector: el prompt del D2, sin cambios."""
    bundle = {r: (PROMPTS / (r + ".txt")).read_text(encoding="utf-8") for r in JSON_ROLES}
    common = (PROMPTS / "common.txt").read_text(encoding="utf-8")
    extra = ""
    if not config.revision:
        extra += "\n" + (PROMPTS / "no_revision.txt").read_text(encoding="utf-8")
    for role in bundle:
        examples = (PROMPTS / ("examples_" + role + ".txt")).read_text(encoding="utf-8") if config.examples else ""
        bundle[role] = common + "\n" + examples + "\n" + bundle[role] + "\n" + extra
    if not config.previous_state:
        bundle["memory"] += "\n" + (PROMPTS / "no_previous_state.txt").read_text(encoding="utf-8")
    bundle["selector"] = (PROMPTS / "selector.txt").read_text(encoding="utf-8")
    bundle["selector_turn"] = (PROMPTS / "selector_turn.txt").read_text(encoding="utf-8")
    if config.search == "paginas":
        examples = (PROMPTS / "examples_selector_paginas.txt").read_text(encoding="utf-8") if config.examples else ""
        bundle["selector_paginas"] = common + "\n" + examples + "\n" + (PROMPTS / "selector_paginas.txt").read_text(encoding="utf-8")
    return bundle


def selector_templates(text):
    return dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)


def state_note(state):
    """El estado de Memoria en el vocabulario del juego, para el mensaje del Selector."""
    parts = []
    for field, value in state.get("green", {}).items():
        parts.append(f"{field} VERDE {', '.join(value) if isinstance(value, list) else value}")
    for field, value in state.get("gray", {}).items():
        parts.append(f"{field} GRIS (nunca) {', '.join(value)}")
    for field, clauses in state.get("yellow", {}).items():
        for clause in clauses:
            parts.append(f"{field} AMARILLO (comparte algo con) {', '.join(clause)}")
    for op, sign in (("eq", "="), ("gt", ">"), ("lt", "<")):
        if state.get("year", {}).get(op) is not None:
            parts.append(f"año {sign} {state['year'][op]}")
    if state.get("used"):
        parts.append("ya jugados " + ", ".join(state["used"]))
    return " · ".join(parts)


class AgentSystem:
    def __init__(self, client, config=None, observer=None):
        self.client, self.config = client, config or AgentConfig()
        self.ns = load_engine()
        self.ns["MAX_ATTEMPTS"] = self.config.max_attempts
        self.prompts = prompt_bundle(self.config)
        # El Selector es la solución D2: mismo prompt y roster que el notebook, verificado byte a byte.
        self.prompts["selector"] = self.prompts["selector"].replace("{ROSTER_TEXT}", self.ns["ROSTER_TEXT"])
        if self.prompts["selector"] != self.ns["SYSTEM_PROMPT"]:
            raise ValueError("prompts/selector.txt ya no coincide con el SYSTEM_PROMPT del notebook")
        self.templates = selector_templates(self.prompts["selector_turn"])
        self.observer = observer or (lambda event: None)

    def metadata(self):
        adapter = self.client.adapter
        adapter_file = Path(adapter) / "adapters.safetensors" if adapter else None
        return {"agents": asdict(self.config), "base_url": self.client.base_url,
                "base_model": "mlx-community/Ministral-3-3B-Instruct-2512-4bit",
                "mlx_lm_version": version("mlx-lm"),
                "engine_sha256": hashlib.sha256((PROMPTS.parent.parent / 'LoLdle_Classic.ipynb').read_bytes()).hexdigest(),
                "model": self.client.model,
                "adapter": Path(adapter).name if adapter else None,
                "adapter_sha256": hashlib.sha256(adapter_file.read_bytes()).hexdigest() if adapter_file and adapter_file.exists() else None,
                "max_tokens_per_call": self.client.max_tokens, "temperature": 0,
                "prompt_sha256": {r: hashlib.sha256(p.encode()).hexdigest() for r, p in self.prompts.items()},
                "prompts": self.prompts}

    def roster_pages(self):
        lines = self.ns["ROSTER_TEXT"].strip().splitlines()
        header, rows = lines[0], lines[1:]
        return [(header, rows[i:i + PAGE_SIZE]) for i in range(0, len(rows), PAGE_SIZE)]

    def _decide_paginas(self, history, previous_state, emit, remaining):
        """v4: Memoria → Selector por páginas → Verificador sobre la lista, con límite de rechazos.
        No acepta target. El código sólo pagina el roster; ninguna herramienta compara filas."""
        roster = self.ns["CHAMPIONS"]
        public = public_history(self.ns, history)
        clues = public_clues(public)
        guessed = [e["guess"] for e in public if e["guess"]]
        pages = self.roster_pages()
        actor, memory, candidate = "memory", None, None
        feedback = {"instruction": "Actualiza las restricciones y decide el siguiente paso."}
        memory_conv, verifier_conv = [], []
        rejected, shortlist, found, page = [], [], [], 0
        rejections, page_errors, search_round = 0, 0, 0
        turn = len(public) + 1

        def call(role, prompt, conv, max_tokens=None, prefix=None, temperature=0, seed=None):
            # A temperatura 0 una entrada idéntica repite la misma salida: los reintentos muestrean
            # con una semilla fija por turno y reintento, así que la corrida sigue siendo reproducible.
            messages = [{"role": "system", "content": prompt}] + conv
            emit("model_call", agent=role, call=len(calls) + 1, messages=copy.deepcopy(messages),
                 sampling={"temperature": temperature, "seed": seed})
            calls.append(role)
            sample = self.client.complete(messages, max_tokens=max_tokens, prefix=prefix, temperature=temperature, seed=seed)
            emit("model_output", agent=role, **sample)
            return sample

        calls = []
        while len(calls) < min(self.config.max_calls_per_turn, remaining):
            try:
                if actor == "memory":
                    if not memory_conv or memory_conv[-1]["role"] == "assistant":
                        payload = {"your_role": "memory", "available_actions": ["entregar_estado", "validar_estado"], "message": feedback}
                        if self.config.previous_state and "reason" not in feedback:
                            payload["new_clues"] = clues[-1:]
                            payload["previous_state"] = previous_state
                        else:
                            payload["history"] = clues
                            if self.config.previous_state:
                                payload["previous_state"] = previous_state
                        memory_conv = [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
                    retry = json.loads(memory_conv[0]["content"]).get("retry", 0)
                    sample = call("memory", self.prompts["memory"], memory_conv, prefix=PREFIX["memory"],
                                  temperature=self.config.retry_temperature if retry else 0,
                                  seed=1000 * turn + retry if retry else None)
                    memory_conv.append({"role": "assistant", "content": sample["content"]})
                    decision = parse_action(sample["content"])
                    if decision["action"] not in ALLOWED["memory"]:
                        raise ValueError(f"acción {decision['action']!r} no disponible para memory")
                    emit("decision", agent="memory", decision=decision)
                    proposed = {k: v for k, v in decision.items() if k != "action"}
                    normalized = normalize_state(proposed, roster)
                    if normalized != proposed:
                        emit("normalized", agent="memory", before=proposed, after=normalized)
                        proposed = normalized
                    errors = state_errors(proposed, roster)
                    if errors:
                        emit("protocol_error", agent="memory", ok=False, errors=errors)
                        first = json.loads(memory_conv[0]["content"])
                        first["previous_attempt_errors"] = errors
                        first["retry"] = first.get("retry", 0) + 1
                        memory_conv = [{"role": "user", "content": json.dumps(first, ensure_ascii=False)}]
                        continue
                    memory = copy.deepcopy(proposed)
                    if decision["action"] == "validar_estado":
                        memory_conv.append({"role": "user", "content": json.dumps({"your_role": "memory", "message": {"ok": True,
                            "instruction": "State schema is valid. Deliver the SAME state with action entregar_estado now."}})})
                        continue
                    emit("handoff", source="memory", destination="selector", state=memory)
                    actor, page, found, shortlist = "selector", 0, [], []
                elif actor == "selector":
                    header, rows = pages[page]
                    excluded = guessed + rejected
                    payload = {"your_role": "selector", "available_actions": ["listar"], "memory": memory,
                               "excluded": excluded, "page": f"{page + 1}/{len(pages)}", "rows": "\n".join([header] + rows)}
                    allowed = years_allowed(memory, roster)
                    if allowed is not None:
                        payload["years_allowed"] = allowed
                    conv = [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
                    sample = call("selector", self.prompts["selector_paginas"], conv, PAGE_MAX_TOKENS, PAGE_PREFIX,
                                  temperature=self.config.search_temperature if search_round else 0,
                                  seed=10000 * turn + 100 * search_round + page if search_round else None)
                    try:
                        decision = parse_action(sample["content"])
                        if decision["action"] != "listar" or not isinstance(decision.get("candidates"), list):
                            raise ValueError("el Selector debe responder listar con una lista de nombres")
                    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                        emit("protocol_error", agent="selector", ok=False, errors=[str(exc)], page=page + 1)
                        page_errors += 1
                        if page_errors < 2:
                            continue
                        # Segunda respuesta ilegible en la misma página: cuenta como página sin candidatos.
                        decision = {"action": "listar", "candidates": []}
                    page_errors = 0
                    names = {r.split("|", 1)[0] for r in rows}
                    # Sólo nombres de esta página, en su orden; los que no están en la página se descartan.
                    listed = [n for n in decision["candidates"] if isinstance(n, str) and n in names and n not in excluded]
                    emit("decision", agent="selector", decision={"action": "listar", "page": page + 1, "candidates": listed,
                                                                "revision": decision.get("revision")})
                    found += [n for n in listed if n not in found]
                    page += 1
                    if page < len(pages):
                        continue
                    shortlist = list(found)
                    if not shortlist and search_round % (self.config.search_retries + 1) != self.config.search_retries:
                        # Búsqueda vacía: otra pasada por el roster, muestreada con otra semilla, antes de molestar a Memoria.
                        # En el cierre suele cumplir una sola fila, y un falso "x" la pierde.
                        search_round += 1
                        emit("search_retry", agent="selector", round=search_round)
                        page, found = 0, []
                        continue
                    if not shortlist:
                        search_round += 1
                        # Arista declarada del grafo: sin candidatos en todo el roster, Memoria revisa su estado.
                        feedback = {"reason": "El Selector no encontró en el roster ningún campeón que cumpla el estado.", "rejected": list(rejected)}
                        emit("handoff", source="selector", destination="memory", **feedback)
                        actor, memory_conv = "memory", []
                        continue
                    candidate = shortlist.pop(0)
                    emit("handoff", source="selector", destination="verifier", candidate=candidate, shortlist=list(shortlist), state=memory)
                    actor, verifier_conv = "verifier", []
                else:
                    limit = rejections >= self.config.max_rejections or not self.config.revision
                    available = ["aprobar", "stop", "ver_atributos"] + ([] if limit else ["revisar_memoria", "revisar_selector"])
                    if not verifier_conv:
                        payload = {"your_role": "verifier", "available_actions": sorted(available), "candidate": candidate,
                                   "history": clues, "memory": memory, "message": {"instruction": "Revisa la propuesta contra cada pista y decide."}}
                        verifier_conv = [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
                    sample = call("verifier", self.prompts["verifier"], verifier_conv, prefix=PREFIX["verifier"])
                    verifier_conv.append({"role": "assistant", "content": sample["content"]})
                    decision = parse_action(sample["content"], lenient=True)
                    action = decision["action"]
                    if action not in available:
                        if action.startswith("revisar_") and not self.config.revision:
                            emit("stop", agent="verifier", reason="revision_disabled", decision=decision)
                            return None, memory, "revision_disabled"
                        raise ValueError(f"acción {action!r} no disponible: " + ("límite de rechazos, aprueba o para" if limit else "acción inválida"))
                    emit("decision", agent="verifier", decision=decision)
                    if action == "stop":
                        return None, memory, "agent_stop: " + str(decision.get("reason", "sin motivo"))
                    if action == "ver_atributos":
                        result = lookup(candidate, roster, memory)
                        emit("tool_result", agent="verifier", tool=action, arguments={"candidate": candidate}, result=result)
                        verifier_conv.append({"role": "user", "content": json.dumps({"your_role": "verifier", "message": result, "candidate": candidate}, ensure_ascii=False)})
                    elif action == "aprobar":
                        emit("approved", agent="verifier", candidate=candidate, state=memory)
                        return candidate, memory, None
                    else:
                        rejections += 1
                        rejected.append(candidate)
                        feedback = {"reason": decision.get("reason"), "candidate": candidate, "rejected": list(rejected)}
                        if action == "revisar_memoria":
                            emit("handoff", source="verifier", destination="memory", **feedback)
                            actor, memory_conv = "memory", []
                        elif shortlist:
                            # El siguiente de la lista del Selector, sin volver a buscar.
                            candidate = shortlist.pop(0)
                            emit("handoff", source="verifier", destination="selector", **feedback)
                            emit("handoff", source="selector", destination="verifier", candidate=candidate, shortlist=list(shortlist), state=memory)
                            verifier_conv = []
                        else:
                            emit("handoff", source="verifier", destination="selector", **feedback)
                            actor, page, found = "selector", 0, []
            except Exception as exc:
                if isinstance(exc, (ValueError, KeyError, TypeError, json.JSONDecodeError)):
                    emit("protocol_error", agent=actor, ok=False, errors=[str(exc)])
                    if actor == "verifier":
                        verifier_conv.append({"role": "user", "content": json.dumps({"your_role": "verifier", "message": {"ok": False, "errors": [str(exc)],
                            "instruction": "Corrige el formato/acción en JSON."}}, ensure_ascii=False)})
                    continue
                emit("model_error", agent=actor, error=f"{type(exc).__name__}: {exc}")
                return None, memory, "model_error"
        emit("stop", agent=actor, reason="call_limit")
        return None, memory, "call_limit"

    def decide(self, history, previous_state, emit, remaining):
        """No acepta target. Sólo observaciones públicas y estado de agentes."""
        if self.config.search == "paginas":
            return self._decide_paginas(history, previous_state, emit, remaining)
        actor, memory, candidate = "memory", None, None
        feedback = {"instruction": "Actualiza las restricciones y decide el siguiente paso."}
        conversations = {r: [] for r in ROLES}
        public = public_history(self.ns, history)
        clues = public_clues(public)
        guessed = [e["guess"] for e in public if e["guess"]]
        # Propuestas que el verificador devolvió en este turno: el selector las ve y decide no repetirlas.
        rejected = []

        def memory_retry(errors):
            # Contexto fresco: la entrada original de Memoria más los errores, sin su respuesta fallida
            # (a temperatura 0 tiende a copiarla). La traza conserva el intento fallido.
            first = json.loads(conversations["memory"][0]["content"])
            first["previous_attempt_errors"] = errors
            # El número de reintento cambia la entrada: a temperatura 0, una entrada idéntica repite la misma salida.
            first["retry"] = first.get("retry", 0) + 1
            conversations["memory"] = [{"role": "user", "content": json.dumps(first, ensure_ascii=False)}]

        for call in range(min(self.config.max_calls_per_turn, remaining)):
            available = sorted(a for a in ALLOWED[actor] if self.config.revision or not a.startswith('revisar_'))
            if conversations[actor] and ('ok' in feedback or 'errors' in feedback or 'attributes' in feedback):
                # El agente ya tiene su contexto del turno; el nuevo mensaje sólo trae el resultado.
                payload = {"your_role": actor, "message": feedback}
                if actor == 'verifier':
                    payload['candidate'] = candidate
            elif actor == "memory":
                payload = {"your_role": actor, "available_actions": available, "message": feedback}
                if self.config.previous_state and "reason" not in feedback:
                    # Actualización incremental: el estado previo ya resume los intentos anteriores.
                    # Ante una crítica recibe el historial completo para reconstruir el estado.
                    payload["new_clues"] = clues[-1:]
                    payload["previous_state"] = previous_state
                else:
                    payload["history"] = clues
                    if self.config.previous_state:
                        payload["previous_state"] = previous_state
            elif actor == "selector":
                payload = None
            else:
                payload = {"your_role": actor, "available_actions": available, "candidate": candidate,
                           "history": clues, "memory": memory, "message": feedback}
            if actor == "selector":
                # Conversación del D2: sistema + intentos jugados; la nota de Memoria va en el último mensaje
                # y los rechazos del turno se agregan como réplicas, igual que el feedback del juego.
                if not conversations["selector"]:
                    base = self.ns["build_messages"](history)
                    note = state_note(memory or {})
                    if note:
                        base[-1] = dict(base[-1], content=base[-1]["content"] + "\n" + self.templates["NOTE"].format(state=note))
                    conversations["selector"] = base[1:]
                elif "reason" in feedback:
                    conversations["selector"].append({"role": "user", "content": self.templates["REJECT"].format(
                        candidate=feedback.get("candidate"), reason=feedback.get("reason"))})
                else:
                    conversations["selector"].append({"role": "user", "content": self.templates["FORMAT"]})
            elif not (actor == "memory" and conversations["memory"] and conversations["memory"][-1]["role"] == "user"):
                # (Tras un reintento, Memoria ya tiene su entrada fresca con los errores.)
                conversations[actor].append({"role": "user", "content": json.dumps(payload, ensure_ascii=False)})
            messages = [{"role": "system", "content": self.prompts[actor]}] + conversations[actor]
            emit("model_call", agent=actor, call=call + 1, messages=copy.deepcopy(messages))
            try:
                sample = self.client.complete(messages, max_tokens=SELECTOR_MAX_TOKENS if actor == "selector" else None,
                                              prefix=PREFIX.get(actor))
            except Exception as exc:
                emit("model_error", agent=actor, error=f"{type(exc).__name__}: {exc}")
                return None, memory, "model_error"
            emit("model_output", agent=actor, **sample)
            conversations[actor].append({"role": "assistant", "content": sample["content"]})
            try:
                if actor == "selector":
                    # Formato D2: la jugada es la última línea; Sé:/Compatibles: quedan en la traza.
                    name = self.ns["parse_response"](last_line(sample["content"]))["name"]
                    if not name:
                        raise ValueError("la última línea no es un campeón del roster")
                    decision = {"action": "proponer", "candidate": name}
                else:
                    decision = parse_action(sample["content"], lenient=actor == "verifier")
                action = decision["action"]
                if action not in ALLOWED[actor]:
                    raise ValueError(f"acción {action!r} no disponible para {actor}")
                if not self.config.revision and action.startswith("revisar_"):
                    emit("stop", agent=actor, reason="revision_disabled", decision=decision)
                    return None, memory, "revision_disabled"
                emit("decision", agent=actor, decision=decision)
                if action == "stop":
                    return None, memory, "agent_stop: " + str(decision.get("reason", "sin motivo"))
                if actor == "memory":
                    proposed = {k: v for k, v in decision.items() if k != "action"}
                    normalized = normalize_state(proposed, self.ns["CHAMPIONS"])
                    if normalized != proposed:
                        emit("normalized", agent=actor, before=proposed, after=normalized)
                        proposed = normalized
                    errors = state_errors(proposed, self.ns["CHAMPIONS"])
                    if errors:
                        feedback = {"ok": False, "errors": errors}
                        emit("protocol_error", agent=actor, **feedback)
                        memory_retry(errors)
                        continue
                    memory = copy.deepcopy(proposed)
                    if action == "validar_estado":
                        feedback = {"ok": True, "instruction": "State schema is valid. Deliver the SAME state with action entregar_estado now. No evidence was added."}
                        emit("tool_result", agent=actor, tool=action, arguments={"state": memory}, result=feedback)
                    else:
                        emit("handoff", source=actor, destination="selector", state=memory)
                        actor, feedback = "selector", {"instruction": "Elige del roster un campeón que cumpla el estado."}
                        conversations["selector"] = []
                elif actor == "selector":
                    candidate = decision["candidate"]
                    emit("handoff", source=actor, destination="verifier", candidate=candidate, state=memory)
                    actor, feedback = "verifier", {"instruction": "Revisa la propuesta contra cada pista y decide."}
                    conversations["verifier"] = []
                else:
                    if decision.get("candidate", candidate) != candidate:
                        raise ValueError("Verificador debe revisar/aprobar el candidato recibido")
                    if action == "ver_atributos":
                        feedback = lookup(candidate, self.ns["CHAMPIONS"], memory)
                        emit("tool_result", agent=actor, tool=action, arguments={"candidate": candidate}, result=feedback)
                    elif action == "aprobar":
                        # Se aplica la aprobación real del agente, incluso si se equivocó.
                        emit("approved", agent=actor, candidate=candidate, state=memory)
                        return candidate, memory, None
                    else:
                        destination = "memory" if action == "revisar_memoria" else "selector"
                        if candidate not in rejected:
                            rejected.append(candidate)
                        feedback = {"reason": decision.get("reason"), "candidate": candidate, "rejected": list(rejected)}
                        emit("handoff", source=actor, destination=destination, **feedback)
                        actor = destination
                        if destination == "memory":
                            conversations["memory"] = []
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                feedback = {"ok": False, "errors": [str(exc)], "instruction": "Corrige el formato/acción en JSON."}
                emit("protocol_error", agent=actor, **feedback)
                if actor == "memory":
                    memory_retry(feedback["errors"])
        emit("stop", agent=actor, reason="call_limit")
        return None, memory, "call_limit"

    def play(self, target, game_number=1):
        """target queda en el evaluador: no pasa a decide(), prompts ni herramientas."""
        if target not in self.ns["CHAMPIONS"]:
            raise ValueError("Objetivo desconocido")
        start, events, history = time.monotonic(), [], []
        previous, stop_reason, turn = empty_state(), None, 0

        def emit(kind, **data):
            item = {"kind": kind, "turn": turn, "t": round(time.monotonic() - start, 4), **jsonable(data)}
            events.append(item)
            self.observer(copy.deepcopy(item))

        constraints = self.ns["empty_constraints"]()
        for turn in range(1, self.config.max_attempts + 1):
            emit("turn_start", history=public_history(self.ns, history))
            calls = sum(e["kind"] == "model_call" for e in events)
            remaining = self.config.max_calls_per_game - calls
            candidate, previous, stop_reason = self.decide(history, previous, emit, remaining)
            if candidate is None:
                break
            original = public_history(self.ns, history)
            strict_errors = validate_move(candidate, original, self.ns["CHAMPIONS"])["errors"]
            event = self.ns["evaluate_attempt"](candidate, target, history, constraints)
            event.update(turn=turn, strict_violation=bool(strict_errors), strict_errors=strict_errors)
            history.append(event)
            emit("game_feedback", event=event)
            if event["solved"]:
                break
        record = {"game": game_number, "target": target, "solved": bool(history and history[-1]["solved"]),
                  "attempts_used": len(history), "trace": history, "agent_trace": events,
                  "stop_reason": stop_reason,
                  "wall_seconds": round(time.monotonic() - start, 3)}
        emit("game_end", solved=record["solved"], attempts=record["attempts_used"], stop_reason=stop_reason)
        return record


def algorithmic_control(ns, target, game_number=1):
    """Sin LLM: techo del filtro de evidencia pública, declarado como control."""
    history, constraints = [], ns["empty_constraints"]()
    for turn in range(1, 11):
        public = public_history(ns, history)
        state = observed_state(public)
        candidates = query_roster(state, ns["CHAMPIONS"])["candidates"]
        if not candidates:
            break
        event = ns["evaluate_attempt"](candidates[0], target, history, constraints)
        event.update(turn=turn, strict_violation=False, strict_errors=[])
        history.append(event)
        if event["solved"]:
            break
    return {"game": game_number, "target": target, "trace": history,
            "attempts_used": len(history), "solved": bool(history and history[-1]["solved"]),
            "agent_trace": [], "stop_reason": None}
