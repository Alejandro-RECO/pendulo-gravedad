"""Modelo físico del péndulo y correcciones.

Ecuaciones (numeración del informe del corte 2):
  (1) d²θ/dt² = −(g/L) sen θ           ecuación exacta (la integra simulacion.py)
  (2) T = 2π √(L/g)                    periodo, aproximación de ángulo pequeño
  (3) T² = (4π²/g) L                   linealización
  (4) g = 4π²/m                        m: pendiente del ajuste T² vs L
  (5) T ≈ T₀ (1 + θ₀²/16)              corrección por amplitud finita (θ₀ en rad)
  (6) T = 2π √[(L² + 2R²/5) / (g L)]  péndulo físico  ->  L_eff = L + 2R²/(5L)
  (14) u_g/g = √[(u_L/L)² + (2u_T/T)²] propagación en cuadratura
  Periodo exacto (media aritmético-geométrica, sin aproximaciones):
      T = T₀ / AGM(1, cos(θ₀/2))
"""
from __future__ import annotations

import math


def periodo_pequeno(L: float, g: float) -> float:
    return 2 * math.pi * math.sqrt(L / g)


def factor_amplitud_serie(theta0_rad: float) -> float:
    """Factor (1 + θ₀²/16) de la ecuación (5)."""
    return 1 + theta0_rad ** 2 / 16


def agm(a: float, b: float, tol: float = 1e-15) -> float:
    while abs(a - b) > tol * a:
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a


def factor_amplitud_exacto(theta0_rad: float) -> float:
    """T/T₀ exacto para amplitud θ₀ (integral elíptica vía AGM)."""
    return 1 / agm(1.0, math.cos(theta0_rad / 2))


def longitud_efectiva(L: float, R: float | None) -> float:
    """Longitud equivalente del péndulo físico. Si R es None, devuelve L."""
    if not R:
        return L
    return L + 2 * R * R / (5 * L)


def u_g_relativa(L: float, u_L: float, T: float, u_T: float) -> float:
    """Ecuación (14): incertidumbre relativa de g para una sola longitud."""
    return math.sqrt((u_L / L) ** 2 + (2 * u_T / T) ** 2)
