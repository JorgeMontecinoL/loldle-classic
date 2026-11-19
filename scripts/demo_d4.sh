#!/usr/bin/env bash
# Demo del Entregable 4: servidores MLX (8083 base, 8084 D3, 8085 D4) + interfaz (http://127.0.0.1:8767).
# USE_EXISTING_MODEL=1 reutiliza servidores ya iniciados. NO_OPEN=1 no abre el navegador.
# Para detener los servidores: pkill -f 'mlx_lm server'
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
MODEL_PORT="${MODEL_PORT:-8083}"
APP_PORT="${APP_PORT:-8767}"
LOGS="results/d4/server_logs"
mkdir -p "$LOGS"
pids=()
cleanup(){ for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM
# Un servidor por adaptador (8083 base, 8084 D3, 8085 D4); quedan arriba al cerrar la demo.
[[ "${USE_EXISTING_MODEL:-0}" == 1 ]] || scripts/servers_d4.sh
"$PY" -m agents_d4.app --port "$APP_PORT" --base-url "http://127.0.0.1:$MODEL_PORT/v1" &
pids+=($!)
[[ "${NO_OPEN:-0}" == 1 ]] || open "http://127.0.0.1:$APP_PORT"
wait
