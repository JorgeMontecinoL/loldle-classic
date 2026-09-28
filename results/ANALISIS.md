# Análisis comparativo — LoLdle Classic con modelos open-weight ≤ 8B

**30 partidas por modelo**, máximo 10 intentos por partida, temperatura 0, `max_tokens` 64, SEED 777. Los **mismos 30 campeones objetivo** para los 10 modelos, así que la comparación es pareada. Cada partida reinicia la conversación; el modelo recibe el roster completo de 173 campeones y, tras cada intento, feedback estilo Wordle sobre siete atributos.

Total: **2844 intentos** evaluados sobre 10 modelos, sin un solo error de API.

## 1. El resultado principal

La tarea es **completamente resoluble con la información que recibe el modelo**. Una línea base que sólo mantiene el conjunto de restricciones reveladas y elige al azar entre los campeones compatibles resuelve **100.0% de las partidas en 3.3 intentos de media**, con 0.0% de violaciones. No hace falta conocimiento del dominio ni heurística de teoría de la información: basta con no contradecir lo ya revelado.

| Estrategia | Resueltas | Tasa violación | Progreso |
|------------|-----------|----------------|----------|
| **Deducción perfecta** (`feasible`) | 100.0% | 0.0% | 100.0% |
| Mejor modelo (`ministral-3-8b-instruct-2512`) | 40.0% | 90.5% | 67.6% |
| Modelo mediano (`meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k`) | 6.7% | 99.6% | 48.1% |
| Azar sin memoria (`random`, 200 sim.) | 6.3% | 97.9% | 53.0% |
| Recorrer el roster (`roster`) | 3.3% | 97.3% | 53.3% |

**2 de los 10 modelos superan el azar de forma estadísticamente significativa; los otros 8 no.** `ministral-3-8b-instruct-2512` resuelve 12/30 frente a los 1.9/30 del azar (p = 0.005), y es el primer modelo de esta serie que demuestra hacer algo más que adivinar.

**Pero la brecha no se cierra, sólo se estrecha.** Incluso el mejor modelo viola restricciones ya reveladas en el 90.5% de sus intentos y resuelve 40.0% de las partidas, frente al 0% y el 100% de la deducción perfecta. El prompting directo sigue muy lejos del techo: esa distancia es lo que el resto del semestre tiene que cerrar.

## 2. Ranking global (índice CFS)

El **CFS** (Constraint-Following Score) resume la tarea en un número. Pesos: cumplimiento de restricciones 35%, resolución 17%, progreso 16%, no enumerar el roster 14%, validez de formato 12%, no repetición 6%. El peso dominante es el cumplimiento de restricciones, que es la capacidad que la tarea mide realmente; la resolución pesa menos porque sobre 30 partidas la mayoría de los modelos no se separa del azar y las diferencias en la cola baja son ruido. El término de enumeración se incorporó tras observar el comportamiento descrito en §5(c): recitar el listado infla el progreso aparente sin deducir nada.

| # | Modelo | B | CFS | Resueltas | Tasa violación | Progreso | Enumera roster | Inválidos |
|---|--------|---|-----|-----------|----------------|----------|----------------|-----------|
| 1 | `ministral-3-8b-instruct-2512` | 8.0 | **0.528** | 12/30 (40.0%) | 90.5% | 67.6% | 0.5% | 0.4% |
| 2 | `ministral-3-3b-instruct-2512` | 3.0 | **0.429** | 6/30 (20.0%) | 95.8% | 54.3% | 1.9% | 10.3% |
| 3 | `exaone-3.5-2.4b-instruct` | 2.4 | **0.404** | 2/30 (6.7%) | 98.3% | 54.3% | 0.0% | 7.0% |
| 4 | `josiefied-qwen2.5-7b-instruct-abliterated-v2` | 7.6 | **0.376** | 4/30 (13.3%) | 96.2% | 56.7% | 48.3% | 0.0% |
| 5 | `falcon3-7b-instruct` | 7.0 | **0.374** | 3/30 (10.0%) | 98.1% | 50.0% | 13.0% | 0.7% |
| 6 | `meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k` | 3.2 | **0.352** | 2/30 (6.7%) | 99.6% | 48.1% | 31.4% | 0.0% |
| 7 | `qwen3.5-4b` | 4.0 | **0.333** | 1/30 (3.3%) | 97.7% | 47.1% | 28.4% | 1.4% |
| 8 | `microsoft_phi-4-mini-instruct` | 3.8 | **0.320** | 1/30 (3.3%) | 100.0% | 39.0% | 6.5% | 31.6% |
| 9 | `josie-7b-v6.0-step2000` | 7.6 | **0.312** | 2/30 (6.7%) | 96.9% | 53.8% | 81.8% | 0.0% |
| 10 | `qwen2.5-7b-instruct` | 7.6 | **0.285** | 1/30 (3.3%) | 97.3% | 53.3% | 96.6% | 0.0% |

