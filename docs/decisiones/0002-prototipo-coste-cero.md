# Decisión 0002 · Prototipo de aprendizaje a coste 0 €

**Fecha:** 2026-10-24
**Estado:** aceptada (sustituye a la [0001](0001-cerebro-por-api-primero.md) como estrategia vigente)

## Contexto
Sin presupuesto. El objetivo principal es **aprender a crear y enfocar una IA especializada** y dejar un prototipo lo mejor posible, documentado como portfolio.

## Decisión
Todo el ciclo se hace con herramientas gratuitas:

| Paso | Cómo |
|---|---|
| Cerebro | Modelo abierto local con **Ollama** (proveedor por defecto en `agent/llm.py`) |
| Conocimiento | RAG local con embeddings abiertos |
| Fiabilidad | Verificador + bucle agente (ya hechos) |
| Especialización | **QLoRA en GPU gratuita** (Kaggle) sobre un modelo pequeño |
| Datos | Mutaciones + DataRaceBench + generación con el propio modelo local filtrada por el verificador |
| Demo | Interfaz local + vídeo + GitHub |

## Por qué no se pierde calidad de aprendizaje
El proceso es **idéntico** al de un producto real: solo cambia el tamaño del modelo. Con un modelo más modesto se ve con más claridad lo que aporta cada pieza (RAG, bucle y fine-tuning), y eso es justo lo que el proyecto quiere enseñar y medir.

## Consecuencias
- El modelo local será más lento y menos listo que uno de frontera: el bucle agente y el verificador compensan parte de esa diferencia.
- Sin web pública que ejecute código (evita coste y riesgos de seguridad).
- Pasar a la versión de pago es cambiar una variable de entorno y desplegar: el diseño no cambia.
