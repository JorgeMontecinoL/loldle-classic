"""Cliente sin dependencias para un servidor OpenAI-compatible local."""
import json
import time
from urllib.request import Request, urlopen


class ModelClient:
    def __init__(self, base_url="http://127.0.0.1:8083/v1", model="default_model",
                 adapter=None, max_tokens=768, timeout=180):
        self.base_url, self.model, self.adapter = base_url.rstrip("/"), model, adapter
        self.max_tokens, self.timeout = max_tokens, timeout

    def complete(self, messages, max_tokens=None):
        body = {"model": self.model, "messages": messages, "temperature": 0,
                "max_tokens": max_tokens or self.max_tokens, "stream": False}
        if self.adapter:
            body["adapters"] = self.adapter
        start = time.monotonic()
        request = Request(self.base_url + "/chat/completions",
                          data=json.dumps(body, ensure_ascii=False).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        choice = payload["choices"][0]
        content = choice["message"].get("content") or ""
        return {"content": content, "latency_s": round(time.monotonic() - start, 4),
                "finish_reason": choice.get("finish_reason"), "usage": payload.get("usage", {})}


def parse_action(text):
    """Acepta JSON puro o una única valla; no inventa campos ni acciones."""
    value = text.strip()
    if value.startswith("```"):
        value = "\n".join(value.splitlines()[1:]).strip()
        if value.endswith("```"):
            value = value[:-3].strip()
    result = json.loads(value)
    if not isinstance(result, dict) or not isinstance(result.get("action"), str):
        raise ValueError("Respuesta debe ser objeto JSON con action de tipo string")
    return result
