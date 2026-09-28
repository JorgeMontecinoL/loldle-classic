#!/usr/bin/env bash
# Levanta todo lo que muestra el video del Entregable 2:
#   - mlx_lm.server en :8081 -> baseline (pesos base, sin adaptador)
#   - mlx_lm.server en :8082 -> solución (mismos pesos; la app pide el adaptador LoRA)
#   - la app del pipeline en vivo en http://127.0.0.1:8765
# Ctrl+C detiene los tres procesos.
#
# Uso, desde la raíz del repo:
#   scripts/demo.sh              # solución = fine-tuning (el juego recibe la jugada del modelo)
#   scripts/demo.sh state-tool   # variante: una herramienta ejecuta la línea «Sé:» del modelo

set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-last-line}"
MODEL="mlx-community/Ministral-3-3B-Instruct-2512-4bit"
ADAPTER="finetune/adapters/final"
PY_FT=".venv-ft/bin/python"
LOGS="results/d2/server_logs"

if [[ ! -x "$PY_FT" ]]; then
  echo "Falta el entorno .venv-ft. Créalo con:"
  echo "  uv venv .venv-ft --python 3.12 && uv pip install --python .venv-ft/bin/python mlx-lm"
  exit 1
fi
if [[ ! -f "$ADAPTER/adapters.safetensors" ]]; then
  echo "Falta el adaptador en $ADAPTER. Entrénalo con:"
  echo "  $PY_FT -m mlx_lm lora --config finetune/lora_config.yaml"
  exit 1
fi

mkdir -p "$LOGS"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT INT TERM

for port in 8081 8082; do
  "$PY_FT" -m mlx_lm server --model "$MODEL" --host 127.0.0.1 --port "$port" \
    > "$LOGS/mlx_$port.log" 2>&1 &
  pids+=($!)
done

echo -n "Esperando a los servidores de modelo"
for port in 8081 8082; do
  until curl -s -m 2 -o /dev/null "http://127.0.0.1:$port/v1/models"; do
    echo -n "."
    sleep 1
  done
done
echo " listos."

python3 pipeline_app/server.py --adapter "$ADAPTER" --solution-mode "$MODE" &
pids+=($!)
sleep 1
[[ -z "${NO_OPEN:-}" ]] && open "http://127.0.0.1:8765" 2>/dev/null || true
wait
