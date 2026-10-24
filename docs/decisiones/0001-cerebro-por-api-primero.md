# Decisión 0001 · Cerebro por API primero, modelo propio después

**Fecha:** 2026-10-24
**Estado:** aceptada

## Contexto
El objetivo es que ParaMentor sea **el mejor asistente en programación paralela**: que razone problemas difíciles en segundos, paralelice y corrija código de forma fiable y sirva de mentor desde principiantes hasta profesionales.

Un modelo abierto de 7-32B, aunque esté ajustado, no razona mejor en general que los modelos grandes de frontera. Empezar por él retrasaría meses tener algo útil.

## Decisión
1. **v0.1-v0.4**: el "cerebro" es un **modelo grande por API**. ParaMentor añade lo que ese modelo no tiene: RAG especializado, verificador y bucle de autocorrección.
2. **v0.5+**: se entrena un **modelo abierto propio** (LoRA/QLoRA) con los datos que el sistema ha ido verificando. Se compara contra el cerebro por API en el eval-set y se usa donde gane o empate: coste, privacidad, ejecución local, uso offline en universidades.
3. El código **no depende de ningún proveedor**: `agent/llm.py` abstrae el modelo (API de Anthropic, cualquier endpoint compatible con OpenAI como vLLM, Ollama u OpenRouter, o un modelo simulado para tests).

## La ventaja real
La ventaja de ParaMentor no está en el tamaño del modelo, sino en el sistema completo:

```
modelo potente + RAG especializado + verificador + bucle de autocorrección + datos verificados
```

Los modelos generalistas no comprueban lo que dicen. ParaMentor no da por buena una paralelización hasta que compila, da el resultado correcto, no tiene carreras y escala.

## Latencia: "en segundos"
- La respuesta del modelo llega en *streaming* en 1-5 s.
- La verificación (compilar, ejecutar con 1/2/4/8 hilos y pasar TSan) llega justo después, en unos 2-5 s, y rellena el panel "Verificación" de la interfaz.
- Si la verificación falla, el bucle agente corrige automáticamente y avisa: "corregido tras detectar una carrera en la línea 9".
- Optimizaciones previstas: compilar en paralelo, una caché por hash de código, entradas pequeñas para TSan y workers de verificación precalentados.

## Consecuencias
- Hay coste por uso de API desde el principio: se necesita límite por usuario y caché.
- Antes de usar salidas de un modelo como datos de entrenamiento hay que revisar los términos de uso del proveedor.
- El eval-set es el árbitro: cada cambio de modelo, prompt o RAG se mide contra él.
