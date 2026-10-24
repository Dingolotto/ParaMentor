# Hoja de ruta (funcionalidades)

> Estrategia, modelo base, datos, barreras y alojamiento: [docs/HOJA_DE_RUTA.md](docs/HOJA_DE_RUTA.md).

> **Visión:** la referencia mundial en programación paralela asistida por IA. Razona problemas difíciles en segundos, paraleliza y corrige código con **garantía verificada** y enseña desde cero hasta nivel HPC profesional.
>
> **Estrategia** ([decisión 0002](docs/decisiones/0002-prototipo-coste-cero.md)): **prototipo de aprendizaje a coste 0 €**. Modelo abierto local con Ollama, RAG local, verificador, bucle agente y fine-tuning en GPU gratuita (Kaggle). Lo de pago (API de frontera, VPS, web pública) es ampliación opcional ([costes](docs/COSTES.md)).

---

## v0.1: núcleo verificable (alcance: C + OpenMP en CPU, Fundamentos e Intermedio)

- [x] Esqueleto del repositorio, arquitectura y registro de decisiones
- [x] Verificador v0: compilar, 1/2/4/8 hilos, comparar con tolerancia, TSan + Archer, speedup
- [x] Bucle agente v0 (`agent/paralelizar.py`): generar, verificar, corregir con informe de líneas
- [x] Capa de modelo independiente del proveedor (Anthropic, endpoint compatible con OpenAI, mock)
- [x] Tests del verificador y del bucle
- [ ] **Eval-set inicial de 50 ejercicios** con trampas (reducción sin `reduction`, dependencias entre iteraciones, `private` sin inicializar, `nowait` mal puesto, `critical` innecesario)
- [ ] Primera medición: % de aprobados del cerebro por API **sin** y **con** el bucle agente
- [ ] RAG v0: especificación OpenMP + documento de ejemplos + apuntes propios, troceado y con referencias a sección
- [ ] Modo **Revisa** v0: detectar carreras, cláusulas incorrectas y dependencias en código del usuario
- [ ] API mínima con *streaming* + verificación asíncrona
- [ ] Web mínima siguiendo el prototipo de Figma: chat, panel de Verificación y gráfica de speedup

## v0.3: mentor de verdad

- [ ] **Diagnóstico de nivel**: 5-8 preguntas al empezar para situar al usuario
- [ ] Explicaciones adaptativas: el mismo concepto explicado para principiante y para profesional
- [ ] **Ruta de aprendizaje** con ejercicios autocorregidos y pistas progresivas (pista, más pista, solución)
- [ ] **Visualizador de hilos**: qué iteraciones ejecuta cada hilo según `schedule`, dónde esperan y dónde chocan
- [ ] Explicación de la carrera de datos: el intercalado concreto de dos hilos que produce el resultado erróneo
- [ ] **Modo examen**: ejercicios cronometrados del estilo de los parciales universitarios
- [ ] Calculadora de Amdahl/Gustafson integrada con los tiempos medidos de verdad
- [ ] Eval-set a 150 ejercicios, Intermedio completo (`tasks`, `taskloop`, `sections`, balanceo)

## v0.5: modelo propio

- [ ] Pipeline de datos: miles de pares (problema → solución) generados y **filtrados por el verificador** (revisar antes los términos de uso del proveedor)
- [ ] Fine-tuning LoRA/QLoRA de un modelo abierto de código (7-32B según el hardware)
- [ ] Comparación en el eval-set: modelo propio frente al cerebro por API, con y sin bucle agente
- [ ] Enrutado híbrido: preguntas fáciles al modelo propio (barato y rápido), difíciles al de frontera
- [ ] Optimización de latencia: caché por hash, workers de verificación precalentados, compilación en paralelo

## v1.0: herramienta profesional

- [ ] Nivel **Avanzado**: falsos compartidos (detección con `perf` + heurística), NUMA, afinidad, SIMD (`omp simd`)
- [ ] **Análisis de rendimiento**: por qué no escala (sobrecarga, desbalanceo, ancho de banda de memoria) con evidencia medida
- [ ] Proyectos de varios ficheros y Makefile/CMake
- [ ] Sandbox seguro (contenedor sin red, con límites) y despliegue público
- [ ] Cuentas, historial y progreso

## v2.0: todo el ecosistema paralelo

- [ ] **MPI** e híbrido MPI+OpenMP (verificador con `mpirun` y MUST para errores de MPI)
- [ ] **GPU**: OpenMP `target`, CUDA, HIP, con verificador en GPU (compute-sanitizer)
- [ ] C++ (`std::execution`, TBB), Fortran
- [ ] Plugin de VS Code: revisión de paralelismo en el editor
- [ ] Ejecución en la máquina del usuario: speedup medido en **su** hardware

## Posibles salidas
- Universidades: corrección automática de prácticas de paralela con explicación del fallo.
- Centros de supercomputación: revisión de código antes de lanzar trabajos caros.
- Portfolio y devlog público como caso de estudio de construir una IA especializada.

---

## Métricas que mandan (en cada entrada del devlog)

| Métrica | Qué mide |
|---|---|
| % aprobados en el eval-set | Corrección real (compila, resultado correcto, sin carreras) |
| % detectado en trampas | Capacidad de revisión |
| Intentos medios hasta aprobar | Calidad del primer intento |
| Speedup medio frente al de la solución de referencia | Calidad de la paralelización |
| Latencia p50 / p95 | "En segundos" de verdad |
| Coste por respuesta | Viabilidad |

## Ramas

| Rama | Contenido |
|---|---|
| `main` / `develop` | Estable / integración |
| `feat/verifier`, `feat/agent-loop` | Núcleo ✓ |
| `feat/eval-set` | Ejercicios y trampas: **siguiente** |
| `feat/rag-baseline`, `feat/revisar` | Conocimiento y modo Revisa |
| `feat/api`, `feat/web-ui` | Producto |
| `feat/data-pipeline`, `feat/finetune` | Modelo propio |
| `docs/devlog` | Diario |
