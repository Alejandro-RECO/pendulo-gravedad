"""Gráficas de la aplicación. Regla del grupo: el tiempo (T, T² o t) siempre en el eje x.

El ajuste es el mismo de analisis.py (T² = m·L + b, g = 4π²/m). Aquí solo se dibuja con los ejes
intercambiados, así que la recta aparece como L = (T² − b)/m. Los números no cambian.
"""
from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from . import modelo  # noqa: E402
from .simulacion import integrar, periodo_simulado  # noqa: E402

AZUL = "#1f4e79"
ROJO = "#c0392b"
GRIS = "#7f8c8d"
VERDE = "#2e7d32"
NARANJA = "#e67e22"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
})


def coma(x: float, dec: int) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def _ejes(ax, titulo, x, y):
    ax.set_title(titulo)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    f = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    ax.xaxis.set_major_formatter(f)
    ax.yaxis.set_major_formatter(f)


def _figura(alto=4.2):
    return plt.subplots(figsize=(6.4, alto), dpi=100)


def recta(r):
    """L vs T²: promedios con barras de error, recta del ajuste y recta teórica."""
    filas, res, u_L = r["filas"], r["resultado"], r["montaje"]["u_L_m"]
    g_ref = r["montaje"]["g_referencia"]
    fig, ax = _figura()
    ax.errorbar([f.T2 for f in filas], [f.L for f in filas], xerr=[f.u_T2 for f in filas],
                yerr=u_L, fmt="o", color=AZUL, ecolor="#555", capsize=3, label="Promedio de 3 mediciones")
    ex = r["filas_excluidas"]
    if ex:
        ax.plot([f.T2 for f in ex], [f.L for f in ex], "s", mfc="white", mec=NARANJA, mew=1.5,
                label="0,70 y 0,90 m (solo para validar)")
    xs = [0, max(f.T2 for f in filas) * 1.08]
    signo = "+" if res["b"] >= 0 else "−"
    ax.plot(xs, [(x - res["b"]) / res["m"] for x in xs], color=ROJO,
            label=f"Ajuste: T² = {coma(res['m'], 3)} L {signo} {coma(abs(res['b']), 3)}  (R² = {coma(res['r2'], 4)})")
    ax.plot(xs, [g_ref * x / (4 * math.pi ** 2) for x in xs], "--", color=GRIS, lw=1,
            label=f"Teórica con g = {coma(g_ref, 3)} m/s²")
    _ejes(ax, "Longitud en función del cuadrado del periodo", "T² (s²)", "Longitud L (m)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    return fig


def parabola(r):
    """L vs T: la relación sin linealizar, L = g (T/2π)²."""
    filas, res, u_L = r["filas"], r["resultado"], r["montaje"]["u_L_m"]
    g_ref = r["montaje"]["g_referencia"]
    fig, ax = _figura()
    ax.errorbar([f.T for f in filas], [f.L for f in filas], xerr=[f.u_T for f in filas], yerr=u_L,
                fmt="o", color=AZUL, ecolor="#555", capsize=3, label="Promedio de 3 mediciones")
    tmax = max(f.T for f in filas) * 1.08
    ts = [tmax * i / 200 for i in range(201)]
    ax.plot(ts, [res["g"] * (t / (2 * math.pi)) ** 2 for t in ts], color=ROJO,
            label=f"L = g(T/2π)² con g = {coma(res['g'], 2)} m/s² (medido)")
    ax.plot(ts, [g_ref * (t / (2 * math.pi)) ** 2 for t in ts], "--", color=GRIS, lw=1,
            label=f"L = g(T/2π)² con g = {coma(g_ref, 3)} m/s²")
    _ejes(ax, "Longitud en función del periodo", "Periodo T (s)", "Longitud L (m)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    return fig


def residuos(r):
    """Diferencia entre el T² medido y el que da la recta."""
    filas, res = r["filas"], r["resultado"]
    fig, ax = _figura(3.6)
    ax.errorbar([f.T2 for f in filas], res["residuos"], yerr=[f.u_T2 for f in filas],
                fmt="s", color=AZUL, ecolor="#555", capsize=3)
    ax.axhline(0, color=ROJO, lw=1)
    _ejes(ax, "Residuos del ajuste", "T² (s²)", "T² medido − T² de la recta (s²)")
    fig.tight_layout()
    return fig


def g_por_longitud(r):
    """g calculada con cada longitud por separado, ubicada según su periodo."""
    filas, res, m = r["filas"], r["resultado"], r["montaje"]
    fig, ax = _figura(3.8)
    ax.errorbar([f.T for f in filas], [f.g_i for f in filas], xerr=[f.u_T for f in filas],
                yerr=[f.u_g_i for f in filas], fmt="o", color=AZUL, ecolor="#555", capsize=3,
                label="g con cada longitud")
    for f in filas:
        ax.annotate(f"{coma(f.L, 2)} m", (f.T, f.g_i), textcoords="offset points", xytext=(6, -12),
                    fontsize=8, color="#555")
    ax.axhline(res["g"], color=ROJO, label=f"g del ajuste: {coma(res['g'], 2)} m/s²")
    ax.axhspan(res["g"] - res["u_g"], res["g"] + res["u_g"], color=ROJO, alpha=0.10)
    ax.axhline(m["g_referencia"], color=GRIS, ls="--", label=f"Bogotá: {coma(m['g_referencia'], 3)} m/s²")
    ax.axhline(m["g_clase"], color=VERDE, ls=":", label=f"Clase: {coma(m['g_clase'], 1)} m/s²")
    _ejes(ax, "Gravedad obtenida con cada longitud", "Periodo T (s)", "g (m/s²)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def oscilaciones(r, L):
    """Número de oscilación vs tiempo acumulado en el cronómetro. La pendiente es 1/T."""
    n = r["montaje"]["n_oscilaciones"]
    g_ref = r["montaje"]["g_referencia"]
    todas = r["series"] + r["series_excluidas"]
    fig, ax = _figura(3.8)
    tmax = 0.0
    for s in [s for s in todas if math.isclose(s.L, L)]:
        t = s.acumulados[:n]
        tmax = max(tmax, t[-1])
        ax.plot(t, range(1, n + 1), "o-", lw=1, label=f"Medición {s.repeticion}: T = {coma(t[-1] / n, 3)} s")
    T_teo = modelo.periodo_pequeno(L, g_ref)
    ax.plot([0, tmax], [0, tmax / T_teo], "--", color=GRIS, lw=1, label=f"Teórico: T = {coma(T_teo, 3)} s")
    _ejes(ax, f"Oscilaciones marcadas en el cronómetro con L = {coma(L, 2)} m",
          "Tiempo acumulado (s)", "Número de oscilación")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    return fig


def efecto_amplitud(r, L):
    """Efecto de la amplitud medido con la simulación: cuánto se alarga T y cuánto cambiaría g."""
    m = r["montaje"]
    g, theta0 = m["g_referencia"], math.radians(m["amplitud_grados"])
    f = periodo_simulado(L, g, theta0) / modelo.periodo_pequeno(L, g)
    g_medido = r["resultado"]["g"]
    # T0 = T/f  ->  T0² = T²/f²  ->  la pendiente baja en f² y g sube en f²
    return {"factor": f, "alarga_pct": (f - 1) * 100, "g_corregido": g_medido * f ** 2,
            "cambio_g": g_medido * (f ** 2 - 1)}


def simulacion(r, L):
    """Ángulo vs tiempo: ecuación exacta (RK4) frente a la aproximación de ángulo pequeño."""
    m = r["montaje"]
    g, theta0 = m["g_referencia"], math.radians(m["amplitud_grados"])
    T0 = modelo.periodo_pequeno(L, g)
    ts, ths = integrar(L, g, theta0, 3 * T0, T0 / 400)
    aprox = [theta0 * math.cos(2 * math.pi * t / T0) for t in ts]
    fig, ax = _figura(3.8)
    ax.plot(ts, [math.degrees(a) for a in ths], color=AZUL, label="Ecuación exacta (simulación RK4)")
    ax.plot(ts, [math.degrees(a) for a in aprox], "--", color=ROJO, lw=1,
            label="Ángulo pequeño: θ = θ0 cos(2πt/T)")
    alarga = efecto_amplitud(r, L)["alarga_pct"]
    _ejes(ax, f"Simulación con L = {coma(L, 2)} m y θ0 = {coma(m['amplitud_grados'], 0)}°: "
              f"el periodo real es {coma(alarga, 2)} % más largo", "Tiempo t (s)", "Ángulo θ (°)")
    ax.legend(fontsize=9, loc="lower left")
    fig.tight_layout()
    return fig
