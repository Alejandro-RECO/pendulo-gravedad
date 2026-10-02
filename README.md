# Péndulo simple — determinación de g con ajuste computacional

Producto del proyecto de aula de Física Mecánica (Fundación Universitaria Compensar, 2026-2).
Integrantes: Camacho Yamith, Matoma Laudy, Revolledo Luis, Sosa Deisy. Docente: Adriana Lizeth Blandon Pedraza.

**Pregunta:** ¿qué valor de la aceleración de la gravedad se obtiene al relacionar el periodo de
oscilación de un péndulo simple con su longitud, y qué diferencia porcentual presenta frente al
valor de referencia local (9,773 m/s²)?

## Qué hace (respuesta a la observación del corte 1)

| | |
|---|---|
| **Lenguaje** | Python 3.10+; solo `numpy` (para validar), `matplotlib` (gráficas) y `openpyxl` (exportar a Excel). El ajuste no usa librerías. |
| **Entrada** | `datos/2026-10-01_pendulo_crudo.csv`: una fila por vuelta del cronómetro (longitud, repetición, vuelta, tiempo de vuelta, tiempo acumulado). Parámetros del montaje en `datos/montaje.json`, incluidas las longitudes excluidas del ajuste (0,90 y 0,70 m: repeticiones incompletas). |
| **Procesamiento** | 1) T = t₁₀/10 por serie · 2) promedio e incertidumbre por longitud · 3) mínimos cuadrados **implementados a mano** de T² vs L · 4) g = 4π²/m con propagación en cuadratura · 5) error % frente a 9,773 m/s² · 6) corrección por amplitud (9°) y por tamaño de la pelota · 7) simulación RK4 de la ecuación exacta. |
| **Salida** | `resultados/`: `reporte.md` (tablas y resultados), `tabla_longitudes.csv`, `resumen.json` y cuatro figuras listas para el informe. |
| **Validación** | `validar.py`: ajuste propio vs `numpy.polyfit`; predicción del periodo en 0,70 y 0,90 m, que no entran en el ajuste, y en 0,60 m dejándola fuera; simulador vs solución exacta; coherencia de los datos crudos. |

> **¿Vas a desarrollar o modificar la aplicación?** Lee primero [`PARA_EL_DESARROLLADOR.md`](PARA_EL_DESARROLLADOR.md): están las decisiones del grupo y los valores que el programa debe reproducir.

## Interfaz gráfica

Doble clic en **`iniciar_app.bat`**. Abre una ventana con el resultado a la izquierda y seis gráficas
a la derecha (L vs T², L vs T, residuos, g por longitud, oscilaciones y simulación). En todas las
gráficas el tiempo va en el eje x; el ajuste es el mismo de `analizar.py` (T² = m·L + b), solo se dibuja
con los ejes intercambiados. Botones: abrir otro CSV, exportar a Excel (con fórmulas para comprobar a
mano) y guardar las gráficas en `resultados/`.

| Archivo | Qué hace |
|---|---|
| `ventana.pyw` | La interfaz (Tkinter). No calcula nada por su cuenta: usa `pendulo/` |
| `pendulo/graficas_app.py` | Las seis gráficas de la interfaz |
| `exportar_excel.py` | Genera el Excel desde el CSV; la hoja «ajuste» compara Excel con el programa |

## Uso

```bash
pip install -r requirements.txt
python analizar.py            # genera resultados/
python validar.py             # debe terminar en "Todas las validaciones pasaron."
python analizar.py --todas    # comparación: sin excluir ninguna longitud -> resultados/todas/
```

## Estructura

```
datos/
  2026-10-01_pendulo_crudo.csv   datos crudos transcritos de las capturas del cronómetro (no se editan a mano)
  montaje.json                   longitud de incertidumbre, amplitud, radio de la pelota, g de referencia
  transcripcion_fotos.py         script que generó el CSV a partir de la lectura de las capturas
  README.md                      procedencia de cada dato y series faltantes
  (las fotos y capturas del cronómetro son evidencias del informe; no se publican aquí)
pendulo/
  datos.py         lectura del CSV y agrupación por serie y por longitud
  estadistica.py   mínimos cuadrados (con y sin intercepto), desviación combinada, propagación
  modelo.py        ecuaciones (2)–(6) y (14), periodo exacto (AGM)
  simulacion.py    integración RK4 de θ'' = −(g/L) sen θ y medición del periodo
  analisis.py      el procesamiento completo
  graficas.py      figuras del informe con coma decimal
analizar.py        programa principal
validar.py         validación del producto
```

## Modelo

| # | Ecuación | Uso |
|---|---|---|
Numeración del informe del corte 2:

| # | Ecuación | Uso |
|---|---|---|
| (1) | d²θ/dt² = −(g/L) sen θ | ecuación exacta; la integra la simulación |
| (2) | T = 2π √(L/g) | periodo para ángulo pequeño |
| (3) | T² = (4π²/g) L | linealización: recta de pendiente m = 4π²/g |
| (4) | g = 4π²/m | g a partir de la pendiente |
| (5) | T ≈ T₀ (1 + θ₀²/16) | corrección por amplitud finita |
| (6) | T = 2π √[(L² + 2R²/5)/(gL)] | péndulo físico: pelota de radio R (L_eff = L + 2R²/5L) |
| (7) | g(φ) GRS80 | referencia local g_ref = 9,773 m/s² |
| (8) | T = t₁₀/10 | periodo de cada serie |
| (9) | u(T̄) = √(s_p²/k + (δt/10)²) | incertidumbre del periodo medio |
| (10)–(12) | m, b, u(m) | mínimos cuadrados |
| (13) | u(g) = g·u(m)/m | incertidumbre de g |
| (14) | u_g/g = √[(u_L/L)² + (2u_T/T)²] | g de cada longitud, en cuadratura |
| (15) | E = \|g_ref − g\|/g_ref × 100 % | error porcentual |

Incertidumbre del periodo medio en cada longitud: u(T̄) = √(s_p²/k + (0,01 s/10)²), donde s_p es la
desviación estándar combinada de las repeticiones de todas las longitudes y k el número de repeticiones.
Incertidumbre de la pendiente: la de mínimos cuadrados a partir de la dispersión de los residuos.
