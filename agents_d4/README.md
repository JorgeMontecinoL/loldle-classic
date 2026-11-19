# Entregable 4 · Selector con adaptador propio

El D4 conserva el sistema del D3 (Memoria → Selector → Verificador, mismo controlador,
motor, prompts, presupuesto y temperatura) y cambia **sólo los pesos del Selector**: un
adaptador LoRA nuevo, `finetune/adapters/d4_selector/`, entrenado con páginas del roster
etiquetadas por las reglas del juego. Memoria y Verificador siguen con el adaptador común
del D3 (`d3_paginas_cot3`). El modelo base es el mismo:
`mlx-community/Ministral-3-3B-Instruct-2512-4bit`, revisión `a962dcb09eee4169c890e544c9eb938f1113fdee`.

**Adaptador publicado:** <https://huggingface.co/MatiasCaamano/loldle-d4-selector-lora>
(revisión `35115f23f12d960cbea09390d897d4f907a7ea3b`, `adapters.safetensors` SHA-256
`bcb99e98591255cf4a3d3d9645764cf9cd9e9a096fb4a3c1c03fadb5004c915a`, el mismo que produjo
estas cifras; verificación en `results/d4/hf_verify.json`).

## Resultados (30 secretos de prueba, `RUN_ID=test_v1`)

Todas las filas son corridas nuevas de este entregable (`results/d4/runs/test_v1/`); D1, D2,
D3 y el control reproducen exactamente las cifras históricas del D3 (`results/d3/raw/`).
Resolver = acertar en hasta 10 jugadas; los paros cuentan como no resueltos. Incompatibles:
intentos válidos posteriores a recibir pistas que incumplen alguna (incluye amarillos y
repetición), sobre los intentos indicados.

| Sistema | Resueltas | Incompatibles | Paros | Llamadas/partida | s modelo/partida* |
|---|---:|---:|---:|---:|---:|
| D1 · prompting directo (base) | 2/30 | 99,1 % (214/216) | 0 | 9,7 | 5,3 |
| D2 · LoRA sin agentes | 14/30 | 81,1 % (150/185) | 0 | 7,2 | 4,7 |
| D3 · tres agentes, LoRA común | 25/30 | 15,4 % (10/65) | 5 | 45,5 | 284,9 |
| **D4 · Selector con adaptador propio** | **29/30** | **12,7 % (9/71)** | **1** | **36,6** | **247,9** |
| Control · filtro por reglas (sin LLM) | 30/30 | 0 % (0/64) | 0 | 0 | 0 |

\*Con la GPU compartida con otro proceso; D3 y D4 corrieron en paralelo, en las mismas
condiciones, y sólo son comparables entre sí (el D3 histórico midió 98 s/partida).

- D3 → D4: 4 partidas ganadas (Morgana, Thresh, Ashe, Soraka), 0 perdidas; McNemar exacto
  p = 0,125 (n = 30): la mejora no es significativa con 30 secretos.
- Entre las 25 resueltas por ambos, el D4 usa 3,28 jugadas de media frente a 3,24; necesita
  más jugadas en LeBlanc, Elise, Kog'Maw y Ezreal, y menos en Xin Zhao, Dr. Mundo y Malzahar.
- Fallos y degradaciones del D4, con su traza: `results/d4/FALLOS_D4.md` (Samira se detiene
  por un fallo de Memoria; Elise se resuelve con dos intentos incompatibles).

**Selector aislado** (mismas entradas, mismo prompt, temperatura 0):

| Entradas | Pesos | Conserva compatibles | Precisión | Páginas exactas | Secreto descartado | Fuera de protocolo |
|---|---|---:|---:|---:|---:|---:|
| `test_generado` (156 páginas nuevas de los 30 secretos de prueba) | base | 191/341 | 191/1234 | 1 | 33/58 | 44 |
| | D3 | 301/341 | 301/315 | 111 | 29/58 | 0 |
| | **D4** | 276/341 | 276/306 | **122** | **6/58** | 0 |
| `d3_test_trace[amarillo]` (280 entradas reales de la prueba del D3) | base | 38/62 | 38/2269 | 6 | 15/40 | 44 |
| | D3 | 40/62 | 40/88 | 237 | 18/40 | 0 |
| | **D4** | **57/62** | 57/97 | 238 | **5/40** | 0 |

Con amarillo de un valor, el D4 conserva 28/30 filas compatibles en `test_generado` (D3: 15/30)
y 23/27 en las trazas (D3: 11/27). En `test_generado` el D4 deja fuera más compatibles en total
(65 frente a 40): 50 de ellos en dos páginas de estado vacío (turno 1), una regresión
explicada en `FALLOS_D4.md`. El D3 reejecutado da salidas idénticas byte a byte a las de sus
trazas (252/252 en prueba y 77/77 en validación a temperatura 0).

