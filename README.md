# ParaMentor

**Tu mentor de programación paralela, en español y con código verificado.**

ParaMentor es una IA especializada en **programación paralela**, empezando por OpenMP en C y siguiendo con MPI y GPU. Razona problemas difíciles en segundos, paraleliza y corrige código, y enseña tanto a principiantes como a profesionales del HPC.

Su diferencia frente a un asistente generalista: **no da por buena una paralelización hasta comprobarla**. Todo el código pasa por un verificador (compila, da el resultado correcto, no tiene carreras de datos y escala). Si falla, el agente recibe el error con la línea culpable y se corrige solo antes de responder.

```
modelo potente + RAG especializado + verificador + autocorrección + datos verificados
```

Empieza con un modelo de frontera por API como cerebro y evolucionará a un modelo abierto propio entrenado con los datos que el sistema ha verificado ([por qué](docs/decisiones/0001-cerebro-por-api-primero.md), [arquitectura](docs/ARQUITECTURA.md)).

## Modos

| Modo | Qué hace |
|---|---|
| **Aprende** | Explica conceptos con ejemplos ejecutables según tu nivel |
| **Paraleliza** | Recibe código secuencial y devuelve la versión OpenMP verificada |
| **Revisa** | Detecta carreras de datos, falsos compartidos y cláusulas mejorables |

## Estado

🚧 **v0.1 en construcción**: verificador, bucle agente de autocorrección y primeros ejercicios funcionando. Ver [ROADMAP.md](ROADMAP.md) y el diario en [docs/devlog](docs/devlog).

## Estructura

```
paramentor/
├── verifier/        # Compila, ejecuta, compara, detecta carreras, mide speedup
├── eval-set/        # Ejercicios de evaluación (seq.c + par.c + exercise.json)
├── rag/             # Ingesta de la especificación y docs de OpenMP
├── data-pipeline/   # Generación de datos filtrados por el verificador
├── finetune/        # Scripts y experimentos LoRA/QLoRA
├── agent/           # Capa de modelo + bucle generar → verificar → corregir
├── api/             # Backend
├── web/             # Frontend
└── docs/devlog/     # Diario del proceso, un hito por entrada
```

## Paralelizar con autocorrección

```bash
pip install anthropic                       # o: pip install openai (para vLLM / Ollama / OpenRouter)
export ANTHROPIC_API_KEY=...
python3 -m agent.paralelizar mi_codigo.c --args 1000000 --args-carreras 10000 --nivel fundamentos

# Con un modelo local en Ollama
PARAMENTOR_PROVIDER=openai OPENAI_BASE_URL=http://localhost:11434/v1 \
PARAMENTOR_MODEL=qwen2.5-coder:14b python3 -m agent.paralelizar mi_codigo.c
```

Devuelve el código paralelo, la explicación de cada pragma, el speedup medido y, si hubo intentos fallidos, por qué se rechazaron.

## Tests

```bash
python3 -m unittest discover -p "test_*.py" -v
```

## Verificador: uso rápido

Requisitos (Linux o WSL): `gcc`, `clang`, `libomp-dev` y los runtimes de sanitizers de LLVM.

```bash
# Ubuntu / Debian / WSL
sudo apt install gcc clang libomp-dev libclang-rt-dev python3

# Un ejercicio
python3 verifier/verifier.py eval-set/ejemplos/01_suma_reduccion

# Todos, guardando resultados
python3 verifier/verifier.py eval-set/ejemplos --json resultados.json

# Probar tu propio código contra un ejercicio
python3 verifier/verifier.py eval-set/ejemplos/02_suma_carrera --candidato mi_solucion.c
```

Salida de ejemplo:

```
=== 02_suma_carrera ===
  Compila                ✓
  Resultado correcto     ✗
  Sin carreras de datos  ✗  (líneas: 7, 9)
  --> SUSPENDIDO
```

### Formato de un ejercicio

```
eval-set/<grupo>/<id>/
├── seq.c           # versión secuencial de referencia
├── par.c           # versión paralela (solución o candidato)
└── exercise.json   # configuración
```

```json
{
  "id": "01_suma_reduccion",
  "titulo": "Serie armónica con reduction",
  "nivel": "fundamentos",
  "enunciado": "Paraleliza el cálculo de la serie armónica H(n) con OpenMP.",
  "args": ["50000000"],
  "args_carreras": ["200000"],
  "tolerancia_rel": 1e-9,
  "repeticiones": 3,
  "speedup_minimo": 1.5
}
```

- `args_carreras`: entrada más pequeña para ThreadSanitizer (va 5-15 veces más lento).
- `tolerancia_rel`: las reducciones en coma flotante cambian el orden de las sumas, así que los números se comparan con tolerancia.
- `speedup_minimo`: opcional, con un 20 % de margen por ruido.

### Cómo decide

1. Compila `seq.c` y `par.c` con `-O2 -fopenmp`.
2. Ejecuta `par.c` con 1, 2, 4 y 8 hilos, varias veces, y compara la salida con la de `seq.c`.
3. Compila `par.c` con `clang -fsanitize=thread` y lo ejecuta con **Archer** (LLVM), que enseña a TSan la semántica de OpenMP y elimina los falsos positivos del runtime.
4. Mide tiempos (mediana) y calcula el speedup.

**Aprueba** si compila, es correcto con todos los hilos y no hay carreras. El speedup se informa, pero solo suspende si el ejercicio fija `speedup_minimo`.

## Licencia

Por decidir. Revisar las licencias de cualquier material de terceros antes de incluirlo en `eval-set/` o `rag/`.
