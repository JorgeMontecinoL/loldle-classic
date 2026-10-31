# Entregable 3 · coordinación de tres agentes

Sistema ejecutable de **Memoria → Selector → Verificador** sobre el mismo
Ministral-3-3B-Instruct-2512 con **los mismos pesos en los tres roles**: un
adaptador LoRA común entrenado para este entregable a partir del adaptador del D2.
Memoria lleva el registro de lo revelado (verdes, grises, amarillos, año, jugados).
El Selector **busca en el roster de a 25 filas**, escribe un veredicto por fila y
lista las que cumplen el estado. El Verificador revisa cada candidato contra las
pistas originales antes de gastar un intento; si lo rechaza con `revisar_selector`,
el controlador pasa el siguiente de la lista (si se agota, el Selector repite la
búsqueda y sólo recibe el nombre excluido; el motivo queda en la traza), y con `revisar_memoria` el motivo sí llega a
Memoria. **Ninguna herramienta deduce**: el código pagina el roster, muestra filas y
calcula los años que permite el estado escrito por Memoria (reformatea ese estado,
no consulta la evidencia), pero no filtra ni compara filas.

Grafo, contrato de cada agente, frontera de información, técnicas y entrenamiento:
[`docs/d3/ARQUITECTURA.md`](../docs/d3/ARQUITECTURA.md).

## Ejecutar la demo

Desde la raíz del repositorio, en macOS con Apple Silicon:

```bash
# Entorno (también sirve sobre el .venv-ft del D2; fija mlx-lm 0.31.3):
uv venv .venv-ft --python 3.12        # omitir si ya existe
uv pip install --python .venv-ft/bin/python -r agents_d3/requirements.txt
# Una sola vez, los pesos base (2,78 GB):
.venv-ft/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/Ministral-3-3B-Instruct-2512-4bit')"

scripts/demo_d3.sh
# http://127.0.0.1:8766
```

Se inicia un servidor MLX en 8083 y la app en 8766, con los pesos guardados en
`results/d3/selection.json` (`paginas`, adaptador `finetune/adapters/d3_paginas_cot3/`).
Se reutiliza `mlx-community/Ministral-3-3B-Instruct-2512-4bit` del caché local.
Como `scripts/demo_d3.sh` espera 120 s a que el servidor responda, en una
instalación nueva conviene bajar antes los pesos con el comando de arriba. Ctrl+C detiene sólo los procesos
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

## Continuidad con el D1 y el D2, y desviaciones declaradas

Misma tarea (LoLdle Classic, 173 campeones, hasta diez jugadas), mismo roster, motor
y checker del notebook, mismos 30 objetivos de prueba y mismo criterio: una jugada es
correcta si es un nombre del roster que no contradice lo revelado ni repite, y la
partida se resuelve al acertar el secreto en diez jugadas. El fallo atacado sigue
siendo el del D1: el modelo no mantiene las restricciones reveladas. Desviaciones:

1. **Adaptador nuevo:** `d3_paginas_cot3`, cinco rondas encadenadas desde el
   adaptador del D2.
2. **Más tokens y llamadas:** hasta 768 tokens por llamada (400 el Selector) frente
   a 64, con 60 llamadas por turno y 160 por partida (46,5 llamadas y 98,0 s de
   modelo por partida frente a 7,2 y 5,7 s del D2).
3. **Métrica estricta:** además de la violación histórica del D1/D2 (ignora
   amarillos) se reporta la estricta, que suma amarillos y repeticiones. Los paros
   cuentan como no resueltos.

## Evaluación reproducible

```bash
.venv-ft/bin/python -m mlx_lm server \
  --model mlx-community/Ministral-3-3B-Instruct-2512-4bit \
  --host 127.0.0.1 --port 8083

# En otra terminal:
scripts/eval_d3.sh test     # 30 objetivos: sistema, ablaciones y comparaciones

# Validación del adaptador seleccionado (reconoce las 15 partidas guardadas):
.venv-ft/bin/python -m agents_d3.evaluate --split valid --weights paginas \
  --base-url http://127.0.0.1:8083/v1 --out results/d3/dev
```

