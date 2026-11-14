"""Pruebas de la operación de tope tarifario (ejecutar: python pruebas.py)."""

import random

from datos import generar_instancias
from estrategia import (
    DIARIO, MENSUAL, PASAJE, SEMANAL, costo_minimo, costo_minimo_contado,
    liquidar_tope
)
from exhaustivo import (
    costo_exhaustivo, costo_exhaustivo_contado, costo_fuerza_bruta
)
from regla_actual import costo_regla_actual, costo_regla_actual_contado

EJEMPLO_MANO = [3, 3, 3, 0, 2, 0, 3]  # resuelto a mano en el README: 36000
CONTRAEJEMPLO = [3, 0, 0, 0, 3, 3, 3, 3, 3]  # regla 55000, óptimo 45500


def probar_casos_limite() -> None:
    """Verifica entrada vacía, un elemento, solo ceros y productos sueltos."""
    assert costo_minimo([]) == 0
    assert costo_exhaustivo([]) == 0
    assert costo_regla_actual([]) == 0
    assert costo_minimo([0]) == 0
    assert costo_minimo([0, 0, 0]) == 0
    assert costo_minimo([1]) == PASAJE
    assert costo_minimo([2]) == 2 * PASAJE
    assert costo_minimo([3]) == DIARIO  # 3 pasajes (11700) > pase diario
    assert costo_minimo([100]) == DIARIO
    assert costo_minimo([1] * 7) == 7 * PASAJE  # 27300 < 36000: sencillos
    assert costo_minimo([2] * 7) == SEMANAL  # 54600 sencillos; diario 66500
    assert costo_minimo([3] * 7) == SEMANAL
    assert costo_minimo([3] * 30) == MENSUAL
    assert costo_minimo([3] * 31) == MENSUAL + DIARIO  # mes de 31 días
    assert costo_minimo([1, 0, 0, 0, 0, 0, 0, 1]) == 2 * PASAJE


def probar_ejemplo_manual() -> None:
    """Verifica el ejemplo pequeño resuelto a mano en el informe."""
    assert costo_minimo(EJEMPLO_MANO) == 36000
    assert costo_exhaustivo(EJEMPLO_MANO) == 36000
    assert costo_fuerza_bruta(EJEMPLO_MANO) == 36000


def probar_contra_exhaustivo() -> None:
    """Compara la DP con las soluciones exhaustivas en instancias pequeñas."""
    for instancia in generar_instancias(25, 9, 4, 2026, prob_dia=0.8):
        assert costo_minimo(instancia) == costo_exhaustivo(instancia)
    for instancia in generar_instancias(25, 7, 5, 7, prob_dia=0.7):
        assert costo_minimo(instancia) == costo_fuerza_bruta(instancia)
    rng = random.Random(11)
    for _ in range(25):
        dias = rng.randint(0, 40)
        instancia = [rng.choice([0, 0, 1, 2, 3, 5]) for _ in range(dias)]
        assert costo_minimo(instancia) == costo_exhaustivo(instancia)


def probar_contadores() -> None:
    """Verifica que las versiones con contador no cambian el resultado."""
    for instancia in generar_instancias(10, 20, 4, 5, prob_dia=0.8):
        assert costo_minimo_contado(instancia)[0] == costo_minimo(instancia)
        valor, _ = costo_exhaustivo_contado(instancia)
        assert valor == costo_minimo(instancia)
        assert costo_regla_actual_contado(instancia)[0] == \
            costo_regla_actual(instancia)
        assert costo_minimo_contado(instancia)[1] == len(instancia)


def ejecutar_pruebas() -> None:
    """Ejecuta todas las pruebas del Caso 1."""
    probar_casos_limite()
    probar_ejemplo_manual()
    probar_contra_exhaustivo()
    probar_contadores()
    print("Todas las pruebas del Caso 1 fueron superadas.")

if __name__ == "__main__":
    ejecutar_pruebas()
