---
base_model: mlx-community/Ministral-3-3B-Instruct-2512-4bit
library_name: mlx
tags:
- mlx
- lora
- loldle
- agents
language:
- es
- en
license: apache-2.0
---

# LoLdle D4 · adaptador LoRA del agente Selector

Adaptador LoRA (MLX) para **Ministral-3-3B-Instruct-2512** en 4 bits
(`mlx-community/Ministral-3-3B-Instruct-2512-4bit`, revisión
`a962dcb09eee4169c890e544c9eb938f1113fdee`). Lo usa **sólo el agente Selector** del
sistema de tres agentes (Memoria → Selector → Verificador) que juega LoLdle Classic
en el proyecto del curso Inteligencia Artificial Generativa (580694), Entregable 4.
Memoria y Verificador siguen con el adaptador común del Entregable 3 (`d3_paginas_cot3`).

`adapters.safetensors` SHA-256: `{SHA256}` — es el archivo que produjo los resultados
reportados en el repositorio del proyecto (`results/d4/`).

## Tarea del Selector

Recibe el estado de restricciones que escribió Memoria (verdes, grises, amarillos, año,
usados), los nombres excluidos y una página de 25 filas del roster. Debe escribir un
veredicto por fila («Nombre ok» o «Nombre x campo») y la lista de filas compatibles,
como JSON que continúa el prefijo `{"action":"listar","revision":`. El prompt de sistema
exacto está en `prompt_selector.txt`.

## Por qué este agente

En la prueba del Entregable 3, 4 de las 5 partidas detenidas (Morgana, Thresh, Ashe,
Soraka) tenían un estado de Memoria que admitía al secreto, pero el Selector lo
descartó en todas las pasadas por el campo amarillo (`positions [["Middle"]]`,
`regions [["Ionia"]]`, `regions [["Demacia","Shadow Isles"]]`). Con amarillos de un
solo valor, el Selector del D3 conservó 13 de 58 filas compatibles.

## Datos

Ronda 1: `data/ronda1/train.jsonl` (2.503 ejemplos, 128 secretos de entrenamiento).
Ronda 2: `data/ronda2/train.jsonl` (1.340 ejemplos de los mismos secretos, concentrados en
amarillos difíciles de `positions` y `regions`). Validación de pérdida: 95 ejemplos de los
15 secretos de validación. Historiales simulados con el motor del juego;
etiquetas calculadas con las reglas del juego sobre el feedback público, sin ningún
modelo de lenguaje. Se sobrerrepresentan páginas con amarillos de un valor y filas que
son subconjunto estricto de la cláusula. Ningún secreto de validación o prueba aparece
en entrenamiento. Detalle: `data/ronda1/report.json` y `data/ronda2/report.json`.

## Entrenamiento

LoRA (sobre pesos de 4 bits) rango 16, escala 20, dropout 0,05, 12 capas, `mask_prompt`,
lote 1 con acumulación 4, mlx-lm 0.31.3, Apple M5 Pro (64 GB).
Ronda 1 (`lora_config_d4_selector_r1.yaml`): desde `d3_paginas_cot3`, lr 2e-5, detenida en
la iteración 1050; se usa su paso 1000. Ronda 2 (`lora_config_d4_selector_r2.yaml`): desde
ese paso, lr 1e-5 cosine, 1.340 iteraciones (1 h 52 min), semilla 4042. Este archivo es el
final de la ronda 2, elegido sólo con validación (`checkpoint_selection.json`).

## Resultados (30 secretos de prueba del proyecto)

| Sistema | Resueltas | Intentos incompatibles | Paros |
|---|---:|---:|---:|
| D3 · Selector con el adaptador común | 25/30 | 15,4 % (10/65) | 5 |
| **D4 · Selector con este adaptador** | **29/30** | **12,7 % (9/71)** | **1** |

McNemar exacto D3 → D4: 4 a 0, p = 0,125 (no significativo con 30 secretos). Selector aislado
sobre 280 entradas reales con amarillo de la prueba del D3: conserva 57/62 filas compatibles
(D3: 40/62) y descarta al secreto en 5/40 páginas (D3: 18/40). Regresiones conocidas: estado
vacío del turno 1 en algunas páginas, límites de año y `species [["Human"]]`.

## Uso

```bash
pip install mlx-lm==0.31.3
mlx_lm.server --model mlx-community/Ministral-3-3B-Instruct-2512-4bit --port 8083
# cada petición al servidor puede llevar "adapters": "<ruta a esta carpeta>"
```

En el repositorio del proyecto:
`python -m agents_d4.evaluate --system d4 --adapter <ruta descargada> --split test --run-id hf_check`.

## Limitaciones

Especializado en un formato y un roster fijos (173 campeones). No mejora a Memoria ni
al Verificador. Ver resultados y fallos en el repositorio del proyecto.