1. **Validación:** las mismas 15 entradas con cada configuración de pesos. Se
   elige por resolución; desempates por menos paros, menor violación estricta y
   menos llamadas. `results/d3/selection.json` congela pesos, configuración y
   hashes de prompts y código; la prueba se niega a correr si cambiaron.
   `scripts/eval_d3.sh valid` documenta cómo se eligieron los pesos, pero no se
   repite con el código actual: `base`, `lora`, `multirol` y `multirol2` se jugaron
   con el protocolo previo (30 llamadas por turno, Selector del v3) y `multirol2`
   exige entrenar `d3_multirol_r2` (`make_data_d3.py --round2` y
   `lora_config_d3_r2.yaml`, desde `d3_multirol`), que no está versionado. Sus
   resultados están en `results/d3/dev/`.
2. **Prueba:** los 30 objetivos de prueba del D1/D2, con el mismo criterio de
   corrección. Sistema completo, tres ablaciones y cuatro comparaciones.
3. **Análisis:** `results/d3/summary.json`, `summary.csv` y `ANALISIS_D3.md`,
   con tamaño, paros, costes, fallos y McNemar pareado exploratorio.

Las corridas guardan al terminar cada partida y se reanudan omitiendo las ya
registradas; un cambio de configuración o de prompts impide reanudar. Como
`results/d3/raw/` ya está completo, `eval_d3.sh test` no vuelve a jugar: repetirlo
desde cero exige mover antes esas trazas (`mv results/d3/raw results/d3/raw_original`).
Una corrida nueva puede diferir en detalles numéricos; la evidencia exacta es la
traza guardada.

## Resultados (prueba, 30 objetivos)

| Variante | Resueltas | Violación estricta | Paros | Llamadas/partida | p frente al sistema |
|---|---:|---:|---:|---:|---:|
| Referencia directa, sin ajuste LoRA | 2 | 99,1% | 0 | 9,7 | < 10⁻⁵ |
| Solución D2 (LoRA, sin agentes) | 14 | 81,1% | 0 | 7,2 | 0,007 |
| **Sistema de tres agentes (v4)** | **25** | **15,4%** | 5 | 46,5 | — |
| sin ejemplos en los prompts | 18 | 39,0% | 12 | 66,9 | 0,12 |
| sin resumen previo de Memoria | 29 | 21,3% | 1 | 44,4 | 0,22 |
| sin devolución para corregir | 14 | 26,7% | 16 | 40,1 | 0,003 |
| D2 con consulta (el código filtra el roster) | 30 | 60,6% | 0 | 4,6 | |
| Sin modelo (el código filtra con toda la evidencia) | 30 | 0,0% | 0 | 0 | |

