# ============================================================
# PRACTICA 09: CLIENTE QUE HACE PETICIONES A LA API
# Archivo: p09_cliente_peticiones.py
#
# OBJETIVO:
# Consumir la API de la practica 08 mediante peticiones HTTP
# con la biblioteca requests, mostrar las respuestas JSON y
# construir una grafica con los datos recibidos.
#
# pip install requests matplotlib
#
# EJECUTAR (en dos terminales):
#   1) uvicorn p08_api_consultas:app --port 8008
#   2) python p09_cliente_peticiones.py
# ============================================================

from pathlib import Path

# requests permite enviar peticiones HTTP desde Python.
import requests

import matplotlib.pyplot as plt

URL_BASE = "http://127.0.0.1:8008"
CARPETA = Path(__file__).with_name("graficas_p09")


def peticion(ruta, **parametros):
    """Envia una peticion GET y devuelve la respuesta en JSON."""
    respuesta = requests.get(f"{URL_BASE}{ruta}", params=parametros, timeout=10)
    print(f"\nGET {respuesta.url} -> {respuesta.status_code}")
    respuesta.raise_for_status()
    return respuesta.json()


def main():
    try:
        requests.get(URL_BASE, timeout=3)
    except requests.ConnectionError:
        print("La API no esta activa. Ejecuta primero:")
        print("  uvicorn p08_api_consultas:app --port 8008")
        return

    CARPETA.mkdir(exist_ok=True)

    # Peticion 1: estadisticas generales.
    estadisticas = peticion("/estadisticas")
    print(f"Aprobados: {estadisticas['aprobados']} | Reprobados: {estadisticas['reprobados']} "
          f"| Aprobacion: {estadisticas['porcentaje_aprobacion']}%")

    # Peticion 2: consulta con filtros (query params).
    alto = peticion("/estudiantes", nivel="Alto", ordenar="horas_estudio")
    for e in alto["estudiantes"]:
        print(f"  {e['estudiante']:<10} {e['horas_estudio']} hrs  calificacion {e['calificacion']}")

    # Peticion 3: un solo estudiante.
    ana = peticion("/estudiantes/Ana")
    print(f"  {ana}")

    # Peticion 4: un estudiante que no existe (error 404).
    respuesta = requests.get(f"{URL_BASE}/estudiantes/Nadie", timeout=10)
    print(f"\nGET {respuesta.url} -> {respuesta.status_code} {respuesta.json()}")

    # Peticion 5: promedios por nivel y grafica construida con la respuesta.
    niveles = peticion("/niveles")
    nombres = [n["nivel"] for n in niveles]
    promedios = [n["calificacion"] for n in niveles]

    plt.figure(figsize=(9, 6))
    barras = plt.bar(nombres, promedios, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    plt.bar_label(barras, fmt="%.1f")
    plt.title("Promedio de calificacion por nivel (datos de la API)", fontweight="bold")
    plt.ylabel("Calificacion promedio")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(CARPETA / "promedio_por_nivel.png", dpi=150)
    plt.close()
    print(f"Grafica guardada: {CARPETA.name}/promedio_por_nivel.png")

    # Peticion 6: descargar una grafica generada por la API.
    imagen = requests.get(f"{URL_BASE}/grafica/barras", timeout=10)
    print(f"\nGET {imagen.url} -> {imagen.status_code} ({imagen.headers['content-type']})")
    (CARPETA / "barras_desde_api.png").write_bytes(imagen.content)
    print(f"Grafica guardada: {CARPETA.name}/barras_desde_api.png")


if __name__ == "__main__":
    main()