**Prompting antes del ajuste** (validación, pesos D3): con un ejemplo resuelto de amarillos el
Selector conserva 11/20 y 32/47 compatibles, frente a 12/20 y 34/47 sin él; descarta al secreto
en 8/12 y 12/33 páginas, frente a 7/12 y 9/33. Más prompting no corrigió el error.

## Punto de partida verificado

- Referencia D3: rama `entregable-3`, commit `10da2ec` (el código de agentes es idéntico a
  `01ebd58`, el commit del póster). `agents_d4.evaluate` se niega a correr si los prompts,
  `runtime.py`, `state.py` o `client.py` del D3 cambiaron (`results/d3/selection.json`).
- Prueba pequeña antes de entrenar: cuatro llamadas reales del Selector del D3 (Morgana,
  turno 4) reejecutadas con `d3_paginas_cot3` dieron salidas **idénticas byte a byte**.
- Las cifras 2/30, 14/30 y 25/30 del informe del D3 están en `results/d3/raw/` (históricas);
  el D4 las vuelve a correr con identificadores nuevos (`results/d4/runs/<run-id>/`).

## Por qué el Selector (evidencia)

`python -m agents_d4.diagnose_d3` → `results/d4/diagnostico_d3.json`. En la prueba del D3:

| Partida | Estado de Memoria admite al secreto | Páginas con el secreto | Veces que el Selector lo descartó | Campo escrito | Amarillo del estado |
|---|---|---:|---:|---|---|
| Morgana | sí, en todas | 12 | 10 | positions / release_year | `positions [["Middle"]]` |
| Ashe | sí, en todas | 13 | 11 | positions / release_year | `positions [["Bottom"]]` |
| Soraka | sí, en todas | 11 | 9 | regions | `regions [["Ionia"]]` |
| Thresh | sí, en todas | 10 | 8 | regions | `regions [["Demacia","Shadow Isles"]]` |
| Samira | sí | 2 | 0 | — | fallo de Memoria (60 errores de protocolo) |

En las 998 llamadas del Selector de esa prueba, cuando el estado tenía un amarillo de un
solo valor el Selector conservó **13 de 58** filas compatibles (22,4 %), frente a 98,7 %
en general. El fallo es leer «amarillo» como «exactamente esto» o «nunca esto», y también
afecta a filas que son subconjunto estricto de la cláusula (Thresh). Morgana muestra que
repetir la búsqueda con muestreo (7 pasadas a temperatura 0,7) no lo corrige.

## Datos

`finetune/make_data_d4.py` (semilla 4040; se regenera byte a byte):

- **Fuente**: historiales simulados con el motor del notebook (política del D2 con ruido 0–50 %).
- **Etiquetas**: reglas del juego sobre el estado público (`agents_d3.state.violations`).
  Ningún modelo de lenguaje genera salidas.
- **Formato**: exactamente la llamada del Selector del D3 (prompt de sistema, JSON con
  `memory`, `excluded`, `page`, `rows`, `years_allowed`) y la respuesta que continúa el
  prefijo `{"action":"listar","revision":`.
- **Partición por secreto** antes de generar (`finetune/data/split.json`, la del D2/D3):
  128 de entrenamiento, 15 de validación, 30 de prueba; intersección vacía.
- **Tamaño y cobertura, ronda 1** (`finetune/data/d4_selector/report.json`): 2.503 ejemplos de
  entrenamiento (918 con una fila compatible bajo amarillo difícil, 294 con amarillo,
  619 con candidatos comunes, 672 sin candidatos; 439 con amarillo de un valor, 570 con
  filas subconjunto de la cláusula; 946 estados distintos) y 95 de validación de pérdida.
- **Ronda 2** (`finetune/data/d4_selector_r2/report.json`): 1.340 ejemplos de los mismos 128
  secretos; 1.109 páginas con una fila compatible bajo amarillo difícil (694 en `positions`,
  421 en `regions`, 363 en `species`), 240 con filas que sólo rompen el amarillo, y 1 de cada 7
  estados con páginas comunes; misma validación de pérdida que la ronda 1.
- **Solapamiento de estados** (no de secretos): 18/95 de validación y 39/156 de
  `test_generado` repiten un estado canónico visto en entrenamiento (típicamente tras la
  primera jugada). Las 441 entradas reales de la prueba del D3 no se usan para entrenar.
- **Revisión**: re-verificación automática de las 61.885 filas con una segunda
  implementación de las reglas (0 discrepancias) y muestra estratificada de 40 ejemplos
  para revisión humana (`results/d4/revision_manual/`).

## Prompting antes de ajustar

`scripts/d4_prompt_test.sh` agrega al prompt del Selector un ejemplo resuelto de amarillos
(`agents_d4/prompts/selector_amarillo.txt`) y lo compara, con los mismos pesos D3, en las
páginas con amarillo de validación. Resultado en `results/d4/RESULTADOS_*.md`. Esa prueba
no entra en la comparación principal ni usa los secretos de prueba.

## Entrenamiento (dos rondas)

LoRA sobre los pesos de 4 bits (QLoRA en la práctica), rango 16, escala 20, dropout 0,05,
12 capas, `mask_prompt`, lote 1 con acumulación 4, `mlx-lm` 0.31.3.

