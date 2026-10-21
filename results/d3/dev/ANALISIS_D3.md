# Entregable 3 · resultados observados

Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.

| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |
|---|---:|---:|---:|---:|---:|---:|---:|
| base/full | 15 | 4 | 0.0% | 0.0% | 11 | 23.5 | 12.0 |
| lora/full | 15 | 0 | 0.0% | — | 15 | 18.0 | 7.7 |

## Interpretación y límites

- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.
- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.
- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.
- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.
- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.

## Comparaciones pareadas

- lora/full → base/full: 4 victorias, 0 derrotas discordantes; p=0.125 (n=15).
- base/full → lora/full: 0 victorias, 4 derrotas discordantes; p=0.125 (n=15).

## Fallos reales

- **base/full · Amumu**: 2 jugadas; call_limit; secuencia: Aatrox, Alistar. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **base/full · Evelynn**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **base/full · Illaoi**: 2 jugadas; call_limit; secuencia: Aatrox, Ambessa. Fuente: `results/d3/dev/valid_base_full.json.gz`.
- **lora/full · Ambessa**: 0 jugadas; call_limit; secuencia: ninguna. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
- **lora/full · Amumu**: 0 jugadas; call_limit; secuencia: ninguna. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
- **lora/full · Corki**: 0 jugadas; call_limit; secuencia: ninguna. Fuente: `results/d3/dev/valid_lora_full.json.gz`.
