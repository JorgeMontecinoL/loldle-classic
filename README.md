# LoLdle Classic — seguimiento de restricciones con un modelo de 3B

Inteligencia Artificial Generativa (580694). **Entregable 2**: la intervención contra
el fallo diagnosticado en el Entregable 1, funcionando de punta a punta y medida
contra el baseline de prompting directo sobre las mismas entradas.

**En una línea:** un fine-tuning LoRA de `ministral-3-3b-instruct-2512` que obliga al
modelo a escribir lo que ya sabe antes de jugar pasa de **1/30 a 14/30** partidas
resueltas con los mismos pesos (p = 0,001), y el mismo modelo, con una consulta al
roster que ejecuta su propio estado, resuelve **30/30**.

## Qué muestra el video

`scripts/demo.sh` levanta la app del **pipeline en vivo** (`http://127.0.0.1:8765`),
que juega la misma partida con dos variantes lado a lado:

| Columna | Modelo | Qué recibe el juego |
|---|---|---|
| **Baseline** · prompting directo | `ministral-3-3b-instruct-2512`, MLX 4-bit, sin ajuste | la respuesta completa, como en el Entregable 1 |
| **Solución** · fine-tuning LoRA | los mismos pesos + el adaptador de `finetune/adapters/final/` | sólo la última línea de la respuesta |

Cada columna ilumina las etapas del pipeline a medida que ocurren —**Historial →
Prompt → Modelo → Parser → Verificador → Juego**, y el feedback vuelve al historial—
y muestra el tablero de fichas, lo que el juego ya reveló y cuántos campeones siguen
siendo compatibles. En la columna de la solución además aparece lo que el modelo
escribe antes de jugar: su línea de estado (**Sé:**) y su lista de **compatibles**,
marcadas con ✓ o ✗ contra el motor del juego.

Nada está simulado. La app ejecuta `play_game` del propio notebook del Entregable 1
contra servidores de modelo reales y se engancha a los dos puntos de extensión que el
notebook ya expone (`query_model` y `show_event`). Cada partida queda registrada en
`results/d2/app_runs/` con la respuesta cruda de cada turno, así lo que se ve en
pantalla se puede rastrear hasta el repositorio.

El botón **Sortear** elige al azar uno de los 30 objetivos de prueba y muestra la
semilla; ninguno de esos 30 fue campeón secreto en los datos de entrenamiento. La
app indica la procedencia de cualquier campeón elegido a mano (prueba, validación o
entrenamiento). El control **Didáctico / Tiempo real** sólo espacia la animación entre
etapas; las llamadas al modelo y sus latencias son las reales.

## Reproducir la demo

Requiere un Mac con Apple Silicon (se desarrolló en un M5 Pro de 64 GB), `uv` y
conexión para descargar los pesos una vez (2,78 GB).

```bash
uv venv .venv-ft --python 3.12
uv pip install --python .venv-ft/bin/python mlx-lm matplotlib
scripts/demo.sh
```

`scripts/demo.sh` arranca dos `mlx_lm.server` con los mismos pesos base
(`mlx-community/Ministral-3-3B-Instruct-2512-4bit`) en los puertos 8081 y 8082,
espera a que respondan y abre la app. La variante de la solución pide el adaptador
LoRA en cada petición; el caché de prompt de `mlx_lm.server` está indexado por
modelo y adaptador, así que las dos variantes nunca comparten activaciones.

## La tarea, igual que en el Entregable 1

El modelo juega **LoLdle Classic**: adivinar un campeón secreto de League of Legends
en un máximo de 10 intentos. Recibe en el prompt el roster completo de 173 campeones
con siete atributos (género, posiciones, especie, recurso, alcance, regiones, año) y,
tras cada intento, feedback estilo Wordle por atributo: VERDE (coincidencia exacta),
AMARILLO (parcial en un atributo multivalor), GRIS (sin coincidencia) y ↑/↓ para el año.

Una jugada es correcta cuando es **exactamente el nombre de un campeón del roster**
que **no contradice ninguna restricción ya revelada** ni repite un intento. El prompt,
el roster, el motor de feedback, el checker de restricciones y el parser son los del
notebook `LoLdle_Classic.ipynb`, sin cambios.

