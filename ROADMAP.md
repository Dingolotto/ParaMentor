# Hoja de ruta

## v0.1: base verificable
Alcance: solo C, solo OpenMP en CPU, niveles Fundamentos e Intermedio.

- [x] Esqueleto del repositorio
- [x] Verificador v0 (`feat/verifier`): compilar, ejecutar 1/2/4/8 hilos, comparar con tolerancia, TSan + Archer, speedup
- [x] 3 ejercicios de ejemplo (reduction correcta, trampa de carrera, matmul)
- [ ] Tests unitarios del verificador (comparador de salidas, parser de TSan)
- [ ] Conjunto de evaluación (`feat/eval-set`): 100-150 ejercicios con enunciado, `seq.c`, solución y trampas
  - [ ] Fundamentos: `parallel`, `parallel for`, `private/shared/firstprivate`, `reduction`
  - [ ] Intermedio: `schedule`, `critical/atomic`, `barrier`, `sections`, `tasks`, balanceo
  - [ ] Trampas: reducción sin `reduction`, dependencias entre iteraciones, variables privadas sin inicializar, `nowait` mal puesto
- [ ] Línea base (`feat/rag-baseline`): modelo abierto de código + RAG sobre la especificación, con números guardados
- [ ] Web mínima (`feat/web-ui`) siguiendo el prototipo de Figma

## v0.5: especialización
- [ ] Pipeline de datos (`feat/data-pipeline`): generar candidatos y quedarse solo con los que pasa el verificador
- [ ] Fine-tuning LoRA/QLoRA (`feat/finetune`) y comparación con la línea base
- [ ] Bucle agente (`feat/agent-loop`): ejecutar, ver fallos, corregir antes de responder

## v1.0: producto
- [ ] Modos Aprende / Paraleliza / Revisa completos
- [ ] Ruta de aprendizaje con ejercicios
- [ ] API (`feat/api`) y despliegue público

## v2.0: ampliación
- [ ] Nivel Avanzado: falsos compartidos, NUMA, SIMD
- [ ] MPI e híbrido MPI+OpenMP
- [ ] GPU: OpenMP `target`, CUDA/HIP
- [ ] Plugin de IDE

## Ramas

| Rama | Contenido | Orden |
|---|---|---|
| `main` / `develop` | Estable e integración | Día 1 |
| `feat/verifier` | Verificador | 1ª |
| `feat/eval-set` | Ejercicios y tests | 2ª |
| `feat/rag-baseline` | Ingesta de docs + modelo base | 3ª |
| `feat/data-pipeline` | Generación y filtrado | 4ª |
| `feat/finetune` | Fine-tuning | 5ª |
| `feat/agent-loop` | Autocorrección | 6ª |
| `feat/api`, `feat/web-ui` | Backend y frontend | Desde la 3ª |
| `docs/devlog` | Diario | Siempre |

## Mejoras pendientes del verificador
- Medir el tiempo dentro del programa (`omp_get_wtime`) en vez de incluir el arranque del proceso.
- Fijar hilos a núcleos (`OMP_PROC_BIND`, `OMP_PLACES`) para tiempos más estables.
- Ejecutar en sandbox (contenedor sin red, límites de CPU/memoria) antes de aceptar código de usuarios o del modelo.
- Detectar falsos compartidos (contadores `perf` o heurística sobre el código).
