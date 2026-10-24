"""Test del bucle agente con un modelo simulado: primer intento con carrera, segundo correcto.
Ejecutar desde la raíz: python3 -m unittest agent.test_agente -v"""
import unittest
from pathlib import Path

from agent.llm import MockLLM
from agent.paralelizar import paralelizar

EJ = Path(__file__).resolve().parent.parent / "eval-set" / "ejemplos"


def envolver(codigo: str, explicacion: str) -> str:
    return f"```c\n{codigo}```\n{explicacion}"


class TestBucleAgente(unittest.TestCase):
    def test_se_autocorrige(self):
        seq = (EJ / "02_suma_carrera" / "seq.c").read_text()
        malo = (EJ / "02_suma_carrera" / "par.c").read_text()
        bueno = (EJ / "01_suma_reduccion" / "par.c").read_text()
        llm = MockLLM([envolver(malo, "Paralelizo el bucle."),
                       envolver(bueno, "Añado reduction(+:suma) para evitar la carrera.")])

        r = paralelizar(seq, llm, args=["2000000"], args_carreras=["100000"], medir=False)

        self.assertTrue(r.verificada)
        self.assertEqual(r.intentos, 2)
        self.assertIn("reduction", r.codigo)
        self.assertIn("carrera en línea", r.historial[0])          # el modelo recibió la línea culpable
        self.assertIn("rechazado", llm.llamadas[1][-1]["content"])  # y el informe en el 2º mensaje

    def test_sin_bloque_de_codigo(self):
        seq = (EJ / "01_suma_reduccion" / "seq.c").read_text()
        r = paralelizar(seq, MockLLM(["No sé hacerlo."]), args=["1000"], max_intentos=2, medir=False)
        self.assertFalse(r.verificada)
        self.assertEqual(len(r.historial), 2)


if __name__ == "__main__":
    unittest.main()
