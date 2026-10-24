# Hoja de ruta estratégica de ParaMentor

> Este documento responde a **qué hacemos primero, cómo se crea y alimenta la IA, dónde se aloja y cómo se le ponen límites**. El detalle de funcionalidades está en [ROADMAP.md](../ROADMAP.md).
>
> Revisado: octubre de 2026.

---

## 1. Resumen en 30 segundos

> **Modo vigente: prototipo de aprendizaje a coste 0 €** ([decisión 0002](decisiones/0002-prototipo-coste-cero.md)). Se recorre el proceso completo de crear una IA especializada sin gastar dinero. La versión de pago (API de frontera, VPS, web pública) queda documentada como **ampliación opcional** para el futuro.

1. **No empezamos creando la IA.** Empezamos por lo que decide si es buena: el **verificador** (hecho) y el **conjunto de evaluación** (siguiente).
2. **Línea base**: un modelo abierto **local** (Ollama) + RAG + verificador + bucle agente. Medimos.
3. **Fine-tuning gratis** (QLoRA en GPU gratuita de Kaggle) con datos verificados. Volvemos a medir: *la mejora medida es el resultado del proyecto*.
4. **Demo local** con la interfaz del Figma + vídeo/GIF y devlog en GitHub como portfolio.

```
 Fase 1          Fase 2                    Fase 3                      Fase 4
 Medir    ──►    Línea base local   ──►    Fine-tuning gratis   ──►    Demo + portfolio
 (eval-set)      (Ollama + RAG + bucle)    (Kaggle, QLoRA)             (web local, vídeo, devlog)
```

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

### Fases 1-2: modelo abierto local (0 €)
Se ejecuta en tu PC con **Ollama**, ya soportado en `agent/llm.py` como proveedor por defecto. El tamaño depende de tu hardware (RAM y GPU): se elige con los datos de la sección "Datos pendientes" del contexto. Será menos listo que un modelo de frontera, y **eso es parte del aprendizaje**: medir cuánto compensan el RAG, el bucle agente y el fine-tuning.

*Ampliación opcional de pago:* cambiar a una API de frontera es una variable de entorno (`PARAMENTOR_PROVIDER=anthropic`).

### Fase 3: modelo abierto propio
Requisitos: licencia que permita uso comercial, bueno en código, que quepa en **una** GPU con QLoRA.

Candidatos a fecha de octubre de 2026 (la lista cambia cada pocos meses, **se decide midiendo en nuestro eval-set**, no por rankings):

| Candidato | Tamaño | Licencia | Por qué |
|---|---|---|---|
| Qwen3.8-27B | 27B denso | Apache-2.0 | La mejor opción actual para una sola GPU en programación agéntica |
| Qwen3.6-27B | 27B denso | Apache-2.0 | Alternativa probada |
| Qwen3.6-35B-A3B | 35B MoE (3B activos) | Apache-2.0 | Muy barato por token: ideal para servir |
| Gemma 4 (variantes pequeñas) | 2-12B | Apache-2.0 | Para experimentos rápidos y ejecución local/offline |

Plan a coste 0: el fine-tuning se hace en una **GPU gratuita de 16 GB** (Kaggle: P100 o 2×T4, unas 30 h/semana), así que se ajustan modelos **pequeños** (unos 1-8B en QLoRA). Los de ~27B quedan para la ampliación de pago. Para aprender el proceso, un modelo pequeño es incluso mejor: entrena rápido y se itera mucho.

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
| **Generación sintética filtrada** | El modelo local resuelve ejercicios muchas veces y **solo se guardan los que aprueba el verificador** (auto-mejora: el modelo aprende de sus propios aciertos verificados) | Volumen gratis y sin problemas de términos de uso |
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

## 6. ¿Dónde se aloja? (versión 0 €)