## 3. Contraste contra el azar

p-valor empírico unilateral: proporción de las 200 simulaciones aleatorias que igualan o superan las partidas resueltas del modelo. Un valor alto significa que el modelo **no se distingue del azar**.

| Modelo | Resueltas | Azar esperado | Δ | p |
|--------|-----------|---------------|---|---|
| `ministral-3-8b-instruct-2512` | 12/30 | 1.9/30 | +33.7% | 0.005 |
| `ministral-3-3b-instruct-2512` | 6/30 | 1.9/30 | +13.7% | 0.020 |
| `exaone-3.5-2.4b-instruct` | 2/30 | 1.9/30 | +0.4% | 0.602 |
| `josiefied-qwen2.5-7b-instruct-abliterated-v2` | 4/30 | 1.9/30 | +7.0% | 0.090 |
| `falcon3-7b-instruct` | 3/30 | 1.9/30 | +3.7% | 0.303 |
| `meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k` | 2/30 | 1.9/30 | +0.4% | 0.602 |
| `qwen3.5-4b` | 1/30 | 1.9/30 | -3.0% | 0.861 |
| `microsoft_phi-4-mini-instruct` | 1/30 | 1.9/30 | -3.0% | 0.861 |
| `josie-7b-v6.0-step2000` | 2/30 | 1.9/30 | +0.4% | 0.602 |
| `qwen2.5-7b-instruct` | 1/30 | 1.9/30 | -3.0% | 0.861 |

Superan el azar con p < 0,05: `ministral-3-8b-instruct-2512`, `ministral-3-3b-instruct-2512`.

## 4. Métricas detalladas

| Modelo | Intentos | Inválidos | Formato ✗ | Repet. | Violaciones / elegibles | Partidas limpias | Turno 1ª violación | Mejor greens |
|--------|----------|-----------|-----------|--------|-------------------------|------------------|--------------------|--------------|
| `ministral-3-8b-instruct-2512` | 252 | 1 (0.4%) | 1 (0.4%) | 2 | 200/221 (90.5%) | 1/30 | 2.03 | 7/7 |
| `ministral-3-3b-instruct-2512` | 272 | 28 (10.3%) | 42 (15.4%) | 52 | 205/214 (95.8%) | 0/30 | 2.10 | 7/7 |
| `exaone-3.5-2.4b-instruct` | 287 | 20 (7.0%) | 20 (7.0%) | 56 | 233/237 (98.3%) | 1/30 | 2.03 | 7/7 |
| `josiefied-qwen2.5-7b-instruct-abliterated-v2` | 291 | 0 (0.0%) | 0 (0.0%) | 15 | 251/261 (96.2%) | 1/30 | 2.21 | 7/7 |
| `falcon3-7b-instruct` | 293 | 2 (0.7%) | 6 (2.0%) | 149 | 256/261 (98.1%) | 0/30 | 2.07 | 7/7 |
| `meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k` | 288 | 0 (0.0%) | 0 (0.0%) | 64 | 257/258 (99.6%) | 1/30 | 2.00 | 7/7 |
| `qwen3.5-4b` | 291 | 4 (1.4%) | 4 (1.4%) | 169 | 251/257 (97.7%) | 1/30 | 2.21 | 7/7 |
| `microsoft_phi-4-mini-instruct` | 291 | 92 (31.6%) | 181 (62.2%) | 101 | 169/169 (100.0%) | 1/30 | 2.00 | 7/7 |
| `josie-7b-v6.0-step2000` | 288 | 0 (0.0%) | 0 (0.0%) | 7 | 250/258 (96.9%) | 1/30 | 2.21 | 7/7 |
| `qwen2.5-7b-instruct` | 291 | 0 (0.0%) | 0 (0.0%) | 0 | 254/261 (97.3%) | 1/30 | 2.21 | 7/7 |

*Partidas limpias* = partidas sin ninguna violación. *Turno 1ª violación* = intento medio en que el modelo contradice por primera vez el feedback ya recibido. *Mejor greens* = máximo de atributos exactos en un intento (7/7 = partida resuelta).

