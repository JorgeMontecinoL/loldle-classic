# Entregable 2 — baseline contra fine-tuning LoRA

**Entradas:** los 30 objetivos de prueba del Entregable 1 (SEED=777), reservados: ninguno aparece como campeón secreto en los datos de entrenamiento. **Criterio:** el mismo del Entregable 1 — salida correcta = nombre exacto de un campeón del roster que no contradice ninguna restricción revelada ni repite un intento previo. Máximo 10 intentos, temperatura 0, `max_tokens` 64.

| Variante | Resueltas | Violación | Compatibles | Inválidos | Intentos medios (resueltas) | Progreso | Enumera roster | CFS | p vs azar |
|---|---|---|---|---|---|---|---|---|---|
| Baseline del Entregable 1 · GGUF Q4_K_M en LM Studio | 6/30 (20.0%) | 95.8% | 4.2% | 10.3% | 5.33 | 54.3% | 1.9% | 0.429 | 0.020 |
| Baseline · MLX 4-bit, prompting directo | 1/30 (3.3%) | 99.1% | 0.9% | 17.1% | 2.00 | 48.6% | 1.9% | 0.364 | 0.861 |
| Solución · fine-tuning LoRA (el juego recibe la jugada del modelo) | 14/30 (46.7%) | 69.7% | 30.3% | 0.5% | 4.00 | 76.7% | 3.8% | 0.601 | 0.005 |
| Variante · fine-tuning LoRA + consulta al roster con el «Sé» del modelo | 30/30 (100.0%) | 55.0% | 45.0% | 0.0% | 4.63 | 100.0% | 10.1% | 0.793 | 0.005 |

CFS con los pesos del Entregable 1: constraint_compliance 35%, solve_rate 17%, progress 16%, no_enumeration 14%, validity 12%, no_repeat 6%.

## Estrategias evaluadas (validación: 15 objetivos reservados)

Los puntos de control y las alternativas se eligieron sólo con estos 15 objetivos; los 30 de prueba se usaron una única vez, con el modelo elegido.

| Estrategia | Resueltas | Violación | Repeticiones | Inválidos | Estado «Sé» exacto |
|---|---|---|---|---|---|
| Baseline · prompting directo | 2/15 | 98.1% | 48.1% | 12.1% | — |
| Diagnóstico · baseline + resumen perfecto de lo revelado en el prompt | 4/15 | 93.3% | 16.3% | 11.9% | — |
| FT «sólo nombre» (detenido en la iteración 240) | 0/15 | 98.5% | 91.9% | 0.0% | — |
| FT «compatibles + jugada» (iteración 100; detenido en ~140) | 1/15 | 96.9% | 60.8% | 0.0% | — |
| FT tres pasos · ronda 1, iteración 100 | 0/15 | 96.9% | 47.3% | 4.0% | 52.7% |
| FT tres pasos · ronda 1, iteración 300 | 2/15 | 91.2% | 68.8% | 0.7% | 73.0% |
| FT tres pasos · ronda 1, iteración 500 | 6/15 | 81.7% | 40.4% | 0.0% | 89.9% |
| FT tres pasos · ronda 1, iteración 700 | 7/15 | 72.2% | 47.8% | 0.0% | 93.3% |
| FT tres pasos · ronda 2 (con repeticiones), iteración 200 | 2/15 | 91.8% | 49.2% | 0.0% | 78.1% |
| FT tres pasos · ronda 2 (con repeticiones), iteración 400 | 6/15 | 76.6% | 47.9% | 0.0% | 97.2% |
| FT tres pasos · ronda 2 (con repeticiones), iteración 800 | 8/15 | 72.2% | 36.7% | 0.0% | 99.0% |
| FT + herramienta · ronda 1, iteración 300 | 14/15 | 57.1% | 0.0% | 0.0% | 98.4% |
| FT + herramienta · ronda 1, iteración 500 | 14/15 | 57.1% | 0.0% | 0.0% | 100.0% |
| FT + herramienta · ronda 1, iteración 700 | 14/15 | 57.1% | 0.0% | 0.0% | 100.0% |
| FT + herramienta · ronda 2, iteración 400 | 14/15 | 58.0% | 0.0% | 0.0% | 98.5% |
| FT + herramienta · ronda 2, iteración 800 | 14/15 | 57.1% | 0.0% | 0.0% | 100.0% |

## La lista de compatibles que escribe el modelo

| Variante | Estado «Sé» exacto | Turnos con lista | Nombres listados compatibles | Nombres inexistentes | Primer nombre compatible | Primer nombre = política |
|---|---|---|---|---|---|---|
| Solución · fine-tuning LoRA (el juego recibe la jugada del modelo) | 97.7% | 216 | 65.0% | 1 | 39.8% | 34.3% |
| Variante · fine-tuning LoRA + consulta al roster con el «Sé» del modelo | 99.3% | 139 | 71.7% | 0 | 55.4% | 48.9% |

*Primer nombre = política*: el primer nombre de la lista es exactamente el primer campeón compatible en orden del roster, que es lo que se entrenó a jugar.

