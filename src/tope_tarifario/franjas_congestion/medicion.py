"""Mediciones de tiempo y operaciones; genera las gráficas de congestión."""

import statistics
import time
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from datos import (  # noqa: E402
    DIAS_HISTORICO, INTERVALOS_DIA, generar_series
)
from estrategias import (  # noqa: E402
    dividir_y_vencer, dividir_y_vencer_contado, fuerza_bruta,
    fuerza_bruta_contado, kadane, kadane_contado
)

RAIZ = Path(__file__).resolve().parents[3]
SALIDA = RAIZ / "graficas" / "tope_tarifario" / "franjas_congestion"
SEMILLA = 2026
INSTANCIAS_POR_TAMANO = 3
TAMANOS_COMPARACION = [500, 1000, 2000, 4000, 8000, 16000]
TAMANOS_ESCALA = [1000 * 2 ** k for k in range(0, 11)]  # 1.000 ... 1.024.000
N_HISTORICO = DIAS_HISTORICO * INTERVALOS_DIA  # 166.440 intervalos

Funcion = Callable[[list[int]], tuple[int, int, int]]

# Un color por estrategia, el mismo en todas las gráficas.
CLAVES = ("fb", "dv", "k")
COLORES = {"fb": "#2a78d6", "dv": "#eb6834", "k": "#1baf7a"}
MARCADORES = {"fb": "s", "dv": "^", "k": "o"}
NOMBRES = {
    "fb": "Fuerza bruta (programa actual)",
    "dv": "Dividir y vencer",
    "k": "Programación dinámica (Kadane)",
}
NOMBRES_CORTOS = {"fb": "Fuerza bruta", "dv": "Dividir y vencer",
                  "k": "Kadane (PD)"}
TINTA, TINTA_2, SUPERFICIE, REJILLA = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"


