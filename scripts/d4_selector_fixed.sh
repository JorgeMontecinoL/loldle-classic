#!/usr/bin/env bash
# Evaluaciones del Selector aislado que no dependen del adaptador nuevo.
# 1) Prueba de prompting en validación (pesos D3, prompt D3 vs prompt con ejemplo de amarillos).
# 2) Selector D3 y Selector base sobre los conjuntos de prueba (trazas del D3: sólo entradas con amarillo).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
URL="${MODEL_URL:-http://127.0.0.1:8083/v1}"
for set in d3_valid_trace valid_generado; do
  for prompt in d3 amarillo; do
    "$PY" -m agents_d4.eval_selector --set "$set" --weights d3 --prompt "$prompt" --only-yellow --base-url "$URL"
  done
done
for weights in d3 base; do
  "$PY" -m agents_d4.eval_selector --set test_generado --weights "$weights" --base-url "$URL"
  # Trazas reales del D3: sólo las entradas con amarillo (280 de 441), donde está el fallo.
  "$PY" -m agents_d4.eval_selector --set d3_test_trace --weights "$weights" --only-yellow --base-url "$URL"
done
