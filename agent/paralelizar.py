"""
Modo Paraleliza con bucle agente: generar -> verificar -> corregir.

  python -m agent.paralelizar mi_codigo.c --args 1000000 --args-carreras 10000
  PARAMENTOR_PROVIDER=openai OPENAI_BASE_URL=http://localhost:11434/v1 python -m agent.paralelizar mi_codigo.c

El código secuencial del usuario es la referencia (seq.c) y la propuesta del
modelo es el candidato (par.c). Solo se devuelve como "verificada" si aprueba.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from agent.llm import LLM, crear_llm
from verifier.verifier import Resultado, verificar

SISTEMA = """Eres ParaMentor, experto mundial en programación paralela con OpenMP en C y mentor paciente.
Tu tarea: paralelizar el programa secuencial que te dan.

Reglas:
- Devuelve EXACTAMENTE un bloque ```c con el programa COMPLETO, compilable con -fopenmp.
- La salida por pantalla debe ser idéntica a la del secuencial (salvo redondeo de coma flotante).
- Cero carreras de datos: usa reduction, private, firstprivate, atomic o critical donde toque.
- Busca speedup real: paraleliza el bucle externo con trabajo suficiente, elige schedule con criterio
  y evita falsos compartidos y sincronización innecesaria.
- Si un bucle tiene dependencias entre iteraciones, no lo paralelices a ciegas: reestructúralo o explica por qué no se puede.
- Después del bloque, explica en español, nivel {nivel}, cada pragma que has añadido y por qué es correcto."""

PLANTILLA_CORRECCION = """El verificador ha rechazado tu versión:
{informe}
Corrige el problema y devuelve de nuevo el programa COMPLETO en un único bloque ```c, con la explicación."""

BLOQUE_C = re.compile(r"```(?:c|cpp|C)?\s*\n(.*?)```", re.S)


@dataclass
class Respuesta:
    verificada: bool
    codigo: str
    explicacion: str
    resultado: Resultado | None
    intentos: int
    historial: list[str] = field(default_factory=list)   # informe de cada intento fallido


def extraer_codigo(texto: str) -> tuple[str, str]:
    bloques = BLOQUE_C.findall(texto)
    if not bloques:
        return "", texto.strip()
    codigo = max(bloques, key=len)
    explicacion = BLOQUE_C.sub("", texto).strip()
    return codigo.strip() + "\n", explicacion


def informe_fallo(r: Resultado, codigo: str) -> str:
    lineas = codigo.splitlines()
    partes = [f"- Compila: {'sí' if r.compila else 'NO'}",
              f"- Resultado correcto: {'sí' if r.correcto else 'NO'}",
              f"- Sin carreras de datos: {'sí' if r.sin_carreras is not False else 'NO'}"]
    for n in r.lineas_carrera:
        if 0 < n <= len(lineas):
            partes.append(f"  carrera en línea {n}: `{lineas[n - 1].strip()}`")
    partes += [f"- {e}" for e in r.errores]
    return "\n".join(partes)


def paralelizar(codigo_seq: str, llm: LLM | None = None, args: list[str] | None = None,
                args_carreras: list[str] | None = None, nivel: str = "intermedio",
                max_intentos: int = 3, medir: bool = True) -> Respuesta:
    llm = llm or crear_llm()
    sistema = SISTEMA.format(nivel=nivel)
    mensajes = [{"role": "user", "content": f"Paraleliza este programa:\n```c\n{codigo_seq}\n```"}]
    historial: list[str] = []
    codigo, explicacion, r = "", "", None

    with tempfile.TemporaryDirectory(prefix="paramentor_ej_") as d:
        ej = Path(d)
        (ej / "seq.c").write_text(codigo_seq, encoding="utf-8")
        cfg = {"id": "peticion_usuario", "args": args or [], "repeticiones": 2}
        if args_carreras is not None:
            cfg["args_carreras"] = args_carreras
        (ej / "exercise.json").write_text(json.dumps(cfg), encoding="utf-8")

        for intento in range(1, max_intentos + 1):
            texto = llm.generar(sistema, mensajes)
            codigo, explicacion = extraer_codigo(texto)
            if not codigo:
                informe = "- No has devuelto ningún bloque ```c."
                r = None
            else:
                (ej / "par.c").write_text(codigo, encoding="utf-8")
                r = verificar(ej, medir=False)
                if r.aprobado:
                    if medir:
                        r = verificar(ej, medir=True)
                    return Respuesta(True, codigo, explicacion, r, intento, historial)
                informe = informe_fallo(r, codigo)
            historial.append(informe)
            mensajes += [{"role": "assistant", "content": texto},
                         {"role": "user", "content": PLANTILLA_CORRECCION.format(informe=informe)}]

    return Respuesta(False, codigo, explicacion, r, max_intentos, historial)


def main() -> int:
    ap = argparse.ArgumentParser(description="ParaMentor: paraleliza y verifica un programa C")
    ap.add_argument("fuente", type=Path)
    ap.add_argument("--args", nargs="*", default=[])
    ap.add_argument("--args-carreras", nargs="*")
    ap.add_argument("--nivel", default="intermedio", choices=["fundamentos", "intermedio", "avanzado"])
    ap.add_argument("--intentos", type=int, default=3)
    ap.add_argument("--proveedor", choices=["anthropic", "openai"])
    ap.add_argument("--salida", type=Path, help="guardar el código paralelo aquí")
    a = ap.parse_args()

    resp = paralelizar(a.fuente.read_text(encoding="utf-8"), crear_llm(a.proveedor), a.args,
                       a.args_carreras, a.nivel, a.intentos)
    print(resp.codigo)
    print(resp.explicacion)
    estado = "VERIFICADA" if resp.verificada else "NO VERIFICADA"
    print(f"\n[{estado} en {resp.intentos} intento(s)]")
    if resp.resultado and resp.resultado.speedup:
        print("Speedup: " + "  ".join(f"{h}h x{s}" for h, s in resp.resultado.speedup.items()))
    for i, inf in enumerate(resp.historial, 1):
        print(f"\nIntento {i} rechazado:\n{inf}")
    if a.salida:
        a.salida.write_text(resp.codigo, encoding="utf-8")
    return 0 if resp.verificada else 1


if __name__ == "__main__":
    sys.exit(main())
