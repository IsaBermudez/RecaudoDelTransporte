"""Generación de series sintéticas de saldo neto por intervalo de 5 minutos."""

import random

INTERVALOS_DIA = 228  # operación de 04:30 a 23:30, en intervalos de 5 minutos
DIAS_HISTORICO = 730  # dos años
ESTACIONES = 80

# Franjas pico (índice del intervalo dentro del día): 06:30-08:30 y 16:30-19:30.
PICOS = ((24, 48), (144, 180))
SESGO_BASE = -8   # fuera de las horas pico los trenes evacuan más de lo que entra
SESGO_PICO = 22   # en hora pico entran más pasajeros de los que se evacuan


def _sesgo(intervalo: int) -> int:
    """Devuelve el sesgo promedio del saldo según la hora del día.

    Args:
        intervalo: Índice del intervalo dentro del día (0 es las 04:30).

    Returns:
        Sesgo (pasajeros por intervalo) que se suma al ruido aleatorio.
    """
    posicion = intervalo % INTERVALOS_DIA
    for inicio, fin in PICOS:
        if inicio <= posicion < fin:
            return SESGO_PICO
    return SESGO_BASE


def generar_series(
    cantidad: int,
    n: int,
    semilla: int = 42,
    amplitud: int = 40,
) -> list[list[int]]:
    """Genera series de saldo neto (entradas menos evacuados) reproducibles.

    Args:
        cantidad: Número de series.
        n: Intervalos por serie.
        semilla: Semilla pseudoaleatoria.
        amplitud: Amplitud del ruido por intervalo.

    Returns:
        Lista de series de enteros.

    Raises:
        ValueError: Si algún parámetro está fuera de rango.
    """
    if cantidad < 0 or n < 0 or amplitud < 0:
        raise ValueError("Parámetros inválidos para generar datos.")
    rng = random.Random(semilla)
    return [
        [rng.randint(-amplitud, amplitud) + _sesgo(k) for k in range(n)]
        for _ in range(cantidad)
    ]
