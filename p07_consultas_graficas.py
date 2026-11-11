# ============================================================
# PRACTICA 07: CONSULTAS CON PANDAS Y GRAFICAS CON MATPLOTLIB
# Archivo: p07_consultas_graficas.py
#
# OBJETIVO:
# Realizar consultas sobre el conjunto de datos de estudiantes
# (el mismo de la practica 06) y representar los resultados
# mediante graficas.
#
# pip install pandas matplotlib
# ============================================================

# Path permite construir rutas de archivos de forma segura.
from pathlib import Path

# pandas permite leer y consultar datos en forma de tabla.
import pandas as pd

# numpy permite calcular la linea de tendencia.
import numpy as np

# matplotlib permite construir las graficas.
import matplotlib.pyplot as plt


# ============================================================
# 1. DATOS
# ============================================================

# Cada clave es una columna y cada lista contiene los valores
# de esa columna por fila.
datos = {
    "estudiante":             ["Ana", "Luis", "Maria", "Carlos", "Sofia", "Pedro", "Elena", "Jorge", "Diego", "Valeria", "Hugo", "Lucia", "Andres", "Camila", "Ivan", "Paola", "Ricardo", "Daniela", "Mateo", "Fernanda"],
    "horas_estudio":          [8, 3, 10, 5, 6, 2, 7, 4, 9, 1, 6, 8, 4, 7, 3, 5, 9, 2, 6, 10],
    "asistencia":             [95, 60, 98, 75, 85, 55, 90, 70, 92, 48, 80, 96, 65, 88, 58, 72, 94, 50, 83, 100],
    "actividades_entregadas": [100, 50, 100, 80, 90, 40, 95, 65, 95, 35, 85, 100, 60, 90, 45, 75, 98, 30, 88, 100],
    "calificacion":           [92, 58, 96, 72, 81, 50, 88, 64, 90, 45, 76, 94, 55, 84, 52, 70, 93, 41, 79, 98],
}

# Archivo CSV donde se guardan los datos.
ARCHIVO = Path(__file__).with_name("datos_estudiantes.csv")

# Carpeta donde se guardaran las graficas generadas.
CARPETA_GRAFICAS = Path(__file__).with_name("graficas_p07")

# Calificacion minima para aprobar.
MINIMO_APROBATORIO = 70


def titulo(texto):
    print(f"\n=== {texto} ===")


def nivel(calificacion):
    """Clasifica una calificacion en Alto, Medio o Bajo."""
    if calificacion >= 85:
        return "Alto"
    if calificacion >= MINIMO_APROBATORIO:
        return "Medio"
    return "Bajo"


# ============================================================
# 2. CONSULTAS
# ============================================================

def consultas(df):
    # Consulta 1: filtrar con una condicion.
    titulo("1. Estudiantes aprobados (calificacion >= 70)")
    aprobados = df[df["calificacion"] >= MINIMO_APROBATORIO]
    print(aprobados[["estudiante", "calificacion"]].to_string(index=False))

    # Consulta 2: filtrar con la condicion contraria.
    titulo("2. Estudiantes reprobados (calificacion < 70)")
    reprobados = df[df["calificacion"] < MINIMO_APROBATORIO]
    print(reprobados[["estudiante", "calificacion"]].to_string(index=False))

    # Consulta 3: varias condiciones con & (y).
    titulo("3. Asistencia >= 90 y mas de 7 horas de estudio")
    destacados = df[(df["asistencia"] >= 90) & (df["horas_estudio"] > 7)]
    print(destacados[["estudiante", "asistencia", "horas_estudio"]].to_string(index=False))

    # Consulta 4: varias condiciones con | (o).
    titulo("4. Estudiantes en riesgo (asistencia < 60 o entregas < 50)")
    riesgo = df[(df["asistencia"] < 60) | (df["actividades_entregadas"] < 50)]
    print(riesgo[["estudiante", "asistencia", "actividades_entregadas"]].to_string(index=False))

    # Consulta 5: ordenar de mayor a menor y tomar los primeros.
    titulo("5. Top 5 de calificaciones")
    print(df.nlargest(5, "calificacion")[["estudiante", "calificacion"]].to_string(index=False))

    # Consulta 6: ordenar de menor a mayor.
    titulo("6. Las 5 calificaciones mas bajas")
    print(df.nsmallest(5, "calificacion")[["estudiante", "calificacion"]].to_string(index=False))

    # Consulta 7: query() permite escribir la condicion como texto.
    titulo("7. query('horas_estudio >= 6 and calificacion < 85')")
    print(df.query("horas_estudio >= 6 and calificacion < 85")[["estudiante", "horas_estudio", "calificacion"]].to_string(index=False))

    # Consulta 8: buscar por texto.
    titulo("8. Estudiantes cuyo nombre empieza con 'D' o 'P'")
    print(df[df["estudiante"].str.startswith(("D", "P"))][["estudiante", "calificacion"]].to_string(index=False))

    # Consulta 9: agrupar por nivel y calcular estadisticas.
    titulo("9. Promedios agrupados por nivel")
    resumen = (
        df.groupby("nivel")[["horas_estudio", "asistencia", "actividades_entregadas", "calificacion"]]
        .mean()
        .round(2)
        .reindex(["Alto", "Medio", "Bajo"])
    )
    print(resumen.to_string())

    # Consulta 10: contar cuantos registros hay en cada grupo.
    titulo("10. Cantidad de estudiantes por nivel")
    print(df["nivel"].value_counts().reindex(["Alto", "Medio", "Bajo"]).to_string())

    # Consulta 11: correlacion entre las variables numericas.
    titulo("11. Correlacion con la calificacion")
    correlacion = df.drop(columns=["estudiante", "nivel"]).corr()["calificacion"].drop("calificacion")
    print(correlacion.round(3).to_string())

    # Consulta 12: estudiantes por encima del promedio del grupo.
    promedio = df["calificacion"].mean()
    titulo(f"12. Estudiantes por encima del promedio ({promedio:.2f})")
    print(df[df["calificacion"] > promedio][["estudiante", "calificacion"]].to_string(index=False))


