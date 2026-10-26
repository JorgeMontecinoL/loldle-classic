# Grafo operativo · Entregable 3 (protocolo v4)

Tres agentes, cada uno una llamada separada al mismo Ministral-3-3B-Instruct-2512
(4 bits, MLX) con **los mismos pesos** (un adaptador LoRA común), su propio prompt
versionado y su propio contexto. **Ninguna herramienta deduce**: el código pagina
el roster y muestra filas, pero no filtra ni compara. Las herramientas
deterministas del D2 quedan sólo como controles de evaluación (`d2_tool`,
`algorithmic`).

```mermaid
flowchart TD
  H[Historial público] -->|pistas del último intento + estado previo| M[Agente Memoria]
  M -->|validar_estado| E[Herramienta: formato y consistencia interna]
  E -->|errores o válido| M
  M -->|entregar_estado: green, gray, yellow, year, used| S[Agente Selector]
  P[Roster paginado: 7 páginas de 25 filas] -->|una página por llamada| S
  S -->|listar: veredicto por fila + nombres que cumplen| S
  S -->|lista vacía en 4 pasadas: sin candidatos| M
  S -->|primer candidato de su lista| V[Agente Verificador]
  V -->|ver_atributos: nombre| A[Herramienta: fila del roster junto al estado, sin comparar]
  A -->|atributos del candidato| V
  H -->|pistas originales| V
  V -->|revisar_selector: rechazo + motivo → siguiente de la lista o nueva búsqueda| S
  V -->|revisar_memoria: pista omitida + motivo| M
  V -->|aprobar: misma propuesta| G[Motor del juego]
  G -->|feedback| H
  G -->|siete verdes o diez intentos| F[Fin de partida]
  V -->|stop| F
  V -.->|tras 3 rechazos sólo aprueba o para| G
  M & S & V -->|60 llamadas por turno o 160 por partida| F
```

## Agentes

| Agente | Recibe | Devuelve | Acciones | Para o transfiere cuando |
|---|---|---|---|---|
| Memoria | Pistas del último intento (campo, valor, color; año con la lectura literal de su flecha) y su estado previo. Ante una crítica: historial completo y motivo | Estado JSON `green`, `gray`, `yellow`, `year`, `used` | `validar_estado`, `entregar_estado` | Transfiere al Selector al entregar un estado válido. No tiene `stop`: su salida es entregar; su límite es el presupuesto |
| Selector | Estado de Memoria, nombres excluidos (jugados o rechazados), años que permite ese estado y una página de 25 filas del roster | Un veredicto por fila (`"Gwen ok"`, `"Ahri x regions"`) y los nombres que cumplen | `listar` (una por página) | Recorre las 7 páginas y entrega su lista al Verificador; si la lista sale vacía repite la búsqueda (3 pasadas muestreadas) y luego devuelve el trabajo a Memoria |
| Verificador | Candidato, pistas originales del historial y estado de Memoria | Aprobación o rechazo con motivo | `ver_atributos`, `aprobar`, `revisar_selector`, `revisar_memoria`, `stop` | Aprueba si nada contradice las pistas; devuelve al Selector una mala jugada (pasa el siguiente de la lista) o a Memoria una pista omitida. Tras 3 rechazos en el turno sólo puede aprobar o parar |

Por qué esta división: el diagnóstico del D1/D2 tiene tres partes y cada agente
toma una. Memoria **conserva lo revelado** (el `Sé:` del D2 guardaba sólo los
verdes). El Selector **busca en el roster**, el paso que el D2 documentó como el más
débil: cruzar condiciones contra 173 filas de una pasada. Aquí lo hace de a 25
filas y con un veredicto explícito por fila. El Verificador es **un control antes de
gastar un intento**: revisa una sola fila contra todas las pistas originales, con
una fuente independiente del estado de Memoria.

## Frontera de información

- Sólo `AgentSystem.play()` y el motor reciben el objetivo secreto. Ni prompts ni
  herramientas lo reciben.
- `validar_estado` comprueba formato, vocabulario y contradicciones internas del
  estado. No deduce restricciones faltantes del historial.
- La paginación entrega filas del roster en su orden, sin filtrar ni marcar nada.
  `years_allowed` lista los años que permite **el estado escrito por Memoria**
  (`eq`/`gt`/`lt`): reformatea el estado del agente, no consulta la evidencia.
- `ver_atributos` devuelve la fila del candidato junto a cada entrada del estado
  del mismo campo. No compara ni marca coincidencias.
- Si el Verificador aprueba una mala propuesta, se juega y se contabiliza. No hay
  reemplazo ni aprobación automática.

## Formato, tolerancias y reintentos

- Memoria, Selector y Verificador responden JSON. La respuesta se **prellena**
  (`{"action":"`, `{"action":"listar","revision":`) para que el adaptador no vuelva
  a otro formato, y se ignora texto posterior al primer objeto.
- El controlador normaliza sólo formatos inequívocos y lo registra (`normalized`):
  listas vacías, cláusulas de listas de un valor, notación `A+B` del D2, prefijo
  `Sé:`, año escrito como texto y `green.release_year = X` como `year.eq = X`.
- **Reintentos muestreados con semilla fija.** A temperatura 0 una entrada idéntica
  repite la misma salida. Un error de formato de Memoria se reintenta con su
  entrada original, los errores, temperatura 0,6 y semilla `1000·turno + reintento`.
  Una búsqueda vacía se repite con temperatura 0,7 y semilla por turno, pasada y
  página. La corrida sigue siendo reproducible; cada llamada guarda temperatura y
  semilla.
