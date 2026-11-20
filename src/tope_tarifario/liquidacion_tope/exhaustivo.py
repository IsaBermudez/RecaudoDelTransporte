"""Soluciones exhaustivas para verificar el costo mínimo."""

from itertools import product

from estrategia import (
    DIAS_MES, DIAS_SEMANA, MENSUAL, SEMANAL, costo_dia, validar_viajes
)


def _resolver(viajes: list[int], dia: int, contador: list[int]) -> int:
    """Explora todas las decisiones desde el primer día sin cubrir.

    Args:
        viajes: Viajes por día.
        dia: Primer día aún no cubierto.
        contador: Contador mutable de llamadas recursivas.

    Returns:
        Costo mínimo de cubrir desde ese día en adelante.
    """
    contador[0] += 1
    if dia >= len(viajes):
        return 0
    if viajes[dia] == 0:
        return _resolver(viajes, dia + 1, contador)
    return min(
        costo_dia(viajes[dia]) + _resolver(viajes, dia + 1, contador),
        SEMANAL + _resolver(viajes, dia + DIAS_SEMANA, contador),
        MENSUAL + _resolver(viajes, dia + DIAS_MES, contador),
    )


def costo_exhaustivo(viajes_por_dia: list[int]) -> int:
    """Calcula el costo mínimo probando todas las decisiones recursivas.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.

    Returns:
        El costo mínimo en pesos.
    """
    validar_viajes(viajes_por_dia)
    return _resolver(viajes_por_dia, 0, [0])


def costo_exhaustivo_contado(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Calcula el costo exhaustivo y cuenta las llamadas recursivas.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.

    Returns:
        Una pareja (costo mínimo en pesos, número de llamadas).
    """
    validar_viajes(viajes_por_dia)
    contador = [0]
    costo = _resolver(viajes_por_dia, 0, contador)
    return costo, contador[0]


def costo_fuerza_bruta(viajes_por_dia: list[int]) -> int:
    """Prueba TODOS los subconjuntos de pases (verifica el modelo).

    Args:
        viajes_por_dia: Viajes de la tarjeta (máximo 7 días).

    Returns:
        El costo mínimo en pesos.

    Raises:
        ValueError: Si la instancia tiene más de 7 días.
    """
    validar_viajes(viajes_por_dia)
    n = len(viajes_por_dia)
    if n > 7:
        raise ValueError("La fuerza bruta solo admite instancias de 7 días.")
    mejor = float("inf")
    for eleccion in product((False, True), repeat=2 * n):
        costo = 0
        cubierto = [False] * n
        for dia in range(n):
            if eleccion[2 * dia]:
                costo += SEMANAL
                for k in range(dia, min(dia + DIAS_SEMANA, n)):
                    cubierto[k] = True
            if eleccion[2 * dia + 1]:
                costo += MENSUAL
                for k in range(dia, min(dia + DIAS_MES, n)):
                    cubierto[k] = True
        costo += sum(costo_dia(v) for v, c in zip(viajes_por_dia, cubierto)
                     if not c)
        mejor = min(mejor, costo)
    return int(mejor)
