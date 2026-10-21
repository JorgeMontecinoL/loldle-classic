# Entregable 3 · resultados observados

Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.

| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |
|---|---:|---:|---:|---:|---:|---:|---:|
| base/full | 2 | 0 | 0.0% | — | 2 | 19.0 | 13.3 |

## Interpretación y límites

- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.
- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.
- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.
- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.
- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.

## Comparaciones pareadas


## Fallos reales

- **base/full · Ambessa**: 1 jugadas; call_limit; secuencia: Aatrox. Fuente: `results/d3/probes_v7/valid_base_full_n2.json.gz`.
- **base/full · Amumu**: 1 jugadas; agent_stop: No evidence to add beyond prior feedback; state schema is fully validated. Partial regions must be derived from yellow feedback, not forced. No further action aligns with constraints.; secuencia: Aatrox. Fuente: `results/d3/probes_v7/valid_base_full_n2.json.gz`.
