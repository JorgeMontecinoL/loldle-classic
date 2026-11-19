"""Sistema del Entregable 4: el grafo del D3 con un adaptador por rol.

No cambia el controlador, los prompts ni el motor del D3 (`agents_d3/runtime.py`):
envuelve el cliente para que cada llamada lleve el adaptador de su rol. El rol se
reconoce por el prompt de sistema exacto de la llamada, que en el D3 es distinto
para Memoria, Selector (por páginas) y Verificador.

Configuraciones (todas con el mismo modelo base, prompts, presupuesto y temperatura):
    d3              Memoria, Selector y Verificador con d3_paginas_cot3 (D3 original).
    d4              Selector con el adaptador nuevo; Memoria y Verificador con d3_paginas_cot3.
    d4_selector_base Selector con el modelo base sin adaptador; los otros con d3_paginas_cot3.
"""
import hashlib
from pathlib import Path

from agents_d3.client import ModelClient
from agents_d3.runtime import AgentConfig, AgentSystem

ROOT = Path(__file__).resolve().parent.parent
BASE_MODEL = "mlx-community/Ministral-3-3B-Instruct-2512-4bit"
BASE_REVISION = "a962dcb09eee4169c890e544c9eb938f1113fdee"
D3_ADAPTER = "finetune/adapters/d3_paginas_cot3"
D4_ADAPTER = "finetune/adapters/d4_selector"   # el elegido en validación (copiado por select_checkpoint)
PROMPTS = Path(__file__).resolve().parent / "prompts"

SYSTEMS = {
    "d3": {"memory": D3_ADAPTER, "selector": D3_ADAPTER, "verifier": D3_ADAPTER},
    "d4": {"memory": D3_ADAPTER, "selector": D4_ADAPTER, "verifier": D3_ADAPTER},
    "d4_selector_base": {"memory": D3_ADAPTER, "selector": None, "verifier": D3_ADAPTER},
}
# Variantes de prompt del Selector. "d3" es el texto del D3 sin cambios; "amarillo" agrega un
# ejemplo resuelto de amarillos (sólo para la prueba de prompting en validación).
SELECTOR_PROMPTS = ("d3", "amarillo")


def adapter_sha(path):
    if not path:
        return None
    file = ROOT / path / "adapters.safetensors"
    return hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None


def resolve(path, override=None):
    if override is not None:
        return override
    return str((ROOT / path).resolve()) if path else None


class RoutedClient(ModelClient):
    """Un ModelClient que elige el adaptador según el rol de la llamada."""

    def __init__(self, base_url, adapters, max_tokens=768, model="default_model", servers=None):
        super().__init__(base_url, model, adapters.get("memory"), max_tokens)
        self.adapters = adapters
        self.home_url = base_url
        # servers: adaptador (ruta absoluta o None) -> URL de un servidor que ya lo tiene cargado.
        # mlx_lm server recarga el modelo cada vez que cambia el adaptador de la petición; con un
        # servidor por adaptador ninguna llamada paga esa recarga y los pesos son los mismos.
        self.servers = servers or {}
        self.role_by_prompt = {}
        self.calls_by_adapter = {}

    def bind(self, prompts):
        self.role_by_prompt = {prompts["memory"]: "memory", prompts["selector_paginas"]: "selector",
                               prompts["verifier"]: "verifier"}

    def complete(self, messages, max_tokens=None, prefix=None, temperature=0, seed=None):
        role = self.role_by_prompt.get(messages[0]["content"])
        if role is None:
            raise ValueError("Llamada sin rol reconocible: el prompt de sistema no es de Memoria, Selector ni Verificador")
        wanted = self.adapters[role]
        key = f"{role}:{Path(wanted).name if wanted else 'base'}"
        self.calls_by_adapter[key] = self.calls_by_adapter.get(key, 0) + 1
        if wanted in self.servers:
            # El adaptador viaja igual en la petición: el servidor dedicado siempre recibe el mismo
            # y no recarga (mlx_lm ignora --adapter-path cuando la petición usa "default_model").
            self.base_url, self.adapter = self.servers[wanted], wanted
        else:
            self.base_url, self.adapter = self.home_url, wanted
        try:
            return super().complete(messages, max_tokens=max_tokens, prefix=prefix, temperature=temperature, seed=seed)
        finally:
            self.base_url, self.adapter = self.home_url, self.adapters.get("memory")


def dedicated_servers():
    """Servidores con un adaptador precargado (scripts/servers_d4.sh), si están arriba."""
    from urllib.request import urlopen
    found = {}
    for path, port in ((None, 8083), (D3_ADAPTER, 8084), (D4_ADAPTER, 8085)):
        url = f"http://127.0.0.1:{port}/v1"
        try:
            with urlopen(url + "/models", timeout=2) as r:
                if r.status == 200:
                    found[resolve(path)] = url
        except Exception:
            pass
    return found if len(found) == 3 else {}


def selector_prompt(system_prompt, variant):
    if variant == "d3":
        return system_prompt
    extra = (PROMPTS / f"selector_{variant}.txt").read_text(encoding="utf-8")
    return system_prompt + "\n" + extra


def build_system(system="d4", base_url="http://127.0.0.1:8083/v1", prompt="d3", config=None,
                 adapter_override=None, observer=None, max_tokens=768, servers=None):
    """adapter_override: ruta (p. ej. un checkpoint o el artefacto bajado de Hugging Face)
    que reemplaza el adaptador del Selector en d4 (se envía por petición).
    servers: {ruta del adaptador o None: URL}; por defecto, los de scripts/servers_d4.sh si están arriba."""
    adapters = {role: resolve(path) for role, path in SYSTEMS[system].items()}
    if adapter_override and system == "d4":
        adapters["selector"] = str(Path(adapter_override).resolve())
    client = RoutedClient(base_url, adapters, max_tokens, servers=dedicated_servers() if servers is None else servers)
    agents = AgentSystem(client, config or AgentConfig(), observer)
    agents.prompts["selector_paginas"] = selector_prompt(agents.prompts["selector_paginas"], prompt)
    client.bind(agents.prompts)
    return agents, client


def describe(system, client, prompt):
    def sha(path):
        if not path:
            return None
        file = Path(path) / "adapters.safetensors"
        return hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None
    return {"system": system, "selector_prompt": prompt, "base_model": BASE_MODEL, "base_revision": BASE_REVISION,
            "adapters": {r: (str(Path(p).relative_to(ROOT)) if p and Path(p).is_relative_to(ROOT) else p)
                         for r, p in client.adapters.items()},
            "adapter_sha256": {r: sha(p) for r, p in client.adapters.items()}}
