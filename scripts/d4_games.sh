#!/usr/bin/env bash
# Partidas completas de prueba: D3 reproducido y D4 en paralelo, cada uno contra su servidor
# (scripts/servers_d4.sh: 8084 D3, 8085 D4), así comparten las mismas condiciones de la máquina.
# Luego D1 directo, D2 y control, y el análisis.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
RUN_ID="${RUN_ID:-test_v1}"
scripts/servers_d4.sh
"$PY" -m agents_d4.evaluate --run-id "$RUN_ID" --split test --system d3 > "results/d4/logs/games_d3_$RUN_ID.log" 2>&1 &
p3=$!
"$PY" -m agents_d4.evaluate --run-id "$RUN_ID" --split test --system d4 > "results/d4/logs/games_d4_$RUN_ID.log" 2>&1 &
p4=$!
wait $p3 $p4
for variant in direct d2_lora algorithmic; do
  "$PY" -m agents_d3.evaluate --split test --weights paginas --variant "$variant" --base-url http://127.0.0.1:8083/v1 --out "results/d4/runs/$RUN_ID/legacy"
done
"$PY" -m agents_d4.analyze --run-id "$RUN_ID"