**El fallo diagnosticado** en el Entregable 1: el modelo no mantiene el conjunto de
restricciones que el juego ya reveló. Viola lo revelado en más del 95% de sus intentos
—la deducción perfecta viola el 0% y resuelve el 100%— y varios modelos sustituyen la
deducción por recitar el roster en orden alfabético.

## Modelo

**`ministral-3-3b-instruct-2512`** (Mistral, 3B; release 2512), elegido entre los
tres candidatos del Entregable 1 —`exaone-3.5-2.4b-instruct` (2,4B),
`ministral-3-3b-instruct-2512` (3,0B) y `josiefied-qwen2.5-7b-instruct-abliterated-v2`
(7,6B)— porque fue **el único de los tres que superó al azar** con prompting directo
(6/30, p = 0,020; josiefied p = 0,090 y exaone p = 0,602), con menos de la mitad de
los parámetros que josiefied, que además recitaba el roster en el 48% de sus
transiciones. exaone es más pequeño, pero con prompting directo rindió exactamente
como el azar.

Pesos: `mlx-community/Ministral-3-3B-Instruct-2512-4bit` (MLX, cuantización afín de
4 bits, grupo 64), servidos con `mlx_lm.server`. Hardware: MacBook con Apple M5 Pro,
64 GB — el mismo equipo del Entregable 1.

## La intervención: fine-tuning LoRA con respuesta en tres pasos

El modelo ajustado responde en tres líneas, y **al juego sólo llega la última**:

```
Sé: Female · Mana · Ranged · Ionia · 2011
Compatibles: Karma
Karma
```

| Línea | Qué ataca |
|---|---|
| `Sé:` lo confirmado hasta ahora (verdes y rango de año) | el fallo del Entregable 1: no mantener las restricciones reveladas |
| `Compatibles:` los primeros campeones del roster que cumplen todo | la búsqueda en el roster; convierte en un procedimiento filtrado el "recitar el roster" que el Entregable 1 detectó |
| la jugada: el primero de la lista | lo que se evalúa, con el criterio del Entregable 1 |

Los datos de entrenamiento se generan con el propio motor del notebook
(`finetune/make_data.py`): partidas simuladas, cortadas en cada turno, cuya respuesta
objetivo calcula el mismo checker de restricciones que mide las violaciones. La
política que se enseña —jugar el primer campeón compatible en orden del roster—
resuelve 173 de 173 partidas en 3,4 intentos de media. Los 30 objetivos de prueba
del Entregable 1 nunca aparecen como campeón secreto en los datos; otros 15 quedan
para validación.

Entrenamiento: `mlx-lm` 0.31.3, LoRA de rango 16 en los 12 bloques superiores de 26
(11,4 M parámetros entrenables, 0,33% del modelo), lote efectivo 4, en dos rondas:

| Ronda | Datos | Pasos | Tasa | Por qué |
|---|---|---|---|---|
| 1 | 832 turnos simulados | 700 | 2e-5, coseno | formato de tres pasos desde el modelo base |
| 2 | 1.216 turnos, 384 con repeticiones en el historial | 800 | 1,5e-5, coseno | la ronda 1 se atascaba repitiendo jugadas (ver límites) |

~5 horas en total y 22 GB de pico en el M5 Pro. El punto de control final (ronda 2,
paso 800) se eligió **sólo con los 15 objetivos de validación**, con una regla fijada
de antemano (más partidas resueltas; a igualdad, menos violaciones); los 30 de prueba
se jugaron una única vez, con ese modelo. Configuraciones comentadas en
`finetune/lora_config.yaml` y `finetune/lora_config_round2.yaml`; logs en
`finetune/logs/`.

El paso a paso —datos, hiperparámetros, elección del punto de control y cómo usar o
fusionar el modelo ajustado— está en **[finetune/README.md](finetune/README.md)**.

## Resultados sobre los 30 objetivos de prueba

Los mismos 30 campeones del Entregable 1 (SEED=777), el mismo motor y el mismo
criterio de corrección para todas las variantes. Detalle completo, pruebas y tablas
por partida en **[results/d2/ANALISIS_D2.md](results/d2/ANALISIS_D2.md)**.

