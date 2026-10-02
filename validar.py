"""Validación del producto: demuestra que el programa calcula bien.

  V1. Mínimos cuadrados propios vs. numpy.polyfit (implementación independiente).
  V2. Predicción: se ajusta sin una longitud y se predice su periodo (prueba más fuerte).
  V3. Simulador RK4 vs. solución exacta (integral elíptica) y vs. ecuación (2).
  V4. Coherencia de los datos crudos: cada vuelta = diferencia de tiempos acumulados.

Uso:  python validar.py
"""
from __future__ import annotations

import math

import numpy as np

from pendulo import estadistica as est
from pendulo import modelo
from pendulo.analisis import procesar
from pendulo.datos import cargar_montaje, leer_series
from pendulo.simulacion import periodo_simulado

fallas = 0


def informe(nombre: str, ok: bool, detalle: str) -> None:
    global fallas
    fallas += 0 if ok else 1
    print(f"[{'PASA' if ok else 'FALLA'}] {nombre}: {detalle}")


def v1_minimos_cuadrados(r: dict) -> None:
    x = np.array([f.L for f in r["filas"]])
    y = np.array([f.T2 for f in r["filas"]])
    coef, cov = np.polyfit(x, y, 1, cov=True)
    a = r["ajuste"]
    dif = max(abs(a.m - coef[0]), abs(a.b - coef[1]),
              abs(a.u_m - math.sqrt(cov[0, 0])), abs(a.u_b - math.sqrt(cov[1, 1])))
    informe("V1 ajuste propio vs numpy.polyfit", dif < 1e-10,
            f"m = {a.m:.6f} vs {coef[0]:.6f}; b = {a.b:.6f} vs {coef[1]:.6f}; máx. diferencia {dif:.1e}")


def _predecir(nombre: str, ajuste_x: list, ajuste_y: list, obj) -> None:
    aj = est.minimos_cuadrados(ajuste_x, ajuste_y)
    T_pred = math.sqrt(aj.evaluar(obj.L))
    # incertidumbre de la predicción (propagando u_m y u_b sin covarianza: cota conservadora)
    u_pred = math.sqrt((obj.L * aj.u_m) ** 2 + aj.u_b ** 2) / (2 * T_pred)
    u_tot = math.hypot(u_pred, obj.u_T)
    z = abs(T_pred - obj.T) / u_tot
    informe(nombre, z < 2,
            f"T predicho = {T_pred:.3f} ± {u_pred:.3f} s; T medido = {obj.T:.3f} ± {obj.u_T:.3f} s "
            f"({obj.n_rep} rep.); diferencia = {(T_pred - obj.T) / obj.T * 100:+.2f} % ({z:.1f} σ)")


def v2_prediccion(r: dict) -> None:
    filas = r["filas"]
    x = [f.L for f in filas]
    y = [f.T2 for f in filas]
    # longitudes excluidas: nunca entraron al ajuste, son una prueba independiente
    for obj in r["filas_excluidas"]:
        _predecir(f"V2 predicción L = {obj.L:.2f} m (excluida del ajuste)", x, y, obj)
    # además, dejar fuera una longitud usada y predecirla con las demás
    obj = next(f for f in filas if math.isclose(f.L, 0.60))
    resto = [f for f in filas if f is not obj]
    _predecir("V2 predicción L = 0.60 m (dejando esa longitud fuera)", [f.L for f in resto], [f.T2 for f in resto], obj)


def v3_simulador(montaje: dict) -> None:
    g = montaje["g_referencia"]
    L = 1.0
    T0 = modelo.periodo_pequeno(L, g)
    Ts = periodo_simulado(L, g, math.radians(0.5))
    e1 = abs(Ts - T0) / T0
    informe("V3a simulador a 0,5° vs ecuación (2)", e1 < 1e-4, f"{Ts:.6f} s vs {T0:.6f} s ({e1 * 100:.4f} %)")
    peor = 0.0
    for a in (9, 30, 60):
        th = math.radians(a)
        exacto = T0 * modelo.factor_amplitud_exacto(th)
        sim = periodo_simulado(L, g, th)
        peor = max(peor, abs(sim - exacto) / exacto)
    informe("V3b simulador vs solución exacta (9°, 30°, 60°)", peor < 1e-5, f"máx. diferencia {peor * 100:.5f} %")


def v4_datos(montaje: dict) -> None:
    series = leer_series(montaje["archivo_datos"])
    peor = 0.0
    for s in series:
        prev = 0.0
        for v, a in zip(s.vueltas, s.acumulados):
            peor = max(peor, abs((a - prev) - v))
            prev = a
    # el cronómetro muestra centésimas truncadas: se admite 0,01 s de diferencia
    informe("V4 vueltas = diferencia de acumulados", peor <= 0.0101,
            f"{len(series)} series, máx. diferencia {peor:.3f} s")


def main() -> None:
    montaje = cargar_montaje()
    r = procesar(montaje)
    v1_minimos_cuadrados(r)
    v2_prediccion(r)
    v3_simulador(montaje)
    v4_datos(montaje)
    print()
    print("Todas las validaciones pasaron." if fallas == 0 else f"{fallas} validación(es) fallaron.")


if __name__ == "__main__":
    main()