| Ronda | Config | Datos | Inicio | lr | Iteraciones |
|---|---|---|---|---|---|
| 1 | `finetune/lora_config_d4_selector_r1.yaml` | `d4_selector` (2.503) | `d3_paginas_cot3` | 2e-5 cosine | detenida en 1050 de 2503 |
| 2 | `finetune/lora_config_d4_selector_r2.yaml` | `d4_selector_r2` (1.340) | ronda 1, paso 1000 | 1e-5 cosine | 1340 (una pasada) |

La ronda 2 (`make_data_d4.py --ronda 2`, semilla 4060) concentra páginas con una fila
compatible bajo un amarillo difícil en `positions` y `regions`, donde el Selector del D3
falla; en `species [["Human"]]` ya acertaba. Por qué se cortó la ronda 1 y qué se usó para
decidirlo: `results/d4/BITACORA.md` (incluye una desviación: se miraron cinco entradas de
la traza de prueba durante la ronda 1). Logs: `finetune/logs/d4_selector_r{1,2}.log`;
curva conjunta: `results/d4/loss_d4_selector.png`. El adaptador publicado se elige sólo con
validación entre ronda 1 paso 1000, ronda 2 paso 670 y ronda 2 final
(`agents_d4/select_checkpoint.py`, `results/d4/checkpoint_selection.json`) y se copia a
`finetune/adapters/d4_selector/`.

## Reproducir

Requisitos: macOS con Apple Silicon y `uv`, desde la raíz del repositorio.

```bash
uv venv .venv-ft --python 3.12
uv pip install --python .venv-ft/bin/python -r agents_d3/requirements.txt
.venv-ft/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/Ministral-3-3B-Instruct-2512-4bit', revision='a962dcb09eee4169c890e544c9eb938f1113fdee')"
```

Servidores del modelo, uno por adaptador (8083 base, 8084 D3, 8085 D4). `mlx_lm server`
recarga el modelo cuando cambia el adaptador de la petición; con un servidor por adaptador el D4
no paga esa recarga y los tiempos de D3 y D4 son comparables:

```bash
scripts/servers_d4.sh
```

Datos, entrenamiento y evaluación:

```bash
.venv-ft/bin/python finetune/make_data_d4.py
.venv-ft/bin/python finetune/make_data_d4.py --ronda 2 --states 8
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config_d4_selector_r1.yaml   # cortar tras guardar el paso 1000
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config_d4_selector_r2.yaml
scripts/d4_selector_fixed.sh          # prompt en validación; Selector base y D3 en prueba
RUN_ID=test_v1 scripts/d4_after_training.sh   # candidatos, elección, Selector D4 y scripts/d4_games.sh
RUN_ID=test_v1 scripts/d4_games.sh            # sólo las partidas: D3 y D4 alternados, D1, D2, control
```

Partidas sueltas:

```bash
.venv-ft/bin/python -m agents_d4.evaluate --run-id mi_corrida --split test --system d4 --targets Morgana,Ashe
```

Con el adaptador publicado en Hugging Face (ver `results/d4/hf_verify.json`):

```bash
.venv-ft/bin/python -m agents_d4.hf_package verify --repo MatiasCaamano/loldle-d4-selector-lora
.venv-ft/bin/python -m agents_d4.eval_selector --set d3_test_trace --adapter hf_release/descarga --label hf
.venv-ft/bin/python -m agents_d4.evaluate --run-id hf_check --split test --system d4 --adapter hf_release/descarga
```

## Demo

```bash
scripts/demo_d4.sh        # http://127.0.0.1:8767
```

Tablero estilo LoLdle Classic (filas por intento, color por atributo, flechas del año),
dos sistemas sobre el mismo secreto (D4, D3, D3 con Selector base, D2, D1, control),
panel plegable con el agente activo y cada mensaje, y la sección «Selector base frente a
ajustado» que ejecuta una misma entrada real del Selector con los tres pesos. Modos: «En
vivo» (llama al sistema real), «Reproducción de traza» (anima un archivo guardado) y «No
disponible» (falta adaptador o servidor). Cada partida en vivo se guarda en
`results/d4/app_runs/`.

## Archivos

- `agents_d4/runtime.py`: cliente que asigna el adaptador por rol; sistemas `d3`, `d4`, `d4_selector_base`.
- `agents_d4/prompts/{memoria,selector,verificador}.txt`: prompt de sistema exacto de cada
  agente (`python -m agents_d4.export_prompts --check` verifica que coinciden con lo que se envía).
- `agents_d4/selector_metrics.py`, `eval_selector.py`: métricas del Selector aislado.
- `agents_d4/evaluate.py`, `analyze.py`: partidas completas y tablas.
- `results/d4/selector_sets/`: entradas del Selector (trazas reales del D3 y generadas por secreto).
- `results/d4/runs/<run-id>/`: trazas completas de cada partida (incluidos los fallos).
