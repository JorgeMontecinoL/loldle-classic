#!/usr/bin/env bash
# Todo lo que sigue al entrenamiento del adaptador del Selector, en orden y sin concurrencia.
#  1. Candidatos: Selector aislado en validación (sólo páginas con amarillo).
#  2. Elección (regla fija, sólo validación) → finetune/adapters/d4_selector/.
#  3. Selector D4 sobre los conjuntos de prueba (mismas entradas que base y D3).
#  4. Partidas completas de prueba: D3 reproducido, D4, D1 directo, D2 y control (RUN_ID).
#  5. Análisis.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY_D3:-.venv-ft/bin/python}"
URL="${MODEL_URL:-http://127.0.0.1:8083/v1}"
RUN_ID="${RUN_ID:-test_v1}"
C=finetune/adapters/d4_selector_ckpts
stage(){ # nombre, archivo de pesos, carpeta con adapter_config.json
  mkdir -p "$C/$1"; cp "$3/adapter_config.json" "$C/$1/"; cp "$2" "$C/$1/adapters.safetensors"; }
stage r1_1000 finetune/adapters/d4_selector_r1/0001000_adapters.safetensors finetune/adapters/d4_selector_r1
stage r2_0670 finetune/adapters/d4_selector_r2/0000670_adapters.safetensors finetune/adapters/d4_selector_r2
stage r2_final finetune/adapters/d4_selector_r2/adapters.safetensors finetune/adapters/d4_selector_r2
cands=()
for name in r1_1000 r2_0670 r2_final; do
  for set in d3_valid_trace valid_generado; do
    "$PY" -m agents_d4.eval_selector --set "$set" --adapter "$C/$name" --label "ckpt_$name" --only-yellow --base-url "$URL"
  done
  cands+=("$name=$C/$name")
done
"$PY" -m agents_d4.select_checkpoint --candidates "${cands[@]}"
"$PY" -m agents_d4.eval_selector --set test_generado --weights d4 --base-url "$URL"
"$PY" -m agents_d4.eval_selector --set d3_test_trace --weights d4 --only-yellow --base-url "$URL"
scripts/d4_games.sh   # partidas D3/D4 alternadas, D1, D2, control y análisis
