# Para quien desarrolla la aplicación del péndulo

**Regla única:** la aplicación y el informe deben dar **los mismos números**. Si hay dos programas que
calculan distinto, la profesora lo nota en la validación y en la sustentación. Este documento fija
las decisiones y los valores que cualquier versión de la aplicación debe reproducir.

## 1. Decisiones del grupo (1 oct 2026)

| Tema | Decisión |
|---|---|
| Longitudes del ajuste | **1,00 · 0,80 · 0,60 · 0,40 · 0,20 m** (3 repeticiones cada una = 15 series) |
| 0,90 y 0,70 m | Fuera del ajuste (solo 2 repeticiones). Se usan **solo para validar**: el modelo predice su periodo |
| Periodo de cada serie | **T = t₁₀ / 10**: tiempo acumulado en la vuelta 10. En 0,40 m rep. 1 y 0,20 m rep. 3 hay 11 vueltas, pero **se usa la 10** (ver nota) |
| Lectura al detener | No se usa: incluye el tiempo hasta la pausa manual |
| Orden en 1,00 m | Por la hora de las capturas: rep. 1 = 20,10 s · rep. 2 = 20,04 s · rep. 3 = 20,22 s |
| g de referencia | 9,773 m/s² (Bogotá), no 9,81 |
| Propagación | **En cuadratura** (observación de la docente): u_g/g = √[(u_L/L)² + (2u_T/T)²] |
| Pelota | C = 8 cm → R = 1,27 cm. L medida hasta el **centro** de la pelota |

Nota sobre n = 11: si se usan las 11 vueltas en esas dos series, g pasa de 9,813 a 9,824 m/s². Las dos
opciones son válidas, pero **hay que escoger una sola**. Se escogió n = 10 para que todas las series sean iguales.

## 2. Método (el que se defiende en el informe)

1. Por serie: T = t₁₀/10.
2. Por longitud: T̄ = promedio de las 3 repeticiones.
3. Incertidumbre de T̄: u(T̄) = √(s_p²/3 + (0,01/10)²), donde s_p es la desviación estándar combinada
   de las repeticiones de las 5 longitudes: s_p² = Σ(nᵢ−1)sᵢ² / Σ(nᵢ−1).
4. u(T̄²) = 2·T̄·u(T̄); u(L) = 3 mm.
5. Mínimos cuadrados **implementados a mano** (no `polyfit`) de y = T̄² contra x = L:
   m = Sxy/Sxx · b = ȳ − m·x̄ · s² = Σres²/(N−2) · u(m) = s/√Sxx · u(b) = s·√(1/N + x̄²/Sxx).
6. g = 4π²/m; u(g) = g·u(m)/m. Error % = |g_ref − g|/g_ref × 100.

## 3. Valores que la aplicación debe reproducir (prueba de aceptación)

| Magnitud | Valor esperado |
|---|---|
| T̄ (s) en 0,20 / 0,40 / 0,60 / 0,80 / 1,00 m | 0,90467 / 1,29033 / 1,55800 / 1,80333 / 2,01200 |
| s_p | 0,01071 s |
| u(T̄) | 0,00627 s |
| Pendiente m | 4,02325 ± 0,03187 s²/m |
| Intercepto b | 0,02823 ± 0,02114 s² |
| R² | 0,99981 |
| **g** | **9,8126 ± 0,0777 m/s²** → se reporta **9,81 ± 0,08 m/s²** |
| Error % | 0,40 % |
| Ajuste por el origen (comparación) | g = 9,720 ± 0,036 m/s² |
| Predicción de 0,70 m (fuera del ajuste) | T = 1,687 s vs medido 1,698 s (−0,70 %) |
| Predicción de 0,90 m (fuera del ajuste) | T = 1,910 s vs medido 1,894 s (+0,83 %) |

Si la aplicación da estos valores con 4 cifras, está bien.

## 4. Qué se puede reutilizar de este repositorio

- `datos/2026-10-01_pendulo_crudo.csv`: datos crudos verificados (coinciden con la hoja de Excel del grupo en los 152 tiempos acumulados).
- `pendulo/estadistica.py`: mínimos cuadrados a mano.
- `pendulo/simulacion.py`: **simulación numérica** (RK4) de la ecuación exacta del péndulo. Muestra que soltarlo a 9° alarga el periodo solo 0,15 %. Se puede agregar a la aplicación como un módulo «simulador».
- `validar.py`: las pruebas de que el programa calcula bien. La rejilla exige demostrar la validación.
- La forma más simple es **usar este repositorio como base** y agregarle la interfaz (menú, lectura del Excel, botones, lo que se quiera). Así hay un solo programa y los números no pueden diferir.
