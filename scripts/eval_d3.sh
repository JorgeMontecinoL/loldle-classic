#!/usr/bin/env bash
# Corridas secuenciales: no mezclar adaptadores en llamadas concurrentes.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
URL="${MODEL_URL:-http://127.0.0.1:8083/v1}"
PHASE="${1:-valid}"
if [[ "$PHASE" == valid ]]; then
  for weights in base lora; do
    "$PY" -m agents_d3.evaluate --split valid --weights "$weights" --base-url "$URL" --out results/d3/dev
  done
  "$PY" -m agents_d3.analyze --input results/d3/dev --out results/d3/dev
  "$PY" -m agents_d3.select
elif [[ "$PHASE" == test ]]; then
  weights=$("$PY" -c 'import json; print(json.load(open("results/d3/selection.json"))["selected_weights"])')
  "$PY" -c 'from agents_d3.select import source_hashes; import json; s=json.load(open("results/d3/selection.json")); assert s["source_hashes"] == source_hashes(), "El protocolo cambió después de selección; revalida antes de prueba"'
  for variant in full no_examples no_previous_state no_revision direct d2_lora d2_tool algorithmic; do
    "$PY" -m agents_d3.evaluate --split test --weights "$weights" --variant "$variant" --base-url "$URL" --out results/d3/raw
  done
  "$PY" -m agents_d3.analyze
else
  echo "Uso: scripts/eval_d3.sh valid|test" >&2
  exit 2
fi
