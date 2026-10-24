# ParaMentor: documento de contexto del proyecto

> Resumen para retomar el proyecto en otra conversación o IA. Léelo entero y continúa desde la sección "Siguiente paso".

## 1. Objetivo

Crear mi propia IA especializada: un **mentor en español de programación paralela**, empezando por **OpenMP en C/C++**, que enseñe desde nivel básico hasta avanzado.

No voy a entrenar un modelo desde cero (inviable en coste). El plan es partir de un **modelo abierto de código** (7B-32B, ejecutable por mí), **especializarlo con fine-tuning (LoRA/QLoRA)** y **darle acceso a documentación con RAG**.

## 2. Cómo se llegó a esta decisión

1. Idea inicial: usar modelos de pesos abiertos (p. ej. DeepSeek) para hacer una IA propia.
2. Primera propuesta: mentor de Java. **Descartada**: hay demasiada competencia (modelos grandes, Copilot, cursos) y un modelo pequeño no destaca en algo tan genérico.
3. Criterio para elegir nicho: (a) los modelos grandes son flojos ahí, (b) hay demanda real, (c) la respuesta se puede **verificar automáticamente**.
4. Decisión final: **programación paralela / HPC, empezando por OpenMP**. Los modelos generales suelen generar código paralelo que compila pero tiene carreras de datos, falsos compartidos o mala escalabilidad, y hay poco material en español.
5. Alternativas valoradas y aparcadas: COBOL/legacy, Verilog/VHDL, PLC (Structured Text), Rust.
6. El diario del proceso de construir la IA (`docs/devlog`) hará de "mentoría de crear IA" y de portfolio en GitHub.

## 3. Propuesta de valor: tres modos

1. **Enseñar**: explica conceptos con ejemplos ejecutables, según el nivel.
2. **Paralelizar**: recibe código secuencial y devuelve la versión OpenMP ya verificada.
3. **Revisar**: detecta carreras de datos, falsos compartidos y malas cláusulas en código paralelo (el diferenciador principal).

## 4. Niveles

- **Fundamentos**: hilos, `parallel`, `parallel for`, `private/shared`, `reduction`.
- **Intermedio**: `schedule`, `critical/atomic`, `barrier`, `sections`, `tasks`, balanceo de carga.
- **Avanzado**: falsos compartidos, NUMA, SIMD, offloading a GPU (`target`), luego MPI e híbrido MPI+OpenMP.

## 5. Alcance de la v0.1

Solo **C**, solo **OpenMP en CPU**, solo niveles **Fundamentos e Intermedio**. Todo lo demás, después.

## 6. Pasos en orden

1. **Verificador** (lo primero): script que, dado un fragmento de código, compila con `-fopenmp`, ejecuta con 1/2/4/8 hilos, compara la salida con la versión secuencial de referencia, pasa un detector de carreras (ThreadSanitizer o Archer de LLVM) y mide el speedup (con tolerancia, los tiempos son ruidosos). Basta una CPU multinúcleo.
2. **Conjunto de evaluación**: unos 100-150 ejercicios, cada uno con enunciado, versión secuencial, tests y criterio de éxito, incluyendo trampas típicas (reducciones sin `reduction`, dependencias entre iteraciones...).
3. **Línea base**: pasar un modelo abierto de código por la evaluación, con RAG sobre la especificación y docs. Guardar los números.
4. **Datos de entrenamiento con filtro**: generar respuestas candidatas con un modelo y **conservar solo las que pasan el verificador**. Revisar antes los términos de uso del modelo generador y las licencias de cualquier código real.
5. **Fine-tuning (LoRA/QLoRA)** con esos datos y volver a medir contra la línea base.
6. **Bucle agente**: que el asistente ejecute su propio código, vea los fallos y se corrija antes de responder.
7. **API + web**; después ampliar a MPI y GPU.

Nota clave: el fine-tuning enseña *cómo* responder (formato, tono, tarea); el *conocimiento* (especificación, docs) va por RAG.

## 7. Estructura de ramas del repositorio