def tiempo_medio(
    funcion: Funcion, datos: list[int], repeticiones: int
) -> float:
    """Mide solo la ejecución de una función sobre datos ya generados.

    Args:
        funcion: Estrategia que se mide.
        datos: Serie de entrada ya construida.
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


def _repeticiones(clave: str, n: int) -> int:
    """Elige cuántas repeticiones cronometrar según el costo esperado.

    Args:
        clave: Estrategia ("fb", "dv" o "k").
        n: Intervalos de la serie.

    Returns:
        Número de repeticiones.
    """
    if clave == "fb":
        return 5 if n <= 2000 else 3 if n <= 4000 else 1
    return min(200, max(3, 400_000 // n))


def medir_comparacion() -> list[dict[str, float]]:
    """Mide las tres estrategias en tamaños donde las tres corren.

    Returns:
        Una fila por tamaño con tiempos (s) y operaciones (promedio sobre
        las instancias de ese tamaño).

    Raises:
        AssertionError: Si las estrategias difieren en la suma máxima.
    """
    funciones = {"fb": fuerza_bruta, "dv": dividir_y_vencer, "k": kadane}
    contadas = {"fb": fuerza_bruta_contado, "dv": dividir_y_vencer_contado,
                "k": kadane_contado}
    filas = []
    for n in TAMANOS_COMPARACION:
        series = generar_series(INSTANCIAS_POR_TAMANO, n, SEMILLA + n)
        acumulado: dict[str, list[float]] = {
            f"{tipo}_{c}": [] for tipo in ("t", "ops") for c in CLAVES
        }
        for serie in series:
            sumas = set()
            for c in CLAVES:
                tramo, ops = contadas[c](serie)
                sumas.add(tramo[0])
                acumulado[f"ops_{c}"].append(ops)
                acumulado[f"t_{c}"].append(
                    tiempo_medio(funciones[c], serie, _repeticiones(c, n)))
            if len(sumas) != 1:
                raise AssertionError(f"Las estrategias difieren en n={n}.")
        fila = {"n": float(n)}
        fila.update({k: statistics.mean(v) for k, v in acumulado.items()})
        filas.append(fila)
    return filas


def medir_escala() -> list[dict[str, float]]:
    """Mide solo dividir y vencer y Kadane en tamaños mucho mayores.

    Returns:
        Una fila por tamaño con los tiempos (s) de las dos estrategias.
    """
    filas = []
    for n in TAMANOS_ESCALA:
        serie = generar_series(1, n, SEMILLA + n)[0]
        repeticiones = min(50, max(1, 2_000_000 // n))
        filas.append({
            "n": float(n),
            "t_dv": tiempo_medio(dividir_y_vencer, serie, repeticiones),
            "t_k": tiempo_medio(kadane, serie, repeticiones),
        })
    return filas


def _formato_miles(valor: float, _posicion: int) -> str:
    """Da formato con punto de miles a un valor del eje.

    Args:
        valor: Valor del eje.
        _posicion: Posición del tick (no se usa).

    Returns:
        Texto del valor con punto como separador de miles.
    """
    return f"{valor:,.0f}".replace(",", ".")


def _grafica(archivo: str, x: list[float], series: dict[str, list[float]],
             ylabel: str, titulo: str, marca_historico: bool = False) -> None:
    """Dibuja una gráfica log-log con una línea por estrategia.

    Args:
        archivo: Nombre del PNG de salida.
        x: Tamaños de entrada (intervalos).
        series: Valores del eje y por estrategia.
        ylabel: Rótulo del eje y.
        titulo: Título de la gráfica.
        marca_historico: Si es True, marca el tamaño del histórico de 2 años.
    """
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    for clave, valores in series.items():
        ax.plot(x, valores, color=COLORES[clave], marker=MARCADORES[clave],
                markersize=7, markeredgecolor=SUPERFICIE,
                markeredgewidth=1.5, linewidth=2, label=NOMBRES[clave])
        ax.annotate(NOMBRES_CORTOS[clave], (x[-1], valores[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    va="center", color=TINTA_2, fontsize=9)
    if marca_historico:
        ax.axvline(N_HISTORICO, color=TINTA_2, linestyle=":", linewidth=1.2)
        ax.annotate("histórico de 2 años\n(166.440 intervalos)",
                    xy=(N_HISTORICO, 0.04),
                    xycoords=("data", "axes fraction"),
                    xytext=(-6, 0), textcoords="offset points",
                    ha="right", va="bottom", color=TINTA_2, fontsize=9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(x[0] / 1.3, x[-1] * 4.5)
    ax.set_xticks(x)
    ax.xaxis.set_major_formatter(FuncFormatter(_formato_miles))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_xlabel("Intervalos de 5 minutos en la serie (n, escala log)",
                  color=TINTA_2)
    ax.set_ylabel(ylabel, color=TINTA_2)
    ax.set_title(titulo, color=TINTA, loc="left", fontsize=12)
    ax.grid(True, which="major", color=REJILLA, linewidth=0.8)
    ax.tick_params(colors=TINTA_2)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.legend(loc="upper left", frameon=False, labelcolor=TINTA_2,
              fontsize=9)
    fig.tight_layout()
    fig.savefig(SALIDA / archivo, dpi=160, facecolor=SUPERFICIE)
    plt.close(fig)


def graficar(comparacion: list[dict[str, float]],
             escala: list[dict[str, float]]) -> None:
    """Guarda tiempo_vs_n.png, operaciones_vs_n.png y tiempo_escala.png.

    Args:
        comparacion: Resultado de medir_comparacion.
        escala: Resultado de medir_escala.
    """
    SALIDA.mkdir(parents=True, exist_ok=True)
    x = [f["n"] for f in comparacion]
    _grafica("tiempo_vs_n.png", x,
             {c: [f[f"t_{c}"] for f in comparacion] for c in CLAVES},
             "Tiempo medio de ejecución (segundos, escala log)",
             "Franjas de congestión: tiempo frente al tamaño de la serie")
    _grafica("operaciones_vs_n.png", x,
             {c: [f[f"ops_{c}"] for f in comparacion] for c in CLAVES},
             "Operaciones elementales (conteo, escala log)",
             "Franjas de congestión: operaciones frente al tamaño de la serie")
    _grafica("tiempo_escala.png", [f["n"] for f in escala],
             {c: [f[f"t_{c}"] for f in escala] for c in ("dv", "k")},
             "Tiempo medio de ejecución (segundos, escala log)",
             "Dividir y vencer y Kadane a gran escala", marca_historico=True)


def ejecutar_experimentos() -> None:
    """Corre los experimentos y guarda únicamente las gráficas."""
    comparacion = medir_comparacion()
    escala = medir_escala()
    graficar(comparacion, escala)


if __name__ == "__main__":
    ejecutar_experimentos()
