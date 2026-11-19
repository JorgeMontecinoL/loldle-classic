# Dónde el D4 todavía falla o empeora

Todas las trazas están en `results/d4/runs/test_v1/test_d4.json.gz` (registro `target == …`);
las del D3 reproducido, en `test_d3.json.gz` del mismo directorio.

## 1. Samira: el sistema se detiene (fallo de Memoria, no del Selector)

D4 y D3 hacen exactamente la misma partida: Aatrox, Kai'Sa y, en el turno 3, Memoria
entrega 60 veces seguidas un estado inválido hasta agotar el presupuesto (`call_limit`,
82 llamadas). El error que devuelve `validar_estado` es siempre el mismo:

```
yellow.regions: got [['Runeterra', 'Shurima'], ['Void', 'Void-Being']]; each clause must be a flat LIST of known values
```

Memoria mezcla en un amarillo de `regions` un valor de `species` (`Void-Being`, de la pista de
Kai'Sa). El estado nunca llega al Selector, así que ajustar el Selector no puede corregirlo.
El reintento de Memoria cambia la semilla y la temperatura (0,6), pero repite el mismo error.
Es el mismo fallo que el D3 documentó para Samira.

## 2. Elise: resuelve, pero peor que el D3 (degradación del Selector)

| | Jugadas | Intentos incompatibles | Llamadas |
|---|---|---:|---:|
| D3 reproducido | Aatrox, Ahri, **Elise** | 0 | 30 |
| D4 | Aatrox, Ahri, Caitlyn, Lulu, **Elise** | 2 | 50 |

Paso a paso (llamadas del Selector D4 con la página de Elise):

1. Turnos 2 y 3: el estado admite años ≤ 2012 (`year.lt = 2013`) y Elise es de 2012, pero el
   Selector D4 escribe «Elise x release_year» y la descarta.
2. Turno 3: en la página 1 acepta a Caitlyn (2011), que rompe `year.gt = 2011`. El
   Verificador (adaptador del D3) la aprueba y se juega un intento incompatible.
3. Turno 4: con `species [["Human"]]`, el Selector D4 descarta a Elise (`Human, Magically
   Altered`, que sí cumple) y acepta a Lulu (`Yordle`, que no comparte nada). El Verificador
   vuelve a aprobar el error.
4. Turno 5: Elise se lista bien y se acierta.

**Por qué.** La ronda 2 concentró los ejemplos en amarillos de `positions` y `regions`, y
dejó pocos casos de límites de año y de `species`, que el adaptador del D3 ya resolvía. El
Selector D4 ganó en lo entrenado y perdió algo de lo que no se repasó. Con LeBlanc, Kog'Maw
y Ezreal pasa lo mismo, en menor grado: necesitan una jugada más que el D3.

## 3. Turno 1: estado vacío (degradación del Selector aislado)

Con el estado vacío que Memoria entrega al empezar (`year` con `eq/gt/lt` en `null`), el
Selector D4 conserva las 25 filas en las páginas 1, 2, 5 y 7, pero **descarta todas** en
las páginas 3 y 4 y 24 de 25 en la 6, escribiendo «x release_year» o «x range_type» sin que
el estado lo pida. En partida no cambia la jugada (el controlador toma Aatrox de la página
1, como el D3), pero explica 50 de los 65 compatibles que el D4 deja fuera en `test_generado`.
La ronda 2 no tenía ningún estado vacío.

## 4. Entradas exactas del D3 que siguen fallando

Sobre las mismas entradas de la traza del D3 (`results/d4/demo_cases.json`), el D4 corrige
Ashe y Thresh, pero en Soraka (`regions [["Ionia"]]`) sigue descartando al secreto y en
Morgana deja de descartarla por `positions` para descartarla por año. En las partidas
completas el D4 resuelve las cuatro porque llega a otros estados.

## Qué haría falta

Una ronda de repaso con estados vacíos, límites de año y `species`, mezclada con la ronda 2,
y el Verificador sigue siendo el del D3: aprueba errores del Selector (Caitlyn, Lulu).
