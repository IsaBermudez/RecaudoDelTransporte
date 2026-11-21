"""Franja de congestión: tramo consecutivo de mayor acumulación."""

Tramo = tuple[int, int, int]


def validar_serie(saldos: list[int]) -> None:
    """Valida que la serie tenga al menos un intervalo.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Raises:
        ValueError: Si la serie está vacía.
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")


# Estrategia 1: fuerza bruta - línea base

def fuerza_bruta(saldos: list[int]) -> Tramo:
    """Evalúa todos los tramos posibles, acumulando la suma sobre la marcha.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        El tramo (suma, inicio, fin) de mayor acumulación.
    """
    validar_serie(saldos)
    n = len(saldos)
    mejor, mejor_i, mejor_j = saldos[0], 0, 0
    for i in range(n):
        acumulado = 0
        for j in range(i, n):
            acumulado += saldos[j]
            if acumulado > mejor:
                mejor, mejor_i, mejor_j = acumulado, i, j
    return mejor, mejor_i, mejor_j


def fuerza_bruta_contado(saldos: list[int]) -> tuple[Tramo, int]:
    """Igual que fuerza_bruta, pero cuenta los tramos evaluados.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        Una pareja (tramo óptimo, tramos evaluados).
    """
    validar_serie(saldos)
    n = len(saldos)
    mejor, mejor_i, mejor_j = saldos[0], 0, 0
    evaluados = 0
    for i in range(n):
        acumulado = 0
        for j in range(i, n):
            acumulado += saldos[j]
            evaluados += 1
            if acumulado > mejor:
                mejor, mejor_i, mejor_j = acumulado, i, j
    return (mejor, mejor_i, mejor_j), evaluados


# Estrategia 2: dividir y vencer

def _cruce(saldos: list[int], lo: int, mid: int, hi: int) -> Tramo:
    """Mejor tramo que contiene los intervalos mid y mid + 1.

    Args:
        saldos: Serie completa.
        lo: Primer índice de la mitad actual.
        mid: Último índice de la mitad izquierda.
        hi: Último índice de la mitad actual.

    Returns:
        El mejor tramo (suma, inicio, fin) que cruza el punto medio.
    """
    acumulado = 0
    mejor_izq, inicio = saldos[mid], mid
    for i in range(mid, lo - 1, -1):
        acumulado += saldos[i]
        if acumulado > mejor_izq:
            mejor_izq, inicio = acumulado, i
    acumulado = 0
    mejor_der, fin = saldos[mid + 1], mid + 1
    for j in range(mid + 1, hi + 1):
        acumulado += saldos[j]
        if acumulado > mejor_der:
            mejor_der, fin = acumulado, j
    return mejor_izq + mejor_der, inicio, fin


def _dividir(saldos: list[int], lo: int, hi: int) -> Tramo:
    """Resuelve el rango [lo, hi] dividiéndolo por la mitad.

    Args:
        saldos: Serie completa (no se copian porciones: se usan índices).
        lo: Primer índice del rango.
        hi: Último índice del rango.

    Returns:
        El mejor tramo (suma, inicio, fin) dentro del rango.
    """
    if lo == hi:
        return saldos[lo], lo, lo
    mid = (lo + hi) // 2
    mejor = _dividir(saldos, lo, mid)
    cruce = _cruce(saldos, lo, mid, hi)
    if cruce[0] > mejor[0]:
        mejor = cruce
    derecha = _dividir(saldos, mid + 1, hi)
    if derecha[0] > mejor[0]:
        mejor = derecha
    return mejor


def dividir_y_vencer(saldos: list[int]) -> Tramo:
    """Divide la serie por la mitad y combina: izquierda, derecha o cruce.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        El tramo (suma, inicio, fin) de mayor acumulación.
    """
    validar_serie(saldos)
    return _dividir(saldos, 0, len(saldos) - 1)


def _cruce_contado(
    saldos: list[int], lo: int, mid: int, hi: int, contador: list[int]
) -> Tramo:
    """Igual que _cruce, pero suma al contador los intervalos visitados.

    Args:
        saldos: Serie completa.
        lo: Primer índice de la mitad actual.
        mid: Último índice de la mitad izquierda.
        hi: Último índice de la mitad actual.
        contador: Contador mutable de intervalos visitados.

    Returns:
        El mejor tramo (suma, inicio, fin) que cruza el punto medio.
    """
    acumulado = 0
    mejor_izq, inicio = saldos[mid], mid
    for i in range(mid, lo - 1, -1):
        contador[0] += 1
        acumulado += saldos[i]
        if acumulado > mejor_izq:
            mejor_izq, inicio = acumulado, i
    acumulado = 0
    mejor_der, fin = saldos[mid + 1], mid + 1
    for j in range(mid + 1, hi + 1):
        contador[0] += 1
        acumulado += saldos[j]
        if acumulado > mejor_der:
            mejor_der, fin = acumulado, j
    return mejor_izq + mejor_der, inicio, fin


def _dividir_contado(
    saldos: list[int], lo: int, hi: int, contador: list[int]
) -> Tramo:
    """Igual que _dividir, pero cuenta los intervalos visitados.

    Args:
        saldos: Serie completa.
        lo: Primer índice del rango.
        hi: Último índice del rango.
        contador: Contador mutable de intervalos visitados.

    Returns:
        El mejor tramo (suma, inicio, fin) dentro del rango.
    """
    if lo == hi:
        contador[0] += 1
        return saldos[lo], lo, lo
    mid = (lo + hi) // 2
    mejor = _dividir_contado(saldos, lo, mid, contador)
    cruce = _cruce_contado(saldos, lo, mid, hi, contador)
    if cruce[0] > mejor[0]:
        mejor = cruce
    derecha = _dividir_contado(saldos, mid + 1, hi, contador)
    if derecha[0] > mejor[0]:
        mejor = derecha
    return mejor


def dividir_y_vencer_contado(saldos: list[int]) -> tuple[Tramo, int]:
    """Igual que dividir_y_vencer, pero cuenta los intervalos visitados.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        Una pareja (tramo óptimo, intervalos visitados).
    """
    validar_serie(saldos)
    contador = [0]
    tramo = _dividir_contado(saldos, 0, len(saldos) - 1, contador)
    return tramo, contador[0]


# Estrategia 3: programación dinámica (algoritmo de Kadane)

def kadane(saldos: list[int]) -> Tramo:
    """Programación dinámica: mejor tramo que termina en cada intervalo.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        El tramo (suma, inicio, fin) de mayor acumulación.
    """
    validar_serie(saldos)
    mejor, mejor_i, mejor_j = saldos[0], 0, 0
    actual, inicio_actual = saldos[0], 0
    for j in range(1, len(saldos)):
        if actual < 0:
            actual, inicio_actual = saldos[j], j
        else:
            actual += saldos[j]
        if actual > mejor:
            mejor, mejor_i, mejor_j = actual, inicio_actual, j
    return mejor, mejor_i, mejor_j


def kadane_contado(saldos: list[int]) -> tuple[Tramo, int]:
    """Igual que kadane, pero cuenta los intervalos revisados.

    Args:
        saldos: Saldo neto de la plataforma en cada intervalo.

    Returns:
        Una pareja (tramo óptimo, intervalos revisados).
    """
    validar_serie(saldos)
    mejor, mejor_i, mejor_j = saldos[0], 0, 0
    actual, inicio_actual = saldos[0], 0
    revisados = 1
    for j in range(1, len(saldos)):
        revisados += 1
        if actual < 0:
            actual, inicio_actual = saldos[j], j
        else:
            actual += saldos[j]
        if actual > mejor:
            mejor, mejor_i, mejor_j = actual, inicio_actual, j
    return (mejor, mejor_i, mejor_j), revisados
