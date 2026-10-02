"""Simulación numérica del péndulo con la ecuación exacta (sin aproximar sen θ ≈ θ).

    d²θ/dt² = -(g/L) sen θ

Se integra con Runge-Kutta de orden 4 (implementado a mano) y el periodo se mide
entre cruces sucesivos por θ = 0 en el mismo sentido, interpolando linealmente
el instante del cruce. Sirve para:
  - cuantificar el error de la aproximación de ángulo pequeño a la amplitud usada (9°);
  - validar el simulador contra la solución exacta (AGM) y contra la ecuación (2).
"""
from __future__ import annotations

import math


def _derivadas(theta: float, omega: float, k: float) -> tuple[float, float]:
    return omega, -k * math.sin(theta)


def integrar(L: float, g: float, theta0: float, t_max: float, dt: float):
    """Devuelve listas (t, θ) desde el reposo en θ₀ (rad)."""
    k = g / L
    t, th, om = 0.0, theta0, 0.0
    ts, ths = [t], [th]
    pasos = int(round(t_max / dt))
    for _ in range(pasos):
        k1 = _derivadas(th, om, k)
        k2 = _derivadas(th + dt / 2 * k1[0], om + dt / 2 * k1[1], k)
        k3 = _derivadas(th + dt / 2 * k2[0], om + dt / 2 * k2[1], k)
        k4 = _derivadas(th + dt * k3[0], om + dt * k3[1], k)
        th += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt
        ts.append(t)
        ths.append(th)
    return ts, ths


def periodo_simulado(L: float, g: float, theta0: float, n_periodos: int = 5, pasos_por_periodo: int = 2000) -> float:
    """Periodo medido en la simulación (s), promediado sobre n_periodos."""
    T0 = 2 * math.pi * math.sqrt(L / g)
    # margen: el periodo real es mayor que T0 (hasta ~18 % a 90°)
    t_max = (n_periodos + 1.5) * T0 * 1.25
    dt = T0 / pasos_por_periodo
    ts, ths = integrar(L, g, theta0, t_max, dt)
    cruces = []  # cruces de positivo a negativo
    for i in range(1, len(ths)):
        if ths[i - 1] > 0 >= ths[i]:
            f = ths[i - 1] / (ths[i - 1] - ths[i])
            cruces.append(ts[i - 1] + f * (ts[i] - ts[i - 1]))
    if len(cruces) < n_periodos + 1:
        raise RuntimeError("La simulación no alcanzó suficientes cruces")
    return (cruces[n_periodos] - cruces[0]) / n_periodos
