# Presupuesto de ParaMentor

## Prototipo de aprendizaje: **0 €** (vigente)

| Pieza | Herramienta gratuita |
|---|---|
| Modelo | Ollama en tu PC |
| Verificador, eval-set, RAG | Tu PC (Linux/WSL), base vectorial local |
| Fine-tuning | Kaggle (GPU de 16 GB, ~30 h/semana), Colab gratis, Lightning AI (15 créditos/mes) |
| Publicar modelo | Hugging Face Hub |
| Escaparate | GitHub + GitHub Pages + vídeo demo |

Único "coste": tiempo y la electricidad del PC.

---

# Ampliación opcional de pago (solo si algún día hay usuarios o financiación)

> Precios consultados en octubre de 2026. Para simplificar se toma 1 $ ≈ 1 € como margen de seguridad. Todo es **orientativo**: revisar antes de contratar.

## Precios de referencia

| Concepto | Precio |
|---|---|
| Claude Haiku 5.5 (API) | $0,10 / $0,50 por millón de tokens (entrada / salida) |
| Claude Sonnet 5.5 (API) | $2 / $10 por millón |
| Claude Opus 5.5 (API) | $4 / $20 por millón |
| Batch API | −50 % (para evaluaciones y generación de datos) |
| Caché de prompt (lectura) | 5-10 % del precio de entrada |
| VPS Hetzner CPX22 (2 vCPU compartidas, 4 GB) | 19,99 €/mes |
| VPS Hetzner CPX32 (4 vCPU compartidas, 8 GB) | 35,99 €/mes |
| VPS Hetzner CCX23 (4 vCPU **dedicadas**, 16 GB) | 86,49 €/mes |
| GPU RunPod RTX A6000 48 GB | $0,59/h (pod) · $1,22/h (serverless) |
| GPU RunPod RTX 4090 24 GB | $0,89/h (pod) |
| Supabase | Gratis (500 MB, se pausa tras 1 semana sin uso) · Pro $25/mes |
| Vercel (frontend) | Gratis (plan Hobby, uso no comercial) |

## Coste por pregunta (estimación)

Supuesto: ~6.000 tokens de entrada (sistema + RAG + código) y ~1.500 de salida por intento, con 1,5 intentos de media gracias al bucle.

| Modelo | Por intento | Por pregunta (×1,5) |
|---|---|---|
| Haiku 5.5 | ~0,0014 $ | **~0,002 $** |
| Sonnet 5.5 | ~0,027 $ | **~0,04 $** |
| Opus 5.5 | ~0,054 $ | ~0,08 $ |

**Enrutado para ahorrar:** filtro de alcance y explicaciones sencillas con Haiku, paralelizar y revisar con Sonnet, Opus solo si Sonnet falla 2 veces. Media estimada: **~0,015-0,02 $ por pregunta**. Un usuario intensivo (100 preguntas/mes) cuesta **~2 $/mes**.

## Coste por fase

| Fase | Duración | Infraestructura | API / GPU | Total fase |
|---|---|---|---|---|
| **1. Medir** | 2 meses | 0 € (tu PC) | Evaluaciones: ~2-4 $ por pasada completa de 50 ejercicios × ~10 pasadas | **~20-50 €** |
| **2. Producto** | 3 meses | VPS 20-36 €/mes + dominio ~1 €/mes + Supabase 0 € | 1.000-2.000 preguntas/mes ≈ 20-40 $/mes | **~130-230 €** |
| **3. Modelo propio** | 3 meses | Lo de la fase 2 | Generación de datos con Batch API ~50-100 $ + entrenamientos QLoRA (~40 h de A6000) ~25-50 $ | **~200-380 €** |
| **Total primer año** | | | | **~350-650 €** |

### Escenario ultra-mínimo (~200-250 € el primer año)
- Todo en local hasta tener usuarios reales.
- Haiku por defecto y Sonnet solo para el modo Paraleliza.
- Supabase gratis y VPS CPX22.
- Un solo entrenamiento QLoRA con un modelo pequeño.

### Lo que NO se paga hasta que haga falta
- **CPU dedicada (86 €/mes)**: con vCPU compartidas el speedup sale ruidoso. Al principio se muestra como "orientativo" y se priorizan corrección y carreras. Se pasa a dedicada cuando haya usuarios que dependan de ese dato.
- **Supabase Pro (25 $/mes)**: cuando la web sea pública y no pueda pausarse.
- **Servir el modelo propio**: solo si gana en el eval-set. Con GPU serverless se paga solo cuando hay uso.

## Formas de bajar más el coste
- Créditos para estudiantes (p. ej. GitHub Student Developer Pack) y programas de créditos de proveedores cloud y de IA: comprobar cuáles están vigentes.
- Caché de respuestas por hash del código: la misma duda de clase la paga una sola vez.
- Batch API para todo lo que no es en tiempo real (evaluaciones, generación de datos): −50 %.
- Modelo de embeddings abierto ejecutado en el propio VPS: 0 € en embeddings.
- Límite diario por usuario desde el primer día.

## Viabilidad
Si un usuario cuesta ~1-2 €/mes, un plan de **3-5 €/mes** o una **licencia para una universidad** cubre de sobra los costes. La parte cara (entrenar) es puntual, no mensual.
