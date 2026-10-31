# Entregable 3 · resultados observados

Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.

| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |
|---|---:|---:|---:|---:|---:|---:|---:|
| base/full | 15 | 0 | 100.0% | 100.0% | 15 | 46.9 | 31.5 |
| lora/full | 15 | 1 | 71.7% | 77.4% | 10 | 39.7 | 44.7 |
| multirol2/full | 15 | 2 | 90.7% | 90.7% | 9 | 36.8 | 44.7 |
| multirol/full | 15 | 5 | 67.4% | 72.1% | 7 | 29.5 | 17.5 |

## Interpretación y límites

- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.
- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.
- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.
- La equivalencia de Memoria exportada compara el conjunto de candidatos de su última entrega por turno con el derivado del feedback público. No garantiza igualdad de todas las cláusulas ni evalúa estados que nunca llegaron a entregarse.
- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.
- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.

## Comparaciones pareadas

- lora/full → base/full: 0 victorias, 1 derrotas discordantes; p=1 (n=15).
- multirol2/full → base/full: 0 victorias, 2 derrotas discordantes; p=0.5 (n=15).
- multirol/full → base/full: 0 victorias, 5 derrotas discordantes; p=0.0625 (n=15).
- base/full → lora/full: 1 victorias, 0 derrotas discordantes; p=1 (n=15).
- multirol2/full → lora/full: 1 victorias, 2 derrotas discordantes; p=1 (n=15).
- multirol/full → lora/full: 1 victorias, 5 derrotas discordantes; p=0.21875 (n=15).
- base/full → multirol2/full: 2 victorias, 0 derrotas discordantes; p=0.5 (n=15).
- lora/full → multirol2/full: 2 victorias, 1 derrotas discordantes; p=1 (n=15).
- multirol/full → multirol2/full: 1 victorias, 4 derrotas discordantes; p=0.375 (n=15).
- base/full → multirol/full: 5 victorias, 0 derrotas discordantes; p=0.0625 (n=15).
- lora/full → multirol/full: 5 victorias, 1 derrotas discordantes; p=0.21875 (n=15).
- multirol2/full → multirol/full: 4 victorias, 1 derrotas discordantes; p=0.375 (n=15).

## Fallos reales

- **base/full · Ambessa**: 2 jugadas; call_limit; secuencia: Kassadin, Rengar. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **base/full · Amumu**: 1 jugadas; call_limit; secuencia: Kassadin. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **base/full · Corki**: 1 jugadas; call_limit; secuencia: Kassadin. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **lora/full · Amumu**: 4 jugadas; call_limit; secuencia: Aatrox, Blitzcrank, Master Yi, Shaco. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
- **lora/full · Corki**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Udyr, Nasus, Warwick, Nasus, Nasus, Nasus, Nasus, Nasus, Nasus. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
- **lora/full · Evelynn**: 2 jugadas; call_limit; secuencia: Aatrox, Diana. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
- **multirol2/full · Ambessa**: 10 jugadas; 10 intentos agotados; secuencia: Gangplank, Kled, K'Sante, Ornn, K'Sante, K'Sante, K'Sante, K'Sante, K'Sante, K'Sante. Fuente: `results/d3/dev/valid_multirol2_full.json.gz`.
- **multirol2/full · Amumu**: 10 jugadas; 10 intentos agotados; secuencia: Gangplank, Master Yi, Nunu & Willump, Warwick, Shaco, Warwick, Warwick, Warwick, Nunu & Willump, Warwick. Fuente: `results/d3/dev/valid_multirol2_full.json.gz`.
- **multirol2/full · Corki**: 5 jugadas; call_limit; secuencia: Gangplank, Master Yi, Nunu & Willump, Jax, Singed. Fuente: `results/d3/dev/valid_multirol2_full.json.gz`.
- **multirol/full · Ambessa**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Gwen, Gwen, Gwen, Gwen, Gwen, Gwen, Gwen, Gwen, Gwen. Fuente: `results/d3/dev/valid_multirol_full.json.gz`.
- **multirol/full · Corki**: 10 jugadas; 10 intentos agotados; secuencia: Aatrox, Brand, Fiddlesticks, Twitch, Karthus, Zilean, Ryze, Kassadin, Ryze, Ryze. Fuente: `results/d3/dev/valid_multirol_full.json.gz`.
- **multirol/full · Evelynn**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/dev/valid_multirol_full.json.gz`.
