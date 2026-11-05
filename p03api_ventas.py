
# ============================================================
# PRACTICA 04: API REST CON FASTAPI Y MONGODB ATLAS
# Archivo: apis/p03_api_ventas.py
#
# OBJETIVO:
# Construir una API REST para administrar ventas mediante
# las operaciones CRUD:
#
# C = Create  -> Crear una venta
# R = Read    -> Consultar ventas
# U = Update  -> Actualizar una venta
# D = Delete  -> Eliminar una venta
#
# BASE DE DATOS: ventas_db
# COLECCION:     ventas
# ============================================================


# ============================================================
# 1. IMPORTAR LAS BIBLIOTECAS
# ============================================================

# os permite recuperar variables de entorno.
import os

# quote_plus codifica caracteres especiales en usuario y
# contraseña antes de construir la URI de MongoDB.
from urllib.parse import quote_plus

# load_dotenv carga las variables definidas en el archivo .env.
from dotenv import load_dotenv

# MongoClient establece la comunicación con MongoDB.
from pymongo import MongoClient

# ObjectId representa los identificadores propios de MongoDB.
from bson import ObjectId

# FastAPI permite crear los endpoints de nuestra API.
from fastapi import FastAPI, HTTPException, Query

# BaseModel permite validar los datos recibidos.
from pydantic import BaseModel, Field, ConfigDict

# Any permite indicar que un diccionario puede contener
# diferentes tipos de valores.
from typing import Any


# ============================================================
# 2. CARGAR LA CONFIGURACION DEL ARCHIVO .env
# ============================================================

# Busca y carga las variables del archivo .env.
# Ejecuta el programa desde la raiz de bigdata_ventas.
load_dotenv()

# Recuperamos las credenciales y los nombres configurados.
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")

# Si no se especifican, utilizamos los nombres de la practica.
MONGO_DB = os.getenv("MONGO_DB", "ventas_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "ventas")


# ============================================================
# 3. VALIDAR LA CONFIGURACION
# ============================================================

# No intentamos conectarnos si faltan las credenciales.
if not all([MONGO_USER, MONGO_PASSWORD, MONGO_CLUSTER]):
    raise RuntimeError(
        "Falta configurar MONGO_USER, MONGO_PASSWORD "
        "o MONGO_CLUSTER en el archivo .env"
    )


# ============================================================
# 4. CONSTRUIR LA URI DE MONGODB ATLAS
# ============================================================

# Codificamos usuario y contraseña para evitar problemas
# con caracteres especiales en la cadena de conexion.
usuario_seguro = quote_plus(MONGO_USER)
contrasena_segura = quote_plus(MONGO_PASSWORD)

# Construimos la direccion completa de MongoDB Atlas.
# La URI no debe imprimirse porque contiene credenciales.
MONGODB_URI = (
    f"mongodb+srv://{usuario_seguro}:{contrasena_segura}"
    f"@{MONGO_CLUSTER}/"
    "?retryWrites=true&w=majority"
)


# ============================================================
# 5. CREAR EL CLIENTE Y SELECCIONAR LA BASE DE DATOS
# ============================================================

# MongoClient administra la conexion con MongoDB.
# El tiempo limite evita esperar indefinidamente si Atlas
# no esta disponible o no permite el acceso.
cliente_mongo = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

# Seleccionamos la base de datos de la practica.
db = cliente_mongo[MONGO_DB]

# Seleccionamos la coleccion donde se guardaran las ventas.
coleccion_ventas = db[MONGO_COLLECTION]


# ============================================================
# 6. CREAR LA APLICACION FASTAPI
# ============================================================

app = FastAPI(
    title="API de Ventas - Practica 04",
    description=(
        "API educativa para administrar ventas con "
        "Python, FastAPI y MongoDB Atlas."
    ),
    version="1.0.0"
)


# ============================================================
# 7. VERIFICAR LA CONEXION AL INICIAR LA API
# ============================================================

@app.on_event("startup")
def verificar_conexion():
    """
    Se ejecuta cuando inicia la aplicacion.

    El comando ping comprueba que MongoDB responda.
    Si la conexion falla, se informa el error y se detiene
    el inicio de la aplicacion.
    """

    try:
        cliente_mongo.admin.command("ping")

        print("========================================")
        print("API DE VENTAS INICIADA CORRECTAMENTE")
        print(f"Base de datos: {MONGO_DB}")
        print(f"Coleccion: {MONGO_COLLECTION}")
        print("Conexion con MongoDB Atlas: OK")
        print("========================================")

    except Exception as error:
        # No mostramos la URI ni la contraseña.
        print("ERROR: No fue posible conectar con MongoDB Atlas.")
        print("Tipo de error:", type(error).__name__)

        # Lanzamos un error para no iniciar la aplicacion
        # como si la base de datos estuviera disponible.
        raise RuntimeError(
            "Verifica las credenciales, el cluster "
            "y el acceso de red de MongoDB Atlas."
        ) from error


# ============================================================
# 8. CERRAR LA CONEXION AL APAGAR LA API
# ============================================================

@app.on_event("shutdown")
def cerrar_conexion():
    """
    Se ejecuta cuando se apaga la aplicacion.
    Cerramos el cliente para liberar sus recursos.
    """

    cliente_mongo.close()
    print("Conexion con MongoDB cerrada.")


# ============================================================
# 9. DEFINIR EL MODELO DE DATOS DE UNA VENTA
# ============================================================

class Venta(BaseModel):
    """
    Define los campos que debe enviar el cliente al crear
    o reemplazar una venta.

    Pydantic comprueba los tipos y las restricciones.
    """

    # Producto vendido. No puede ser una cadena vacia.
    producto: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre del producto vendido"
    )

    # Cantidad: debe ser un entero mayor que cero.
    cantidad: int = Field(
        gt=0,
        description="Cantidad de unidades vendidas"
    )

    # Precio por unidad: no puede ser negativo.
    precio_unitario: float = Field(
        ge=0,
        description="Precio de una unidad del producto"
    )

    # Cliente que realizo la compra.
    cliente: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre o identificador del cliente"
    )

    # Categoria a la que pertenece el producto.
    categoria: str = Field(
        default="General",
        min_length=1,
        max_length=60,
        description="Categoria del producto"
    )

    # Rechaza campos adicionales que no esten definidos
    # en el modelo para detectar errores de captura.
    model_config = ConfigDict(extra="forbid")


