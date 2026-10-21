# Entregable 3 · coordinación de tres agentes

Sistema ejecutable de **Memoria → Selector → Verificador**, con herramientas,
transferencias y ciclos de revisión decididos mediante acciones JSON del mismo
Ministral-3-3B-Instruct-2512. Continúa el fallo observado en D1/D2: omitir o
violar restricciones, buscar candidatos incorrectos y repetir jugadas.
No entrena nuevos pesos: compara el modelo base con el adaptador LoRA del D2
para elegir **una configuración común a los tres roles** usando validación.

## Ejecutar la demo

Desde la raíz del repositorio, en macOS con Apple Silicon:

```bash
# Si no existe el entorno del D2:
uv venv .venv-ft --python 3.12
uv pip install --python .venv-ft/bin/python -r agents_d3/requirements.txt

scripts/demo_d3.sh
# http://127.0.0.1:8766
```

Se inicia un servidor MLX en 8083 y la app en 8766. Se reutiliza el modelo
`mlx-community/Ministral-3-3B-Instruct-2512-4bit` del caché local; una instalación
nueva necesita descargar aproximadamente 2,78 GB. El adaptador del D2 está en
`finetune/adapters/final/`. No requiere LM Studio ni servicios de pago.
Ctrl+C detiene sólo los procesos iniciados por el script.

Si el modelo ya está servido en 8083:

```bash
USE_EXISTING_MODEL=1 scripts/demo_d3.sh
```

`MODEL_PORT`, `APP_PORT`, `NO_OPEN=1` y `D3_WEIGHTS=base|lora` permiten cambiar
puertos, evitar abrir el navegador o explorar otros pesos. La demo usa la
selección guardada si existe; antes de seleccionar usa base. Un override de
pesos en la demo no altera los resultados experimentales.

Elige un objetivo y una referencia (prompting directo o D2 LoRA). La app
juega primero con agentes y después con la referencia sobre **el mismo
objetivo**. Se ejecutan secuencialmente para no alternar adaptadores entre
peticiones concurrentes. Muestra el agente activo, consultas, críticas,
estado escrito por Memoria, respuestas completas y tableros comparables.
Seleccionar un evento muestra su entrada/salida exacta. Las partidas se
registran en `results/d3/app_runs/*.json.gz`.

Los botones «Ver fallo» reproducen **trazas guardadas**, etiquetadas de forma
visible; no llaman al modelo y no se presentan como ejecuciones en vivo.
La tabla se ordena al pulsar cualquier métrica.

## Evaluación reproducible

Mantén el servidor MLX activo. Puedes iniciarlo separado:

```bash
.venv-ft/bin/python -m mlx_lm server \
  --model mlx-community/Ministral-3-3B-Instruct-2512-4bit \
  --host 127.0.0.1 --port 8083

# En otra terminal:
scripts/eval_d3.sh valid
scripts/eval_d3.sh test
```

1. **Validación:** las mismas 15 entradas con agentes base y agentes LoRA.
   Se elige por resolución; desempates por menos paros, menor violación
   estricta y menos llamadas. `results/d3/selection.json` congela pesos,
   configuración y hashes de prompts/código antes de mirar prueba.
2. **Prueba:** los mismos 30 objetivos reservados del entrenamiento del D2,
   ya usados para medir D1/D2. No se usan para ajustar el protocolo D3.
   Se corre el sistema completo, tres ablaciones y cuatro controles.
3. **Análisis:** genera `results/d3/summary.json`, `summary.csv` y
   `ANALISIS_D3.md`, con tamaño real, ejecución completa/parcial, costes,
   paros, fallos y McNemar pareado exploratorio.

Las corridas guardan al terminar cada partida y se reanudan omitiendo sólo
partidas ya registradas. Cambios de configuración o prompts impiden reanudar
un archivo existente. No uses `--force` para reemplazar evidencia final.
No hay checkpoint a mitad de una partida; una interrupción repite esa partida.

Ejemplo de exploración **sólo en validación**:

```bash
.venv-ft/bin/python -m agents_d3.evaluate --split valid --weights base \
  --limit 2 --out results/d3/exploracion
```

Leer una traza comprimida:

```bash
.venv-ft/bin/python - <<'PY'
from agents_d3.analyze import read
from pathlib import Path
p = read(Path('results/d3/raw/test_base_full.json.gz'))
print(p['records'][0]['agent_trace'])
PY
```

