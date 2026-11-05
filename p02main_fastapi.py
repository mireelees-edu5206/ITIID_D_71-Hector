
# ============================================================
# PROYECTO: MI PRIMERA API CON FASTAPI
# ARCHIVO: mainfastapi.py
# OBJETIVO: Crear una API que responda a solicitudes HTTP.
# ============================================================

#pip install fastapi "uvicorn[standard]"
#¿Qué instalamos?
#- fastapi: permite definir la API y sus operaciones.
#- uvicorn: ejecuta el servidor web que recibirá las peticiones.
#- standard: instala dependencias adicionales útiles para ejecutar y desarrollar el servidor.

# 1. Importamos FastAPI.
# FastAPI nos proporciona las herramientas para construir la API.
from fastapi import FastAPI
from pydantic import BaseModel

# 2. Creamos la aplicación.
# Esta variable representa nuestra API.
app = FastAPI(
    title="Mi primera API",
    description="API educativa desarrollada con Python",
    version="1.0.0"
)

# Modelo del JSON que recibirá el endpoint POST.
class Mensaje(BaseModel):
    texto: str


# ============================================================
# ENDPOINT 1: RUTA PRINCIPAL
# ============================================================

# @app.get("/") indica que atenderemos solicitudes HTTP GET
# realizadas a la ruta raíz "/".
#
# La función inicio() se ejecutará cuando un cliente visite
# esa ruta.
#
# FastAPI convierte automáticamente el diccionario de Python
# en una respuesta JSON.

@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a mi primera API",
        "estado": "Funcionando",
        "lenguaje": "Python"
    }


# ============================================================
# ENDPOINT 2: RUTA DE SALUDO
# ============================================================

# Esta ruta permite consultar un saludo.
# La dirección será /saludo.

@app.get("/saludo")
def saludo():
    return {
        "mensaje": "Hola, estamos aprendiendo a crear APIs"
    }

# POST recibe datos enviados por el cliente y los devuelve.
@app.post("/hola")
def eco(mensaje: Mensaje):
    return {"mensaje_recibido": mensaje.texto}


#¿Qué acabamos de construir?

#Hay cuatro conceptos importantes:

#Concepto	        Explicación
#app = FastAPI()	Crea la aplicación.
#@app.get("/")	    Define una operación GET para la ruta raíz.
#def inicio()	    Contiene la lógica que se ejecutará.
#return {...}	    Devuelve datos que FastAPI convierte en JSON.
#@app.post("/eco")  Recibe un JSON y devuelve el texto enviado.

#Un endpoint es una dirección de la API asociada a una operación. 
#Por ejemplo, /saludo usa GET y /eco usa POST.