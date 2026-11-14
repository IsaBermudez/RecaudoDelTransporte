"""Mediciones de tiempo y operaciones; genera las dos gráficas del Caso 1."""

import math
import statistics
import time
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from datos import generar_instancias  # noqa: E402
from estrategia import costo_minimo, costo_minimo_contado  # noqa: E402
from exhaustivo import (  # noqa: E402
    costo_exhaustivo, costo_exhaustivo_contado
)
from regla_actual import (  # noqa: E402
    costo_regla_actual, costo_regla_actual_contado
)

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "graficas" / "tope_tarifario"
SEMILLA = 2026
PROB_DIA = 0.95          # "todos o casi todos" los días con viaje
MAX_VIAJES = 4
INSTANCIAS_POR_TAMANO = 3
TAMANOS_COMPARACION = [10, 15, 20, 25, 30, 40, 50, 60]
TAMANOS_ESCALA = [30 * 2 ** k for k in range(0, 13)]  # 30 ... 122880 días
TARJETAS_REALES = 950_000
POTENCIA_KW = 0.5        # 500 W
VENTANA_H = 4.0
CIERRES_POR_ANIO = 12


def tiempo_medio(
    funcion: Callable[[list[int]], int],
    datos: list[int],
    repeticiones: int,
) -> float:
    """Mide solo la ejecución de una función sobre datos ya generados.

    Args:
        funcion: Función de costo que se mide.
        datos: Instancia de entrada ya construida.
        repeticiones: Cantidad de ejecuciones cronometradas.

    Returns:
        Tiempo medio por ejecución en segundos.
    """
    muestras = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion(datos)
        muestras.append(time.perf_counter() - inicio)
    return statistics.mean(muestras)


def _repeticiones_exhaustivo(n: int) -> int:
    """Elige cuántas repeticiones cronometrar según el costo esperado.

    Args:
        n: Días del periodo.

    Returns:
        Número de repeticiones para la solución exhaustiva.
    """
    if n <= 30:
        return 5
    return 2 if n <= 45 else 1


def medir_comparacion() -> list[dict[str, float]]:
    """Mide DP, exhaustiva y regla actual en tamaños donde las tres corren.

    Returns:
        Una fila por tamaño con tiempos (s) y operaciones (promedio sobre
        las instancias de ese tamaño).

    Raises:
        AssertionError: Si la DP y la exhaustiva difieren en alguna instancia.
    """
    filas = []
    for n in TAMANOS_COMPARACION:
        instancias = generar_instancias(
            INSTANCIAS_POR_TAMANO, n, MAX_VIAJES, SEMILLA + n, PROB_DIA
        )
        acumulado: dict[str, list[float]] = {
            "t_dp": [], "t_ex": [], "t_regla": [],
            "ops_dp": [], "ops_ex": [], "ops_regla": [],
        }
        for datos in instancias:
            valor_dp, ops_dp = costo_minimo_contado(datos)
            valor_ex, ops_ex = costo_exhaustivo_contado(datos)
            _, ops_regla = costo_regla_actual_contado(datos)
            if valor_dp != valor_ex:
                raise AssertionError(f"DP y exhaustiva difieren en n={n}.")
            acumulado["ops_dp"].append(ops_dp)
            acumulado["ops_ex"].append(ops_ex)
            acumulado["ops_regla"].append(ops_regla)
            acumulado["t_dp"].append(tiempo_medio(costo_minimo, datos, 200))
            acumulado["t_ex"].append(tiempo_medio(
                costo_exhaustivo, datos, _repeticiones_exhaustivo(n)))
            acumulado["t_regla"].append(
                tiempo_medio(costo_regla_actual, datos, 200))
        fila = {"n_dias": float(n)}
        fila.update({k: statistics.mean(v) for k, v in acumulado.items()})
        filas.append(fila)
    return filas


