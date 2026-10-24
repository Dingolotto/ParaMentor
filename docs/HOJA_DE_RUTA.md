# Hoja de ruta estratégica de ParaMentor

> Este documento responde a **qué hacemos primero, cómo se crea y alimenta la IA, dónde se aloja y cómo se le ponen límites**. El detalle de funcionalidades está en [ROADMAP.md](../ROADMAP.md).
>
> Revisado: octubre de 2026.

---

## 1. Resumen en 30 segundos

1. **No empezamos creando la IA.** Empezamos por lo que decide si la IA es buena: el **verificador** (hecho) y el **conjunto de evaluación** (siguiente).
2. Después lanzamos un **producto útil** con un modelo de frontera por API + RAG + verificador + barreras. Ya es mejor que un chat genérico porque comprueba lo que dice.
3. Mientras la gente lo usa, acumulamos **datos verificados**. Con ellos **entrenamos nuestro modelo** (fine-tuning de un modelo abierto) y lo comparamos con el de la API.
4. El modelo propio se aloja y se sirve **solo cuando el eval-set demuestra que está a la altura**.

```
 Fase 1            Fase 2                  Fase 3                     Fase 4
 Medir      ──►    Producto con API  ──►   Modelo propio       ──►    Escalar
 (eval-set)        (web pública v0.1)      (fine-tuning + datos)      (MPI, GPU, IDE, universidades)
```

---

## 2. ¿Cómo se crea una IA? (y cuál es la nuestra)

Hay tres niveles. Solo tiene sentido hacer los dos últimos:

| Nivel | Qué es | Coste | ¿Lo hacemos? |
|---|---|---|---|
| **Pre-entrenamiento desde cero** | Enseñar a un modelo a "hablar y programar" leyendo billones de palabras | Millones de euros y meses de miles de GPUs | ❌ No: nadie a nuestra escala lo hace |
| **Fine-tuning (LoRA/QLoRA)** | Coger un modelo abierto que ya programa bien y ajustarlo con miles de ejemplos nuestros para que trabaje como queremos | Horas en una GPU alquilada, decenas de euros | ✅ Fase 3 |
| **RAG + agente + herramientas** | Sin reentrenar: darle en cada pregunta la documentación relevante, dejarle ejecutar y comprobar su código y que se corrija | Coste de uso del modelo | ✅ Desde ya |

**Nuestra IA = modelo base + LoRA propio + RAG + verificador + bucle agente + barreras.** El "cerebro" se puede cambiar; lo que es nuestro y difícil de copiar son los **datos verificados, el eval-set, el verificador y el diseño pedagógico**.

### Qué es LoRA, en una frase
En vez de modificar los miles de millones de parámetros del modelo, se entrenan unas pequeñas matrices "adaptador" (un ~0,1-1 % del tamaño) que se suman encima. QLoRA hace lo mismo con el modelo comprimido a 4 bits, así que cabe en una sola GPU.

### Qué aprende cada pieza

| Pieza | Aporta | Ejemplo |
|---|---|---|
| Modelo base | Saber programar en general | Escribir C correcto |
| **Fine-tuning** | **Cómo** responder: formato, tono de mentor, hábitos | Detectar siempre la reducción, explicar el porqué, adaptar el nivel |
| **RAG** | **Qué** sabe: conocimiento exacto y actualizable | La regla de la especificación sobre `lastprivate` |
| Verificador + agente | **Fiabilidad** | No entregar código con carreras |

Regla de oro: **el conocimiento no se mete con fine-tuning, se mete con RAG.** Es más barato, se actualiza sin reentrenar y permite citar la fuente.

---

## 3. ¿En qué modelo nos basamos?

### Fases 1-2: cerebro por API
Un modelo de frontera (Anthropic u otro), configurable en `agent/llm.py`. Razona mejor que cualquier modelo que podamos ejecutar nosotros y nos permite tener algo útil ya.

### Fase 3: modelo abierto propio
Requisitos: licencia que permita uso comercial, bueno en código, que quepa en **una** GPU con QLoRA.

Candidatos a fecha de octubre de 2026 (la lista cambia cada pocos meses, **se decide midiendo en nuestro eval-set**, no por rankings):

