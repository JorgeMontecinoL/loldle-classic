# Entregable 3 · resultados observados

Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.

| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |
|---|---:|---:|---:|---:|---:|---:|---:|
| base/direct | 30 | 2 | 98.1% | 99.1% | 0 | 9.7 | 6.6 |
| lora/d2_lora | 30 | 14 | 69.7% | 81.1% | 0 | 7.2 | 5.7 |
| lora/d2_tool | 30 | 30 | 55.0% | 60.6% | 0 | 4.6 | 3.7 |
| none/algorithmic | 30 | 30 | 0.0% | 0.0% | 0 | 0.0 | 0.0 |
| paginas/full | 30 | 25 | 3.1% | 15.4% | 5 | 46.5 | 98.0 |
| paginas/no_examples | 30 | 18 | 30.5% | 39.0% | 12 | 66.9 | 125.3 |
| paginas/no_previous_state | 30 | 29 | 9.3% | 21.3% | 1 | 44.4 | 91.5 |
| paginas/no_revision | 30 | 14 | 4.4% | 26.7% | 16 | 40.1 | 82.9 |

## Interpretación y límites

- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.
- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.
- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.
- La equivalencia de Memoria exportada compara el conjunto de candidatos de su última entrega por turno con el derivado del feedback público. No garantiza igualdad de todas las cláusulas ni evalúa estados que nunca llegaron a entregarse.
- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.
- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.

## Comparaciones pareadas

- base/direct → paginas/full: 24 victorias, 1 derrotas discordantes; p=1.54972e-06 (n=30).
- lora/d2_lora → paginas/full: 13 victorias, 2 derrotas discordantes; p=0.00738525 (n=30).
- lora/d2_tool → paginas/full: 0 victorias, 5 derrotas discordantes; p=0.0625 (n=30).
- none/algorithmic → paginas/full: 0 victorias, 5 derrotas discordantes; p=0.0625 (n=30).
- paginas/no_examples → paginas/full: 11 victorias, 4 derrotas discordantes; p=0.118469 (n=30).
- paginas/no_previous_state → paginas/full: 1 victorias, 5 derrotas discordantes; p=0.21875 (n=30).
- paginas/no_revision → paginas/full: 12 victorias, 1 derrotas discordantes; p=0.00341797 (n=30).

## Fallos reales

- **base/direct · Karma**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Malzahar, Malzahar, Xerath, Xerath, Ryze, None, Ryze, None, Ryze. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **base/direct · Zoe**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Malzahar, Kai'Sa, Kai'Sa, Kassadin, Malzahar, Kai'Sa, Kassadin, Kassadin, Malzahar. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **base/direct · Nocturne**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Kassadin, None, Kassadin, Kassadin, Kog'Maw, Kassadin. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **lora/d2_lora · Karma**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Ahri, LeBlanc, Lux, Syndra, Lux, Syndra, LeBlanc, LeBlanc, Lux. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **lora/d2_lora · Samira**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Kalista, Mel, Xayah, Zeri, Neeko, Renata Glasc, Xayah, None, Kai'Sa. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **lora/d2_lora · Nocturne**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Akali, Diana, Leona, Sejuani, Vi, Sejuani, Vi, Sejuani, Vi. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **paginas/full · Samira**: 2 jugadas; call_limit; secuencia: Aatrox, Kai'Sa. Fuente: `results/d3/raw/test_paginas_full.json.gz`.
- **paginas/full · Morgana**: 3 jugadas; call_limit; secuencia: Aatrox, Ahri, LeBlanc. Fuente: `results/d3/raw/test_paginas_full.json.gz`.
- **paginas/full · Thresh**: 2 jugadas; call_limit; secuencia: Aatrox, Lucian. Fuente: `results/d3/raw/test_paginas_full.json.gz`.
- **paginas/no_examples · Nocturne**: 2 jugadas; call_limit; secuencia: Ahri, Jarvan IV. Fuente: `results/d3/raw/test_paginas_no_examples.json.gz`.
- **paginas/no_examples · LeBlanc**: 1 jugadas; call_limit; secuencia: Ahri. Fuente: `results/d3/raw/test_paginas_no_examples.json.gz`.
- **paginas/no_examples · Morgana**: 2 jugadas; call_limit; secuencia: Ahri, Cassiopeia. Fuente: `results/d3/raw/test_paginas_no_examples.json.gz`.
- **paginas/no_previous_state · Pantheon**: 4 jugadas; call_limit; secuencia: Aatrox, Darius, Gangplank, Olaf. Fuente: `results/d3/raw/test_paginas_no_previous_state.json.gz`.
- **paginas/no_revision · Samira**: 1 jugadas; revision_disabled; secuencia: Aatrox. Fuente: `results/d3/raw/test_paginas_no_revision.json.gz`.
- **paginas/no_revision · Veigar**: 1 jugadas; revision_disabled; secuencia: Aatrox. Fuente: `results/d3/raw/test_paginas_no_revision.json.gz`.
- **paginas/no_revision · Morgana**: 3 jugadas; call_limit; secuencia: Aatrox, Ahri, LeBlanc. Fuente: `results/d3/raw/test_paginas_no_revision.json.gz`.