| Componente | Dónde | Coste |
|---|---|---|
| Modelo (inferencia) | Tu PC con Ollama | 0 € |
| Verificador | Tu PC (Linux/WSL) | 0 € |
| RAG | Base vectorial local (Chroma/SQLite) con modelo de embeddings abierto. Alternativa: Supabase gratis + pgvector | 0 € |
| Fine-tuning | Kaggle Notebooks (GPU gratis, ~30 h/semana, sesiones de 12 h). Alternativas: Google Colab gratis, Lightning AI (15 créditos/mes) | 0 € |
| Modelo entrenado | Hugging Face Hub (repositorio de modelos público) o en local | 0 € |
| Interfaz | Web **local** siguiendo el Figma (o Gradio para ir rápido) | 0 € |
| Escaparate público | Repo de GitHub + README con GIFs + vídeo demo + GitHub Pages con la landing estática | 0 € |

**¿Por qué no una web pública que ejecute código?** Porque exige un servidor con sandbox (que cuesta dinero) y abre riesgos de seguridad. Para un prototipo de aprendizaje, la demo en vídeo y el repo enseñan lo mismo. Ojo también con Hugging Face Spaces: en 2026 hay quejas de usuarios de que la capa gratuita se ha recortado (Docker marcado como de pago para algunas cuentas), así que no contamos con ella.

*Ampliación opcional de pago (si algún día hay usuarios o financiación):* ver [COSTES.md](COSTES.md).

## 7. Fases, con criterio de salida

Cada fase termina cuando se cumple su criterio, no por fecha. Las fechas son aproximadas para alguien que estudia a la vez (respetando exámenes).

### Fase 0: cimientos ✅ (octubre de 2026)
Verificador, bucle agente, capa de modelo, tests y repo.

### Fase 1: medir (noviembre-diciembre de 2026)
- Eval-set de **50 ejercicios** propios + una selección de DataRaceBench.
- Generador de **mutaciones** (trampas automáticas).
- ✅ **Sale cuando:** el eval-set se ejecuta entero con un comando y da un informe.

### Fase 2: línea base local (enero-febrero de 2027)
- Elegir modelo según tu hardware y ejecutarlo con Ollama.
- RAG local sobre especificación + ejemplos + apuntes.
- Barreras 1, 2, 4, 6 y 7 (las que no cuestan dinero).
- Medir: modelo solo → + RAG → + bucle agente. **Tres números, tres entradas de devlog.**
- ✅ **Sale cuando:** sabemos cuánto aporta cada pieza.

### Fase 3: fine-tuning gratis (marzo-mayo de 2027)
- Dataset verificado: mutaciones + DataRaceBench + ejercicios generados por el **propio modelo local** y filtrados por el verificador (sin coste ni problemas de términos de uso).
- QLoRA en Kaggle con Unsloth/PEFT sobre un modelo pequeño.
- Volver a medir y publicar la comparativa antes/después.
- ✅ **Sale cuando:** hay una mejora medida (o una explicación clara de por qué no la hay, que también es aprendizaje).

### Fase 4: demo y portfolio (verano de 2027)
- Interfaz local con el diseño del Figma: chat, panel de Verificación y speedup.
- Vídeo demo, README con GIFs, landing en GitHub Pages y modelo publicado en Hugging Face.
- ✅ **Sale cuando:** alguien externo entiende el proyecto en 2 minutos mirando el repo.

## 8. Lo que **no** hacemos (para no perder tiempo)

- Entrenar desde cero.
- Meter conocimiento por fine-tuning.
- Entrenar el modelo propio antes de tener eval-set y datos verificados.
- Gastar dinero en esta etapa: todo lo de pago es ampliación opcional.
- Alojar una GPU 24/7 sin usuarios.
- Abrir la ejecución de código al público sin sandbox.
- Elegir modelo por rankings de internet en vez de por **nuestro** eval-set.

---

## Fuentes
- [Best Open Source LLMs 2026 (morphllm)](https://www.morphllm.com/best-open-source-llm)
- [Free cloud GPU 2026 (AIMultiple)](https://aimultiple.com/free-cloud-gpu)
- [Hilo de Hugging Face sobre la capa gratuita de Spaces](https://discuss.huggingface.co/t/docker-sdk-now-marked-as-paid-when-creating-a-new-space/177580/5)
- [DataRaceBench (LLNL, GitHub)](https://github.com/LLNL/dataracebench)
- [Especificaciones OpenMP](https://www.openmp.org/specifications/)