def medir_escala() -> list[dict[str, float]]:
    """Mide solo DP y regla actual en tamaños mucho mayores (extrapolación).

    Returns:
        Una fila por tamaño con tiempos (s) y operaciones.
    """
    filas = []
    for n in TAMANOS_ESCALA:
        datos = generar_instancias(1, n, MAX_VIAJES, SEMILLA + n, PROB_DIA)[0]
        repeticiones = max(3, 4000 // max(1, n // 30))
        repeticiones = min(repeticiones, 200)
        filas.append({
            "n_dias": float(n),
            "t_dp": tiempo_medio(costo_minimo, datos, repeticiones),
            "t_regla": tiempo_medio(costo_regla_actual, datos, repeticiones),
            "ops_dp": float(costo_minimo_contado(datos)[1]),
            "ops_regla": float(costo_regla_actual_contado(datos)[1]),
        })
    return filas


def graficar_comparacion(filas: list[dict[str, float]]) -> None:
    """Guarda tiempo_vs_n.png y operaciones_vs_n.png.

    Args:
        filas: Resultado de medir_comparacion.
    """
    SALIDA.mkdir(parents=True, exist_ok=True)
    x = [f["n_dias"] for f in filas]
    for archivo, claves, ylabel, titulo in [
        ("tiempo_vs_n.png",
         [("t_dp", "Programación dinámica"),
          ("t_ex", "Solución exhaustiva"),
          ("t_regla", "Regla actual")],
         "Tiempo medio de ejecución (segundos, escala log)",
         "Tope tarifario: tiempo de ejecución frente a los días del periodo"),
        ("operaciones_vs_n.png",
         [("ops_dp", "Programación dinámica (celdas calculadas)"),
          ("ops_ex", "Solución exhaustiva (llamadas recursivas)"),
          ("ops_regla", "Regla actual (días revisados; igual a la DP)")],
         "Operaciones elementales (conteo, escala log)",
         "Tope tarifario: operaciones frente a los días del periodo"),
    ]:
        plt.figure(figsize=(8, 5))
        estilos = {
            "dp": {"marker": "o", "markersize": 10, "linewidth": 3},
            "ex": {"marker": "s", "markersize": 6, "linewidth": 1.8},
            "regla": {"marker": "x", "markersize": 8, "linewidth": 1.5,
                      "linestyle": "--", "color": "tab:green"},
        }
        for clave, etiqueta in claves:
            estilo = estilos[clave.split("_")[-1]]
            plt.plot(x, [f[clave] for f in filas], label=etiqueta, **estilo)
        plt.yscale("log")
        plt.xlabel("Días del periodo (días)")
        plt.ylabel(ylabel)
        plt.title(titulo)
        plt.legend()
        plt.grid(True, which="both", alpha=0.4)
        plt.tight_layout()
        plt.savefig(SALIDA / archivo, dpi=160)
        plt.close()


def factores_al_duplicar(filas: list[dict[str, float]]) -> None:
    """Imprime cuánto se multiplicó cada medida al duplicar el tamaño.

    Args:
        filas: Resultado de medir_comparacion.
    """
    por_n = {int(f["n_dias"]): f for f in filas}
    print("\nFactor de crecimiento al duplicar el tamaño:")
    for a in sorted(por_n):
        b = 2 * a
        if b in por_n:
            fa, fb = por_n[a], por_n[b]
            print(f"  {a:>3} -> {b:>3} días | "
                  + " | ".join(
                      f"{k}: x{fb[k] / fa[k]:.2f}"
                      for k in ("t_dp", "t_ex", "t_regla",
                                "ops_dp", "ops_ex", "ops_regla")))


def extrapolar(filas: list[dict[str, float]]) -> None:
    """Estima tiempo y energía en el volumen real (estimación, no medición).

    Args:
        filas: Resultado de medir_comparacion (para estimar el crecimiento
            de la exhaustiva).
    """
    tarjetas = generar_instancias(300, 31, 5, SEMILLA, prob_dia=0.8)

    def por_tarjeta(funcion: Callable[[list[int]], int], rep: int) -> float:
        """Mide el tiempo medio por tarjeta sobre el lote de 31 días.

        Args:
            funcion: Función de costo que se mide.
            rep: Veces que se recorre todo el lote.

        Returns:
            Tiempo medio por tarjeta en segundos.
        """
        inicio = time.perf_counter()
        for _ in range(rep):
            for t in tarjetas:
                funcion(t)
        return (time.perf_counter() - inicio) / (rep * len(tarjetas))

    tiempos = {
        "Programación dinámica": por_tarjeta(costo_minimo, 10),
        "Regla actual": por_tarjeta(costo_regla_actual, 10),
        "Solución exhaustiva": por_tarjeta(costo_exhaustivo, 1),
    }
    print("\nExtrapolación a 950.000 tarjetas (31 días, 500 W):")
    for nombre, t in tiempos.items():
        total_s = t * TARJETAS_REALES
        horas = total_s / 3600
        kwh = POTENCIA_KW * horas
        cabe = "cabe" if horas <= VENTANA_H else "NO cabe"
        print(f"  {nombre:<22} {t * 1e6:8.1f} us/tarjeta -> "
              f"{total_s:9.1f} s = {horas:.4f} h ({cabe} en 4 h) | "
              f"{kwh:.5f} kWh/cierre | {kwh * CIERRES_POR_ANIO:.4f} kWh/año")
    dif = (tiempos["Programación dinámica"] - tiempos["Regla actual"])
    kwh_dif = POTENCIA_KW * dif * TARJETAS_REALES / 3600 * CIERRES_POR_ANIO
    print(f"  Diferencia DP - regla actual: {kwh_dif:.5f} kWh/año "
          "(positiva = la DP consume más)")
    # crecimiento de la exhaustiva entre los dos tamaños mayores medidos
    a, b = filas[-2], filas[-1]
    por_dia = (b["ops_ex"] / a["ops_ex"]) ** (1 / (b["n_dias"] - a["n_dias"]))
    print(f"  Exhaustiva: las llamadas crecen ~x{por_dia:.3f} por cada día "
          f"extra (x{por_dia ** 30:.0f} por 30 días más).")
    t60 = b["t_ex"]
    for d in (90, 120, 180):
        horas = t60 * por_dia ** (d - b["n_dias"]) / 3600
        print(f"    estimado a {d} días: {horas:.3g} h por tarjeta"
              f" ({'inviable' if horas * TARJETAS_REALES > 1e4 else 'ok'})")
    cuantos = math.floor(VENTANA_H * 3600 / tiempos["Solución exhaustiva"])
    print(f"  En 4 h la exhaustiva liquidaría ~{cuantos:,} tarjetas de "
          f"31 días (el mes real exige {TARJETAS_REALES:,}).")


def ejecutar_experimentos() -> None:
    """Corre los experimentos, guarda las dos gráficas e imprime las tablas."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    comparacion = medir_comparacion()
    escala = medir_escala()
    graficar_comparacion(comparacion)
    for fila in comparacion:
        print({k: round(v, 8) for k, v in fila.items()})
    factores_al_duplicar(comparacion)
    extrapolar(comparacion)
    print("\nDP a gran escala:")
    for fila in escala[::3]:
        print({k: round(v, 8) for k, v in fila.items()})


if __name__ == "__main__":
    ejecutar_experimentos()