«Referencia directa» es el modelo base MLX 4 bits con el prompt del D1, corrido de
nuevo bajo el protocolo del D3 (no el GGUF del D1, que resolvió 6/30; en el D2 esta
configuración resolvió 1/30, la diferencia es Samira). «Violación estricta» es la
tasa de «intentos incompatibles» del póster. «Paros»: partidas detenidas por
protocolo o presupuesto; v4 es el protocolo final (ver la historia en
[`docs/d3/ARQUITECTURA.md`](../docs/d3/ARQUITECTURA.md#historia-del-protocolo)).

Lectura:

- El sistema **supera a la solución del D2**: 25 frente a 14, con 13 victorias y 2
  derrotas pareadas (p = 0,007), y viola lo revelado en 15% de sus jugadas frente a
  81%. Frente a la referencia directa: 24 victorias y 1 derrota (p < 10⁻⁵). La mejora
  corresponde a toda la configuración: también cambian el adaptador y el cómputo.
  Las ablaciones no miden el aporte de cada agente; paginación, prellenado JSON y
  `ver_atributos` no tienen ablación propia.
- **Revisión con devolución del candidato** (14/30, 12 derrotas y 1 victoria,
  p = 0,003): el Verificador sigue presente, pero pedir revisión detiene la partida
  (13 paros `revision_disabled`, más 3 por presupuesto), así que la prueba mide a la
  vez revisar y poder continuar y sobreestima el aporte. El motivo de
  `revisar_selector` sólo se registra; únicamente `revisar_memoria`, nunca usado en
  prueba, lo entrega.
- **Ejemplos en contexto** (18/30, p = 0,12, no significativo): retirarlos de los
  tres roles reduce la resolución y más que duplica los incompatibles; sugiere
  utilidad sin identificar qué agente se beneficia, y el adaptador se entrenó con
  ejemplos en el prompt.
- **Resumen previo de Memoria** (29/30, p = 0,22): sin él, Memoria reconstruye el
  estado con todas las pistas y resuelve más, con más incompatibles (21,3% frente a
  15,4%). Cuestiona la ventaja del resumen incremental sin probar que reconstruir sea
  superior; el resultado apareció en prueba y no se usó para cambiar el sistema.
- **Los 5 paros terminan al agotar las 60 llamadas de un turno**, por causas
  distintas. En cuatro (Morgana, Thresh, Ashe, Soraka) Memoria entrega un estado
  equivalente al público, pero el Selector descarta al secreto en todas las pasadas:
  a Morgana y a Ashe las marca incompatibles por posición ante un amarillo de un solo
  valor, un caso que su ejemplo no cubre. El Verificador sólo revisa lo que recibe.
  En Samira, el caso del video, el fallo es de Memoria: encadena 60 respuestas fuera
  de protocolo en el tercer turno. El sistema es más caro que el D2: 46,5 llamadas y
  98 s de modelo por partida, frente a 7,2 y 5,7 s.
- Los controles con código resuelven 30/30: la tarea es resoluble y lo que se mide es
  cuánto de la deducción logra hacer el modelo. Se excluyeron del sistema por
  decisión del equipo, porque hacen la deducción que el entregable pide al modelo.

## Trazas

Cada partida de los cuatro `results/d3/raw/test_paginas_*.json.gz` (30 por
configuración) guarda en `records[i].agent_trace` los eventos en orden, entre otros
`model_call` (los mensajes exactos que recibió el agente), `model_output`,
`decision`, `handoff`, `tool_result`, `protocol_error` y `stop`; las de
`test_base_direct`, `test_lora_d2_lora` y `test_lora_d2_tool` guardan sólo
`records[i].trace` (respuesta cruda y feedback por jugada). Archivos:
`test_paginas_full` (sistema), `test_paginas_no_examples|no_previous_state|no_revision`
(ablaciones), `test_base_direct` (referencia directa), `test_lora_d2_lora` (solución
D2), `test_lora_d2_tool` y `test_none_algorithmic` (controles). Casos del video:
Mordekaiser y Samira en `test_paginas_full`; el D2 sobre Mordekaiser en
`test_lora_d2_lora`. Las partidas en vivo de la app se guardan en
`results/d3/app_runs/` (se crea al jugar; no se versiona).

Decisiones del sistema completo en prueba: el Verificador aprobó 95 veces, devolvió
18 (todas `revisar_selector`) y consultó `ver_atributos` 113; el Selector hizo 998
llamadas `listar` y el controlador volvió 11 veces a Memoria tras cuatro pasadas
vacías; Memoria emitió 170 `entregar_estado` (110 válidos, entregados al Selector; los otros
60, todos de Samira, fallaron la validación de formato) y nunca pidió `validar_estado`.

```bash
python3 - <<'EOF'
import gzip, json
d = json.load(gzip.open('results/d3/raw/test_paginas_full.json.gz'))
for r in d['records']:
    if r['stop_reason']:
        stop = [e for e in r['agent_trace'] if e['kind'] == 'stop'][-1]
        print(r['target'], r['stop_reason'], stop['agent'])   # los 5 paros y quién se detuvo
EOF
```

## Métricas y límites

- **Resolución:** partidas resueltas / todas las partidas, incluidos paros.
- **Violación histórica:** checker del D1/D2; ignora amarillos.
- **Violación estricta:** incompatibilidad con todo el feedback público,
  incluidos amarillos y repetición, sobre jugadas válidas tras el feedback.
- **Coste:** directo y D2 permiten 64 tokens por turno; los agentes, hasta 768 por
  llamada (400 el Selector), 60 llamadas por turno y 160 por partida.
- McNemar compara resolución sobre objetivos pareados; las comparaciones múltiples
  son exploratorias. 30 objetivos no permiten inferir robustez general.
- Partición: 128 objetivos de entrenamiento, 15 de validación y 30 de prueba. Los de
  prueba ya se habían observado en evaluaciones previas (D1, D2 y, en este
  entregable, la prueba parcial del v1 y la del v3, antes de diseñar el v4); hay una
  corrida por objetivo: no establecen fiabilidad general.
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
- `agents_d3/state.py`: formato del estado, `validar_estado`, `ver_atributos` y
  funciones deterministas auxiliares; `query_roster` sólo la usan métricas y controles.
- `finetune/make_data_d3.py`, `finetune/lora_config_d3*.yaml`: datos y
  entrenamiento del adaptador común.
- `results/d3/dev/`: validación. `results/d3/raw/`: prueba final.
- `results/d3/v1/`, `v2_herramientas/`, `v3/`: protocolos anteriores, conservados
  como historia.
- `results/d3/probes*`: exploraciones del protocolo v1, no son resultados.
