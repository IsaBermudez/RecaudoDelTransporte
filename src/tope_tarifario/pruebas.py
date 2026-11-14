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


def probar_liquidacion() -> None:
    """Verifica que la devolución es la diferencia exacta."""
    minimo = costo_minimo(EJEMPLO_MANO)
    assert liquidar_tope(EJEMPLO_MANO, minimo + 4000) == 4000
    assert liquidar_tope(EJEMPLO_MANO, minimo) == 0
    assert liquidar_tope(EJEMPLO_MANO, minimo - 1) == 0  # nunca negativa
    assert liquidar_tope(EJEMPLO_MANO, 0) == 0
    cobrado_regla = costo_regla_actual(CONTRAEJEMPLO)
    assert liquidar_tope(CONTRAEJEMPLO, cobrado_regla) == 9500
    for instancia in generar_instancias(50, 31, 5, 99, prob_dia=0.8):
        cobrado = costo_regla_actual(instancia)
        devolucion = liquidar_tope(instancia, cobrado)
        assert devolucion == cobrado - costo_minimo(instancia)
        assert devolucion >= 0
        assert cobrado - devolucion == costo_minimo(instancia)


def probar_regla_actual() -> None:
    """Verifica que la regla actual nunca baja del mínimo y falla a veces."""
    assert costo_regla_actual(CONTRAEJEMPLO) == 55000
    assert costo_minimo(CONTRAEJEMPLO) == 45500
    assert costo_regla_actual(CONTRAEJEMPLO) > costo_minimo(CONTRAEJEMPLO)
    peores = 0
    for instancia in generar_instancias(300, 31, 5, 3, prob_dia=0.7):
        assert costo_regla_actual(instancia) >= costo_minimo(instancia)
        peores += costo_regla_actual(instancia) > costo_minimo(instancia)
    assert peores > 0


def probar_entradas_invalidas() -> None:
    """Verifica que los viajes negativos se rechazan."""
    for funcion in (costo_minimo, costo_exhaustivo, costo_regla_actual):
        try:
            funcion([1, -1])
        except ValueError:
            continue
        raise AssertionError("Se esperaba ValueError para viajes negativos.")


def ejecutar_pruebas() -> None:
    """Ejecuta todas las pruebas del Caso 1."""
    probar_casos_limite()
    probar_ejemplo_manual()
    probar_contra_exhaustivo()
    probar_contadores()
    probar_liquidacion()
    probar_regla_actual()
    probar_entradas_invalidas()
    print("Todas las pruebas del Caso 1 fueron superadas.")


if __name__ == "__main__":
    ejecutar_pruebas()
