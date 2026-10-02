# Datos crudos — 1 de octubre de 2026

## Cómo se tomaron
- Pivote: puntilla. Hilo de nailon que atraviesa una pelota de goma.
- Masa: 13 g (balanza digital SF-400, capacidad 10 kg, resolución 1 g).
- Pelota: circunferencia C = 8 cm medida con cinta de costura → D = 2,55 cm, R = 1,27 cm.
- Longitud L: del punto de suspensión al **centro** de la pelota, con cinta de costura de 150 cm (división 1 mm).
- Amplitud: 9° desde la vertical, con un transportador digital del celular (referencia 90,0°).
- Tiempo: cronómetro del celular **con vueltas**: se marcó una vuelta por oscilación completa, 10 vueltas por serie.
  El dato que se usa es el **tiempo acumulado en la vuelta 10**; la lectura al detener incluye el tiempo hasta la pausa manual.
- Lugar sin corrientes de aire apreciables.

## Transcripción
Las 19 series se leyeron de las capturas de pantalla (dos por serie: vueltas 1–5 y 6–10).
Se hicieron **dos transcripciones independientes** (Claude a partir de las fotos de Deisy y la hoja de
Excel del compañero). Los **152 tiempos acumulados** de las 5 longitudes comunes coinciden exactamente.
Las únicas diferencias son de 0,01 s en algunas vueltas sueltas, porque el cronómetro muestra centésimas
truncadas y una transcripción leyó la vuelta en pantalla y la otra la calculó restando acumulados.

## Series faltantes
| Longitud | Repetición | Motivo |
|---|---|---|
| 0,90 m | 2 | Las capturas `L90_r2_*` son copias idénticas de `L90_r1_*` (mismo archivo). |
| 0,70 m | 1 | `L70_R1_1` es copia de `L80_R3_1` y `L70_R1_2` es copia de `L70_R2_2`. |

Según la hora de las capturas (1:28 y 1:30 para 0,90 m; 1:39–1:40 para 0,70 m) no hay captura de esas
series. Quedan 19 series en lugar de 21. No se rellenan.

**Decisión del grupo (1 oct 2026):** las longitudes con repeticiones incompletas (0,90 y 0,70 m) se
excluyen del ajuste; se configura en `montaje.json`. El criterio es el número de repeticiones (todas las
longitudes usadas tienen 3), no el valor obtenido. Sus datos siguen en el CSV y se usan para validar: el modelo ajustado con
las otras 5 longitudes predice su periodo. Con las 7 longitudes, g = 9,88 ± 0,13 m/s² (`analizar.py --todas`).

## Orden de las repeticiones en 1,00 m
Por la hora de las capturas: rep. 1 = 20,10 s (1:21), rep. 2 = 20,04 s (1:22), rep. 3 = 20,22 s (1:24).
La hoja de Excel del compañero las numera 20,22 / 20,10 / 20,04. El orden no cambia ningún resultado.

## Series con 11 vueltas
0,40 m rep. 1 y 0,20 m rep. 3 tienen 11 vueltas registradas. Para que todas las series sean
comparables se usa la vuelta 10 (n = 10); la vuelta 11 queda en el CSV.
