"""Cliente sin dependencias para un servidor OpenAI-compatible local."""
import json
import re
import time
from urllib.request import Request, urlopen


BASE_MODEL = "mlx-community/Ministral-3-3B-Instruct-2512-4bit"
_TEMPLATE = None


def chat_template():
    """Tokenizador local del modelo base, sólo para su plantilla de chat."""
    global _TEMPLATE
    if _TEMPLATE is None:
        from huggingface_hub import snapshot_download
        from transformers import AutoTokenizer
        _TEMPLATE = AutoTokenizer.from_pretrained(snapshot_download(BASE_MODEL, local_files_only=True))
    return _TEMPLATE


class ModelClient:
    def __init__(self, base_url="http://127.0.0.1:8083/v1", model="default_model",
                 adapter=None, max_tokens=768, timeout=180):
        self.base_url, self.model, self.adapter = base_url.rstrip("/"), model, adapter
        self.max_tokens, self.timeout = max_tokens, timeout

    def complete(self, messages, max_tokens=None, prefix=None, temperature=0, seed=None):
        """prefix fuerza el comienzo de la respuesta (prefill), p. ej. '{"action":"' para roles JSON.
        Usa /completions con la plantilla de chat del modelo; la respuesta incluye el prefijo."""
        body = {"model": self.model, "temperature": temperature,
                "max_tokens": max_tokens or self.max_tokens, "stream": False}
        if seed is not None:
            body["seed"] = seed  # muestreo reproducible en los reintentos
        if prefix:
            text = chat_template().apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
            body["prompt"] = text.removeprefix("<s>") + prefix  # el servidor agrega BOS al tokenizar
            endpoint = "/completions"
        else:
            body["messages"] = messages
            endpoint = "/chat/completions"
        if self.adapter:
            body["adapters"] = self.adapter
        start = time.monotonic()
        request = Request(self.base_url + endpoint,
                          data=json.dumps(body, ensure_ascii=False).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        choice = payload["choices"][0]
        content = (prefix + choice.get("text", "")) if prefix else (choice["message"].get("content") or "")
        return {"content": content, "latency_s": round(time.monotonic() - start, 4),
                "finish_reason": choice.get("finish_reason"), "usage": payload.get("usage", {})}


def parse_action(text, lenient=False):
    """Acepta JSON puro o una única valla; no inventa campos ni acciones.

    lenient (sólo acciones sin carga, como las del Verificador): si el JSON está roto,
    toma el único "action" y "reason" escritos literalmente en el texto."""
    value = text.strip()
    if value.startswith("```"):
        value = "\n".join(value.splitlines()[1:]).strip()
        if value.endswith("```"):
            value = value[:-3].strip()
    try:
        # Primer objeto JSON completo; se ignora texto posterior (el adaptador a veces sigue en formato D2).
        result = json.JSONDecoder(strict=False).raw_decode(value)[0] if value.startswith("{") else json.loads(value)
    except json.JSONDecodeError:
        actions = set(re.findall(r'"action"\s*:\s*"([a-z_]+)"', value))
        if not lenient or len(actions) != 1:
            raise
        reason = re.search(r'"reason"\s*:\s*"([^"]*)"', value)
        result = {"action": actions.pop(), "reason": reason.group(1) if reason else None, "lenient_parse": True}
    if not isinstance(result, dict) or not isinstance(result.get("action"), str):
        raise ValueError("Respuesta debe ser objeto JSON con action de tipo string")
    return result
