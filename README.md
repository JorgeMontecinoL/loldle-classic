# LoLdle Classic — laboratorio en Jupyter

Notebook para evaluar si un modelo local mantiene restricciones a través de varias rondas de LoLdle Classic.

## Ejecutar

1. Abre LoLdle_Classic.ipynb desde esta carpeta.
2. Usa un kernel Python 3 con Jupyter/IPython; el notebook usa solo la biblioteca estándar y la visualización integrada de IPython.
3. Inicia el servidor local de LM Studio con su API OpenAI-compatible activa, normalmente en http://localhost:1234.
4. En la primera celda define MODEL_NAME y ajusta los hiperparámetros si hace falta.
5. Ejecuta el self-check y luego cambia RUN_NOW a True en la última celda.

El notebook prueba un solo modelo por corrida. Repite la corrida con el mismo SEED y NUM_GAMES para comparar modelos en los mismos objetivos. BASE_URL apunta por defecto a http://localhost:1234/v1 y API_KEY puede ser cualquier string aceptado por LM Studio.

No se exportan resultados a archivos: la traza completa y el resumen quedan en la variable results de la sesión.

## Qwen en LM Studio

Para `qwen3.5-4b-instruct-revised`, desactiva manualmente el modo de razonamiento (Thinking/Reasoning) en LM Studio antes de ejecutar la partida. El notebook necesita que la respuesta final llegue en `content`; si el modelo consume el límite pensando y deja `content` vacío, se detiene con un error descriptivo.

## Archivos vigentes

- LoLdle_Classic.ipynb: parser del roster, motor de feedback, cliente LM Studio, loop, vista en vivo, métricas y self-check.
- data/champions_173_prompt.txt: roster congelado de 173 campeones usado por el notebook.
- data/champions_173.json: snapshot JSON preservado como artefacto existente; no es la fuente activa del notebook.

## Métricas

- Intentos inválidos y respuestas fuera de formato: total y porcentaje sobre todas las respuestas.
- Violaciones de restricción: intentos con al menos una contradicción y porcentaje sobre intentos válidos posteriores a feedback.
- Repeticiones: total de campeones repetidos dentro de una partida.
- Partidas resueltas y porcentaje de resolución.
- Promedio de intentos para acertar, calculado solo sobre partidas resueltas.

Las respuestas fuera de formato que contienen un único campeón reconocible reciben feedback y pueden resolver la partida. Las banderas de repetición y contradicción se contabilizan de forma independiente.
