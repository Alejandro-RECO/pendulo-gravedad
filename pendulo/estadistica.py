"""Mínimos cuadrados e incertidumbres, implementados a mano (sin numpy.polyfit).

Recta y = m x + b ajustada por mínimos cuadrados ordinarios:

    m = Sxy / Sxx                     b = ȳ - m x̄
    s² = Σ(yᵢ - m xᵢ - b)² / (N - 2)   (varianza de los residuos)
    u(m) = s / √Sxx                   u(b) = s · √(1/N + x̄²/Sxx)
    R² = 1 - Σ residuos² / Σ (yᵢ - ȳ)²

Ajuste por el origen y = m x:
    m = Σxy / Σx²     s² = Σ(y - m x)² / (N - 1)     u(m) = s / √Σx²

Propagación (en cuadratura, criterio del curso):
    y = x²       ->  u(y) = 2 |x| u(x)
    g = 4π²/m    ->  u(g) = g · u(m)/m
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Ajuste:
    m: float
    b: float
    u_m: float
    u_b: float
    r2: float
    n: int
    residuos: list[float]

    def evaluar(self, x: float) -> float:
        return self.m * x + self.b


def minimos_cuadrados(x: list[float], y: list[float]) -> Ajuste:
    n = len(x)
    if n != len(y) or n < 3:
        raise ValueError("Se necesitan al menos 3 pares (x, y) del mismo tamaño")
    xm = sum(x) / n
    ym = sum(y) / n
    sxx = sum((xi - xm) ** 2 for xi in x)
    sxy = sum((xi - xm) * (yi - ym) for xi, yi in zip(x, y))
    m = sxy / sxx
    b = ym - m * xm
    res = [yi - (m * xi + b) for xi, yi in zip(x, y)]
    ss_res = sum(e * e for e in res)
    ss_tot = sum((yi - ym) ** 2 for yi in y)
    s = math.sqrt(ss_res / (n - 2))
    return Ajuste(
        m=m,
        b=b,
        u_m=s / math.sqrt(sxx),
        u_b=s * math.sqrt(1 / n + xm * xm / sxx),
        r2=1 - ss_res / ss_tot,
        n=n,
        residuos=res,
    )


def minimos_cuadrados_origen(x: list[float], y: list[float]) -> Ajuste:
    n = len(x)
    sxx = sum(xi * xi for xi in x)
    m = sum(xi * yi for xi, yi in zip(x, y)) / sxx
    res = [yi - m * xi for xi, yi in zip(x, y)]
    s = math.sqrt(sum(e * e for e in res) / (n - 1))
    ym = sum(y) / n
    r2 = 1 - sum(e * e for e in res) / sum((yi - ym) ** 2 for yi in y)
    return Ajuste(m=m, b=0.0, u_m=s / math.sqrt(sxx), u_b=0.0, r2=r2, n=n, residuos=res)


def media(v: list[float]) -> float:
    return sum(v) / len(v)


def desviacion(v: list[float]) -> float:
    m = media(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def desviacion_combinada(grupos: list[list[float]]) -> tuple[float, int]:
    """Desviación estándar combinada (pooled) de varios grupos y sus grados de libertad.

    s_p² = Σ (nᵢ - 1) sᵢ² / Σ (nᵢ - 1)
    """
    num = 0.0
    gl = 0
    for g in grupos:
        if len(g) < 2:
            continue
        m = media(g)
        num += sum((x - m) ** 2 for x in g)
        gl += len(g) - 1
    return math.sqrt(num / gl), gl


def g_desde_pendiente(m: float, u_m: float) -> tuple[float, float]:
    g = 4 * math.pi ** 2 / m
    return g, g * u_m / m


def error_porcentual(experimental: float, referencia: float) -> float:
    return abs(referencia - experimental) / referencia * 100
