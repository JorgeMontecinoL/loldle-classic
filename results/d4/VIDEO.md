# Video del Entregable 4 · recorrido para grabar (≤ 3:00)

**Grabado:** [`docs/d4/videoD4.mp4`](../../docs/d4/videoD4.mp4) (2:08, 1440×900, sin audio), regrabado el
25-11-2026 con la ficha del Selector simplificada para quien no conoce el juego. Se capturó la pestaña de Chrome con el screencast del protocolo de
depuración (sin grabar la pantalla), en una sola toma y siguiendo este guion; los rótulos de abajo se agregan dentro de
la página durante la grabación. Las partidas de Thresh son en vivo: D3 se detiene por `call_limit` (2 intentos,
80 llamadas, 162 s) y D4 acierta en 3 intentos (30 llamadas, 60 s), como en `test_v1`. Los tramos largos se aceleraron
al montar (×4 Selector, ×6 D3, ×3 D4, ×2 traza de Samira) y el rótulo lo indica.

Para volver a grabarlo a mano basta con seguir el guion (⇧⌘5 en macOS). Todo lo que se muestra es real: la interfaz llama al
sistema (servidor MLX + adaptadores del repositorio) o reproduce trazas guardadas,
rotuladas como tales.

## Preparación (fuera de cámara)

```bash
scripts/demo_d4.sh          # servidor MLX en 8083 + interfaz en http://127.0.0.1:8767
```

Esperar a que el selector «Sistema B» muestre «D4 · Selector con adaptador propio · En vivo».
Ventana del navegador a pantalla completa (≥ 1400 px de ancho, para ver los dos tableros
lado a lado). Grabar con ⇧⌘5 → «Grabar pantalla completa».

## Guion

| Tiempo | Qué hacer | Qué se ve |
|---|---|---|
| 0:00–0:15 | Encabezado | Memoria → Selector (ajustado) → Verificador; el secreto sólo lo usa el motor. |
| 0:15–1:05 | Sección «Selector base frente a ajustado», caso **Ashe · turno 4 · página 1/7** → «Ejecutar base, D3 y D4». | Pensado para quien no conoce el juego: arriba, la tarea en una frase y las pistas en palabras (mujer, maná, a distancia, posición incluye Bottom, año 2009); por columna, una frase de veredicto y una grilla de los 25 nombres (verde = se queda, gris = descarta, rojo = error, borde dorado = el secreto). Base: se queda con Ashe y 6 que no cumplen. D3: descarta a Ashe. D4: se queda sólo con Ashe. Los 25 veredictos con su regla quedan plegados en «Ver los 25 veredictos». (Con la entrada de Morgana el D4 todavía la descarta, por año: ver `results/d4/FALLOS_D4.md`.) |
| 1:05–2:25 | Arriba: secreto **Thresh** (o Morgana), Sistema A = D3, Sistema B = D4 → «Jugar A y luego B». Abrir el panel «Agentes» del tablero B. | Filas del tablero al ritmo del motor, colores por atributo, flechas del año; agente activo y cada mensaje (estado de Memoria, página y veredictos del Selector, decisión del Verificador); acierto, intentos, llamadas, tiempo y motivo de parada. |
| 2:25–2:50 | Caso de falla del D4: secreto **Samira**, «Ver una partida guardada» → `results/d4/runs/test_v1/test_d4.json.gz` → «Reproducir en A». | Traza guardada, rotulada; Memoria repite 60 veces un estado inválido (`Void-Being` en `regions`) y se detiene por `call_limit` (ver `results/d4/FALLOS_D4.md`). |
| 2:50–3:00 | Tabla «Resultados con procedencia». | Histórico (D3) frente a reproducido (D4), mismos 30 secretos. |

Si una partida en vivo no reproduce la evaluación (las corridas a temperatura 0
pueden variar), decirlo en pantalla y mostrar la traza guardada del mismo secreto.

Prueba del 18-11-2026 (en vivo, sin otros procesos en la GPU): con Thresh el D3 no
resuelve (Aatrox, Lucian; `call_limit`, 80 llamadas, 157 s) y el D4 acierta en 3 intentos
(30 llamadas, 60 s), igual que en `test_v1`. Son unos 3,5 min en total: en el video,
acelerar la partida del D3 (×4) o cortarla después de mostrar que el Selector rechaza
todas las páginas. Los valores por defecto de la interfaz ya son Thresh, el caso
`ashe-t4-p1` y la traza `results/d4/runs/test_v1/test_d4.json.gz`.

## Entradas y trazas usadas

- Caso del Selector: `results/d4/demo_cases.json`, id `ashe-t4-p1` (de `results/d3/raw/test_paginas_full.json.gz`).
- Partidas en vivo: se guardan en `results/d4/app_runs/` con hora y sistema.
- Evaluación de prueba: `results/d4/runs/test_v1/`.

Tras subir el video, pegar el enlace en `README.md` (sección del Entregable 4) y en `\videourl` de `D4.tex`.
