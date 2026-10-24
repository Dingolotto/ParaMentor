# Arquitectura

```
                ┌──────────────────────────── Web (chat, editor, ruta de aprendizaje) ─┐
                │  respuesta en streaming  ·  panel de Verificación  ·  speedup chart  │
                └───────────────▲───────────────────────────────┬──────────────────────┘
                                │                               │
                           ┌────┴───────────── API ─────────────▼────┐
                           │ sesiones · nivel del usuario · caché    │
                           └────┬───────────────────────────────▲────┘
                                │                               │
     ┌──────────── Agente (agent/) ────────────────────────────────────────────┐
     │  1. Recuperar contexto (RAG)  ──►  2. Generar (LLM)  ──►  3. Verificar   │
     │         ▲                                                    │          │
     │         └──────── 4. Si falla: errores + líneas al modelo ◄──┘          │
     └──────┬──────────────────────┬─────────────────────────┬─────────────────┘
            │                      │                         │
   ┌────────▼───────┐    ┌─────────▼─────────┐     ┌─────────▼──────────┐
   │ RAG (rag/)     │    │ LLM (agent/llm.py)│     │ Verificador        │
   │ spec OpenMP,   │    │ API de frontera → │     │ gcc/clang -fopenmp │
   │ ejemplos, docs,│    │ modelo propio     │     │ 1/2/4/8 hilos      │
   │ apuntes        │    │ (v0.5+)           │     │ TSan + Archer      │
   └────────────────┘    └───────────────────┘     │ speedup            │
                                                    └─────────┬──────────┘
                                                              │ resultados verificados
                                                    ┌─────────▼──────────┐
                                                    │ data-pipeline/     │──► finetune/
                                                    │ solo lo que aprueba│
                                                    └────────────────────┘
```

## Cómo se usa el verificador en cada modo

| Modo | `seq.c` (referencia) | `par.c` (candidato) |
|---|---|---|
| **Paraleliza** | el código secuencial del usuario | la propuesta del modelo |
| **Revisa** | versión secuencial derivada por el modelo (o la del usuario si la da) | el código paralelo del usuario |
| **Aprende / ejercicios** | la referencia del ejercicio | la solución del alumno o del modelo |

## Seguridad
Ejecutar código de usuarios y de un modelo es arriesgado. Antes de abrirlo al público, cada verificación debe correr en un contenedor **sin red**, con límites de CPU, memoria y tiempo, con un sistema de ficheros efímero y con un usuario sin privilegios.
