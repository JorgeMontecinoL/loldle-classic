#!/usr/bin/env bash
# Un servidor MLX por adaptador: 8083 base, 8084 d3_paginas_cot3 (D3), 8085 d4_selector (D4).
# mlx_lm server recarga el modelo cada vez que cambia el adaptador pedido; con un servidor por
# adaptador el D4 (que alterna adaptadores entre roles) no paga esa recarga y los tiempos de D3 y
# D4 son comparables. El cliente (agents_d4.runtime) envía igual el adaptador en cada petición:
# mlx_lm ignora --adapter-path cuando la petición usa "default_model"; así cada servidor recibe siempre
# el mismo adaptador y no vuelve a cargar el modelo.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
LOGS=results/d4/server_logs
mkdir -p "$LOGS"
M=mlx-community/Ministral-3-3B-Instruct-2512-4bit
start(){ # puerto, [adaptador]
  if curl -fsS --max-time 2 "http://127.0.0.1:$1/v1/models" >/dev/null 2>&1; then echo "puerto $1 ya activo"; return; fi
  if [[ -n "${2:-}" ]]; then
    nohup "$PY" -m mlx_lm server --model "$M" --adapter-path "$2" --host 127.0.0.1 --port "$1" > "$LOGS/mlx_$1.log" 2>&1 &
  else
    nohup "$PY" -m mlx_lm server --model "$M" --host 127.0.0.1 --port "$1" > "$LOGS/mlx_$1.log" 2>&1 &
  fi
  for _ in {1..120}; do curl -fsS --max-time 2 "http://127.0.0.1:$1/v1/models" >/dev/null 2>&1 && break; sleep 1; done
  echo "puerto $1 listo ${2:-(base)}"
}
start 8083
start 8084 finetune/adapters/d3_paginas_cot3
start 8085 finetune/adapters/d4_selector
