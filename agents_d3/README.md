# Entregable 3 · coordinación de tres agentes

Sistema ejecutable de **Memoria → Selector → Verificador** sobre el mismo
Ministral-3-3B-Instruct-2512 con **los mismos pesos en los tres roles**: un
adaptador LoRA común entrenado para este entregable a partir del adaptador del D2.
Memoria lleva el registro de lo revelado (verdes, grises, amarillos, año, jugados).
El Selector **busca en el roster de a 25 filas**, escribe un veredicto por fila y
lista las que cumplen el estado. El Verificador revisa cada candidato contra las
pistas originales antes de gastar un intento y lo devuelve con un motivo.
**Ninguna herramienta deduce**: el código pagina el roster y muestra filas, pero no
filtra ni compara.

Grafo, contrato de cada agente, frontera de información, técnicas y entrenamiento:
[`docs/d3/ARQUITECTURA.md`](../docs/d3/ARQUITECTURA.md).

## Ejecutar la demo

Desde la raíz del repositorio, en macOS con Apple Silicon:

```bash
# Si no existe el entorno del D2:
uv venv .venv-ft --python 3.12
uv pip install --python .venv-ft/bin/python -r agents_d3/requirements.txt

scripts/demo_d3.sh
# http://127.0.0.1:8766
```

Se inicia un servidor MLX en 8083 y la app en 8766, con los pesos guardados en
`results/d3/selection.json` (`paginas`, adaptador `finetune/adapters/d3_paginas_cot3/`).
Se reutiliza `mlx-community/Ministral-3-3B-Instruct-2512-4bit` del caché local;
una instalación nueva descarga unos 2,78 GB. Ctrl+C detiene sólo los procesos
iniciados por el script. Si el modelo ya está servido: `USE_EXISTING_MODEL=1
scripts/demo_d3.sh`. `MODEL_PORT`, `APP_PORT`, `NO_OPEN=1` y `D3_WEIGHTS` cambian
puertos, navegador o pesos (`paginas` usa la búsqueda por páginas; los demás,
la del v3).

La app juega primero con los agentes y después con la referencia elegida
(prompting directo o D2) **sobre el mismo objetivo**, de forma secuencial. Muestra
el agente activo, cada página revisada, cada transferencia con su motivo, el estado
escrito por Memoria, las respuestas completas y los tableros. Seleccionar un evento
muestra su entrada y salida exactas. Las partidas quedan en
`results/d3/app_runs/*.json.gz`. Los botones «Ver fallo» reproducen **trazas
guardadas**, etiquetadas como tales; no llaman al modelo.

