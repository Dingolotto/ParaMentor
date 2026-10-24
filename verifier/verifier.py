#!/usr/bin/env python3
"""
ParaMentor - Verificador de código OpenMP (v0.1)

Dado un ejercicio (seq.c de referencia + par.c candidato + exercise.json):
  1. Compila ambas versiones con -fopenmp.
  2. Ejecuta la versión paralela con 1/2/4/8 hilos (varias repeticiones)
     y compara la salida con la secuencial (tolerancia numérica).
  3. Pasa ThreadSanitizer + Archer (LLVM) para detectar carreras de datos.
  4. Mide el speedup (mediana de varias ejecuciones).

Uso:
  python verifier/verifier.py eval-set/ejemplos/01_suma_reduccion
  python verifier/verifier.py eval-set/ejemplos/02_suma_carrera --candidato otro.c
  python verifier/verifier.py eval-set/ejemplos --json resultados.json   # todos los ejercicios

Código de salida: 0 si compila, es correcto y no hay carreras; 1 en otro caso.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

HILOS_POR_DEFECTO = [1, 2, 4, 8]
TIMEOUT_S = 60
RACE_RE = re.compile(r"WARNING: ThreadSanitizer: data race")
NUM_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$|^[+-]?(inf|nan)$", re.I)


# --------------------------------------------------------------------------- #
# Configuración del ejercicio
# --------------------------------------------------------------------------- #
@dataclass
class Ejercicio:
    ruta: Path
    id: str
    titulo: str = ""
    nivel: str = "fundamentos"
    args: list[str] = field(default_factory=list)
    args_carreras: list[str] | None = None   # entrada más pequeña para TSan (es lento)
    stdin: str | None = None
    tolerancia_rel: float = 1e-9
    tolerancia_abs: float = 1e-12
    repeticiones: int = 3
    hilos: list[int] = field(default_factory=lambda: list(HILOS_POR_DEFECTO))
    speedup_minimo: float | None = None      # opcional; con 'tolerancia' de ruido
    flags_extra: list[str] = field(default_factory=list)

    @classmethod
    def cargar(cls, ruta: Path) -> "Ejercicio":
        cfg_path = ruta / "exercise.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
        cfg.setdefault("id", ruta.name)
        campos = {k: v for k, v in cfg.items() if k in cls.__dataclass_fields__}
        return cls(ruta=ruta, **campos)


@dataclass
class Resultado:
    id: str
    compila: bool = False
    correcto: bool | None = None
    sin_carreras: bool | None = None          # None = detector no disponible
    lineas_carrera: list[int] = field(default_factory=list)
    speedup: dict[str, float] = field(default_factory=dict)
    tiempos_s: dict[str, float] = field(default_factory=dict)
    speedup_ok: bool | None = None
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @property
    def aprobado(self) -> bool:
        return bool(self.compila and self.correcto and self.sin_carreras is not False)


# --------------------------------------------------------------------------- #
# Herramientas
# --------------------------------------------------------------------------- #
def buscar_archer() -> str | None:
    if os.environ.get("ARCHER_LIB") and Path(os.environ["ARCHER_LIB"]).exists():
        return os.environ["ARCHER_LIB"]
    candidatos = sorted(glob.glob("/usr/lib/llvm-*/lib/libarcher.so"), reverse=True)
    candidatos += glob.glob("/usr/local/lib/libarcher.so") + glob.glob("/opt/homebrew/opt/libomp/lib/libarcher.dylib")
    return candidatos[0] if candidatos else None


def compilador_rendimiento() -> str:
    return os.environ.get("CC") or ("gcc" if shutil.which("gcc") else "clang")


def compilar(cc: str, fuente: Path, salida: Path, flags: list[str]) -> tuple[bool, str]:
    cmd = [cc, str(fuente), "-o", str(salida), "-fopenmp", *flags, "-lm"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode == 0, (p.stderr or "").strip()


def ejecutar(binario: Path, args: list[str], stdin: str | None, hilos: int | None,
             env_extra: dict[str, str] | None = None) -> tuple[int, str, str, float]:
    env = os.environ.copy()
    if hilos is not None:
        env["OMP_NUM_THREADS"] = str(hilos)
    env.setdefault("OMP_DYNAMIC", "false")
    if env_extra:
        env.update(env_extra)
    t0 = time.perf_counter()
    try:
        p = subprocess.run([str(binario), *args], input=stdin, capture_output=True,
                           text=True, env=env, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout ({TIMEOUT_S}s)", float(TIMEOUT_S)
    return p.returncode, p.stdout, p.stderr, time.perf_counter() - t0


# --------------------------------------------------------------------------- #
# Comparación de salidas
# --------------------------------------------------------------------------- #
def salidas_iguales(ref: str, obt: str, rel: float, abs_: float) -> tuple[bool, str]:
    a, b = ref.split(), obt.split()
    if len(a) != len(b):
        return False, f"número de tokens distinto ({len(a)} vs {len(b)})"
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        if NUM_RE.match(x) and NUM_RE.match(y):
            fx, fy = float(x), float(y)
            if abs(fx - fy) <= max(abs_, rel * max(abs(fx), abs(fy))):
                continue
        return False, f"token {i}: esperado '{x}', obtenido '{y}'"
    return True, ""


# --------------------------------------------------------------------------- #
# Fases
# --------------------------------------------------------------------------- #
def fase_correccion(ej: Ejercicio, bin_seq: Path, bin_par: Path, r: Resultado) -> str | None:
    rc, ref, err, _ = ejecutar(bin_seq, ej.args, ej.stdin, 1)
    if rc != 0:
        r.errores.append(f"la versión secuencial falla (rc={rc}): {err[:300]}")
        r.correcto = False
        return None
    for h in ej.hilos:
        for rep in range(ej.repeticiones):
            rc, out, err, _ = ejecutar(bin_par, ej.args, ej.stdin, h)
            if rc != 0:
                r.correcto = False
                r.errores.append(f"{h} hilos, rep {rep + 1}: falla (rc={rc}) {err[:300]}")
                return ref
            ok, motivo = salidas_iguales(ref, out, ej.tolerancia_rel, ej.tolerancia_abs)
            if not ok:
                r.correcto = False
                r.errores.append(f"{h} hilos, rep {rep + 1}: salida incorrecta, {motivo}")
                return ref
    r.correcto = True
    return ref


def fase_carreras(ej: Ejercicio, candidato: Path, tmp: Path, r: Resultado) -> None:
    archer = buscar_archer()
    if not shutil.which("clang") or not archer:
        r.avisos.append("detector de carreras no disponible (falta clang o libarcher)")
        return
    bin_tsan = tmp / "par_tsan"
    ok, err = compilar("clang", candidato, bin_tsan,
                       ["-fsanitize=thread", "-g", "-O1", *ej.flags_extra])
    if not ok:
        r.avisos.append(f"no se pudo compilar con TSan: {err[:300]}")
        return
    env = {
        "OMP_TOOL_LIBRARIES": archer,
        "TSAN_OPTIONS": "ignore_noninstrumented_modules=1 exitcode=0",
        "ARCHER_OPTIONS": "verbose=0",
    }
    args = ej.args_carreras if ej.args_carreras is not None else ej.args
    lineas: set[int] = set()
    hay_carrera = False
    nombre = re.escape(candidato.name)
    for h in (2, 4):
        _, _, err, _ = ejecutar(bin_tsan, args, ej.stdin, h, env)
        if RACE_RE.search(err):
            hay_carrera = True
            lineas.update(int(m) for m in re.findall(rf"{nombre}:(\d+)", err))
    r.lineas_carrera = sorted(lineas)
    r.sin_carreras = not hay_carrera


def fase_speedup(ej: Ejercicio, bin_seq: Path, bin_par: Path, r: Resultado) -> None:
    k = max(3, ej.repeticiones)
    mediana = lambda b, h: statistics.median(ejecutar(b, ej.args, ej.stdin, h)[3] for _ in range(k))
    t_seq = mediana(bin_seq, 1)
    r.tiempos_s["seq"] = round(t_seq, 4)
    nucleos = os.cpu_count() or 1
    for h in ej.hilos:
        t = mediana(bin_par, h)
        r.tiempos_s[str(h)] = round(t, 4)
        r.speedup[str(h)] = round(t_seq / t, 2) if t > 0 else 0.0
    if any(h > nucleos for h in ej.hilos):
        r.avisos.append(f"la máquina tiene {nucleos} núcleos: el speedup con más hilos no es representativo")
    if ej.speedup_minimo is not None:
        mejor = max(r.speedup.values(), default=0.0)
        r.speedup_ok = mejor >= ej.speedup_minimo * 0.8   # 20 % de margen por ruido


# --------------------------------------------------------------------------- #
# Orquestación
# --------------------------------------------------------------------------- #
def verificar(ruta: Path, candidato: Path | None = None, medir: bool = True) -> Resultado:
    ej = Ejercicio.cargar(ruta)
    r = Resultado(id=ej.id)
    seq = ruta / "seq.c"
    par = candidato or (ruta / "par.c")
    for f in (seq, par):
        if not f.exists():
            r.errores.append(f"no existe {f}")
            return r

    with tempfile.TemporaryDirectory(prefix="paramentor_") as d:
        tmp = Path(d)
        cc = compilador_rendimiento()
        bin_seq, bin_par = tmp / "seq", tmp / "par"
        flags = ["-O2", "-Wall", *ej.flags_extra]
        ok_s, err_s = compilar(cc, seq, bin_seq, flags)
        ok_p, err_p = compilar(cc, par, bin_par, flags)
        if not ok_s:
            r.errores.append(f"seq.c no compila: {err_s[:500]}")
        if not ok_p:
            r.errores.append(f"{par.name} no compila: {err_p[:500]}")
        r.compila = ok_s and ok_p
        if not r.compila:
            return r
        if "warning" in err_p:
            r.avisos.append("warnings de compilación en la versión paralela")

        fase_correccion(ej, bin_seq, bin_par, r)
        fase_carreras(ej, par, tmp, r)
        if medir and r.correcto:
            fase_speedup(ej, bin_seq, bin_par, r)
    return r


def imprimir(r: Resultado) -> None:
    m = lambda v: "✓" if v else ("?" if v is None else "✗")
    print(f"\n=== {r.id} ===")
    print(f"  Compila                {m(r.compila)}")
    print(f"  Resultado correcto     {m(r.correcto)}")
    extra = f"  (líneas: {', '.join(map(str, r.lineas_carrera))})" if r.lineas_carrera else ""
    print(f"  Sin carreras de datos  {m(r.sin_carreras)}{extra}")
    if r.speedup:
        print("  Speedup                " + "  ".join(f"{h}h: x{s}" for h, s in r.speedup.items()))
    if r.speedup_ok is not None:
        print(f"  Speedup mínimo         {m(r.speedup_ok)}")
    for e in r.errores:
        print(f"  ERROR: {e}")
    for a in r.avisos:
        print(f"  aviso: {a}")
    print(f"  --> {'APROBADO' if r.aprobado else 'SUSPENDIDO'}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Verificador OpenMP de ParaMentor")
    ap.add_argument("ruta", type=Path, help="carpeta de un ejercicio o carpeta con varios")
    ap.add_argument("--candidato", type=Path, help="fichero .c a verificar (por defecto par.c)")
    ap.add_argument("--sin-speedup", action="store_true", help="no medir tiempos (más rápido)")
    ap.add_argument("--json", type=Path, help="guardar resultados en un fichero JSON")
    a = ap.parse_args()

    if (a.ruta / "seq.c").exists():
        rutas = [a.ruta]
    else:
        rutas = sorted(p for p in a.ruta.iterdir() if (p / "seq.c").exists())
        if not rutas:
            print(f"No hay ejercicios en {a.ruta}", file=sys.stderr)
            return 2

    resultados = []
    for ruta in rutas:
        cand = a.candidato.resolve() if a.candidato and len(rutas) == 1 else None
        r = verificar(ruta, cand, medir=not a.sin_speedup)
        imprimir(r)
        resultados.append(r)

    if len(resultados) > 1:
        n_ok = sum(r.aprobado for r in resultados)
        print(f"\nTotal: {n_ok}/{len(resultados)} aprobados")
    if a.json:
        a.json.write_text(json.dumps([asdict(r) | {"aprobado": r.aprobado} for r in resultados],
                                     indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if all(r.aprobado for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
