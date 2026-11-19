# Revisión de etiquetas del dataset del Selector (D4)

Las etiquetas no las produce un modelo de lenguaje: salen de aplicar las reglas del juego
(`agents_d3.state.violations`) al estado público reconstruido desde el feedback del motor.
Aun así se revisan de tres maneras.

## 1. Re-verificación automática completa

`python -m agents_d4.review_data` vuelve a calcular cada veredicto con una segunda
implementación de las reglas, escrita aparte y leyendo la página tal como la ve el
Selector (`verificacion_automatica.json`):

- Ronda 1: 2.503 ejemplos, 61.885 filas re-verificadas, **0 discrepancias**.
- Ronda 2 (`--data finetune/data/d4_selector_r2 --tag _r2`): 1.340 ejemplos, 33.144 filas, **0 discrepancias**.
- En cada ejemplo, el secreto de la partida, si está en la página y no fue excluido, queda «ok».
- `candidates` coincide siempre con las filas «ok».

## 2. Revisión asistida (Claude, no humana)

Claude revisó a mano, fila por fila, los dos primeros ejemplos de `muestra.md`
(50 filas): ejemplo 2394 (amarillo `regions [["Runeterra","Shurima"]]`, Amumu
`Shurima` ok por subconjunto; Blitzcrank y Braum x regions; Alistar excluido aunque
cumple) y ejemplo 1183 (dos amarillos; Nidalee ok, Lux x regions por el verde de
Ixtal, Neeko excluida). 50/50 veredictos correctos. Esta revisión no reemplaza la del
equipo.

## 3. Revisión humana del equipo (pendiente)

`muestra.md`: 40 ejemplos estratificados (20 con amarillo difícil, 8 con amarillo,
6 con candidatos, 6 sin candidatos; semilla 4242). Pendiente: que una persona del equipo
marque ✔/✘ en la columna «Revisor» de al menos las filas «ok» y las «x» por campo
amarillo, y anote aquí nombre, fecha y resultado.

| Revisor | Fecha | Ejemplos | Filas revisadas | Errores |
|---|---|---:|---:|---:|
| (pendiente) | | | | |