## Comparación pareada · Solución · fine-tuning LoRA (el juego recibe la jugada del modelo) contra el baseline MLX

- Resueltas sólo por la solución: **14** (Zoe, Veigar, LeBlanc, Thresh, Ashe, Xin Zhao, Lissandra, Elise, Ekko, Briar, Diana, Aatrox, Zeri, Jhin)
- Resueltas sólo por el baseline: **1** (Malzahar)
- Resueltas por ambos: 0
- McNemar exacto sobre los pares discordantes: p = 0.0009766
- Diferencia en tasa de violación (solución − baseline), IC 95 % bootstrap por objetivo: [-38.6%, -21.4%]

## Comparación pareada · Variante · fine-tuning LoRA + consulta al roster con el «Sé» del modelo contra el baseline MLX

- Resueltas sólo por la solución: **29** (Karma, Samira, Zoe, Nocturne, Veigar, LeBlanc, Morgana, Thresh, Ashe, Zilean, Xin Zhao, Tryndamere, Pantheon, Vladimir, Lissandra, Elise, Ekko, Briar, Mordekaiser, Diana, Aatrox, Zeri, Zac, Xerath, Kog'Maw, Dr. Mundo, Jhin, Soraka, Ezreal)
- Resueltas sólo por el baseline: **0** (—)
- Resueltas por ambos: 1
- McNemar exacto sobre los pares discordantes: p = 3.725e-09
- Diferencia en tasa de violación (solución − baseline), IC 95 % bootstrap por objetivo: [-52.5%, -36.9%]

## Dónde falla · Solución · fine-tuning LoRA (el juego recibe la jugada del modelo)

| Objetivo | Intentos | Violaciones | Inválidos | Repeticiones | Mejor verdes | Propuestas |
|---|---|---|---|---|---|---|
| Karma | 10 | 8/9 | 0 | 5 | 5/7 | Aatrox → Ahri → LeBlanc → Lux → Syndra → Lux → Syndra → LeBlanc → LeBlanc → Lux |
| Samira | 10 | 5/8 | 1 | 1 | 4/7 | Aatrox → Kalista → Mel → Xayah → Zeri → Neeko → Renata Glasc → Xayah → «Yinx» → Kai'Sa |
| Nocturne | 10 | 9/9 | 0 | 4 | 3/7 | Aatrox → Akali → Diana → Leona → Sejuani → Vi → Sejuani → Vi → Sejuani → Vi |
| Morgana | 10 | 6/9 | 0 | 6 | 4/7 | Aatrox → Ahri → Ashe → Nidalee → Nidalee → Nidalee → Ashe → Nidalee → Nidalee → Nidalee |
| Zilean | 10 | 6/9 | 0 | 6 | 4/7 | Aatrox → Corki → Twitch → Fiddlesticks → Twitch → Twitch → Twitch → Twitch → Twitch → Twitch |
| Tryndamere | 10 | 8/9 | 0 | 7 | 3/7 | Aatrox → Darius → Garen → Garen → Garen → Garen → Garen → Garen → Garen → Garen |
| Pantheon | 10 | 5/9 | 0 | 2 | 4/7 | Aatrox → Blitzcrank → Darius → Fizz → Lee Sin → Master Yi → Gragas → Gragas → Gragas → Alistar |
| Vladimir | 10 | 8/9 | 0 | 3 | 4/7 | Aatrox → Corki → Draven → Viktor → Swain → Swain → Swain → LeBlanc → Urgot → Viktor |
| Mordekaiser | 10 | 8/9 | 0 | 6 | 4/7 | Aatrox → Darius → Garen → Gragas → Garen → Garen → Garen → Garen → Garen → Garen |
| Zac | 10 | 9/9 | 0 | 7 | 3/7 | Aatrox → Yasuo → Yasuo → Yasuo → Lucian → Yasuo → Yasuo → Yasuo → Yasuo → Yasuo |
| Xerath | 10 | 7/9 | 0 | 4 | 4/7 | Aatrox → Corki → Draven → Graves → Viktor → Viktor → Viktor → Talon → Viktor → Viktor |
| Kog'Maw | 10 | 7/9 | 0 | 3 | 4/7 | Aatrox → Corki → Draven → Ziggs → Lucian → Twitch → Varus → Ziggs → Ziggs → Ziggs |
| Dr. Mundo | 10 | 8/9 | 0 | 7 | 4/7 | Aatrox → Blitzcrank → Warwick → Warwick → Warwick → Warwick → Warwick → Warwick → Warwick → Warwick |
| Malzahar | 10 | 8/9 | 0 | 5 | 4/7 | Aatrox → Corki → Draven → Viktor → Swain → Viktor → Swain → Viktor → Swain → Viktor |
| Soraka | 10 | 7/9 | 0 | 6 | 4/7 | Aatrox → Ahri → Ashe → Nidalee → Nidalee → Nidalee → Nidalee → Nidalee → Nidalee → Nidalee |
| Ezreal | 10 | 6/9 | 0 | 2 | 5/7 | Aatrox → Corki → Draven → Varus → Ziggs → Kog'Maw → Twitch → Kog'Maw → Karthus → Kog'Maw |
