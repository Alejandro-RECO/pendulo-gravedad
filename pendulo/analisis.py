"""Procesamiento completo: de las vueltas del cronómetro al valor de g con incertidumbre."""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import estadistica as est
from . import modelo
from .datos import Longitud, Serie, agrupar, leer_series
from .simulacion import periodo_simulado


@dataclass
class FilaLongitud:
    L: float
    L_eff: float
    n_rep: int
    periodos: list[float]
    T: float          # periodo medio medido (s)
    s: float          # desviación de las repeticiones (s)
    u_T: float        # incertidumbre del periodo medio (s)
    T0: float         # periodo corregido a amplitud nula (s)
    T2: float         # T² medido (s²)
    u_T2: float
    g_i: float        # g calculada solo con esta longitud (m/s²)
    u_g_i: float


def procesar(montaje: dict) -> dict:
    n = montaje["n_oscilaciones"]
    u_L = montaje["u_L_m"]
    R = montaje.get("radio_esfera_m")
    g_ref = montaje["g_referencia"]
    theta0 = math.radians(montaje["amplitud_grados"])
    res_t = montaje["resolucion_cronometro_s"]

    excluidas_L = [float(v) for v in montaje.get("longitudes_excluidas_m", [])]

    def excluida(L: float) -> bool:
        return any(math.isclose(L, e) for e in excluidas_L)

    todas_series: list[Serie] = leer_series(montaje["archivo_datos"])
    # Las longitudes excluidas no entran en ningún cálculo del ajuste; solo se usan para validar.
    series = [s for s in todas_series if not excluida(s.L)]
    longitudes: list[Longitud] = agrupar(series)
    longitudes_excl: list[Longitud] = agrupar([s for s in todas_series if excluida(s.L)])

    # --- Dispersión entre repeticiones (desviación combinada de las longitudes usadas)
    s_p, gl = est.desviacion_combinada([lg.periodos(n) for lg in longitudes])

    # --- Dispersión de las vueltas individuales (mide el efecto del tiempo de reacción)
    desv_vueltas = []
    for s in series:
        v = s.vueltas[:n]
        m = est.media(v)
        desv_vueltas.extend(x - m for x in v)
    sigma_vuelta = math.sqrt(sum(d * d for d in desv_vueltas) / (len(desv_vueltas) - len(series)))

    # Factor de amplitud T/T0 medido en la simulación de la ecuación exacta (1). El cociente no depende
    # de L ni de g, así que se simula con L = 1 m. Es el que se usa en la corrección por amplitud.
    f_amp = periodo_simulado(1.0, g_ref, theta0) / modelo.periodo_pequeno(1.0, g_ref)

    def fila_de(lg: Longitud) -> FilaLongitud:
        T = lg.T_media(n)
        k = len(lg.series)
        # tipo A (desviación combinada / √k) y resolución del cronómetro repartida en n oscilaciones
        u_T = math.sqrt(s_p ** 2 / k + (res_t / n) ** 2)
        T0 = T / f_amp
        g_i = 4 * math.pi ** 2 * lg.L / T ** 2
        return FilaLongitud(
            L=lg.L, L_eff=modelo.longitud_efectiva(lg.L, R), n_rep=k, periodos=lg.periodos(n),
            T=T, s=lg.desviacion(n), u_T=u_T, T0=T0, T2=T * T, u_T2=2 * T * u_T,
            g_i=g_i, u_g_i=g_i * modelo.u_g_relativa(lg.L, u_L, T, u_T),
        )

    filas = [fila_de(lg) for lg in longitudes]
    filas_excluidas = [fila_de(lg) for lg in longitudes_excl]

    x = [f.L for f in filas]
    y = [f.T2 for f in filas]

    def resumen_ajuste(aj: est.Ajuste) -> dict:
        g, u_g = est.g_desde_pendiente(aj.m, aj.u_m)
        return dict(m=aj.m, u_m=aj.u_m, b=aj.b, u_b=aj.u_b, r2=aj.r2, n=aj.n,
                    g=g, u_g=u_g, error_pct=est.error_porcentual(g, g_ref),
                    sigmas=abs(g - g_ref) / u_g, residuos=aj.residuos)

    principal = est.minimos_cuadrados(x, y)
    origen = est.minimos_cuadrados_origen(x, y)
    # con corrección de amplitud (ec. 5 exacta) y, si se conoce R, de péndulo físico
    corregido = est.minimos_cuadrados([f.L_eff for f in filas], [f.T0 ** 2 for f in filas])
    # comprobación: todas las series sueltas en lugar de las medias
    todas = est.minimos_cuadrados([s.L for s in series], [s.periodo(n) ** 2 for s in series])

    return dict(
        montaje=montaje,
        n_series=len(series),
        series=series,
        filas=filas,
        filas_excluidas=filas_excluidas,
        series_excluidas=[s for s in todas_series if excluida(s.L)],
        s_p=s_p, gl=gl,
        sigma_vuelta=sigma_vuelta,
        desv_vueltas=desv_vueltas,
        factor_amplitud=f_amp,
        factor_amplitud_ec5=modelo.factor_amplitud_serie(theta0),
        factor_amplitud_exacto=modelo.factor_amplitud_exacto(theta0),
        ajuste=principal,
        resultado=resumen_ajuste(principal),
        resultado_origen=resumen_ajuste(origen),
        resultado_corregido=resumen_ajuste(corregido),
        resultado_todas=resumen_ajuste(todas),
        intercepto_cm=principal.b / principal.m * 100,
    )
