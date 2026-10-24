# Decisión 0003 · Modelos locales según el hardware

**Fecha:** 2026-10-24
**Estado:** aceptada

## Hardware de desarrollo

| Pieza | Modelo | Implicación |
|---|---|---|
| CPU | Intel Core i7-13700HX: 16 núcleos (8 P + 8 E), 24 hilos | Sobra para el verificador. Los núcleos son heterogéneos, así que el speedup con más de 8 hilos no es representativo |
| RAM | 32 GB DDR5 | Permite repartir un modelo entre GPU y RAM |
| GPU | NVIDIA GeForce RTX 5060 Laptop, 8 GB GDDR7 | Ejecuta modelos de ~7 GB enteros en GPU; QLoRA de modelos pequeños en local |
| SO | Windows + WSL2 (Ubuntu) | Ollama en Windows y verificador en WSL |

## Decisión

| Rol | Modelo | Tamaño aprox. (Q4) | Motivo |
|---|---|---|---|
| **Principal (calidad)** | Qwen3.6-35B-A3B | ~21 GB | MoE con 3B parámetros activos: funciona fluido repartido entre GPU y RAM. Es la mejor calidad ejecutable en esta máquina |
| **Rápido (iteración)** | Mellum2-12B-A2.5B-Thinking | ~7 GB | Cabe entero en la GPU: ideal para pruebas y desarrollo |
| Descartado | Qwen3.6-27B (denso) | ~16 GB | Necesita 16 GB de VRAM; aquí iría casi todo en CPU |

Los tags exactos se comprueban en ollama.com/library antes de descargar. Tamaños estimados por número de parámetros.

## Pregunta central del proyecto
> ¿Un modelo **pequeño especializado** (fine-tuning con datos verificados) alcanza a uno **3 veces mayor** sin especializar en programación paralela?

- Línea base: el modelo principal, con y sin RAG y con y sin bucle agente.
- Especializado: QLoRA del modelo pequeño, en local (8 GB) para pruebas o en Kaggle (16 GB) para el entrenamiento serio.
- El árbitro es el eval-set medido con el verificador.

## Configuración

1. **Ollama en Windows** (no en WSL), para usar toda la RAM y la GPU sin el límite de memoria de WSL.
2. `C:\Users\<usuario>\.wslconfig`:
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```
   Después, `wsl --shutdown`. Así el código en WSL llega a Ollama en `localhost:11434`.
3. Variable de entorno en WSL: `export PARAMENTOR_MODEL=<tag del modelo>`.

## Ajustes pendientes en el verificador
- Medir speedup con 1/2/4/8 hilos fijados a los núcleos de rendimiento (`OMP_PLACES=cores`, `OMP_PROC_BIND=close`).
- Cerrar aplicaciones pesadas al medir: el modelo de ~21 GB y 32 GB de RAM van justos.

## Fuentes
- [Best Ollama models (BenchLM)](https://www.benchlm.ai/best/ollama-models)
- [RTX 5060 Laptop, 8 GB GDDR7 (Notebookcheck)](https://www.notebookcheck.net/GeForce-RTX-5060-laptops-GPU-unveiled-with-8-GB-GDDR7-VRAM-and-100-Watts-max-power.999887.0.html)
