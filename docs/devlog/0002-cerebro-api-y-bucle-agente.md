# 0002 · Cerebro por API y bucle agente

**Fecha:** 2026-10-24
**Rama:** `feat/agent-loop`

## Decisión
Se adopta la [decisión 0001](../decisiones/0001-cerebro-por-api-primero.md): un modelo de frontera por API como cerebro en v0.1 y un modelo propio a partir de la v0.5. El motivo es tener algo **útil ya** y medir con el eval-set cuándo el modelo propio está a la altura.

## Qué se ha hecho
- `agent/llm.py`: interfaz única para el modelo. Proveedores: Anthropic, cualquier endpoint compatible con OpenAI (vLLM, Ollama, OpenRouter) y `MockLLM` para tests.
- `agent/paralelizar.py`: bucle generar → verificar → corregir. El código del usuario hace de `seq.c` de referencia y la propuesta del modelo de `par.c`. Cuando falla, el modelo recibe un informe con la **línea exacta** de la carrera y el error de salida.
- Test con modelo simulado: el primer intento (sin `reduction`) se rechaza con la línea 9 señalada, el segundo aprueba. **9/9 tests OK.**
- ROADMAP rehecho con la visión completa: mentor adaptativo, visualizador de hilos, modo examen, análisis de rendimiento, MPI/GPU y plugin de IDE.

## Pendiente de medir (siguiente entrada)
- % de aprobados del cerebro por API en el eval-set, sin bucle y con bucle.
- Latencia por fase: generación, compilación, ejecución y TSan.
