#!/usr/bin/env bash
# Reproduce los números del Entregable 2 sobre los 30 objetivos de prueba.
# Requiere los servidores de modelo de scripts/demo.sh (o equivalentes) arriba:
#   :8081 baseline · :8082 solución (la petición incluye el adaptador).
#
# Uso, desde la raíz del repo:
#   scripts/eval_d2.sh            # baseline + solución (ambos modos) + análisis
#   scripts/eval_d2.sh --no-base  # sólo la solución

set -euo pipefail
cd "$(dirname "$0")/.."
ADAPTER="finetune/adapters/final"
COMMON=(--api-model default_model --params 3.0 --out-dir results/d2/raw --force)

if [[ "${1:-}" != "--no-base" ]]; then
  python3 run_benchmark.py --label baseline --base-url http://127.0.0.1:8081/v1 "${COMMON[@]}"
fi
python3 run_benchmark.py --label lora --base-url http://127.0.0.1:8082/v1 \
  --adapter "$ADAPTER" --submit last-line "${COMMON[@]}"
python3 run_benchmark.py --label lora_tool --base-url http://127.0.0.1:8082/v1 \
  --adapter "$ADAPTER" --submit state-tool "${COMMON[@]}"
python3 analyze_d2.py