| Variante | Resueltas | Viola lo revelado | Repeticiones | Inválidas | Intentos medios (resueltas) |
|---|---|---|---|---|---|
| Baseline del Entregable 1 · GGUF Q4_K_M en LM Studio | 6/30 | 95,8% | 24% | 10,3% | 5,3 |
| Baseline · MLX 4-bit, los mismos pesos que se ajustaron | 1/30 | 99,1% | 44% | 17,1% | 2,0 |
| **Solución · fine-tuning LoRA** | **14/30** | 69,7% | 41% | 0,5% | 4,0 |
| Variante · fine-tuning + consulta al roster | **30/30** | 55,0% | 0% | 0% | 4,6 |

Comparación pareada (McNemar exacto sobre las partidas en que las variantes difieren):

| | contra el baseline MLX (mismos pesos) | contra el baseline GGUF del Entregable 1 |
|---|---|---|
| Fine-tuning LoRA | 14 a 1 · **p = 0,001** | 11 a 3 · p = 0,057 (no significativo al 5%) |
| Fine-tuning + consulta | 29 a 0 · p = 4·10⁻⁹ | 24 a 0 · p = 1·10⁻⁷ |

Qué cambió dentro del modelo, medido turno a turno contra el motor del juego:

| | Baseline | Fine-tuning LoRA |
|---|---|---|
| Línea `Sé:` idéntica a lo realmente revelado | — (no la escribe) | **97,7%** de los turnos |
| Respuestas que no son un nombre del roster | 17,1% | 0,5% |
| Jugadas que contradicen lo revelado sin ser repeticiones | ~55% | ~29% |

La **variante con consulta al roster** usa el mismo modelo ajustado, pero una
herramienta ejecuta su línea `Sé:` contra el roster y juega el primer campeón que la
cumple. La herramienta nunca recibe el feedback: sólo lo que el modelo dice saber y
los nombres ya jugados. Su resultado es la prueba de dónde está el cuello de botella:
el modelo ya rastrea bien el estado (el fallo del Entregable 1), y lo que le queda
débil es la búsqueda en el roster.

### Estrategias evaluadas

Todas sobre los 15 objetivos de validación, antes de tocar el conjunto de prueba
(tabla completa en el análisis):

| Estrategia | Resueltas | Qué mostró |
|---|---|---|
| Baseline · prompting directo | 2/15 | viola lo revelado en el 98% de los intentos |
| Diagnóstico · baseline con un resumen perfecto de lo revelado en el prompt | 4/15 | aun con el estado dado, viola el 93%: el cuello de botella también es la búsqueda |
| Fine-tuning «sólo nombre» | 0/15 | ~5 tokens supervisados por ejemplo de ~5.500: aprendió el formato pero no la búsqueda, y a mitad de camino inventaba campeones («Melphite»); detenido en el paso 240 |
| Fine-tuning «compatibles + jugada» | 1/15 | aprendió el formato pero su lista no dependía de la partida; detenido en el paso ~140, así que no se comparó a igual presupuesto |
| Fine-tuning de tres pasos · ronda 1 (pasos 100 / 300 / 500 / 700) | 0 · 2 · 6 · 7 /15 | el estado se aprende rápido (53% → 93% exacto); la búsqueda, lento |
| Fine-tuning de tres pasos · ronda 2 (pasos 200 / 400 / 800, **el 800 es el elegido**) | 2 · 6 · 8 /15 | reiniciar la tasa hunde el paso 200; al final, estado exacto en el 99% de los turnos |
| Fine-tuning + consulta al roster | 14/15 | ver Twisted Fate, abajo |

## Dónde falla la solución, y por qué

**Zac, con el fine-tuning puro** (objetivo de prueba; es el que salió al sortear en la
app). El modelo escribe su estado sin error —`Male · Melee · 2013`— y propone Yasuo,
que lo cumple pero contradice descartes que esa línea no registra. Luego repite Yasuo
siete veces: el bucle de repetición descrito en los límites. De las 16 partidas de
prueba que no resuelve, 13 terminan así, con tres o más repeticiones (Tryndamere:
Garen ×8; Dr. Mundo: Warwick ×8); las otras tres (Samira, Pantheon, Ezreal) fallan
por jugadas que contradicen lo revelado, sin llegar a atascarse.

