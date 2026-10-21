"""Máquina de estados dirigida por acciones del modelo, con ciclos acotados."""
import copy
import hashlib
import json
import time
from importlib.metadata import version
from dataclasses import asdict, dataclass
from pathlib import Path

from run_benchmark import load_engine
from .client import parse_action
from .state import empty_state, jsonable, public_history, state_errors, validate_move
from .state import query_roster, observed_state, violations

PROMPTS = Path(__file__).resolve().parent / "prompts"
ROLES = ("memory", "selector", "verifier")
ALLOWED = {
    "memory": {"validar_estado", "entregar_estado", "stop"},
    "selector": {"consultar_roster", "proponer", "revisar_memoria", "stop"},
    "verifier": {"validar_jugada", "aprobar", "revisar_selector", "revisar_memoria", "stop"},
}


@dataclass
class AgentConfig:
    examples: bool = True
    previous_state: bool = True
    revision: bool = True
    max_calls_per_turn: int = 18
    max_calls_per_game: int = 160
    max_attempts: int = 10


def prompt_bundle(config):
    bundle = {r: (PROMPTS / (r + ".txt")).read_text(encoding="utf-8") for r in ROLES}
    common = (PROMPTS / "common.txt").read_text(encoding="utf-8")
    extra = ""
    if not config.revision:
        extra += "\n" + (PROMPTS / "no_revision.txt").read_text(encoding="utf-8")
    for role in bundle:
        examples = (PROMPTS / ("examples_" + role + ".txt")).read_text(encoding="utf-8") if config.examples else ""
        bundle[role] = common + "\n" + examples + "\n" + bundle[role] + "\n" + extra
    if not config.previous_state:
        bundle["memory"] += "\n" + (PROMPTS / "no_previous_state.txt").read_text(encoding="utf-8")
    return bundle


class AgentSystem:
    def __init__(self, client, config=None, observer=None):
        self.client, self.config = client, config or AgentConfig()
        self.ns = load_engine()
        self.ns["MAX_ATTEMPTS"] = self.config.max_attempts
        self.prompts = prompt_bundle(self.config)
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

    def decide(self, history, previous_state, emit, remaining):
        """No acepta target. Sólo observaciones públicas y estado de agentes."""
        actor, memory, candidate = "memory", None, None
        feedback = {"instruction": "Actualiza las restricciones y decide el siguiente paso."}
        conversations = {r: [] for r in ROLES}
        public = public_history(self.ns, history)
        for call in range(min(self.config.max_calls_per_turn, remaining)):
            available = [a for a in ALLOWED[actor] if self.config.revision or not a.startswith('revisar_')]
            payload = {"your_role": actor, "available_actions": sorted(available),
                       "history": public, "memory": memory, "candidate": candidate,
                       "message": feedback}
            if actor == "memory":
                payload.pop("candidate")
                # Unión por atributo de valores y colores públicos, sin inferir restricciones.
                payload['history'] = [{"turn": e['turn'], "guess": e['guess'],
                    "clues": [{"field": f, "value": (v if isinstance(v, list) or f == 'release_year' else [v]),
                               "feedback": e['feedback'][f]}
                              for f, v in (e['attributes'] or {}).items() if f != 'name'] if e['feedback'] else []}
                    for e in public]
            if actor == "selector":
                payload.pop("history")
            if actor == "memory" and self.config.previous_state:
                payload["previous_state"] = previous_state
            if conversations[actor] and ('ok' in feedback or 'errors' in feedback):
                # La evidencia ya está en el contexto; el nuevo turno destaca el resultado real.
                payload = {"your_role": actor, "message": feedback}
                if actor == 'verifier':
                    payload['candidate'] = candidate
                if actor in ('selector', 'verifier'):
                    # Cada decisión posterior a herramienta se basa en su resultado vigente.
                    # El historial original se recibió antes de auditar y sigue disponible a la herramienta.
                    conversations[actor] = []
            conversations[actor].append({"role": "user", "content": json.dumps(payload, ensure_ascii=False)})
            messages = [{"role": "system", "content": self.prompts[actor]}] + conversations[actor]
            emit("model_call", agent=actor, call=call + 1, messages=copy.deepcopy(messages))
            try:
                sample = self.client.complete(messages)
            except Exception as exc:
                emit("model_error", agent=actor, error=f"{type(exc).__name__}: {exc}")
                return None, memory, "model_error"
            emit("model_output", agent=actor, **sample)
            conversations[actor].append({"role": "assistant", "content": sample["content"]})
            try:
                decision = parse_action(sample["content"])
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
                    errors = state_errors(proposed, self.ns["CHAMPIONS"])
                    if errors:
                        feedback = {"ok": False, "errors": errors}
                        emit("protocol_error", agent=actor, **feedback)
                        continue
                    memory = copy.deepcopy(proposed)
                    if action == "validar_estado":
                        feedback = {"ok": True, "instruction": "State schema is valid. Deliver the SAME state with action entregar_estado now. No evidence was added."}
                        emit("tool_result", agent=actor, tool=action, arguments={"state": memory}, result=feedback)
                    else:
                        emit("handoff", source=actor, destination="selector", state=memory)
                        actor, feedback = "selector", {"instruction": "Selecciona una jugada con el estado entregado."}
                elif actor == "selector":
                    if action == "consultar_roster":
                        args = decision.get("arguments", {})
                        if not isinstance(args, dict) or args.get("state_id", "memory") != "memory":
                            raise ValueError("consultar_roster requiere state_id=memory")
                        limit = args.get("limit", 12)
                        if type(limit) is not int or not 1 <= limit <= 30:
                            raise ValueError("limit debe ser entero entre 1 y 30")
                        feedback = query_roster(memory, self.ns["CHAMPIONS"], limit)
                        emit("tool_result", agent=actor, tool=action, arguments=args, result=feedback)
                    elif action == "proponer":
                        candidate = decision.get("candidate")
                        if not isinstance(candidate, str):
                            raise ValueError("candidate debe ser texto")
                        emit("handoff", source=actor, destination="verifier", candidate=candidate, state=memory)
                        actor, feedback = "verifier", {"instruction": "Audita la propuesta y decide."}
                    else:
                        feedback = {"reason": decision.get("reason"), "candidate": candidate}
                        emit("handoff", source=actor, destination="memory", **feedback)
                        actor = "memory"
                else:
                    if action in ("validar_jugada", "aprobar"):
                        if decision.get("candidate", candidate) != candidate:
                            raise ValueError("Verificador debe auditar/aprobar el candidato recibido")
                        if action == "validar_jugada":
                            feedback = validate_move(candidate, public, self.ns["CHAMPIONS"])
                            emit("tool_result", agent=actor, tool=action, arguments={"candidate": candidate}, result=feedback)
                        else:
                            # Se aplica la aprobación real del agente, incluso si se equivocó.
                            emit("approved", agent=actor, candidate=candidate, state=memory)
                            return candidate, memory, None
                    else:
                        destination = "memory" if action == "revisar_memoria" else "selector"
                        feedback = {"reason": decision.get("reason"), "candidate": candidate}
                        emit("handoff", source=actor, destination=destination, **feedback)
                        actor = destination
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                feedback = {"ok": False, "errors": [str(exc)], "instruction": "Corrige el formato/acción en JSON."}
                emit("protocol_error", agent=actor, **feedback)
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
