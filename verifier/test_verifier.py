"""Tests del verificador. Ejecutar desde la raíz: python3 -m unittest discover -v"""
import unittest
from pathlib import Path

from verifier.verifier import salidas_iguales, verificar

EJEMPLOS = Path(__file__).resolve().parent.parent / "eval-set" / "ejemplos"


class TestComparador(unittest.TestCase):
    def test_iguales(self):
        self.assertTrue(salidas_iguales("1 2 hola", "1 2 hola", 1e-9, 1e-12)[0])

    def test_tolerancia_flotante(self):
        self.assertTrue(salidas_iguales("18.3047492383", "18.3047492384", 1e-9, 1e-12)[0])

    def test_fuera_de_tolerancia(self):
        self.assertFalse(salidas_iguales("18.30", "0.69", 1e-9, 1e-12)[0])

    def test_numero_de_tokens(self):
        self.assertFalse(salidas_iguales("1 2", "1", 1e-9, 1e-12)[0])

    def test_texto_distinto(self):
        self.assertFalse(salidas_iguales("ok", "ko", 1e-9, 1e-12)[0])


class TestEjemplos(unittest.TestCase):
    def test_reduccion_aprueba(self):
        self.assertTrue(verificar(EJEMPLOS / "01_suma_reduccion", medir=False).aprobado)

    def test_carrera_suspende(self):
        r = verificar(EJEMPLOS / "02_suma_carrera", medir=False)
        self.assertFalse(r.aprobado)
        self.assertFalse(r.sin_carreras)


if __name__ == "__main__":
    unittest.main()
