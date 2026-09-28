# Cómo se hizo el fine-tuning

LoRA sobre `ministral-3-3b-instruct-2512` (pesos MLX de 4 bits) para que el modelo
escriba lo que el juego ya le reveló antes de jugar. Esta carpeta tiene todo lo
necesario para rehacerlo: el generador de datos, las configuraciones, los logs y el
adaptador elegido. Los resultados y el porqué del formato están en el
[README principal](../README.md).

## El modelo ajustado

Son los pesos base públicos más el adaptador LoRA de [`adapters/final/`](adapters/final/)
(45 MB): el punto de control del paso 800 de la ronda 2, elegido con los objetivos de
validación. Es el único que se versiona; los demás se regeneran con las
configuraciones de esta carpeta.

| | |
|---|---|
| Pesos base | `mlx-community/Ministral-3-3B-Instruct-2512-4bit` (2,78 GB; `mlx-lm` los descarga solo) |
| Adaptador | LoRA de rango 16 y escala 20 en los 12 bloques superiores de 26: 11,4 M parámetros, el 0,33% del modelo |
| Entrada que espera | la conversación del juego tal como la arma `build_messages` del notebook: roster en el prompt de sistema y feedback en cada turno |

Cómo usarlo, desde la raíz del repo:

```bash
# La app del pipeline y la evaluación: el servidor aplica el adaptador en cada petición
scripts/demo.sh
scripts/eval_d2.sh

# Cualquier comando de mlx-lm, con el adaptador sobre los pesos base
.venv-ft/bin/python -m mlx_lm generate --model mlx-community/Ministral-3-3B-Instruct-2512-4bit \
    --adapter-path finetune/adapters/final --prompt "..."

# Un modelo independiente, con el adaptador fusionado (6,4 GB, 16 bits)
.venv-ft/bin/python -m mlx_lm fuse --model mlx-community/Ministral-3-3B-Instruct-2512-4bit \
    --adapter-path finetune/adapters/final --dequantize --save-path ministral-3b-loldle
```

Los resultados se midieron con pesos base + adaptador. En nuestra comprobación, el
modelo fusionado con `--dequantize` genera exactamente lo mismo que esa combinación.
Sin `--dequantize` pesa 1,8 GB, pero vuelve a cuantizar los pesos a 4 bits y sus
salidas cambian: ese ya no es el modelo evaluado.

## 1. Datos: partidas simuladas con el motor del juego

[`make_data.py`](make_data.py) carga el motor del notebook `LoLdle_Classic.ipynb` y
simula partidas con él. Cada ejemplo es la conversación exacta que ve el modelo en el
pipeline —mismo prompt de sistema con el roster, mismos mensajes de feedback—, cortada
en el turno en que debe jugar. Sólo se entrena la respuesta de ese turno
(`mask_prompt`), y la calcula el mismo checker de restricciones que mide las
violaciones en la evaluación. Un ejemplo real de la ronda 2, después de jugar Aatrox y
Nunu & Willump:

```
Sé: Mana · Melee · >2013
Compatibles: Lillia, Nilah, Qiyana, Rell
Lillia
```

| Qué hay en los datos | Para qué |
|---|---|
| Partidas con la política «primer compatible en orden del roster», un ejemplo por turno | la política que se enseña: resuelve 173 de 173 partidas en 3,4 intentos de media |
| 4 ejemplos por objetivo tomados de partidas con jugadas al azar (con probabilidad 0,25, 0,5 o 1) | historiales que ya violaron restricciones, como los del baseline: enseñan a recuperarse |
| El primer turno, 12 veces | es idéntico para todos los objetivos |
| Sólo en la ronda 2: 3 historiales por objetivo con 1 a 3 repeticiones | salir del bucle de repetición que dejó la ronda 1 |

La partición de objetivos está en [`data/split.json`](data/split.json):

| Conjunto | Objetivos | Uso |
|---|---|---|
| Prueba | 30, los del Entregable 1 (`SEED=777`) | nunca son el campeón secreto en los datos; se jugaron una sola vez, al final |
| Validación | 15 | pérdida de validación y elección del punto de control |
| Entrenamiento | 128 | los datos de entrenamiento |

```bash
python3 finetune/make_data.py --format reasoned                   # ronda 1: 832 + 65 ejemplos
python3 finetune/make_data.py --format reasoned --sample-seed 2027 \
    --noisy-per-target 4 --repeats-per-target 3 --out reasoned_round2   # ronda 2: 1.216
cp finetune/data/reasoned/valid.jsonl finetune/data/reasoned_round2/valid.jsonl
```

Los `.jsonl` no se versionan (55 MB con todos los formatos): las semillas fijas los
regeneran byte a byte idénticos a los que se usaron para entrenar.

## 2. Entrenamiento

`mlx-lm` 0.31.3 en un MacBook con Apple M5 Pro de 64 GB:

