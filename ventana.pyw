"""Péndulo simple: cálculo de la gravedad (interfaz gráfica).

Se abre con iniciar_app.bat. Todos los cálculos los hace el paquete pendulo/ (el mismo que usan
analizar.py y validar.py), así que la ventana y el informe dan los mismos números.
"""

import copy
import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # noqa: E402

from pendulo import estadistica as est  # noqa: E402
from pendulo import graficas_app as gr  # noqa: E402
from pendulo.analisis import procesar  # noqa: E402
from pendulo.datos import cargar_montaje  # noqa: E402
from exportar_excel import exportar  # noqa: E402

coma = gr.coma
RESULTADOS = RAIZ / "resultados"

GRAFICAS = [
    ("L vs T²", "recta"),
    ("L vs T", "parabola"),
    ("Residuos", "residuos"),
    ("g por longitud", "g"),
    ("Oscilaciones", "oscilaciones"),
    ("Simulación", "simulacion"),
]

TEXTOS = {
    "recta": "Los puntos quedan sobre una recta: T² es proporcional a L, como dice la ec. (3). "
             "De la pendiente sale g = 4π²/m. Los cuadrados naranja (0,70 y 0,90 m) no entran al ajuste.",
    "parabola": "Sin elevar al cuadrado, la relación es una curva. La línea roja usa el g medido; "
                "la punteada, el valor de Bogotá.",
    "residuos": "Distancia de cada punto a la recta. Quedan cerca de cero y sin un patrón: la recta "
                "describe bien los datos.",
    "g": "g calculada con cada longitud por separado. Las longitudes cortas tienen barras más grandes "
         "porque los 3 mm de error en L pesan más. La franja roja es el resultado del ajuste.",
    "oscilaciones": "Cada punto es una vuelta marcada en el cronómetro. La pendiente de cada recta es 1/T: "
                    "entre más larga la cuerda, más lenta la oscilación.",
    "simulacion": "Simulación de la ecuación exacta del péndulo frente a la de ángulo pequeño. "
                  "A 9° las dos curvas casi coinciden: la aproximación del modelo es válida.",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Péndulo simple - cálculo de g")
        self.geometry("1200x720")
        self.minsize(950, 600)

        self.montaje = cargar_montaje()
        self.r = None
        self.figura = None
        self.grafica = tk.StringVar(value="recta")

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=24)
        estilo.configure("Toolbutton", padding=(10, 5))

        self._barra()
        cuerpo = ttk.Frame(self, padding=(10, 0, 10, 10))
        cuerpo.pack(fill="both", expand=True)
        self._panel_izquierdo(cuerpo)
        self._panel_grafica(cuerpo)
        self.calcular()

    # ---------- interfaz

    def _barra(self):
        barra = ttk.Frame(self, padding=10)
        barra.pack(fill="x")
        ttk.Label(barra, text="Péndulo simple: cálculo de la gravedad",
                  font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(barra, text="Guardar gráficas", command=self.guardar).pack(side="right", padx=3)
        ttk.Button(barra, text="Exportar a Excel", command=self.a_excel).pack(side="right", padx=3)
        ttk.Button(barra, text="Abrir datos", command=self.abrir).pack(side="right", padx=3)
        self.lbl_archivo = ttk.Label(barra, text="", foreground="#666")
        self.lbl_archivo.pack(side="right", padx=10)

    def _panel_izquierdo(self, padre):
        izq = ttk.Frame(padre, width=340)
        izq.pack(side="left", fill="y", padx=(0, 10))
        izq.pack_propagate(False)

        ttk.Label(izq, text="Promedio de las 3 mediciones", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.tabla = ttk.Treeview(izq, columns=("L", "T", "T2"), show="headings", height=6)
        for col, titulo in [("L", "L (m)"), ("T", "T (s)"), ("T2", "T² (s²)")]:
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=100, anchor="center")
        self.tabla.pack(fill="x", pady=(4, 4))
        fila = ttk.Frame(izq)
        fila.pack(anchor="w")
        ttk.Button(fila, text="Ver mediciones", command=self.ver_mediciones).pack(side="left")
        ttk.Button(fila, text="Instrumentos", command=self.ver_instrumentos).pack(side="left", padx=4)

        ttk.Label(izq, text="Resultado", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(16, 4))
        self.lbl_g = tk.Label(izq, text="g = —", font=("Segoe UI", 18, "bold"), fg="#1f4e79", anchor="w")
        self.lbl_g.pack(fill="x")
        self.lbl_resultado = ttk.Label(izq, text="", justify="left", font=("Segoe UI", 10))
        self.lbl_resultado.pack(anchor="w", pady=(4, 0))

        ttk.Label(izq, text="Qué significa", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(16, 4))
        self.lbl_lectura = ttk.Label(izq, text="", wraplength=320, justify="left")
        self.lbl_lectura.pack(anchor="w")

        fila2 = ttk.Frame(izq)
        fila2.pack(anchor="w", side="bottom")
        ttk.Button(fila2, text="Comprobar cálculo", command=self.comprobar).pack(side="left")
        ttk.Button(fila2, text="Validar aplicación", command=self.validar).pack(side="left", padx=4)

    def _panel_grafica(self, padre):
        der = ttk.Frame(padre)
        der.pack(side="left", fill="both", expand=True)
        botones = ttk.Frame(der)
        botones.pack(fill="x")
        for texto, clave in GRAFICAS:
            ttk.Radiobutton(botones, text=texto, value=clave, variable=self.grafica,
                            style="Toolbutton", command=self.dibujar).pack(side="left", padx=1)
        self.sel_L = ttk.Combobox(botones, state="readonly", width=9)
        self.sel_L.bind("<<ComboboxSelected>>", lambda _e: self.dibujar())

        self.marco_fig = ttk.Frame(der)
        self.marco_fig.pack(fill="both", expand=True, pady=(6, 0))
        self.lbl_texto = ttk.Label(der, text="", wraplength=800, justify="left", foreground="#444")
        self.lbl_texto.pack(fill="x", pady=(4, 0))

    # ---------- cálculo

    def abrir(self):
        ruta = filedialog.askopenfilename(initialdir=RAIZ / "datos", title="Datos crudos (una fila por vuelta)",
                                          filetypes=[("CSV", "*.csv")])
        if ruta:
            self.montaje["archivo_datos"] = ruta
            self.calcular()

    def calcular(self):
        try:
            self.r = procesar(copy.deepcopy(self.montaje))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("No se pudieron procesar los datos", str(e))
            return
        self.lbl_archivo.configure(text=Path(self.montaje["archivo_datos"]).name)
        self.mostrar_resultado()
        todas = sorted({s.L for s in self.r["series"] + self.r["series_excluidas"]}, reverse=True)
        self.sel_L["values"] = [coma(L, 2) + " m" for L in todas]
        self.sel_L.current(0)
        self.dibujar()

    def mostrar_resultado(self):
        r, m = self.r, self.montaje
        res = r["resultado"]
        self.tabla.delete(*self.tabla.get_children())
        for f in sorted(r["filas"], key=lambda f: -f.L):
            self.tabla.insert("", "end", values=(coma(f.L, 2), coma(f.T, 3), coma(f.T2, 3)))

        self.lbl_g.configure(text=f"g = ({coma(res['g'], 2)} ± {coma(res['u_g'], 2)}) m/s²")
        error_clase = est.error_porcentual(res["g"], m["g_clase"])
        signo = "+" if res["b"] >= 0 else "−"
        self.lbl_resultado.configure(text=(
            f"Recta:  T² = {coma(res['m'], 3)} L {signo} {coma(abs(res['b']), 3)}\n"
            f"R² = {coma(res['r2'], 4)}\n\n"
            f"Error frente a {coma(m['g_referencia'], 3)} m/s² (Bogotá):  {coma(res['error_pct'], 2)} %\n"
            f"Error frente a {coma(m['g_clase'], 1)} m/s² (clase):  {coma(error_clase, 2)} %\n\n"
            f"Corregido por amplitud ec. (5) y tamaño de la pelota ec. (6):\n"
            f"g = ({coma(r['resultado_corregido']['g'], 2)} ± {coma(r['resultado_corregido']['u_g'], 2)}) m/s²"))

        z_clase = abs(res["g"] - m["g_clase"]) / res["u_g"]
        dif_refs = abs(m["g_clase"] - m["g_referencia"]) / m["g_referencia"] * 100
        lectura = [
            f"La diferencia con {coma(m['g_referencia'], 3)} m/s² es "
            + ("menor que la incertidumbre: el resultado coincide con el valor de Bogotá."
               if res["sigmas"] <= 1 else
               f"{coma(res['sigmas'], 1)} veces la incertidumbre"
               + (": el resultado coincide con el valor de Bogotá." if res["sigmas"] <= 2 else
                  ": el resultado no coincide con el valor de Bogotá.")),
            (f"Con esta incertidumbre no se alcanza a distinguir {coma(m['g_referencia'], 3)} de "
             f"{coma(m['g_clase'], 1)} m/s², que difieren solo {coma(dif_refs, 2)} %."
             if res["sigmas"] <= 2 and z_clase <= 2 else
             f"El resultado se distingue de {coma(m['g_clase'], 1)} m/s²."),
            f"El corte con el eje equivale a {coma(r['intercepto_cm'], 1)} cm de longitud: "
            + ("compatible con cero, la longitud se midió bien." if abs(res["b"]) <= 2 * res["u_b"]
               else "distinto de cero, revisar la medición de L."),
        ]
        self.lbl_lectura.configure(text="\n\n".join(lectura))

    # ---------- gráficas

    def crear_figura(self, clave):
        L = float(self.sel_L.get().replace(" m", "").replace(",", "."))
        return {
            "recta": lambda: gr.recta(self.r),
            "parabola": lambda: gr.parabola(self.r),
            "residuos": lambda: gr.residuos(self.r),
            "g": lambda: gr.g_por_longitud(self.r),
            "oscilaciones": lambda: gr.oscilaciones(self.r, L),
            "simulacion": lambda: gr.simulacion(self.r, L),
        }[clave]()

    def dibujar(self):
        if self.r is None:
            return
        clave = self.grafica.get()
        if clave in ("oscilaciones", "simulacion"):
            self.sel_L.pack(side="left", padx=8)
        else:
            self.sel_L.pack_forget()
        for w in self.marco_fig.winfo_children():
            w.destroy()
        if self.figura is not None:
            plt.close(self.figura)
        self.figura = self.crear_figura(clave)
        lienzo = FigureCanvasTkAgg(self.figura, master=self.marco_fig)
        NavigationToolbar2Tk(lienzo, self.marco_fig).update()
        lienzo.get_tk_widget().pack(fill="both", expand=True)
        lienzo.mpl_connect("resize_event", lambda _e: self.figura.tight_layout())
        lienzo.draw()
        texto = TEXTOS[clave]
        if clave == "simulacion":
            ef = gr.efecto_amplitud(self.r, float(self.sel_L.get().replace(" m", "").replace(",", ".")))
            texto += (f" Si se corrige este efecto, g pasa de {coma(self.r['resultado']['g'], 3)} a "
                      f"{coma(ef['g_corregido'], 3)} m/s² (cambio de {coma(ef['cambio_g'], 3)} m/s², "
                      f"menor que la incertidumbre de {coma(self.r['resultado']['u_g'], 2)} m/s²).")
        self.lbl_texto.configure(text=texto)

    # ---------- ventanas secundarias

    def _ventana_tabla(self, titulo, columnas, filas, nota=""):
        v = tk.Toplevel(self)
        v.title(titulo)
        t = ttk.Treeview(v, columns=[c for c, _, _ in columnas], show="headings", height=min(len(filas), 20))
        for c, encabezado, ancho in columnas:
            t.heading(c, text=encabezado)
            t.column(c, width=ancho, anchor="center")
        for fila in filas:
            t.insert("", "end", values=fila)
        t.pack(padx=10, pady=10)
        if nota:
            ttk.Label(v, text=nota, wraplength=700, justify="left").pack(padx=10, pady=(0, 10), anchor="w")

    def ver_mediciones(self):
        n = self.montaje["n_oscilaciones"]
        filas = []
        for s in sorted(self.r["series"] + self.r["series_excluidas"], key=lambda s: (-s.L, s.repeticion)):
            uso = "validación" if s in self.r["series_excluidas"] else "ajuste"
            filas.append((coma(s.L, 2), s.repeticion, n, coma(s.t_n(n), 2), coma(s.periodo(n), 3), uso))
        m = self.montaje
        self._ventana_tabla(
            "Mediciones",
            [("L", "L (m)", 80), ("rep", "Medición", 80), ("n", "Oscilaciones", 90),
             ("t", "t₁₀ (s)", 90), ("T", "T = t₁₀/10 (s)", 110), ("uso", "Uso", 90)],
            filas,
            f"Amplitud {coma(m['amplitud_grados'], 0)} ± {coma(m['u_amplitud_grados'], 0)}° · "
            f"masa {coma(m['masa_kg'] * 1000, 0)} ± {coma(m['u_masa_kg'] * 1000, 0)} g · "
            f"radio de la pelota {coma(m['radio_esfera_m'] * 100, 2)} cm · L medida al centro de la pelota. "
            "0,70 y 0,90 m tienen 2 mediciones y solo se usan para validar.")

    def ver_instrumentos(self):
        filas = [(i["instrumento"], i["magnitud"], i["resolucion"], i["u_instrumento"], i["u_efectiva"],
                  i["justificacion"]) for i in self.montaje["instrumentos"]]
        self._ventana_tabla(
            "Incertidumbre de los instrumentos",
            [("i", "Instrumento", 260), ("m", "Magnitud", 70), ("r", "Resolución", 80),
             ("ui", "Del instrumento", 105), ("ue", "Efectiva", 120), ("j", "Justificación", 380)],
            filas,
            "u_g/g = √[(u_L/L)² + (2u_T/T)²]  (propagación en cuadratura). "
            f"Dispersión medida entre vueltas: {coma(self.r['sigma_vuelta'], 3)} s; "
            f"desviación combinada entre repeticiones: s_p = {coma(self.r['s_p'], 4)} s.")

    def comprobar(self):
        import numpy as np
        r, res = self.r, self.r["resultado"]
        x = [f.L for f in r["filas"]]
        y = [f.T2 for f in r["filas"]]
        m_np, b_np = np.polyfit(x, y, 1)
        lineas = [
            "Mínimos cuadrados del programa vs numpy.polyfit:",
            f"   pendiente {res['m']:.6f} vs {m_np:.6f}",
            f"   corte     {res['b']:.6f} vs {b_np:.6f}",
            "",
            "Predicción de longitudes que no entraron al ajuste:",
        ]
        for f in r["filas_excluidas"]:
            T_pred = math.sqrt(res["m"] * f.L + res["b"])
            lineas.append(f"   L = {coma(f.L, 2)} m:  predicho {coma(T_pred, 3)} s,  medido {coma(f.T, 3)} s  "
                          f"({coma((T_pred - f.T) / f.T * 100, 2)} %)")
        lineas += ["", "Para la batería completa de pruebas: python validar.py"]
        messagebox.showinfo("Comprobar cálculo", "\n".join(lineas))

    def validar(self):
        """Corre las pruebas de validar.py y muestra el resultado de cada una."""
        import contextlib
        import io
        import validar
        validar.fallas = 0
        salida = io.StringIO()
        self.config(cursor="watch")
        self.update()
        try:
            with contextlib.redirect_stdout(salida):
                validar.main()
        finally:
            self.config(cursor="")
        texto = salida.getvalue().replace("[PASA]", "✔").replace("[FALLA]", "✘")
        messagebox.showinfo("Validación de la aplicación", texto)

    def guardar(self):
        RESULTADOS.mkdir(exist_ok=True)
        L = self.sel_L.get()
        for _, clave in GRAFICAS:
            fig = self.crear_figura(clave)
            fig.savefig(RESULTADOS / f"app-{clave}.png", dpi=300, bbox_inches="tight")
            plt.close(fig)
        messagebox.showinfo("Guardado", f"Gráficas guardadas en:\n{RESULTADOS}\n\n"
                                        f"(oscilaciones y simulación con L = {L})")

    def a_excel(self):
        ruta = filedialog.asksaveasfilename(initialdir=RAIZ / "datos", defaultextension=".xlsx",
                                            initialfile="2026-10-01_pendulo.xlsx", filetypes=[("Excel", "*.xlsx")])
        if not ruta:
            return
        try:
            exportar(self.r, Path(ruta))
        except PermissionError:
            messagebox.showerror("No se pudo guardar", "Cierre el archivo en Excel e intente de nuevo.")
            return
        messagebox.showinfo("Exportado", f"Excel guardado en:\n{ruta}")


def nitidez_windows():
    """Evita que la ventana se vea borrosa con el escalado de pantalla de Windows."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    nitidez_windows()
    App().mainloop()