# ============================================================
# 3. GRAFICAS
# ============================================================

COLORES_NIVEL = {"Alto": "#2a9d8f", "Medio": "#e9c46a", "Bajo": "#e76f51"}


def quitar_marco(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def guardar(nombre):
    ruta = CARPETA_GRAFICAS / nombre
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Grafica guardada: {ruta.relative_to(Path(__file__).parent)}")


def grafica_barras(df):
    """Barras: calificacion de cada estudiante ordenada."""
    ordenado = df.sort_values("calificacion", ascending=False)
    colores = [COLORES_NIVEL[n] for n in ordenado["nivel"]]

    plt.figure(figsize=(14, 7))
    plt.bar(ordenado["estudiante"], ordenado["calificacion"], color=colores)
    plt.axhline(MINIMO_APROBATORIO, color="red", linestyle="--", linewidth=2, label="Minimo aprobatorio (70)")
    plt.axhline(df["calificacion"].mean(), color="gray", linestyle=":", linewidth=2, label=f"Promedio ({df['calificacion'].mean():.1f})")

    for x, y in zip(ordenado["estudiante"], ordenado["calificacion"]):
        plt.text(x, y + 1, str(y), ha="center", fontsize=9)

    plt.title("Calificacion por estudiante", fontsize=18, fontweight="bold")
    plt.xlabel("Estudiante", fontsize=13, fontweight="bold")
    plt.ylabel("Calificacion", fontsize=13, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 105)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend(loc="upper right")
    quitar_marco(plt.gca())
    guardar("01_barras_calificaciones.png")


def grafica_dispersion(df):
    """Dispersion: relacion entre horas de estudio y calificacion."""
    plt.figure(figsize=(11, 7))
    for nivel_actual, grupo in df.groupby("nivel"):
        plt.scatter(grupo["horas_estudio"], grupo["calificacion"], s=120,
                    color=COLORES_NIVEL[nivel_actual], edgecolor="black", label=nivel_actual)

    for _, fila in df.iterrows():
        plt.annotate(fila["estudiante"], (fila["horas_estudio"], fila["calificacion"]),
                     xytext=(5, 5), textcoords="offset points", fontsize=8)

    # Linea de tendencia calculada con una regresion lineal simple.
    pendiente, intercepto = np.polyfit(df["horas_estudio"], df["calificacion"], 1)
    x = sorted(df["horas_estudio"].unique())
    plt.plot(x, [pendiente * v + intercepto for v in x], color="black", linestyle="--",
             label=f"Tendencia (y = {pendiente:.1f}x + {intercepto:.1f})")

    plt.title("Horas de estudio vs calificacion", fontsize=18, fontweight="bold")
    plt.xlabel("Horas de estudio", fontsize=13, fontweight="bold")
    plt.ylabel("Calificacion", fontsize=13, fontweight="bold")
    plt.grid(linestyle="--", alpha=0.5)
    plt.legend()
    quitar_marco(plt.gca())
    guardar("02_dispersion_horas_vs_calificacion.png")


def grafica_pastel(df):
    """Pastel: porcentaje de aprobados y reprobados."""
    aprobados = (df["calificacion"] >= MINIMO_APROBATORIO).sum()
    reprobados = len(df) - aprobados

    plt.figure(figsize=(8, 8))
    plt.pie([aprobados, reprobados],
            labels=[f"Aprobados ({aprobados})", f"Reprobados ({reprobados})"],
            colors=["#2a9d8f", "#e76f51"], autopct="%1.1f%%", startangle=90,
            explode=(0, 0.06), wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 13})
    plt.title("Porcentaje de aprobacion", fontsize=18, fontweight="bold")
    guardar("03_pastel_aprobacion.png")