| Candidato | Tamaño | Licencia | Por qué |
|---|---|---|---|
| Qwen3.8-27B | 27B denso | Apache-2.0 | La mejor opción actual para una sola GPU en programación agéntica |
| Qwen3.6-27B | 27B denso | Apache-2.0 | Alternativa probada |
| Qwen3.6-35B-A3B | 35B MoE (3B activos) | Apache-2.0 | Muy barato por token: ideal para servir |
| Gemma 4 (variantes pequeñas) | 2-12B | Apache-2.0 | Para experimentos rápidos y ejecución local/offline |

Plan: primeros experimentos con un modelo **pequeño** (barato y rápido de iterar). El serio, con uno de ~27B.

---

## 4. ¿Cómo se alimenta la IA?

### 4.1 Conocimiento (RAG): lo que debe *saber*

```
Fuentes ─► trocear por sección ─► embeddings ─► Postgres + pgvector (Supabase) ─► top-k en cada pregunta ─► respuesta con cita
```

| Fuente | Uso | Ojo con |
|---|---|---|
| Especificación OpenMP 6.0 (nov 2024, con errata en nov 2025) | Reglas exactas de cada directiva y cláusula | Copyright de OpenMP: indexar para uso interno y citar; no redistribuir el PDF |
| Documento de ejemplos OpenMP 6.0/6.0.1 | Ejemplos canónicos | Igual |
| Tutoriales de centros HPC (LLNL, etc.) | Explicaciones didácticas | Licencia de cada uno |
| **Apuntes y ejercicios propios** | Estilo docente en español | El activo más valioso |

Cuando salga la 6.1 (ahora en borrador de comentarios), se reindexa y listo. Esa es la ventaja de RAG.

### 4.2 Comportamiento (fine-tuning): cómo debe *trabajar*

Formato: un fichero JSONL con conversaciones (`usuario → respuesta ideal`). Objetivo: **2.000-10.000 ejemplos de calidad**, mejor pocos y verificados que muchos y dudosos.

| Fuente de ejemplos | Cómo | Valor |
|---|---|---|
| **DataRaceBench** (LLNL, licencia BSD) | Microbenchmarks OpenMP etiquetados con carrera y sin carrera | Oro para el modo **Revisa** y para evaluar |
| **Mutaciones automáticas** | Coger código correcto y romperlo a propósito: quitar `reduction`, cambiar `private` por `shared`, añadir `nowait`, crear una dependencia. El fallo queda etiquetado | Miles de trampas con la respuesta conocida |
| **Generación sintética filtrada** | El modelo de la API resuelve ejercicios y **solo se guardan los que aprueba el verificador** | Volumen; revisar los términos de uso del proveedor |
| **Uso real (con permiso)** | Conversaciones de usuarios que acaban en código verificado | Lo más realista |
| **Pares de preferencia** | Para el mismo problema, una respuesta que aprueba y otra que suspende | Entrenamiento por preferencias (DPO): el modelo aprende a preferir lo correcto |

El verificador es lo que convierte datos baratos en **datos fiables**.

---

## 5. Barreras: que no se salga de lo que se le pregunta

Sí, hacen falta. Ahorran dinero, tiempo y evitan respuestas absurdas. Pero **no deben ser tan rígidas** que rechacen preguntas legítimas cercanas (C, compiladores, arquitectura de computadores, rendimiento, Linux para HPC).

| Capa | Qué hace | Cuándo |
|---|---|---|
| **1. Filtro de alcance** | Clasifica cada pregunta como *dentro* (paralela/HPC), *adyacente* (C, arquitectura, rendimiento) o *fuera*. Si está fuera, responde con una frase amable y redirige. Usa un modelo pequeño y barato o embeddings | Fase 2 |
| **2. Prompt de sistema** | Define rol, alcance, formato y "si no lo sabes, dilo" | Ya (`agent/paralelizar.py`) |
| **3. Búsquedas acotadas** | Primero RAG. Web solo si RAG no cubre, y solo en **dominios permitidos** (openmp.org, llnl.gov, documentación de gcc/clang, centros HPC). Máximo N búsquedas por pregunta | Fase 2 |
| **4. Presupuestos** | Máximo 3 intentos de autocorrección, tiempo límite por verificación, máximo de tokens y coste por usuario y día | Ya, en parte (`max_intentos`, `TIMEOUT_S`) |
| **5. Sandbox** | El código se ejecuta en un contenedor sin red, con límites de CPU, memoria y tiempo, y usuario sin privilegios | **Obligatorio antes de abrirlo al público** |
| **6. Anti-inyección** | El código y los ficheros del usuario son **datos**: si un comentario dice "ignora tus instrucciones", no se obedece | Fase 2 |
| **7. Honestidad en la salida** | Nunca marca "verificado" sin verificador. Si TSan no está disponible o el caso no es comprobable, lo dice | Ya |
| **8. Fine-tuning** | El modelo propio aprende también a redirigir lo que está fuera de alcance | Fase 3 |

