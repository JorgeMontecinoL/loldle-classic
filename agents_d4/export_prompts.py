"""Escribe el prompt de sistema exacto de cada agente, un archivo por agente.

Los prompts se componen desde `agents_d3/prompts/` (common + ejemplos + rol). Este
script guarda el texto final que recibe el modelo en cada rol y falla si el archivo
versionado ya no coincide con lo que el sistema envía (`--check`).

    .venv-ft/bin/python -m agents_d4.export_prompts          # escribe
    .venv-ft/bin/python -m agents_d4.export_prompts --check  # verifica
"""
import argparse
import hashlib
from pathlib import Path

from agents_d3.runtime import AgentConfig, prompt_bundle

OUT = Path(__file__).resolve().parent / "prompts"
FILES = {"memoria.txt": "memory", "selector.txt": "selector_paginas", "verificador.txt": "verifier"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    bundle = prompt_bundle(AgentConfig())
    bad = []
    for name, role in FILES.items():
        path = OUT / name
        text = bundle[role]
        if args.check:
            if path.read_text(encoding="utf-8") != text:
                bad.append(name)
        else:
            path.write_text(text, encoding="utf-8")
        print(name, hashlib.sha256(text.encode()).hexdigest()[:16])
    if bad:
        raise SystemExit(f"Prompts desactualizados: {bad}")


if __name__ == "__main__":
    main()