## 5. Diagnóstico del fallo

El fallo **no es de conocimiento**. El roster completo va en el prompt, los modelos nombran campeones reales y el formato de salida es correcto en la gran mayoría de los intentos. El fallo es de **razonamiento deductivo acumulativo**: el modelo no mantiene el conjunto de restricciones reveladas a lo largo de la conversación.

Tres evidencias concretas:

**(a) La información está ahí y es abundante.** Tras un solo intento informativo el espacio de candidatos compatibles cae de 173 a 12.1 campeones, y al tercer intento a 4.3. Tamaño medio del conjunto factible por turno:

| Turno | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|-------|---|---|---|---|---|---|---|---|
| Candidatos | 173 | 12.1 | 4.3 | 2.4 | 1.8 | 1.5 | 1.3 | 1 |

**(b) La violación aparece de inmediato y no se recupera.** En promedio el primer intento contradictorio llega en el turno 2.1, es decir en cuanto hay algo que recordar. Sólo 8 de las 300 partidas jugadas terminan sin ninguna violación.

**(c) Varios modelos sustituyen la deducción por enumerar el roster.** Cuando no saben qué hacer, proponen el siguiente campeón del listado en vez de uno compatible. Fracción de transiciones que avanzan exactamente una posición en el roster (el azar daría ~0,6%):

| Modelo | Paso consecutivo | Avance hacia adelante |
|--------|------------------|-----------------------|
| `qwen2.5-7b-instruct` | 96.6% | 100.0% |
| `josie-7b-v6.0-step2000` | 81.8% | 95.7% |
| `josiefied-qwen2.5-7b-instruct-abliterated-v2` | 48.3% | 90.0% |
| `meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k` | 31.4% | 70.5% |
| `qwen3.5-4b` | 28.4% | 44.0% |
| `falcon3-7b-instruct` | 13.0% | 44.8% |
| `microsoft_phi-4-mini-instruct` | 6.5% | 35.5% |
| `ministral-3-3b-instruct-2512` | 1.9% | 56.5% |
| `ministral-3-8b-instruct-2512` | 0.5% | 65.2% |
| `exaone-3.5-2.4b-instruct` | 0.0% | 55.3% |

`qwen2.5-7b-instruct` recorre el roster en orden en 96.6% de sus transiciones: está ignorando el feedback por completo y usando el prompt como una lista que recitar.

Violaciones agregadas por atributo, sumando los 10 modelos:

| Atributo | Violaciones |
|----------|-------------|
| Género | 2006 |
| Posiciones | 1747 |
| Año | 1651 |
| Alcance | 1534 |
| Regiones | 1512 |
| Especie | 933 |
| Recurso | 867 |

## 6. Viabilidad de ejecución

| Modelo | B | Latencia media | Corrida de 30 partidas | Errores API |
|--------|---|----------------|------------------------|-------------|
| `exaone-3.5-2.4b-instruct` | 2.4 | 0.24 s | 70 s | 0 |
| `ministral-3-3b-instruct-2512` | 3.0 | 0.28 s | 77 s | 0 |
| `meta-llama-llama-3.2-3b-instruct-qlora-malaysian-16k` | 3.2 | 0.20 s | 58 s | 0 |
| `microsoft_phi-4-mini-instruct` | 3.8 | 0.61 s | 177 s | 0 |
| `qwen3.5-4b` | 4.0 | 0.27 s | 79 s | 0 |
| `falcon3-7b-instruct` | 7.0 | 0.34 s | 99 s | 0 |
| `josiefied-qwen2.5-7b-instruct-abliterated-v2` | 7.6 | 0.34 s | 98 s | 0 |
| `josie-7b-v6.0-step2000` | 7.6 | 0.34 s | 98 s | 0 |
| `qwen2.5-7b-instruct` | 7.6 | 0.34 s | 97 s | 0 |
| `ministral-3-8b-instruct-2512` | 8.0 | 0.38 s | 97 s | 0 |

Los 8 modelos corren localmente en LM Studio (API compatible con OpenAI) con prompts de ~5.000 tokens. La corrida completa —2844 llamadas— tomó 16 minutos sin un solo error. La viabilidad de hardware queda demostrada empíricamente, no estimada.

`qwen3.5-4b` requiere un ajuste: es un modelo de razonamiento y con `max_tokens=64` agota la generación en `reasoning_content` devolviendo `content` vacío en el 100% de los intentos. Se corrige enviando `reasoning_effort: "none"` en el cuerpo de la petición.