El nombre final depende de los pesos seleccionados (`base` o `lora`).
Se guardan prompts efectivos, hashes, modelo, adaptador, todos los mensajes,
acciones, resultados de herramientas, latencias y uso de tokens. Temperatura
0 reduce la variación, pero diferencias de versión, caché y aritmética del
servidor pueden cambiar salidas. Una traza guardada es la evidencia exacta de
esa corrida; volver a generar no es una garantía de identidad byte a byte.

## Técnicas y ablaciones

| Variante | Cambio único |
|---|---|
| `full` | Estado explícito anterior + ejemplos por rol + crítica con revisión |
| `no_previous_state` | Sin reinyección del estado del turno anterior; conserva historial completo |
| `no_examples` | Sin ejemplos en los tres roles |
| `no_revision` | Sin devoluciones a Memoria o Selector; conserva auditoría, aprobación y parada |
| `direct` | Prompt directo del notebook, pesos base, salida completa |
| `d2_lora` | Pesos LoRA, formato de tres líneas del D2, envía última línea |
| `d2_tool` | D2 LoRA + filtro de su línea «Sé», control heredado |
| `algorithmic` | Sin modelo: reconstrucción determinista de todo el feedback y primer compatible |

Las ablaciones conservan tres roles, herramientas, modelo, objetivos y
presupuestos. No son eliminaciones acumulativas. Retirar estado anterior no
elimina el historial; mide el aporte de reinyección, no toda la memoria.

La selección tras herramientas sigue una política simple de primer candidato.
Las herramientas pueden resolver una parte importante del juego: el control
sin LLM ayuda a identificar su aporte. Tres roles no implican tres modelos
independientes ni superioridad automática frente a una sola herramienta.

## Métricas y límites

- **Resolución:** partidas resueltas / todas las partidas, incluidos paros.
- **Violación histórica:** mismo checker de D1/D2; no usa pistas amarillas.
- **Violación estricta:** incompatibilidad con todo el feedback público,
  incluidos amarillos y repetición, sobre jugadas válidas después de feedback.
- **Paros/cobertura:** indispensables si se envían pocas o ninguna jugada.
  Una tasa de violación baja puede deberse a abstención, no a jugar bien.
- **Coste:** llamadas, tokens de salida y segundos de generación por partida.
  Directo/D2 permiten 64 tokens por turno; D3 permite 768 por llamada, hasta
  18 llamadas por turno y 160 por partida. No son presupuestos iguales.
- CFS se exporta como referencia histórica; no decide el ranking de agentes
  porque los paros pueden producir puntuaciones engañosas.
- McNemar compara resolución sobre objetivos pareados; las comparaciones
  múltiples son exploratorias. Son 30 objetivos, no 30 réplicas del mismo
  prompt. No permite inferir razonamiento general ni robustez en otros juegos.

No se modifica el motor, el adaptador ni los resultados del D1/D2. El roster
local contiene 173 campeones; la evaluación no interactúa con el sitio web.
La cuantización MLX difiere del GGUF del D1. El servidor emitió una advertencia
de regex del tokenizer: se conserva la pila instalada para comparación y se
declara esta limitación; cambiarla exigiría volver a medir los controles.

## Arquitectura y evidencia

- `docs/d3/ARQUITECTURA.md`: grafo completo, frontera de información,
  herramientas, mensajes, ciclos y condiciones de parada.
- `agents_d3/prompts/`: instrucciones y ejemplos editables por rol.
- `agents_d3/runtime.py`: controlador dirigido por acciones del modelo.
- `agents_d3/state.py`: herramientas públicas, sin acceso al secreto.
- `results/d3/probes*`: exploraciones de protocolo en validación, incluidos
  formatos fallidos. No se agregan a los resultados finales.
- `results/d3/dev/`: comparación de pesos en validación.
- `results/d3/raw/`: corridas finales y ablaciones.

Para el video de hasta tres minutos: mostrar objetivo común, lanzar una
comparación real, inspeccionar una transferencia y un resultado de auditoría,
mostrar las métricas guardadas y reproducir un fallo claramente etiquetado.
No confundir un éxito aislado con la tasa medida sobre 30 objetivos.
El informe LaTeX y el video se entregan como archivos aparte del repositorio.
