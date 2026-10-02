"""Lectura de los datos crudos y agregación por serie y por longitud.

El CSV crudo tiene una fila por vuelta (oscilación marcada en el cronómetro):
    longitud_m, repeticion, vuelta, t_vuelta_s, t_acumulado_s, amplitud_grados, masa_g, fotos

El periodo de cada serie se obtiene del tiempo acumulado en la vuelta n (n = 10):
    T = t_n / n
El número grande del cronómetro NO se usa: incluye el tiempo hasta la pausa manual.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def cargar_montaje(ruta: str | Path | None = None) -> dict:
    ruta = Path(ruta) if ruta else RAIZ / "datos" / "montaje.json"
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class Serie:
    L: float                      # longitud (m), del pivote al centro de la pelota
    repeticion: int
    vueltas: list[float]          # tiempo de cada vuelta (s)
    acumulados: list[float]       # tiempo acumulado en cada vuelta (s)

    def t_n(self, n: int) -> float:
        """Tiempo acumulado en la vuelta n (s)."""
        if len(self.acumulados) < n:
            raise ValueError(f"La serie L={self.L} rep={self.repeticion} tiene menos de {n} vueltas")
        return self.acumulados[n - 1]

    def periodo(self, n: int) -> float:
        """Periodo medio de la serie: T = t_n / n."""
        return self.t_n(n) / n


@dataclass
class Longitud:
    L: float
    series: list[Serie] = field(default_factory=list)

    def periodos(self, n: int) -> list[float]:
        return [s.periodo(n) for s in self.series]

    def T_media(self, n: int) -> float:
        p = self.periodos(n)
        return sum(p) / len(p)

    def desviacion(self, n: int) -> float:
        """Desviación estándar muestral de los periodos de las repeticiones."""
        p = self.periodos(n)
        if len(p) < 2:
            return float("nan")
        m = sum(p) / len(p)
        return math.sqrt(sum((x - m) ** 2 for x in p) / (len(p) - 1))


def leer_series(ruta: str | Path) -> list[Serie]:
    ruta = Path(ruta)
    if not ruta.is_absolute():
        ruta = RAIZ / ruta
    grupos: dict[tuple[float, int], list[tuple[int, float, float]]] = {}
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            clave = (float(fila["longitud_m"]), int(fila["repeticion"]))
            grupos.setdefault(clave, []).append(
                (int(fila["vuelta"]), float(fila["t_vuelta_s"]), float(fila["t_acumulado_s"]))
            )
    series = []
    for (L, rep), filas in grupos.items():
        filas.sort()
        series.append(Serie(L, rep, [v for _, v, _ in filas], [a for _, _, a in filas]))
    series.sort(key=lambda s: (s.L, s.repeticion))
    return series


def agrupar(series: list[Serie]) -> list[Longitud]:
    por_L: dict[float, Longitud] = {}
    for s in series:
        por_L.setdefault(s.L, Longitud(s.L)).series.append(s)
    return [por_L[k] for k in sorted(por_L)]
