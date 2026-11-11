# ============================================================
# PRACTICA 08: API DE CONSULTAS Y GRAFICAS CON FASTAPI
# Archivo: p08_api_consultas.py
#
# OBJETIVO:
# Exponer las consultas de la practica 07 como endpoints para
# que un cliente pueda hacer peticiones HTTP (GET) y recibir
# los resultados en JSON o como una grafica en PNG.
#
# pip install fastapi "uvicorn[standard]" pandas matplotlib
#
# EJECUTAR:
#   uvicorn p08_api_consultas:app --reload --port 8008
#
# PROBAR:
#   http://127.0.0.1:8008/docs
# ============================================================

# io permite guardar la imagen en memoria en lugar de un archivo.
import io

# Usamos un backend sin ventana porque el servidor no muestra graficas.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

# Reutilizamos los datos y la clasificacion de la practica 07.
from p07_consultas_graficas import COLORES_NIVEL, MINIMO_APROBATORIO, datos, nivel


# ============================================================
# 1. PREPARAR LOS DATOS
# ============================================================

df = pd.DataFrame(datos)
df["nivel"] = df["calificacion"].apply(nivel)
df["aprobado"] = df["calificacion"] >= MINIMO_APROBATORIO

COLUMNAS_NUMERICAS = ["horas_estudio", "asistencia", "actividades_entregadas", "calificacion"]


def a_json(tabla):
    """Convierte un DataFrame en una lista de diccionarios."""
    return tabla.to_dict(orient="records")


# ============================================================
# 2. CREAR LA APLICACION
# ============================================================

app = FastAPI(
    title="API de consultas de estudiantes",
    description="Consultas y graficas sobre el rendimiento academico",
    version="1.0.0",
)


# ============================================================
# 3. ENDPOINTS DE CONSULTA
# ============================================================

@app.get("/")
def inicio():
    return {
        "mensaje": "API de consultas de estudiantes",
        "documentacion": "/docs",
        "endpoints": [
            "/estudiantes",
            "/estudiantes/{nombre}",
            "/estadisticas",
            "/niveles",
            "/top",
            "/grafica/{tipo}",
        ],
    }


# GET /estudiantes?min_calificacion=80&nivel=Alto&ordenar=horas_estudio
# Los parametros despues de "?" se llaman query params y sirven
# para filtrar la consulta.
@app.get("/estudiantes")
def listar_estudiantes(
    min_calificacion: int = Query(default=0, ge=0, le=100),
    max_calificacion: int = Query(default=100, ge=0, le=100),
    nivel: str | None = Query(default=None, pattern="^(Alto|Medio|Bajo)$"),
    aprobado: bool | None = None,
    ordenar: str = Query(default="calificacion", pattern="^(estudiante|horas_estudio|asistencia|actividades_entregadas|calificacion)$"),
    descendente: bool = True,
):
    resultado = df[df["calificacion"].between(min_calificacion, max_calificacion)]
    if nivel:
        resultado = resultado[resultado["nivel"] == nivel]
    if aprobado is not None:
        resultado = resultado[resultado["aprobado"] == aprobado]
    resultado = resultado.sort_values(ordenar, ascending=not descendente)
    return {"total": len(resultado), "estudiantes": a_json(resultado)}


# GET /estudiantes/Ana  -> consulta un solo registro.
@app.get("/estudiantes/{nombre}")
def obtener_estudiante(nombre: str):
    fila = df[df["estudiante"].str.lower() == nombre.lower()]
    if fila.empty:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return a_json(fila)[0]


# GET /estadisticas -> promedio, minimo, maximo de cada columna.
@app.get("/estadisticas")
def estadisticas():
    descripcion = df[COLUMNAS_NUMERICAS].describe().round(2)
    return {
        "total_estudiantes": len(df),
        "aprobados": int(df["aprobado"].sum()),
        "reprobados": int((~df["aprobado"]).sum()),
        "porcentaje_aprobacion": round(df["aprobado"].mean() * 100, 2),
        "estadisticas": descripcion.to_dict(),
    }


# GET /niveles -> agrupa por nivel (equivalente a GROUP BY en SQL).
@app.get("/niveles")
def niveles():
    resumen = df.groupby("nivel")[COLUMNAS_NUMERICAS].mean().round(2)
    resumen["cantidad"] = df["nivel"].value_counts()
    resumen = resumen.reindex(["Alto", "Medio", "Bajo"]).reset_index()
    return a_json(resumen)


# GET /top?n=5&columna=asistencia
@app.get("/top")
def top(
    n: int = Query(default=5, ge=1, le=20),
    columna: str = Query(default="calificacion", pattern="^(horas_estudio|asistencia|actividades_entregadas|calificacion)$"),
):
    return a_json(df.nlargest(n, columna)[["estudiante", columna]])


# ============================================================
# 4. ENDPOINT DE GRAFICAS
# ============================================================

def imagen_png(fig):
    """Convierte una figura de matplotlib en una respuesta PNG."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")


# GET /grafica/barras | dispersion | pastel | niveles
@app.get("/grafica/{tipo}")
def grafica(tipo: str):
    fig, ax = plt.subplots(figsize=(11, 6))

    if tipo == "barras":
        ordenado = df.sort_values("calificacion", ascending=False)
        ax.bar(ordenado["estudiante"], ordenado["calificacion"],
               color=[COLORES_NIVEL[n] for n in ordenado["nivel"]])
        ax.axhline(MINIMO_APROBATORIO, color="red", linestyle="--", label="Minimo aprobatorio")
        ax.set_title("Calificacion por estudiante", fontweight="bold")
        ax.set_ylabel("Calificacion")
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
    elif tipo == "dispersion":
        ax.scatter(df["horas_estudio"], df["calificacion"],
                   c=[COLORES_NIVEL[n] for n in df["nivel"]], s=100, edgecolor="black")
        ax.set_title("Horas de estudio vs calificacion", fontweight="bold")
        ax.set_xlabel("Horas de estudio")
        ax.set_ylabel("Calificacion")
    elif tipo == "pastel":
        conteo = df["aprobado"].value_counts().reindex([True, False])
        ax.pie(conteo, labels=["Aprobados", "Reprobados"], autopct="%1.1f%%",
               colors=["#2a9d8f", "#e76f51"], startangle=90)
        ax.set_title("Porcentaje de aprobacion", fontweight="bold")
    elif tipo == "niveles":
        conteo = df["nivel"].value_counts().reindex(["Alto", "Medio", "Bajo"])
        ax.bar(conteo.index, conteo.values, color=[COLORES_NIVEL[n] for n in conteo.index])
        ax.set_title("Estudiantes por nivel", fontweight="bold")
        ax.set_ylabel("Cantidad")
    else:
        plt.close(fig)
        raise HTTPException(status_code=404, detail="Usa: barras, dispersion, pastel o niveles")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return imagen_png(fig)