El video de la entrega ([`docs/d3/videoD3.mp4`](../docs/d3/videoD3.mp4)) y cómo
repetirlo se describen en el [README raíz](../README.md#video-del-entregable-3).

## Reproducir el entrenamiento

Cada ronda parte del adaptador de la anterior (unas 1-2 h cada una en un M5 Pro,
pico ~20 GB). Desde el adaptador final del D2:

```bash
PY=.venv-ft/bin/python
$PY finetune/make_data_d3.py
$PY -m mlx_lm lora --config finetune/lora_config_d3.yaml
$PY finetune/make_data_d3.py --paginas
$PY -m mlx_lm lora --config finetune/lora_config_d3_paginas.yaml
$PY finetune/make_data_d3.py --paginas --out d3_paginas_cot
$PY -m mlx_lm lora --config finetune/lora_config_d3_paginas_cot.yaml
$PY finetune/make_data_d3.py --paginas --out d3_paginas_cot2
$PY -m mlx_lm lora --config finetune/lora_config_d3_paginas_cot2.yaml
$PY finetune/make_data_d3.py --paginas --repaso 300 --semilla 10 --out d3_paginas_cot3
$PY -m mlx_lm lora --config finetune/lora_config_d3_paginas_cot3.yaml
```

Los datos de las rondas de páginas se generan con el prompt vigente del Selector,
así que regenerar una ronda anterior con el prompt actual no reproduce sus datos
exactos; el adaptador seleccionado (`d3_paginas_cot3`) está versionado. La
partición es la del D2: 128 objetivos de entrenamiento; los 15 de validación sólo
miden la pérdida; los 30 de prueba no aparecen. Las etiquetas las calcula el motor
del notebook a partir de la evidencia pública.

## Evaluación reproducible

```bash
.venv-ft/bin/python -m mlx_lm server \
  --model mlx-community/Ministral-3-3B-Instruct-2512-4bit \
  --host 127.0.0.1 --port 8083

# En otra terminal:
scripts/eval_d3.sh valid    # 15 objetivos con cada peso común + selección
scripts/eval_d3.sh test     # 30 objetivos: sistema, ablaciones y comparaciones
```

1. **Validación:** las mismas 15 entradas con cada configuración de pesos. Se
   elige por resolución; desempates por menos paros, menor violación estricta y
   menos llamadas. `results/d3/selection.json` congela pesos, configuración y
   hashes de prompts y código; la prueba se niega a correr si cambiaron.
2. **Prueba:** los 30 objetivos reservados del D1/D2, con el mismo criterio de
   corrección. Sistema completo, tres ablaciones y cuatro comparaciones.
3. **Análisis:** `results/d3/summary.json`, `summary.csv` y `ANALISIS_D3.md`,
   con tamaño, paros, costes, fallos y McNemar pareado exploratorio.

Las corridas guardan al terminar cada partida y se reanudan omitiendo las ya
registradas; un cambio de configuración o de prompts impide reanudar.

## Resultados (prueba, 30 objetivos)

| Variante | Resueltas | Violación estricta | Paros por presupuesto | Llamadas/partida |
|---|---:|---:|---:|---:|
| Prompting directo (D1) | 2 | 99,1% | 0 | 9,7 |
| Solución D2 (adaptador, sin agentes) | 14 | 81,1% | 0 | 7,2 |
| **Sistema de agentes v4** | **25** | **15,4%** | 5 | 46,5 |
| sin ejemplos | 18 | 39,0% | 12 | 66,9 |
| sin estado previo | 29 | 21,3% | 1 | 44,4 |
| sin revisión | 14 | 26,7% | 16 | 40,1 |
| Control D2: herramienta que filtra el roster | 30 | 60,6% | 0 | 4,6 |
| Control sin LLM: filtro con toda la evidencia | 30 | 0,0% | 0 | 0 |

Lectura:

- El sistema **supera a la solución del D2**: 25 frente a 14, con 13 victorias y 2
  derrotas pareadas (p = 0,007), y viola lo revelado en 15% de sus jugadas frente a
  81%. Frente al prompting directo: 24 victorias y 1 derrota.
- **Crítica con revisión** es la técnica que más aporta: sin ella el sistema baja a
  14 (12 derrotas y 1 victoria, p = 0,003). **Los ejemplos** aportan 7 partidas.
- **El estado previo reinyectado no ayuda**: sin él, Memoria reconstruye el estado
  desde el historial completo en cada turno y el sistema resuelve 29. El resultado
  aparece en prueba y no se usó para cambiar el sistema; es la primera mejora a
  validar.
- Los 5 fallos terminan por presupuesto: la búsqueda no encuentra la única fila que
  cumple al final de la partida. El sistema es más caro que el D2: 46,5 llamadas y
  98 s de modelo por partida, frente a 7,2 y 5,7 s.
- Los controles con herramienta resuelven 30/30: una búsqueda hecha por código
  resuelve el juego. Se excluyeron del sistema por decisión del equipo, porque
  hacen la deducción que el entregable pide al modelo.

## Métricas y límites

- **Resolución:** partidas resueltas / todas las partidas, incluidos paros.
- **Violación histórica:** checker del D1/D2; ignora amarillos.
- **Violación estricta:** incompatibilidad con todo el feedback público,
  incluidos amarillos y repetición, sobre jugadas válidas tras el feedback.
- **Coste:** directo y D2 permiten 64 tokens por turno; los agentes, hasta 768 por
  llamada (400 el Selector), 60 llamadas por turno y 160 por partida.
- McNemar compara resolución sobre objetivos pareados; las comparaciones múltiples
  son exploratorias. 30 objetivos no permiten inferir robustez general.
- Las sondas sobre objetivos de entrenamiento sobreestiman el sistema: esos
  campeones fueron secretos en los datos del adaptador. Sólo validación y prueba
  son evidencia.
- Los reintentos muestrean con semilla fija y quedan registrados en cada llamada.
  Aun así, versión, caché y aritmética del servidor pueden cambiar salidas; una
  traza guardada es la evidencia exacta de esa corrida.

## Archivos

- `agents_d3/prompts/`: un archivo versionado por agente (`memory.txt`,
  `selector_paginas.txt`, `verifier.txt`), sus ejemplos y los textos de ablación.
  `selector.txt` y `selector_turn.txt` son el Selector del v3 (prompt del D2).
- `agents_d3/runtime.py`: controlador dirigido por las acciones de los modelos
  (`_decide_paginas` para v4; `decide` conserva el v3).
- `agents_d3/state.py`: formato del estado, `validar_estado`, `ver_atributos` y las
  funciones deterministas que sólo usan métricas y controles.
- `finetune/make_data_d3.py`, `finetune/lora_config_d3*.yaml`: datos y
  entrenamiento del adaptador común.
- `results/d3/dev/`: validación. `results/d3/raw/`: prueba final.
- `results/d3/v1/`, `v2_herramientas/`, `v3/`: protocolos anteriores, conservados
  como historia.
- `results/d3/probes*`: exploraciones del protocolo v1, no son resultados.
