"""Línea base: la regla simplificada que usa hoy el sistema."""

from estrategia import (
    DIAS_MES, DIAS_SEMANA, MENSUAL, SEMANAL, costo_dia, validar_viajes
)


def costo_regla_actual(viajes_por_dia: list[int]) -> int:
    """Calcula lo que cobra hoy la regla simplificada del sistema.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.

    Returns:
        El costo cobrado en pesos.
    """
    validar_viajes(viajes_por_dia)
    n = len(viajes_por_dia)
    primero = next((i for i, v in enumerate(viajes_por_dia) if v > 0), n)
    total = 0
    inicio_mes = primero
    while inicio_mes < n:
        fin_mes = min(inicio_mes + DIAS_MES, n)
        cobro_mes = 0
        inicio_sem = inicio_mes
        while inicio_sem < fin_mes:
            fin_sem = min(inicio_sem + DIAS_SEMANA, fin_mes)
            bloque = viajes_por_dia[inicio_sem:fin_sem]
            suma = sum(costo_dia(v) for v in bloque)
            cobro_mes += min(suma, SEMANAL)
            inicio_sem = fin_sem
        total += min(cobro_mes, MENSUAL)
        inicio_mes = fin_mes
    return total


def costo_regla_actual_contado(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Igual que costo_regla_actual, pero cuenta los días revisados.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.

    Returns:
        Una pareja (costo cobrado en pesos, días revisados).
    """
    validar_viajes(viajes_por_dia)
    n = len(viajes_por_dia)
    primero = next((i for i, v in enumerate(viajes_por_dia) if v > 0), n)
    total = 0
    revisados = 0
    inicio_mes = primero
    while inicio_mes < n:
        fin_mes = min(inicio_mes + DIAS_MES, n)
        cobro_mes = 0
        inicio_sem = inicio_mes
        while inicio_sem < fin_mes:
            fin_sem = min(inicio_sem + DIAS_SEMANA, fin_mes)
            suma = 0
            for v in viajes_por_dia[inicio_sem:fin_sem]:
                suma += costo_dia(v)
                revisados += 1
            cobro_mes += min(suma, SEMANAL)
            inicio_sem = fin_sem
        total += min(cobro_mes, MENSUAL)
        inicio_mes = fin_mes
    return total, revisados
