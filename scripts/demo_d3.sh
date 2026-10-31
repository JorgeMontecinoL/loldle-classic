#!/usr/bin/env bash
# Inicia la demo y un único servidor, salvo USE_EXISTING_MODEL=1.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
MODEL_PORT="${MODEL_PORT:-8083}"
APP_PORT="${APP_PORT:-8766}"
LOGS="results/d3/server_logs"
mkdir -p "$LOGS"
pids=()
cleanup(){ for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM
if [[ "${USE_EXISTING_MODEL:-0}" != 1 ]]; then
  "$PY" -m mlx_lm server --model mlx-community/Ministral-3-3B-Instruct-2512-4bit --host 127.0.0.1 --port "$MODEL_PORT" > "$LOGS/mlx_$MODEL_PORT.log" 2>&1 &
  pids+=($!)
  ready=0
  for _ in {1..120}; do
    if curl -fsS --max-time 2 "http://127.0.0.1:$MODEL_PORT/v1/models" > /dev/null 2>&1; then ready=1; break; fi
    kill -0 "${pids[0]}" 2>/dev/null || { echo "MLX no inició. Revisa $LOGS/mlx_$MODEL_PORT.log"; exit 1; }
    sleep 1
  done
  [[ "$ready" == 1 ]] || { echo "Tiempo de arranque agotado"; exit 1; }
fi
weights="${D3_WEIGHTS:-}"
if [[ -z "$weights" ]]; then
  weights=$("$PY" -c 'import json; from pathlib import Path; p=Path("results/d3/selection.json"); print(json.loads(p.read_text())["selected_weights"] if p.exists() else "base")')
fi
"$PY" -m agents_d3.app --weights "$weights" --port "$APP_PORT" --base-url "http://127.0.0.1:$MODEL_PORT/v1" &
pids+=($!)
[[ "${NO_OPEN:-0}" == 1 ]] || open "http://127.0.0.1:$APP_PORT"
wait
