"""Generación de instancias sintéticas reproducibles."""

import random


def generar_instancias(
    cantidad: int,
    dias: int = 30,
    max_viajes: int = 5,
    semilla: int = 42,
    prob_dia: float = 1.0,
) -> list[list[int]]:
    """Genera series de viajes por día con semilla fija.

    Args:
        cantidad: Número de instancias.
        dias: Días por instancia.
        max_viajes: Máximo de viajes en un día con viajes.
        semilla: Semilla pseudoaleatoria.
        prob_dia: Probabilidad de que un día tenga al menos un viaje.

    Returns:
        Instancias sintéticas de viajes diarios.

    Raises:
        ValueError: Si algún parámetro está fuera de rango.
    """
    if cantidad < 0 or dias < 0 or max_viajes < 1:
        raise ValueError("Parámetros inválidos para generar datos.")
    if not 0.0 <= prob_dia <= 1.0:
        raise ValueError("prob_dia debe estar entre 0 y 1.")
    rng = random.Random(semilla)
    return [
        [rng.randint(1, max_viajes) if rng.random() < prob_dia else 0
         for _ in range(dias)]
        for _ in range(cantidad)
    ]
