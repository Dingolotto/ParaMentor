# 0001 · Esqueleto y verificador v0

**Fecha:** 2026-10-24
**Rama:** `feat/verifier`

## Qué se ha hecho
- Estructura del repositorio, README y ROADMAP.
- `verifier/verifier.py`: compila, ejecuta con 1/2/4/8 hilos, compara con tolerancia numérica, detecta carreras con ThreadSanitizer + Archer y mide speedup.
- Tres ejercicios de ejemplo en `eval-set/ejemplos/`.

## Resultados (máquina de pruebas, 2 núcleos)

| Ejercicio | Compila | Correcto | Sin carreras | Speedup 2h |
|---|---|---|---|---|
| 01_suma_reduccion | ✓ | ✓ | ✓ | x1.79 |
| 02_suma_carrera | ✓ | ✗ | ✗ (líneas 7, 9) | n/a |
| 03_matmul | ✓ | ✓ | ✓ | x1.30 |

El verificador detecta la trampa de la reducción sin `reduction` por los dos caminos: salida incorrecta y carrera señalada en la línea del `pragma` y en la de la suma.

## Lo aprendido
- **TSan solo no vale con OpenMP**: con el runtime de LLVM salen falsos positivos incluso en código correcto. Hace falta **Archer** (`OMP_TOOL_LIBRARIES=libarcher.so`) y `TSAN_OPTIONS=ignore_noninstrumented_modules=1`. Con eso, el código con `reduction` da 0 avisos y el código con carrera los sigue dando.
- Con `gcc` + `libgomp` TSan no sirve porque libgomp no está instrumentado, así que la detección de carreras se compila siempre con `clang`.
- Las sumas en coma flotante cambian de orden al paralelizar, así que comparar la salida exacta suspendería soluciones correctas: se compara con tolerancia relativa.
- Medir speedup en una máquina de 2 núcleos con 4 y 8 hilos no es representativo; el verificador lo avisa.

## Siguiente
- Tests unitarios del verificador.
- Empezar `feat/eval-set` con ejercicios propios de la asignatura de Programación Paralela.
- Rellenar datos de hardware para elegir modelo base.
