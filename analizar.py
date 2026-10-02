"""Análisis completo del péndulo: lee los datos crudos, ajusta T² vs L, obtiene g y genera
las tablas y gráficas del informe en resultados/.

Uso:
    python analizar.py            # excluye las longitudes de montaje.json["longitudes_excluidas_m"]
    python analizar.py --todas    # incluye todas las longitudes (comparación)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from pendulo import graficas
from pendulo.analisis import procesar
from pendulo.datos import RAIZ, cargar_montaje
from pendulo.graficas import coma


def escribir_tabla(r: dict, ruta: Path) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["L_m", "repeticiones", "T_medio_s", "s_rep_s", "u_T_s", "T2_s2", "u_T2_s2",
                    "T0_corregido_s", "L_eff_m", "g_i_m_s2", "u_g_i_m_s2"])
        for x in r["filas"]:
            w.writerow([x.L, x.n_rep, f"{x.T:.4f}", f"{x.s:.4f}", f"{x.u_T:.4f}", f"{x.T2:.4f}",
                        f"{x.u_T2:.4f}", f"{x.T0:.4f}", f"{x.L_eff:.5f}", f"{x.g_i:.3f}", f"{x.u_g_i:.3f}"])


def reporte(r: dict) -> str:
    m = r["montaje"]
    p, o, c, t = r["resultado"], r["resultado_origen"], r["resultado_corregido"], r["resultado_todas"]
    L = []
    L.append("# Resultados del análisis — péndulo simple\n")
    L.append(f"Datos: `{m['archivo_datos']}` · {r['n_series']} series · n = {m['n_oscilaciones']} oscilaciones por serie · "
             f"g_ref = {coma(m['g_referencia'], 3)} m/s²\n")
    if r["filas_excluidas"]:
        ex = ", ".join(f"{coma(f.L, 2)} m ({f.n_rep} rep.)" for f in r["filas_excluidas"])
        L.append(f"**Excluidas del ajuste por repeticiones incompletas:** {ex}. Se usan solo para validar la predicción.\n")
    L.append("## Periodos por longitud (usadas en el ajuste)\n")
    L.append("| L (m) | Rep. | T̄ (s) | s (s) | u(T̄) (s) | T̄² (s²) | g solo con esta L (m/s²) |")
    L.append("|---|---|---|---|---|---|---|")
    for x in r["filas"]:
        L.append(f"| {coma(x.L, 2)} | {x.n_rep} | {coma(x.T, 3)} | {coma(x.s, 3)} | {coma(x.u_T, 3)} | "
                 f"{coma(x.T2, 3)} ± {coma(x.u_T2, 3)} | {coma(x.g_i, 2)} ± {coma(x.u_g_i, 2)} |")
    L.append("")
    L.append(f"- Desviación combinada entre repeticiones: s_p = {coma(r['s_p'], 4)} s ({r['gl']} grados de libertad).")
    L.append(f"- Dispersión de las vueltas individuales: σ = {coma(r['sigma_vuelta'], 3)} s por vuelta "
             f"({len(r['desv_vueltas'])} vueltas). Es el efecto del tiempo de reacción en cada pulsación.")
    L.append("")
    L.append("## Ajuste T² = m·L + b (mínimos cuadrados propios)\n")
    L.append("| Ajuste | m (s²/m) | b (s²) | R² | g (m/s²) | E % | |g−g_ref|/u_g |")
    L.append("|---|---|---|---|---|---|---|")

    def fila(nombre, a):
        return (f"| {nombre} | {coma(a['m'], 4)} ± {coma(a['u_m'], 4)} | {coma(a['b'], 4)} ± {coma(a['u_b'], 4)} | "
                f"{coma(a['r2'], 5)} | **{coma(a['g'], 3)} ± {coma(a['u_g'], 3)}** | {coma(a['error_pct'], 2)} | {coma(a['sigmas'], 1)} |")
    L.append(fila("Principal: promedios, recta libre", p))
    L.append(fila("Por el origen (b = 0)", o))
    L.append(fila(f"Corregido: amplitud {coma(m['amplitud_grados'], 0)}° y péndulo físico R = {coma((m.get('radio_esfera_m') or 0) * 100, 2)} cm", c))
    L.append(fila("Comprobación: todas las series sueltas", t))
    L.append("")
    L.append(f"- Intercepto expresado como longitud: b/m = {coma(r['intercepto_cm'], 1)} cm. "
             f"{'Compatible con cero' if abs(p['b']) < 2 * p['u_b'] else 'NO compatible con cero'} "
             f"(b = {coma(p['b'], 3)} ± {coma(p['u_b'], 3)} s²).")
    L.append(f"- Factor de amplitud a {coma(m['amplitud_grados'], 0)}°, medido en la simulación de (1): "
             f"T/T₀ = {coma(r['factor_amplitud'], 5)} (+{coma((r['factor_amplitud'] - 1) * 100, 2)} %). "
             f"Con (5): {coma(r['factor_amplitud_ec5'], 5)}; solución exacta: {coma(r['factor_amplitud_exacto'], 5)}. "
             "La corrección de la Tabla 3 usa el de la simulación.")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--todas", action="store_true", help="no excluir ninguna longitud")
    ap.add_argument("--salida", default="resultados", help="carpeta de salida")
    args = ap.parse_args()

    montaje = cargar_montaje()
    if args.todas:
        montaje = dict(montaje, longitudes_excluidas_m=[])
        if args.salida == "resultados":
            args.salida = "resultados/todas"
    salida = RAIZ / args.salida
    salida.mkdir(parents=True, exist_ok=True)

    r = procesar(montaje)
    texto = reporte(r)
    (salida / "reporte.md").write_text(texto, encoding="utf-8")
    escribir_tabla(r, salida / "tabla_longitudes.csv")
    resumen = {k: {kk: vv for kk, vv in v.items() if kk != "residuos"}
               for k, v in r.items() if k.startswith("resultado")}
    (salida / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    graficas.grafica_T2_vs_L(r, salida / "corte2-fig3-T2-vs-L.png")
    graficas.grafica_residuos(r, salida / "corte2-fig4-residuos.png")
    graficas.grafica_vueltas(r, salida / "corte2-anexo-dispersion-vueltas.png")
    graficas.grafica_amplitud(montaje, salida / "corte2-fig5-efecto-amplitud.png")
    print(texto)


if __name__ == "__main__":
    main()