## 7. Los tres candidatos

Los 2 modelos que superan el azar de forma significativa entran directamente; para el tercer puesto, donde las diferencias de resolución ya son ruido, el criterio es **qué tan buena base ofrece cada modelo para el andamiaje** de los próximos entregables: que no degenere en recitar el listado, que respete el formato y que deje margen de mejora atacando la gestión de estado.

**1. `ministral-3-8b-instruct-2512` (8.0B) — CFS 0.528.** Resuelve 12/30 (40.0%), viola restricciones en 90.5% de sus intentos elegibles, progreso medio 67.6%, 0.4% de respuestas inválidas, 2 repeticiones y 0.38 s de latencia media por intento.

El único modelo que se acerca a hacer la tarea. Resuelve 12/30 con p = 0.005 contra el azar, tiene la **tasa de violación más baja del estudio** (90.5%, siete puntos por debajo del siguiente) y el mejor progreso medio (67.6%). Casi no enumera el roster (0.5%): cuando acierta es porque dedujo, no porque barrió. Con 0.4% de respuestas inválidas es además directamente usable dentro de un pipeline.

**2. `ministral-3-3b-instruct-2512` (3.0B) — CFS 0.429.** Resuelve 6/30 (20.0%), viola restricciones en 95.8% de sus intentos elegibles, progreso medio 54.3%, 10.3% de respuestas inválidas, 52 repeticiones y 0.28 s de latencia media por intento.

La apuesta por eficiencia. Con 3B —el 38% del techo— resuelve 6/30 y **también supera el azar de forma significativa** (p = 0.020), algo que ningún otro modelo por debajo de 8B consigue. Enumera el roster sólo un 1.9%. Su punto débil es la disciplina de formato: 28 respuestas inválidas (10.3%), corregible con validación externa y reintento.

**3. `exaone-3.5-2.4b-instruct` (2.4B) — CFS 0.404.** Resuelve 2/30 (6.7%), viola restricciones en 98.3% de sus intentos elegibles, progreso medio 54.3%, 7.0% de respuestas inválidas, 56 repeticiones y 0.24 s de latencia media por intento.

El control de bajo coste, y el más pequeño del estudio con 2,4B. No supera el azar (p = 0.602), pero tiene **0.0% de enumeración**: cuando falla, falla intentando deducir en vez de recitar el listado. Es el más barato por intento, lo que lo hace útil como banco de pruebas rápido del andamiaje antes de gastar cómputo en los Ministral.

Para el bono por tamaño, `ministral-3-3b-instruct-2512` es el modelo más pequeño que supera el azar de forma significativa: 3.0B, un 38% del techo, resolviendo 6/30 con p = 0.020. La defensa es de tarea y no de tamaño: supera a los siete modelos de 7B y 7,6B del estudio en el índice compuesto, y lo hace con menos de la mitad de sus parámetros. El más pequeño del podio es `exaone-3.5-2.4b-instruct` con 2.4B.

## 8. Qué implica para los próximos entregables

La elección de modelo **sí importa**, y más de lo que sugería la primera tanda: `ministral-3-8b-instruct-2512` resuelve 12/30 donde la mediana del estudio resuelve 2/30, y lo hace con la tasa de violación más baja medida. Cualquier andamiaje debe construirse sobre esa base, no sobre los modelos de la cola.

Pero el mejor modelo sigue violando restricciones en 90.5% de sus intentos y dejando 18 de 30 partidas sin resolver, frente a un techo del 100%. **El modelo solo no basta.** La brecha que queda no es de capacidad lingüística sino de gestión de estado, y se ataca con andamiaje externo:

1. **Memoria explícita de restricciones** — mantener el conjunto revelado fuera del modelo y reinyectarlo como texto en cada turno, en vez de esperar que lo reconstruya del historial.
2. **Filtrado del espacio de candidatos** — pasar de 173 nombres a los 4.3 compatibles y pedir la elección sobre esa lista corta.
3. **Descomposición del razonamiento** — separar «actualizar restricciones» de «elegir candidato» en dos llamadas, en vez de exigir ambas en una respuesta de 64 tokens.

La señal más útil para diseñar ese andamiaje está en §5(c): los modelos que enumeran el roster ocupan el fondo del ranking y los dos que lo superan el azar casi no enumeran. La diferencia entre recitar y deducir es exactamente lo que el andamiaje tiene que amplificar.