| Rama | Contenido | Orden |
|---|---|---|
| `main` / `develop` | Estable e integración, con README | Día 1 |
| `feat/verifier` | Compilar, ejecutar, comparar, detectar carreras, medir | 1ª |
| `feat/eval-set` | Ejercicios y tests | 2ª |
| `feat/rag-baseline` | Ingesta de especificación y docs + modelo base | 3ª |
| `feat/data-pipeline` | Generación y filtrado con el verificador | 4ª |
| `feat/finetune` | Scripts y experimentos | 5ª |
| `feat/agent-loop` | Autocorrección con ejecución | 6ª |
| `feat/api`, `feat/web-ui` | Backend y frontend | En paralelo desde la 3ª |
| `docs/devlog` | Diario del proceso | Siempre |

Una entrada de diario por hito, con métricas antes y después.

## 8. Datos a reunir de primeras

- Especificación de OpenMP y su documento de ejemplos (públicos; comprobar condiciones antes de redistribuir).
- Benchmarks y material docente abierto (p. ej. NAS, Rodinia, PolyBench, tutoriales de centros de supercomputación). **Comprobar la licencia de cada uno.**
- Mis propios ejercicios y soluciones (el activo más valioso).

## 9. Prototipo visual (prompt para Figma Make)

```
Design a responsive web app prototype called "ParaMentor", an AI mentor specialized in parallel programming (OpenMP in C/C++, later MPI and GPU), from beginner to expert. All UI text in Spanish. Modern developer-tool aesthetic, dark mode by default with light toggle, monospace font for code, accent color electric teal on deep navy.

Screens:
1. Landing: headline "Tu mentor de programación paralela", subtitle about verified code, three feature cards (Aprende, Paraleliza, Revisa), level selector (Fundamentos / Intermedio / Avanzado), "Probar ahora" button.
2. Main chat: left sidebar with history and level selector; central chat with syntax-highlighted code blocks; below each code block a "Verificación" panel showing: Compila ✓, Resultado correcto ✓, Sin carreras de datos ✓ (or a red warning with the offending line highlighted), and a small bar chart of speedup with 1, 2, 4, 8 threads. Mode switch: Explicar / Paralelizar / Revisar / Depurar. Input accepts pasted code or .c/.cpp files.
3. Paralelizar screen: split view, sequential code on the left, parallel OpenMP version on the right with changed lines highlighted, plus explanations of each pragma and the speedup chart.
4. Revisar screen: user code with inline annotations marking race conditions, false sharing and suboptimal clauses, each with a suggested fix.
5. Learning path: roadmap map of topics (Hilos, parallel for, reduction, scheduling, tasks, falsos compartidos, SIMD, GPU offload, MPI) with progress and "Practicar" buttons.
6. Exercise screen: statement, code editor, "Ejecutar y verificar" button, results panel, hints.
Include realistic sample content (e.g., parallelizing a matrix multiplication and fixing a reduction race). Add interactive transitions.
```

## 10. Hoja de ruta futura

- **v0.1**: verificador + evaluación + modelo base con RAG + web mínima.
- **v0.5**: fine-tuning con datos verificados y bucle de autocorrección.
- **v1.0**: los tres modos completos, ruta de aprendizaje y despliegue público.
- **v2.0**: MPI, GPU (CUDA/HIP/OpenMP offload), Fortran, plugin de IDE.
- **Posible salida**: universidades y centros de supercomputación (docencia y revisión de código).

## 11. Riesgos

- Medir speedup es delicado y depende de la máquina: priorizar corrección y ausencia de carreras sobre rendimiento puro.
- Los detectores de carreras no encuentran todo: el verificador reduce errores, no los elimina.
- Licencias de datos y términos del modelo generador pueden complicar un uso comercial.
- Proyecto largo: trabajar con hitos pequeños y mantener el diario.

## 12. Datos pendientes (rellenar)

- CPU (modelo y número de núcleos): _______
- GPU (si hay) y memoria: _______
- RAM: _______
- Nivel de Python: _______
- Objetivo principal (aprender / proyecto personal / producto): _______
- Presupuesto para GPU en la nube (si aplica): _______

## 13. Preferencias de trabajo

- Ir por hitos pequeños y documentar el proceso en GitHub.
- Respuestas en español.
- _(añade aquí cualquier otra preferencia)_

## 14. Siguiente paso

Crear el esqueleto del repositorio (README, estructura de carpetas, `ROADMAP.md`) y un primer borrador del script verificador en Python (`feat/verifier`). Después, elegir el modelo base según el hardware indicado en la sección 12.
