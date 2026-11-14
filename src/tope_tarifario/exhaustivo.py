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