```bash
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config.yaml          # ronda 1
.venv-ft/bin/python -m mlx_lm lora --config finetune/lora_config_round2.yaml   # ronda 2, desde la ronda 1
cp finetune/adapters/ministral-3b-loldle-r2/{adapters.safetensors,adapter_config.json} \
   finetune/adapters/final/
```

| | Valor | Nota |
|---|---|---|
| Método | LoRA sobre los pesos de 4 bits | los mismos pesos que el baseline: las dos variantes difieren sólo en el adaptador |
| Bloques | los 12 superiores de 26 | con lote 4 en los 26 bloques, un paso tardaba 70 s y usaba 52 GB |
| Rango · escala · dropout | 16 · 20 · 0,05 | 11,4 M parámetros entrenables |
| Lote | 1, con acumulación de gradiente 4 | los ejemplos miden ~5.500 tokens (el más largo, 7.363) porque el prompt lleva el roster entero |
| Tasa | 2e-5 en la ronda 1 y 1,5e-5 en la ronda 2, coseno con calentamiento | 1e-4 divergía: mlx-lm multiplica la salida LoRA por la escala (20) |
| Pérdida | sólo la respuesta del último turno (`mask_prompt`) | el prompt y el historial no se aprenden |

| Ronda | Datos | Pasos | Pérdida de validación | Tiempo | Memoria pico |
|---|---|---|---|---|---|
| 1 | 832 ejemplos | 700 (0,84 épocas) | 3,37 → 0,32 | 2,2 h | 22,0 GB |
| 2 | 1.216 ejemplos | 800 (0,66 épocas) | 0,32 → 0,26; sube a 0,47 al reiniciar la tasa | 2,5 h | 21,5 GB |

Los logs completos están en [`logs/`](logs/): la pérdida de entrenamiento, la tasa, la
velocidad y la memoria cada 20 pasos, y la pérdida de validación cada 100.

## 3. Elección del punto de control, sólo con validación

`mlx-lm` guarda un punto de control cada 100 pasos. Los candidatos se jugaron contra los
15 objetivos de validación con una regla fijada de antemano —más partidas resueltas; a
igualdad, menos violaciones— y los 30 de prueba se jugaron una sola vez, con el elegido.

| Punto de control | Resueltas en validación | Línea `Sé:` exacta |
|---|---|---|
| Ronda 1 · paso 100 | 0/15 | 52,7% de los turnos |
| Ronda 1 · paso 300 | 2/15 | 73,0% |
| Ronda 1 · paso 500 | 6/15 | 89,9% |
| Ronda 1 · paso 700 | 7/15 | 93,3% |
| Ronda 2 · paso 200 | 2/15 | 78,1% |
| Ronda 2 · paso 400 | 6/15 | 97,2% |
| **Ronda 2 · paso 800, el elegido** | **8/15** | **99,0%** |

En prueba, ese adaptador resuelve 14/30; el baseline con los mismos pesos, 1/30.

Para evaluar un punto de control se copia a una carpeta como `adapters.safetensors`,
junto con `adapter_config.json`, y se juega contra el servidor de la solución (el del
puerto 8082 de `scripts/demo.sh`):

```bash
python3 run_benchmark.py --label <nombre> --base-url http://127.0.0.1:8082/v1 \
    --api-model default_model --params 3.0 --adapter <carpeta> --submit last-line \
    --targets-json finetune/data/split.json --targets-key valid --out-dir results/d2/dev
```

Todas las corridas de validación están en `results/d2/dev/` y en la tabla de
estrategias de [`results/d2/ANALISIS_D2.md`](../results/d2/ANALISIS_D2.md).

## 4. Lo que se probó antes y se descartó

| Respuesta enseñada | Configuración | En validación |
|---|---|---|
| Sólo el nombre | [`lora_answer_only.yaml`](lora_answer_only.yaml), datos `--format answer` | 0/15 en el paso 240: con ~5 tokens supervisados por ejemplo de ~5.500 aprendió el formato, no la búsqueda, y empezó a inventar campeones («Melphite») |
| Compatibles + jugada, sin la línea `Sé:` | [`lora_candidates_only.yaml`](lora_candidates_only.yaml), datos `--format candidates` | 1/15 en el paso 100: su lista casi no dependía de la partida |

Las dos usaron los mismos hiperparámetros y se detuvieron antes de tiempo (en el paso
240 y antes del 140) al ver que no aprendían lo necesario, así que no se compararon a
igual presupuesto.

## Archivos

| Archivo | Qué es |
|---|---|
| `make_data.py` | Generador de datos: simula partidas con el motor del notebook y escribe `data/<formato>/{train,valid}.jsonl` y `data/split.json` |
| `lora_config.yaml` | Ronda 1 |
| `lora_config_round2.yaml` | Ronda 2, que continúa desde el adaptador de la ronda 1 |
| `lora_answer_only.yaml`, `lora_candidates_only.yaml` | Alternativas descartadas |
| `data/split.json` | Partición de objetivos: prueba, validación y entrenamiento |
| `adapters/final/` | El adaptador elegido y su configuración |
| `logs/` | Logs de las cuatro corridas de entrenamiento |