**Twisted Fate, con la consulta al roster** (objetivo de validación). El estado del
modelo fue correcto los 10 turnos —`Male · Mana · Ranged · 2009`— y aun así no se
resolvió: en 2009 hay muchos campeones masculinos, de maná y a distancia, y sin los
descartes la herramienta los recorre en orden alfabético (Blitzcrank, Corki,
Fiddlesticks, Heimerdinger, Karthus, Ryze, Teemo) y se queda sin intentos antes de
llegar a la T. Es el "recitar el roster" del Entregable 1 reapareciendo, filtrado,
cuando el estado queda incompleto.

Ambas partidas se pueden jugar en la app: Zac con `scripts/demo.sh`, Twisted Fate con
`scripts/demo.sh state-tool`, eligiéndolo en la lista.

## Desviaciones respecto del Entregable 1, declaradas

1. **Formato de la respuesta.** El modelo ajustado escribe dos líneas de trabajo
   (`Sé:` y `Compatibles:`) antes de la jugada, y el pipeline envía al juego sólo
   la última línea. El criterio de corrección se aplica a esa jugada sin cambios:
   nombre exacto del roster, sin contradecir lo revelado ni repetir. Hay precedente
   en el propio Entregable 1: `qwen3.5-4b` era un modelo de razonamiento y se evaluó
   sólo su respuesta final, no su `reasoning_content`.
2. **Pila de inferencia.** El Entregable 1 corrió el GGUF Q4_K_M en LM Studio. Un
   GGUF cuantizado no se puede entrenar, así que el Entregable 2 usa los pesos MLX
   4-bit que sí se entrenaron, servidos con `mlx_lm.server`, y **re-mide el baseline
   sobre esos mismos pesos**: baseline y solución difieren sólo en el adaptador.
   El prompt es idéntico token a token (5.246 tokens en el primer turno en ambas
   pilas) y las plantillas de chat sólo difieren en un mensaje de error; aun así,
   el baseline MLX rinde peor que el GGUF (1/30 frente a 6/30), por la cuantización
   (Q4_K_M ≈ 4,8 bits/peso con tensores a 6 bits, frente a 4 bits afín). Se reportan
   ambos.
3. **Tokens de salida.** Se mantiene `max_tokens=64`: la respuesta de tres líneas mide
   33 tokens de mediana y 48 como máximo en los datos de entrenamiento.

## Límites conocidos, y por qué ocurren

- **Bucle de repetición bajo decodificación greedy.** Es la causa de casi todas las
  partidas que el fine-tuning puro no resuelve (el 41% de sus jugadas son
  repeticiones). Repetir un campeón no aporta información: el feedback es el mismo,
  el estado no cambia y, a temperatura 0, el modelo vuelve a proponer lo mismo. El
  bucle además se refuerza solo: cada repetición deja otra copia del nombre en el
  contexto y la hace más probable. La ronda 2 añadió 384 historiales con 1–3
  repeticiones y no bastó: en inferencia las cadenas son más largas. Ejemplo en la
  sección anterior (Zac).
- **La búsqueda en el roster sigue siendo el paso débil.** El modelo escribe su
  estado correctamente en más del 90% de los turnos, pero sólo parte de los nombres
  que lista cumplen ese estado: cruzar cinco condiciones contra 173 filas en una
  pasada es lo que menos aprende un 3B con este presupuesto de entrenamiento.
- **El estado registra lo confirmado, no lo descartado.** `Sé:` guarda los verdes y
  el rango de año, pero no los grises; por eso incluso la variante con herramienta
  viola descartes en el 55% de sus jugadas, aunque resuelva todas. Añadir los grises
  alarga la respuesta hasta 94 tokens, por encima del límite de 64. Ejemplo en la
  sección anterior (Twisted Fate).
- **La variante con herramienta excluye lo ya jugado.** La consulta recibe la línea
  `Sé:` del modelo y la lista de campeones ya propuestos, que está a la vista en la
  conversación; nunca recibe el feedback. Ese descarte de repeticiones es trabajo del
  código, y explica parte de su ventaja.
- **Sensibilidad a la cuantización.** Con el mismo prompt, el baseline cae de 6/30
  (GGUF Q4_K_M) a 1/30 (MLX 4-bit). Los resultados son de estos pesos concretos.
- **Tamaño de la evaluación.** 30 objetivos de prueba y 15 de validación: los
  intervalos de confianza son anchos y diferencias de una o dos partidas no son
  significativas.

## Reproducir todo desde cero

Cada paso lee lo que produjo el anterior; los datos y la partición salen de semillas
fijas, así que se regeneran idénticos.

