#!/usr/bin/env bash
# Prueba de prompting (sólo validación): ¿un ejemplo más claro de amarillos corrige al Selector del D3?
# Mismos pesos (d3_paginas_cot3), mismas entradas; cambia sólo el texto del prompt.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
URL="${MODEL_URL:-http://127.0.0.1:8083/v1}"
for set in d3_valid_trace valid_generado; do
  for prompt in d3 amarillo; do
    "$PY" -m agents_d4.eval_selector --set "$set" --weights d3 --prompt "$prompt" --only-yellow --base-url "$URL"
  done
done