- Límites: 10 jugadas, 60 llamadas por turno, 160 por partida, 3 rechazos por turno,
  768 tokens por llamada (400 el Selector).

## Pesos comunes

Un solo adaptador LoRA para los tres roles, entrenado con la entrada exacta de
cada agente y etiquetas calculadas por el motor a partir de la evidencia pública,
como en el D2. En la partida cada agente decide solo. Partición del D2: 128
objetivos de entrenamiento; los 15 de validación sólo miden la pérdida y eligen
pesos; los 30 de prueba no aparecen. Cadena de entrenamiento (cada ronda parte de
la anterior):

| Ronda | Config | Datos | Qué aprende |
|---|---|---|---|
| D2 | `lora_config_round2.yaml` | `make_data.py` | Selector en formato `Sé/Compatibles` |
| 1 | `lora_config_d3.yaml` | `make_data_d3.py` | Memoria, Verificador y Selector D2 (v3) |
| 2 | `lora_config_d3_paginas.yaml` | `--paginas` | Selector por páginas, sólo lista (respondía `[]`; descartada como final) |
| 3 | `lora_config_d3_paginas_cot.yaml` | `--paginas --out d3_paginas_cot` | Veredicto por fila |
| 4 | `lora_config_d3_paginas_cot2.yaml` | `--paginas --out d3_paginas_cot2` | Años permitidos |
| 5 | `lora_config_d3_paginas_cot3.yaml` | `--paginas --repaso 300 --semilla 10 --out d3_paginas_cot3` | Más búsqueda y repaso de Memoria (**seleccionado**) |

Selector por páginas medido contra el motor en objetivos de validación:
ronda 2, nunca lista; ronda 3, precisión 37% y exhaustividad 23%; ronda 4, 83% y
42% (el error dominante era el año); ronda 5, 65% y 98%, y el primer nombre listado
cumple en 8 de 9 turnos.

## Técnicas de prompting por agente

| Técnica | Agente | Fallo del D1/D2 que ataca | Medición en prueba |
|---|---|---|---|
| Descomposición en roles (memoria / búsqueda / control) | Los tres | Un solo prompt mezclaba recordar, buscar y jugar | Sistema 25/30 frente a D2 14/30 |
| Crítica con revisión (critique-revise) | Verificador → Selector/Memoria | Jugadas que contradicen lo revelado | Sin revisión: 14/30 (−11) |
| Ejemplos resueltos (few-shot) | Los tres | Mala lectura de verde/gris/amarillo y de las filas | Sin ejemplos: 18/30 (−7) |
| Memoria explícita incremental (estado previo reinyectado) | Memoria | Olvidar restricciones de intentos anteriores | Sin estado previo: **29/30 (+4)**: reconstruir desde el historial completo funciona mejor |
| Búsqueda paginada con veredicto por fila (razonamiento estructurado) | Selector | Cruzar condiciones contra 173 filas de una pasada | Exhaustividad 23% → 98% entre rondas (validación) |
| Salida estructurada con prefill | Los tres | Respuestas fuera de formato | Errores de protocolo registrados |
| Uso de herramienta decidido por el agente | Verificador | Juzgar atributos que no conoce | Trazas `ver_atributos` |

## Resultados en prueba (30 objetivos, mismo criterio)

| Variante | Resueltas | Violación estricta | Paros por presupuesto |
|---|---:|---:|---:|
| Prompting directo (D1) | 2 | 99,1% | 0 |
| Solución D2 (adaptador, sin agentes) | 14 | 81,1% | 0 |
| **Sistema de agentes v4** | **25** | **15,4%** | 5 |
| sin ejemplos | 18 | 39,0% | 12 |
| sin estado previo | 29 | 21,3% | 1 |
| sin revisión | 14 | 26,7% | 16 |
| Control D2: herramienta que filtra el roster | 30 | 60,6% | 0 |
| Control sin LLM | 30 | 0,0% | 0 |

Comparaciones pareadas (McNemar exacto, exploratorio): el sistema gana 13 y pierde
2 frente al D2 (p = 0,007), y 24 a 1 frente al prompting directo. Sin revisión
pierde 12 y gana 1 (p = 0,003). Los 5 fallos del sistema terminan por presupuesto.
Resuelve en 3,24 intentos de media.

## Historia del protocolo

- **v1** (`results/d3/v1/`): herramientas que filtraban el roster y auditaban
  contra toda la evidencia; bucles de los agentes. 4/15 en validación.
- **v2** (`results/d3/v2_herramientas/`): mismas herramientas, bucles corregidos;
  10/15. Descartado por decisión del equipo: esas herramientas hacen la deducción
  que el entregable pide al modelo (son la variante que el D2 trató como control).
- **v3** (`results/d3/v3/`): sin herramientas que deduzcan; Selector en el formato
  del D2 y adaptador multirol. 5/15 en validación y 9/30 en prueba: el Selector
  acertaba 37% de sus jugadas y repetía la rechazada (bucle greedy).
- **v4** (este documento): Selector por páginas con veredicto por fila, años
  permitidos, límite de rechazos y reintentos muestreados. Validación: D2 8/15,
  v4 6/15 (ronda 4), 9/15 (ronda 5) y 11/15 (ronda 5 con búsqueda repetida,
  seleccionado). Prueba: 25/30.

Todos los ajustes se hicieron con objetivos de entrenamiento y validación. La
prueba de v1 (parcial) y la de v3 se observaron antes de diseñar v4; ningún
objetivo de prueba entró en datos ni en decisiones. El resultado de la ablación
sin estado previo (29/30) aparece en prueba y no se usó para cambiar el sistema.