# ============================================================
# 10. CONVERTIR DOCUMENTOS DE MONGODB A JSON
# ============================================================

def serializar_venta(documento: dict[str, Any]) -> dict[str, Any]:
    """
    Convierte un documento de MongoDB en un diccionario
    que FastAPI puede devolver como JSON.

    MongoDB utiliza _id con tipo ObjectId.
    JSON no admite ObjectId, por eso lo convertimos a texto.
    """

    # Creamos una copia para no modificar el documento original.
    venta = documento.copy()

    # Transformamos ObjectId en una cadena de caracteres.
    venta["_id"] = str(venta["_id"])

    # Calculamos el importe total de la venta.
    venta["total"] = round(
        venta["cantidad"] * venta["precio_unitario"],
        2
    )

    return venta


# ============================================================
# 11. ENDPOINT PRINCIPAL
# ============================================================

@app.get("/")
def inicio():
    """
    GET /

    Permite comprobar que la API esta respondiendo.
    No consulta ni modifica las ventas.
    """

    return {
        "mensaje": "Bienvenido a la API de Ventas",
        "estado": "activa",
        "documentacion": "/docs",
        "base_datos": MONGO_DB,
        "coleccion": MONGO_COLLECTION
    }


# ============================================================
# 12. ENDPOINT DE SALUD DE LA BASE DE DATOS
# ============================================================

@app.get("/salud")
def comprobar_salud():
    """
    GET /salud

    Comprueba si MongoDB responde en ese momento.
    Devuelve un error HTTP 503 si no esta disponible.
    """

    try:
        cliente_mongo.admin.command("ping")

        return {
            "api": "disponible",
            "mongodb": "conectado"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="La base de datos no esta disponible."
        ) from error


# ============================================================
# 13. CONSULTAR TODAS LAS VENTAS
# ============================================================

@app.get("/ventas")
def listar_ventas(
    limite: int = Query(default=20, ge=1, le=100),
    saltar: int = Query(default=0, ge=0)
):
    """
    GET /ventas

    Recupera las ventas almacenadas.

    limite:
        Maximo de documentos que se devolveran.

    saltar:
        Numero de documentos que se omiten.
        Es util para implementar paginacion.
    """

    try:
        # Ordenamos por identificador para mantener
        # un orden consistente en las consultas.
        cursor = (
            coleccion_ventas
            .find()
            .sort("_id", 1)
            .skip(saltar)
            .limit(limite)
        )

        # Convertimos cada documento a un diccionario JSON.
        ventas = [
            serializar_venta(documento)
            for documento in cursor
        ]

        # Contamos los documentos existentes en la coleccion.
        total_documentos = coleccion_ventas.count_documents({})

        return {
            "total_documentos": total_documentos,
            "cantidad_devueltos": len(ventas),
            "limite": limite,
            "saltar": saltar,
            "ventas": ventas
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar las ventas."
        ) from error