def grafica_histograma(df):
    """Histograma: distribucion de las calificaciones."""
    plt.figure(figsize=(11, 7))
    plt.hist(df["calificacion"], bins=range(40, 101, 10), color="#264653", edgecolor="white", rwidth=0.9)
    plt.axvline(df["calificacion"].mean(), color="red", linestyle="--", linewidth=2,
                label=f"Promedio = {df['calificacion'].mean():.1f}")
    plt.title("Distribucion de calificaciones", fontsize=18, fontweight="bold")
    plt.xlabel("Rango de calificacion", fontsize=13, fontweight="bold")
    plt.ylabel("Numero de estudiantes", fontsize=13, fontweight="bold")
    plt.xticks(range(40, 101, 10))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    quitar_marco(plt.gca())
    guardar("04_histograma_calificaciones.png")


def grafica_promedios_nivel(df):
    """Barras agrupadas: promedios de cada variable por nivel."""
    columnas = ["asistencia", "actividades_entregadas", "calificacion"]
    resumen = df.groupby("nivel")[columnas].mean().reindex(["Alto", "Medio", "Bajo"])

    ax = resumen.plot(kind="bar", figsize=(11, 7), color=["#457b9d", "#a8dadc", "#1d3557"], rot=0, width=0.75)
    for contenedor in ax.containers:
        ax.bar_label(contenedor, fmt="%.1f", fontsize=9)
    ax.set_title("Promedios por nivel de rendimiento", fontsize=18, fontweight="bold")
    ax.set_xlabel("Nivel", fontsize=13, fontweight="bold")
    ax.set_ylabel("Promedio", fontsize=13, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(["Asistencia", "Actividades entregadas", "Calificacion"])
    quitar_marco(ax)
    guardar("05_promedios_por_nivel.png")


def grafica_tablero(df):
    """Tablero: las cuatro graficas principales en una sola figura."""
    fig, axs = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("Tablero de rendimiento academico", fontsize=22, fontweight="bold")

    ordenado = df.sort_values("calificacion", ascending=False)
    axs[0, 0].bar(ordenado["estudiante"], ordenado["calificacion"],
                  color=[COLORES_NIVEL[n] for n in ordenado["nivel"]])
    axs[0, 0].axhline(MINIMO_APROBATORIO, color="red", linestyle="--")
    axs[0, 0].set_title("Calificacion por estudiante", fontweight="bold")
    axs[0, 0].tick_params(axis="x", rotation=60, labelsize=8)

    axs[0, 1].scatter(df["horas_estudio"], df["calificacion"],
                      c=[COLORES_NIVEL[n] for n in df["nivel"]], s=90, edgecolor="black")
    axs[0, 1].set_title("Horas de estudio vs calificacion", fontweight="bold")
    axs[0, 1].set_xlabel("Horas")
    axs[0, 1].set_ylabel("Calificacion")

    conteo = df["nivel"].value_counts().reindex(["Alto", "Medio", "Bajo"])
    axs[1, 0].pie(conteo, labels=conteo.index, autopct="%1.0f%%",
                  colors=[COLORES_NIVEL[n] for n in conteo.index], startangle=90)
    axs[1, 0].set_title("Estudiantes por nivel", fontweight="bold")

    axs[1, 1].plot(ordenado["estudiante"], ordenado["asistencia"], marker="o", label="Asistencia")
    axs[1, 1].plot(ordenado["estudiante"], ordenado["actividades_entregadas"], marker="s", label="Actividades")
    axs[1, 1].set_title("Asistencia y actividades (orden por calificacion)", fontweight="bold")
    axs[1, 1].tick_params(axis="x", rotation=60, labelsize=8)
    axs[1, 1].legend()

    for ax in axs.flat:
        quitar_marco(ax)

    plt.figtext(0.01, 0.005, "Fuente: datos_estudiantes.csv | Elaboracion propia | UTVT", fontsize=10, color="gray")
    guardar("06_tablero.png")


# ============================================================
# 4. PROGRAMA PRINCIPAL
# ============================================================

def main():
    # Guardamos y volvemos a leer el CSV, igual que en la practica 06.
    pd.DataFrame(datos).to_csv(ARCHIVO, index=False)
    df = pd.read_csv(ARCHIVO)
    print(f"Archivo leido: {ARCHIVO.name} ({df.shape[0]} filas, {df.shape[1]} columnas)")

    # Agregamos una columna calculada a partir de la calificacion.
    df["nivel"] = df["calificacion"].apply(nivel)

    consultas(df)

    titulo("Generando graficas")
    CARPETA_GRAFICAS.mkdir(exist_ok=True)
    grafica_barras(df)
    grafica_dispersion(df)
    grafica_pastel(df)
    grafica_histograma(df)
    grafica_promedios_nivel(df)
    grafica_tablero(df)

    print("\n" + "=" * 60)
    print("Consultas y graficas generadas correctamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()
