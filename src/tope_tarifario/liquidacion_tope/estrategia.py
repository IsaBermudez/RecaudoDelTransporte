"""Liquidación del tope tarifario de una tarjeta (programación dinámica)."""

PASAJE = 3900
DIARIO = 9500
SEMANAL = 36000
MENSUAL = 135000
DIAS_SEMANA = 7
DIAS_MES = 30


def validar_viajes(viajes_por_dia: list[int]) -> None:
    """Valida que no existan cantidades de viajes negativas.

    Args:
        viajes_por_dia: Viajes registrados en cada día.

    Raises:
        ValueError: Si algún día tiene una cantidad negativa de viajes.
    """
    if any(v < 0 for v in viajes_por_dia):
        raise ValueError("Los viajes diarios no pueden ser negativos.")


def costo_dia(viajes: int) -> int:
    """Calcula lo más barato entre pasajes sencillos y pase diario.

    Args:
        viajes: Viajes realizados en un día.

    Returns:
        Costo del día en pesos (0 si no hubo viajes).
    """
    return min(viajes * PASAJE, DIARIO)


def costo_minimo(viajes_por_dia: list[int]) -> int:
    """Calcula el costo de la combinación más barata que cubre los viajes.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes. El índice 0
            es el primer día; un día sin viajes vale 0.

    Returns:
        El costo mínimo en pesos.
    """
    validar_viajes(viajes_por_dia)
    n = len(viajes_por_dia)
    dp = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        v = viajes_por_dia[i]
        if v == 0:
            dp[i] = dp[i + 1]
        else:
            dp[i] = min(
                costo_dia(v) + dp[i + 1],
                SEMANAL + dp[min(i + DIAS_SEMANA, n)],
                MENSUAL + dp[min(i + DIAS_MES, n)],
            )
    return dp[0]


def costo_minimo_contado(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Igual que costo_minimo, pero cuenta las celdas de la tabla calculadas.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.

    Returns:
        Una pareja (costo mínimo en pesos, celdas dp calculadas).
    """
    validar_viajes(viajes_por_dia)
    n = len(viajes_por_dia)
    dp = [0] * (n + 1)
    celdas = 0
    for i in range(n - 1, -1, -1):
        celdas += 1
        v = viajes_por_dia[i]
        if v == 0:
            dp[i] = dp[i + 1]
        else:
            dp[i] = min(
                costo_dia(v) + dp[i + 1],
                SEMANAL + dp[min(i + DIAS_SEMANA, n)],
                MENSUAL + dp[min(i + DIAS_MES, n)],
            )
    return dp[0], celdas


def liquidar_tope(viajes_por_dia: list[int], cobrado: int) -> int:
    """Calcula la devolución que corresponde al usuario.

    Args:
        viajes_por_dia: Viajes de la tarjeta en cada día del mes.
        cobrado: Pesos que se le cobraron durante el mes.

    Returns:
        La diferencia entre lo cobrado y el costo mínimo, nunca negativa.
    """
    return max(0, cobrado - costo_minimo(viajes_por_dia))