```bash
# 1. Entorno de fine-tuning (MLX, Python 3.12)
uv venv .venv-ft --python 3.12
uv pip install --python .venv-ft/bin/python mlx-lm matplotlib

# 2. Datos (ronda 1 y ronda 2)
python3 finetune/make_data.py --format reasoned
python3 finetune/make_data.py --format reasoned --sample-seed 2027 \
    --noisy-per-target 4 --repeats-per-target 3 --out reasoned_round2
cp finetune/data/reasoned/valid.jsonl finetune/data/reasoned_round2/valid.jsonl

# 3. Entrenamiento (2,2 h y 2,5 h en un M5 Pro)
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config.yaml
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config_round2.yaml

# 4. Evaluación sobre los 30 objetivos de prueba y análisis
#    (con los servidores de scripts/demo.sh arriba)
scripts/eval_d2.sh
```

El paso 3 deja los puntos de control en `finetune/adapters/`; el elegido por
validación se copia a `finetune/adapters/final/`, que es el que usan la app y la
evaluación. Las alternativas descartadas se reproducen con
`finetune/lora_answer_only.yaml` y `finetune/lora_candidates_only.yaml`
(datos: `make_data.py --format answer` y `--format candidates`).

## Estructura

| Ruta | Qué es |
|---|---|
| `LoLdle_Classic.ipynb` | Motor del juego: roster, feedback, checker de restricciones, parser, loop y métricas. Fuente única de la lógica. |
| `run_benchmark.py` | Arnés de evaluación. Ejecuta las celdas del notebook y juega N partidas contra un servidor compatible con OpenAI; `--submit` elige qué parte de la respuesta recibe el juego. |
| `pipeline_app/` | App del pipeline en vivo (`server.py` + `index.html`), sólo biblioteca estándar. |
| `scripts/demo.sh` | Levanta los dos servidores de modelo y la app: lo que muestra el video. |
| `scripts/eval_d2.sh` | Reproduce los números de prueba del Entregable 2. |
| `finetune/README.md` | Cómo se hizo el fine-tuning, paso a paso, y cómo usar el modelo ajustado. |
| `finetune/make_data.py` | Genera los datos de entrenamiento con el motor del notebook. |
| `finetune/lora_*.yaml` | Configuraciones de entrenamiento, comentadas con lo medido. |
| `finetune/adapters/final/` | El adaptador LoRA elegido (45 MB). |
| `finetune/logs/` | Logs de las cuatro corridas de entrenamiento. |
| `analyze_d2.py` | Métricas, comparación pareada, estrategias evaluadas y casos de falla. |
| `docs/make_pipeline_diagram.py` | Diagrama del pipeline para el PDF (`docs/pipeline_diagram*.pdf`). |
| `results/d2/` | Resultados del Entregable 2: `ANALISIS_D2.md`, `summary.json`, trazas por variante en `raw/`, evaluaciones de validación en `dev/`, partidas jugadas en la app en `app_runs/`. |
| `results/` | Resultados del Entregable 1 (`ANALISIS.md`, `informe.html`, trazas en `raw/`). |
| `analyze_results.py`, `baselines.py` | Análisis y líneas base del Entregable 1. |
| `Evidencia.md` | Evidencia del Entregable 1: una partida con `ministral-3-8b-instruct-2512`, exportada de LM Studio. |

## Entregable 1

El diagnóstico de partida está en **[results/ANALISIS.md](results/ANALISIS.md)**
(versión navegable: [results/informe.html](results/informe.html)): 10 modelos
open-weight de hasta 8B, 30 partidas cada uno, contra líneas base sin LLM. La
deducción perfecta resuelve el 100% sin violar nada; ocho de los diez modelos quedan
en la banda del azar y sólo los dos Ministral la superan de forma significativa.

```bash
python3 run_benchmark.py      # 10 modelos × 30 partidas vía LM Studio -> results/raw/
python3 baselines.py          # líneas base sin LLM                     -> results/baselines.json
python3 analyze_results.py    # métricas e informe                      -> results/ANALISIS.md
```

Configuración: 30 partidas, 10 intentos, `SEED=777`, `temperature=0`,
`max_tokens=64`, prompt en rol `system`; `qwen3.5-4b` necesita
`reasoning_effort: "none"` (declarado en `MODEL_EXTRA_BODY`).