# ============================================================
# 14. CONSULTAR UNA VENTA POR SU IDENTIFICADOR
# ============================================================

@app.get("/ventas/{venta_id}")
def obtener_venta(venta_id: str):
    """
    GET /ventas/IDENTIFICADOR

    Busca una venta especifica por su ObjectId de MongoDB.
    """

    # Primero comprobamos que el identificador sea valido.
    if not ObjectId.is_valid(venta_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador de la venta no es valido."
        )

    try:
        # Convertimos la cadena a ObjectId para buscarla.
        documento = coleccion_ventas.find_one(
            {"_id": ObjectId(venta_id)}
        )

        # Si no existe, respondemos con HTTP 404.
        if documento is None:
            raise HTTPException(
                status_code=404,
                detail="La venta solicitada no existe."
            )

        return serializar_venta(documento)

    except HTTPException:
        # Conservamos los codigos HTTP generados arriba.
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar la venta."
        ) from error


# ============================================================
# 15. REGISTRAR UNA NUEVA VENTA
# ============================================================

@app.post("/ventas", status_code=201)
def crear_venta(venta: Venta):
    """
    POST /ventas

    Recibe una venta validada por Pydantic y la inserta
    en la coleccion de MongoDB.
    """

    try:
        # Convertimos el modelo validado en un diccionario.
        datos = venta.model_dump()

        # insert_one guarda un nuevo documento en MongoDB.
        resultado = coleccion_ventas.insert_one(datos)

        # Recuperamos el documento que acabamos de guardar.
        documento = coleccion_ventas.find_one(
            {"_id": resultado.inserted_id}
        )

        # Devolvemos el registro creado con su identificador.
        return {
            "mensaje": "Venta registrada correctamente",
            "venta": serializar_venta(documento)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible registrar la venta."
        ) from error


# ============================================================
# 16. ACTUALIZAR UNA VENTA EXISTENTE
# ============================================================

@app.put("/ventas/{venta_id}")
def actualizar_venta(venta_id: str, venta: Venta):
    """
    PUT /ventas/IDENTIFICADOR

    Reemplaza los campos definidos de una venta existente.

    Como se utiliza el modelo Venta completo, el cliente debe
    enviar todos los campos requeridos en la solicitud.
    """

    # Validar el identificador antes de consultar MongoDB.
    if not ObjectId.is_valid(venta_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador de la venta no es valido."
        )

    try:
        # Convertimos el modelo validado a diccionario.
        datos_actualizados = venta.model_dump()

        # $set actualiza los campos indicados.
        resultado = coleccion_ventas.update_one(
            {"_id": ObjectId(venta_id)},
            {"$set": datos_actualizados}
        )

        # Si no coincide ningun documento, la venta no existe.
        if resultado.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="No existe la venta que deseas actualizar."
            )

        # Recuperamos la venta actualizada.
        documento = coleccion_ventas.find_one(
            {"_id": ObjectId(venta_id)}
        )

        return {
            "mensaje": "Venta actualizada correctamente",
            "venta": serializar_venta(documento),
            "modificada": resultado.modified_count > 0
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible actualizar la venta."
        ) from error


# ============================================================
# 17. ELIMINAR UNA VENTA
# ============================================================

@app.delete("/ventas/{venta_id}")
def eliminar_venta(venta_id: str):
    """
    DELETE /ventas/IDENTIFICADOR

    Elimina una venta de la coleccion.

    ATENCION:
    La eliminacion es real y no se revierte automaticamente.
    """

    # Verificamos que el identificador tenga un formato valido.
    if not ObjectId.is_valid(venta_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador de la venta no es valido."
        )

    try:
        # delete_one elimina el documento que coincide.
        resultado = coleccion_ventas.delete_one(
            {"_id": ObjectId(venta_id)}
        )

        # Si no se elimino nada, la venta no existia.
        if resultado.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="No existe la venta que deseas eliminar."
            )

        return {
            "mensaje": "Venta eliminada correctamente",
            "id_eliminado": venta_id
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No fue posible eliminar la venta."
        ) from error
