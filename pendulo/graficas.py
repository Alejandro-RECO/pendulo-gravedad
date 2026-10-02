"""Gráficas del informe (matplotlib), con coma decimal y unidades en los ejes."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from . import modelo  # noqa: E402
from .simulacion import periodo_simulado  # noqa: E402

AZUL = "#2a78d6"
NARANJA = "#eb6834"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
REJILLA = "#e4e3df"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.edgecolor": TINTA_2,
    "axes.labelcolor": TINTA,
    "axes.titlesize": 10.5,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "axes.grid": True,
    "grid.color": REJILLA,
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def coma(x: float, dec: int) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def coma_tex(x: float, dec: int) -> str:
    """Número con coma decimal para usar dentro de $...$ (mathtext pone espacio tras una coma suelta)."""
    return f"{x:.{dec}f}".replace(".", "{,}")


def _formato_coma(ax, dx: int, dy: int) -> None:
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: coma(v, dx)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: coma(v, dy)))


def grafica_T2_vs_L(r: dict, ruta: Path) -> None:
    filas = r["filas"]
    res = r["resultado"]
    u_L = r["montaje"]["u_L_m"]
    n = r["montaje"]["n_oscilaciones"]
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    # series individuales (contexto)
    ax.plot([s.L for s in r["series"]], [s.periodo(n) ** 2 for s in r["series"]], "o",
            ms=4, mfc="none", mec=TINTA_2, mew=0.8, alpha=0.6, label="Series individuales", zorder=2)
    # medias con barras de error
    ax.errorbar([f.L for f in filas], [f.T2 for f in filas],
                xerr=[u_L] * len(filas), yerr=[f.u_T2 for f in filas],
                fmt="o", ms=6, color=AZUL, mec="white", mew=1, ecolor=AZUL, elinewidth=1.2,
                capsize=3, label="Promedio por longitud", zorder=3)
    ex = r.get("filas_excluidas") or []
    if ex:
        ax.plot([f.L for f in ex], [f.T2 for f in ex], "s", ms=6, mfc="white", mec=NARANJA, mew=1.4,
                label="Excluidas del ajuste (2 repeticiones)", zorder=3)
    xs = [0, 1.08]
    ax.plot(xs, [res["m"] * v + res["b"] for v in xs], "-", color=NARANJA, lw=2,
            label="Ajuste por mínimos cuadrados", zorder=1)
    ec = (f"$T^2 = ({coma_tex(res['m'], 3)} \\pm {coma_tex(res['u_m'], 3)})\\,L"
          f" + ({coma_tex(res['b'], 3)} \\pm {coma_tex(res['u_b'], 3)})$\n"
          f"$R^2 = {coma_tex(res['r2'], 4)}$\n"
          "Barras de error menores que el marcador")
    ax.text(0.03, 0.97, ec, transform=ax.transAxes, va="top", fontsize=9.5, color=TINTA)
    ax.set_xlim(0, 1.08)
    ax.set_ylim(0, 4.6)
    ax.set_xlabel("Longitud del péndulo, $L$ (m)")
    ax.set_ylabel("Cuadrado del periodo, $T^2$ (s$^2$)")
    ax.set_title("Cuadrado del periodo en función de la longitud del péndulo")
    ax.legend(loc="lower right", fontsize=9)
    _formato_coma(ax, 1, 1)
    fig.savefig(ruta)
    plt.close(fig)


def grafica_residuos(r: dict, ruta: Path) -> None:
    filas = r["filas"]
    res = r["resultado"]
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    ax.axhline(0, color=TINTA_2, lw=1)
    ax.errorbar([f.L for f in filas], res["residuos"], yerr=[f.u_T2 for f in filas],
                fmt="o", ms=6, color=AZUL, mec="white", mew=1, elinewidth=1.2, capsize=3,
                label="Usadas en el ajuste")
    ex = r.get("filas_excluidas") or []
    res_ex = [f.T2 - (res["m"] * f.L + res["b"]) for f in ex]
    if ex:
        ax.errorbar([f.L for f in ex], res_ex, yerr=[f.u_T2 for f in ex], fmt="s", ms=6, mfc="white",
                    mec=NARANJA, mew=1.4, ecolor=NARANJA, elinewidth=1, capsize=3,
                    label="Excluidas del ajuste (no lo determinan)")
        ax.legend(loc="lower left", fontsize=8.5)
    ax.set_xlim(0, 1.08)
    todos = list(res["residuos"]) + res_ex
    lim = max(max(abs(e) for e in todos) + max(f.u_T2 for f in filas), 0.05) * 1.25
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("Longitud del péndulo, $L$ (m)")
    ax.set_ylabel("Residuo de $T^2$ (s$^2$)")
    ax.set_title("Residuos del ajuste lineal de $T^2$ frente a $L$")
    _formato_coma(ax, 1, 2)
    fig.savefig(ruta)
    plt.close(fig)


def grafica_vueltas(r: dict, ruta: Path) -> None:
    d = r["desv_vueltas"]
    sig = r["sigma_vuelta"]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    ancho = 0.02
    bins = [i * ancho - 0.25 for i in range(int(0.5 / ancho) + 1)]
    ax.hist(d, bins=bins, color=AZUL, edgecolor="white", linewidth=1)
    for k in (-1, 1):
        ax.axvline(k * sig, color=NARANJA, lw=1.5, ls="--")
    ax.text(sig + 0.008, ax.get_ylim()[1] * 0.9, f"$\\pm\\sigma = \\pm{coma_tex(sig, 3)}$ s",
            color=TINTA, fontsize=9)
    ax.set_xlabel("Diferencia entre cada vuelta y el promedio de su serie (s)")
    ax.set_ylabel("Número de vueltas")
    ax.set_title(f"Dispersión de los periodos individuales ({len(d)} vueltas, {r['n_series']} series)")
    _formato_coma(ax, 2, 0)
    fig.savefig(ruta)
    plt.close(fig)


def grafica_amplitud(montaje: dict, ruta: Path) -> list[tuple[float, float, float, float]]:
    """Error de la aproximación de ángulo pequeño: simulación vs. ec. (5) vs. exacto."""
    g = montaje["g_referencia"]
    L = 1.0
    T0 = modelo.periodo_pequeno(L, g)
    angulos = [2, 5, 9, 15, 20, 30, 40, 50, 60]
    tabla = []
    for a in angulos:
        th = math.radians(a)
        sim = periodo_simulado(L, g, th) / T0
        tabla.append((a, (sim - 1) * 100, (modelo.factor_amplitud_serie(th) - 1) * 100,
                      (modelo.factor_amplitud_exacto(th) - 1) * 100))
    fino = [i * 0.5 for i in range(0, 121)]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(fino, [(modelo.factor_amplitud_exacto(math.radians(a)) - 1) * 100 for a in fino],
            color=TINTA_2, lw=1, ls=":", label="Solución exacta (integral elíptica)")
    ax.plot(fino, [(modelo.factor_amplitud_serie(math.radians(a)) - 1) * 100 for a in fino],
            color=NARANJA, lw=2, label="Aproximación, ec. (5)")
    ax.plot([t[0] for t in tabla], [t[1] for t in tabla], "o", ms=6, color=AZUL, mec="white",
            mew=1, label="Simulación numérica (RK4)", zorder=3)
    a9 = montaje["amplitud_grados"]
    e9 = (modelo.factor_amplitud_exacto(math.radians(a9)) - 1) * 100
    ax.annotate(f"{coma(a9, 0)}°: +{coma(e9, 2)} %", xy=(a9, e9), xytext=(a9 + 5, e9 + 2.2),
                arrowprops=dict(arrowstyle="-", color=TINTA_2, lw=0.8), fontsize=9, color=TINTA)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 8)
    ax.set_xlabel(r"Amplitud angular inicial, $\theta_0$ (°)")
    ax.set_ylabel(r"Aumento del periodo, $(T/T_0 - 1)$ (%)")
    ax.set_title("Efecto de la amplitud sobre el periodo del péndulo")
    ax.legend(loc="upper left", fontsize=9)
    _formato_coma(ax, 0, 0)
    fig.savefig(ruta)
    plt.close(fig)
    return tabla
