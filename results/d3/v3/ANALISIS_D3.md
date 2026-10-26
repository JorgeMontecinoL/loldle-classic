# Entregable 3 · resultados observados

Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.

| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |
|---|---:|---:|---:|---:|---:|---:|---:|
| base/direct | 30 | 2 | 98.1% | 99.1% | 0 | 9.7 | 6.6 |
| lora/d2_lora | 30 | 14 | 69.7% | 81.1% | 0 | 7.2 | 5.7 |
| lora/d2_tool | 30 | 30 | 55.0% | 60.6% | 0 | 4.6 | 3.7 |
| multirol/full | 30 | 9 | 72.6% | 78.1% | 17 | 31.8 | 20.4 |
| multirol/no_examples | 30 | 14 | 66.2% | 74.8% | 7 | 30.6 | 34.1 |
| multirol/no_previous_state | 30 | 8 | 67.3% | 74.5% | 20 | 33.0 | 26.1 |
| multirol/no_revision | 30 | 11 | 71.2% | 80.0% | 11 | 24.0 | 26.4 |
| none/algorithmic | 30 | 30 | 0.0% | 0.0% | 0 | 0.0 | 0.0 |

## Interpretación y límites

- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.
- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.
- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.
- La equivalencia de Memoria exportada compara el conjunto de candidatos de su última entrega por turno con el derivado del feedback público. No garantiza igualdad de todas las cláusulas ni evalúa estados que nunca llegaron a entregarse.
- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.
- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.

## Comparaciones pareadas

- base/direct → multirol/full: 9 victorias, 2 derrotas discordantes; p=0.0654297 (n=30).
- lora/d2_lora → multirol/full: 1 victorias, 6 derrotas discordantes; p=0.125 (n=30).
- lora/d2_tool → multirol/full: 0 victorias, 21 derrotas discordantes; p=9.53674e-07 (n=30).
- multirol/no_examples → multirol/full: 1 victorias, 6 derrotas discordantes; p=0.125 (n=30).
- multirol/no_previous_state → multirol/full: 1 victorias, 0 derrotas discordantes; p=1 (n=30).
- multirol/no_revision → multirol/full: 1 victorias, 3 derrotas discordantes; p=0.625 (n=30).
- none/algorithmic → multirol/full: 0 victorias, 21 derrotas discordantes; p=9.53674e-07 (n=30).

## Fallos reales

- **base/direct · Karma**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Malzahar, Malzahar, Xerath, Xerath, Ryze, None, Ryze, None, Ryze. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **base/direct · Zoe**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Malzahar, Kai'Sa, Kai'Sa, Kassadin, Malzahar, Kai'Sa, Kassadin, Kassadin, Malzahar. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **base/direct · Nocturne**: 10 jugadas; 10 intentos agotados; secuencia: Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Kassadin, None, Kassadin, Kassadin, Kog'Maw, Kassadin. Fuente: `results/d3/raw/test_base_direct.json.gz`.
- **lora/d2_lora · Karma**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Ahri, LeBlanc, Lux, Syndra, Lux, Syndra, LeBlanc, LeBlanc, Lux. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **lora/d2_lora · Samira**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Kalista, Mel, Xayah, Zeri, Neeko, Renata Glasc, Xayah, None, Kai'Sa. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **lora/d2_lora · Nocturne**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Akali, Diana, Leona, Sejuani, Vi, Sejuani, Vi, Sejuani, Vi. Fuente: `results/d3/raw/test_lora_d2_lora.json.gz`.
- **multirol/full · Karma**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_full.json.gz`.
- **multirol/full · Samira**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_full.json.gz`.
- **multirol/full · Zoe**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_full.json.gz`.
- **multirol/no_examples · Karma**: 2 jugadas; call_limit; secuencia: Aatrox, Ahri. Fuente: `results/d3/raw/test_multirol_no_examples.json.gz`.
- **multirol/no_examples · Samira**: 2 jugadas; call_limit; secuencia: Aatrox, Kalista. Fuente: `results/d3/raw/test_multirol_no_examples.json.gz`.
- **multirol/no_examples · Nocturne**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_examples.json.gz`.
- **multirol/no_previous_state · Karma**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_previous_state.json.gz`.
- **multirol/no_previous_state · Samira**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_previous_state.json.gz`.
- **multirol/no_previous_state · Zoe**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_previous_state.json.gz`.
- **multirol/no_revision · Karma**: 5 jugadas; revision_disabled; secuencia: Aatrox, Ahri, Syndra, Syndra, Syndra. Fuente: `results/d3/raw/test_multirol_no_revision.json.gz`.
- **multirol/no_revision · Samira**: 1 jugadas; revision_disabled; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_revision.json.gz`.
- **multirol/no_revision · Zoe**: 1 jugadas; revision_disabled; secuencia: Aatrox. Fuente: `results/d3/raw/test_multirol_no_revision.json.gz`.
