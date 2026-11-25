# Bitácora del Entregable 4 (decisiones de desarrollo, en orden)

Fecha: 17 de noviembre de 2026. Equipo: Apple M5 Pro, 64 GB, mlx-lm 0.31.3, un servidor
`mlx_lm server` en el puerto 8083 con el modelo base; los adaptadores viajan por petición.

1. **Referencia fijada.** Rama `entregable-4` desde `origin/main` (merge del D3, código de
   agentes igual a `10da2ec`). `agents_d3.select.source_hashes()` coincide con
   `results/d3/selection.json` y el SHA-256 de `d3_paginas_cot3` coincide con el registrado.
2. **Prueba pequeña.** Cuatro llamadas reales del Selector del D3 (Morgana, turno 4)
   reejecutadas con `d3_paginas_cot3`: idénticas byte a byte. Después, 77/77 salidas a
   temperatura 0 de la validación del D3 también idénticas.
3. **Diagnóstico** (`agents_d4/diagnose_d3.py`) sobre la traza de prueba del D3, como pedía
   el encargo: el Selector descarta al secreto bajo amarillos de un valor o de subconjunto.
4. **Datos de la ronda 1** (`make_data_d4.py`, semilla 4040): 2.503 ejemplos.
5. **Prueba de prompting** (sólo validación, pesos D3): un ejemplo resuelto de amarillos
   no mejora (12→11 de 20 compatibles en `d3_valid_trace[amarillo]`; 34→32 de 47 en
   `valid_generado[amarillo]`).
6. **Ronda 1** (lr 2e-5 desde `d3_paginas_cot3`). La pérdida de validación subió de 0,028
   a 0,062 (iteración 250) y volvió a 0,030 (iteración 1000). **Desviación declarada:**
   para vigilarla se ejecutaron los puntos de control 500 y 1000 sobre las cinco entradas
   de demo, que vienen de la traza de **prueba** del D3 (Morgana, Ashe, Soraka, Thresh y
   Mordekaiser). Ambos seguían descartando a los cuatro secretos. Con eso y con el
   recuento por campo del D3 (en validación acierta `species [["Human"]]` y falla en
   `positions`/`regions`) se decidió detener la ronda 1 en la iteración 1050 y entrenar
   una ronda 2 concentrada. Esas cinco entradas de prueba no se usan para elegir el punto
   de control; desde aquí los controles intermedios usan sólo entradas de validación
   (`results/d4/valid_probe_cases.json`).
   La ronda 1 se guardó en `finetune/adapters/d4_selector/` y se renombró a
   `d4_selector_r1/` (su log conserva la ruta original; la config ya apunta a la nueva).
7. **Ronda 2** (`make_data_d4.py --ronda 2`, semilla 4060, 1.340 ejemplos; lr 1e-5 desde el
   punto de control 1000 de la ronda 1).
8. **Elección del adaptador**: regla fija de `agents_d4/select_checkpoint.py`, sólo con
   validación, entre ronda 1 paso 1000, ronda 2 paso 670 y ronda 2 final.
9. **Infraestructura de las partidas.** La primera partida del D3 reproducido (Karma) dio las
   mismas jugadas que la traza histórica pero 3,3 veces más lenta. Dos causas: (a) desde las
   13:50 corría en el mismo equipo otro experimento del usuario con un modelo de 12B
   (`e7_mecanismo.py`), que comparte la GPU durante toda esta sesión, incluido el
   entrenamiento; (b) `mlx_lm server` recarga el modelo cada vez que cambia el adaptador de la
   petición, lo que penalizaría sólo al D4 (alterna adaptadores entre roles). Se descartó esa
   corrida parcial (`results/d4/runs/descartadas/`), se levantó un servidor por adaptador
   (`scripts/servers_d4.sh`; salidas verificadas idénticas byte a byte a la traza del D3 y al
   envío por petición). Las tres primeras partidas (Karma y Samira del D3, Karma del D4) se
   jugaron alternadas; como así tomaba ~8 h, el resto se jugó con D3 y D4 **en paralelo**,
   cada uno contra su servidor (`scripts/d4_games.sh`), de modo que ambos comparten las
   mismas condiciones de la máquina. Los tiempos reproducidos sólo son comparables entre sí,
   no con los históricos del D3.
10. **Prueba**: Selector aislado (base, D3, D4) y partidas completas (D1, D2, D3 reproducido,
   D4, control) con `RUN_ID=test_v1`, una sola vez, con el adaptador ya elegido. El D3
   reproducido da las mismas jugadas y cifras que el histórico (25/30, 10/65 incompatibles).
11. **Hugging Face.** `MatiasCaamano/loldle-d4-selector-lora`, público. Descarga sin sesión:
   SHA-256 idéntico; 40/40 salidas del Selector idénticas en `test_generado`; Morgana y Elise
   con el adaptador descargado repiten jugadas y número de llamadas (`results/d4/hf_verify.json`).
12. **Demo.** `scripts/demo_d4.sh` probado en vivo: D4 con Ashe, 5 jugadas, 50 llamadas
   (`results/d4/app_runs/`). En la entrada exacta de Morgana de la traza del D3 el D4 todavía
   descarta a Morgana (ahora por año), así que el video usa la de Ashe.

Los 30 secretos de prueba ya se habían observado en el D1–D3 y sus trazas guiaron el
diagnóstico; los resultados de prueba no son una medida independiente de generalización.
Para eso se reporta además `test_generado`: estados nuevos de los 30 secretos de prueba,
generados con otra semilla y nunca entrenados.