---

## 6. ¿Dónde se aloja?

| Fase | Componente | Dónde | Coste orientativo* |
|---|---|---|---|
| 1 | Todo | Tu PC (Linux/WSL) + API del modelo | Uso de API: pocos €/mes en desarrollo |
| 2 | Frontend (web) | Vercel o Netlify | Gratis en plan básico |
| 2 | Backend (API) + verificador | **VPS con Docker** (Hetzner, OVH...). No vale serverless: hay que ejecutar gcc/clang y contenedores sandbox, y medir speedup con núcleos dedicados | ~5-20 €/mes |
| 2 | Base de datos, usuarios, pgvector para RAG | **Supabase** (ya lo controlas) | Gratis al principio |
| 2 | Cerebro | API del proveedor | Por uso: con límites y caché |
| 3 | Entrenamiento | GPU alquilada por horas (RunPod, Vast.ai, Lambda...). 48 GB van holgados para QLoRA de ~27B | Decenas de € por entrenamiento |
| 3 | Servir el modelo propio | GPU serverless que cobra por segundo (Modal, RunPod Serverless) con vLLM; o versión cuantizada en local con Ollama para demos | Por uso; cero cuando nadie lo usa |
| 4 | Escala | Varios workers de verificación + modelo propio + API de frontera para lo difícil (enrutado híbrido) | Según tráfico |

\* Precios orientativos: comprobar antes de contratar. Desglose completo en [COSTES.md](COSTES.md).

---

## 7. Fases, con criterio de salida

Cada fase termina cuando se cumple su criterio, no por fecha. Las fechas son aproximadas para alguien que estudia a la vez (respetando exámenes).

### Fase 0: cimientos ✅ (octubre de 2026)
Verificador, bucle agente, capa de modelo, tests y repo.

### Fase 1: medir (noviembre-diciembre de 2026)
- Eval-set de **50 ejercicios** propios + una selección de DataRaceBench.
- Generador de **mutaciones** (trampas automáticas).
- Medición: % de aprobados del modelo de la API **sin** y **con** bucle agente.
- ✅ **Sale cuando:** tenemos números reales y una entrada de devlog que los explica.

### Fase 2: producto v0.1 (enero-marzo de 2027)
- RAG sobre especificación + ejemplos + apuntes, con citas.
- Modos Paraleliza y Revisa por API, con streaming + verificación asíncrona.
- Barreras 1-6.
- Web siguiendo el Figma, VPS con sandbox y Supabase.
- ✅ **Sale cuando:** 5-10 compañeros la usan para estudiar paralela, con más del 90 % de respuestas verificadas sin fallos en el eval-set.

### Fase 3: modelo propio v0.5 (abril-junio de 2027)
- Dataset de 2.000+ ejemplos verificados.
- QLoRA sobre el modelo base elegido midiendo en el eval-set.
- Comparativa honesta contra la API y publicación en el devlog.
- ✅ **Sale cuando:** el modelo propio + bucle iguala a la API en Fundamentos/Intermedio a menor coste. Entonces se activa el enrutado híbrido.

### Fase 4: escalar (verano de 2027 en adelante)
Nivel Avanzado, MPI, GPU, plugin de IDE y propuesta a universidades y centros HPC.

---

## 8. Lo que **no** hacemos (para no perder tiempo)

- Entrenar desde cero.
- Meter conocimiento por fine-tuning.
- Entrenar el modelo propio antes de tener eval-set y datos verificados.
- Alojar una GPU 24/7 sin usuarios.
- Abrir la ejecución de código al público sin sandbox.
- Elegir modelo por rankings de internet en vez de por **nuestro** eval-set.

---

## Fuentes
- [Best Open Source LLMs 2026 (morphllm)](https://www.morphllm.com/best-open-source-llm)
- [DataRaceBench (LLNL, GitHub)](https://github.com/LLNL/dataracebench)
- [Especificaciones OpenMP](https://www.openmp.org/specifications/)
