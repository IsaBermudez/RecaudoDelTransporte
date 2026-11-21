"""Pruebas de la operación de franjas de congestión."""

import math
import random

from datos import generar_series
from estrategias import (
    dividir_y_vencer, dividir_y_vencer_contado, fuerza_bruta,
    fuerza_bruta_contado, kadane, kadane_contado
)

ESTRATEGIAS = (fuerza_bruta, dividir_y_vencer, kadane)
CLASICO = [-2, 1, -3, 4, -1, 2, 1, -5, 4]  # óptimo: 6, intervalos 3 a 6


def referencia_cubica(saldos: list[int]) -> int:
    """Suma máxima recalculando cada tramo desde cero.

    Args:
        saldos: Serie de saldos.

    Returns:
        La mayor suma de un tramo no vacío.
    """
    return max(
        sum(saldos[i:j + 1])
        for i in range(len(saldos))
        for j in range(i, len(saldos))
    )


def verificar_tramo(saldos: list[int], tramo: tuple[int, int, int]) -> None:
    """Comprueba que el tramo reportado existe y alcanza la suma indicada.

    Args:
        saldos: Serie de saldos.
        tramo: Tupla (suma, inicio, fin).

    Raises:
        AssertionError: Si el tramo es inválido o su suma no coincide.
    """
    suma, inicio, fin = tramo
    assert 0 <= inicio <= fin < len(saldos)
    assert sum(saldos[inicio:fin + 1]) == suma


def probar_casos_limite() -> None:
    """Verifica un elemento, solo negativos, solo positivos y empates."""
    for f in ESTRATEGIAS:
        assert f([5]) == (5, 0, 0)
        assert f([-5]) == (-5, 0, 0)
        assert f([0, 0, 0])[0] == 0
        assert f([-3, -1, -2]) == (-1, 1, 1)  # todo negativo: el mayor
        assert f([1, 2, 3]) == (6, 0, 2)
        assert f([4, -1, 2, 1]) == (6, 0, 3)
        assert f(CLASICO) == (6, 3, 6)
        assert f([7, -100, 7]) [0] == 7
        assert f([3, -3, 3])[0] == 3  # empate: la suma es única
        verificar_tramo([3, -3, 3], f([3, -3, 3]))
        assert f([5, -1, 5]) == (9, 0, 2)  # cruzar el negativo conviene


def probar_contra_referencia() -> None:
    """Compara las tres estrategias con la referencia cúbica."""
    rng = random.Random(2026)
    for _ in range(300):
        n = rng.randint(1, 25)
        saldos = [rng.randint(-30, 30) for _ in range(n)]
        esperado = referencia_cubica(saldos)
        for f in ESTRATEGIAS:
            tramo = f(saldos)
            assert tramo[0] == esperado
            verificar_tramo(saldos, tramo)


def probar_series_grandes() -> None:
    """Compara las estrategias entre sí con series sintéticas largas."""
    rng = random.Random(7)
    for semilla in range(30):
        n = rng.randint(100, 1500)
        saldos = generar_series(1, n, semilla)[0]
        resultados = [f(saldos) for f in ESTRATEGIAS]
        assert len({r[0] for r in resultados}) == 1
        for tramo in resultados:
            verificar_tramo(saldos, tramo)
    dia = generar_series(3, 228 * 3, 11)  # tres días de operación
    for saldos in dia:
        assert len({f(saldos)[0] for f in ESTRATEGIAS}) == 1


def probar_no_modifica_entrada() -> None:
    """Verifica que el archivo de entrada no se modifica."""
    saldos = generar_series(1, 400, 5)[0]
    copia = list(saldos)
    for f in ESTRATEGIAS:
        f(saldos)
        assert saldos == copia


def probar_contadores() -> None:
    """Verifica que los contadores no alteran el resultado y su orden."""
    for n in (1, 2, 3, 10, 57, 228, 1000):
        saldos = generar_series(1, n, n)[0]
        tramo_fb, ops_fb = fuerza_bruta_contado(saldos)
        tramo_dv, ops_dv = dividir_y_vencer_contado(saldos)
        tramo_k, ops_k = kadane_contado(saldos)
        assert tramo_fb == fuerza_bruta(saldos)
        assert tramo_dv == dividir_y_vencer(saldos)
        assert tramo_k == kadane(saldos)
        assert ops_fb == n * (n + 1) // 2
        assert ops_k == n
        assert ops_dv <= n * (math.ceil(math.log2(n)) + 1)


def probar_generador() -> None:
    """Verifica que los datos sintéticos son reproducibles y válidos."""
    assert generar_series(2, 50, 3) == generar_series(2, 50, 3)
    assert generar_series(1, 50, 3) != generar_series(1, 50, 4)
    assert generar_series(0, 10) == []
    assert any(v < 0 for v in generar_series(1, 300, 1)[0])
    assert any(v > 0 for v in generar_series(1, 300, 1)[0])
    try:
        generar_series(1, -1)
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError para n negativo.")


def probar_entradas_invalidas() -> None:
    """Verifica que la serie vacía se rechaza."""
    funciones = ESTRATEGIAS + (
        fuerza_bruta_contado, dividir_y_vencer_contado, kadane_contado
    )
    for f in funciones:
        try:
            f([])
        except ValueError:
            continue
        raise AssertionError("Se esperaba ValueError para serie vacía.")


def ejecutar_pruebas() -> None:
    """Ejecuta todas las pruebas de la operación de franjas de congestión."""
    probar_casos_limite()
    probar_contra_referencia()
    probar_series_grandes()
    probar_no_modifica_entrada()
    probar_contadores()
    probar_generador()
    probar_entradas_invalidas()
    print("Todas las pruebas de franjas de congestión fueron superadas.")


if __name__ == "__main__":
    ejecutar_pruebas()
