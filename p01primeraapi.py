
# ============================================================
# API BÁSICA UTILIZANDO SOLAMENTE PYTHON
# Sin ningun framework
# ============================================================

#¿Qué es una API?
#Una API (Application Programming Interface, o interfaz de programación de aplicaciones) 
#permite que dos programas se comuniquen entre sí.

#Por ejemplo, se desarrollan un sistema de inteligencia artificial 
#para recomendar rutas de transporte. La interfaz gráfica solicita una ruta, 
#la API recibe la petición, procesa los datos y devuelve una respuesta.

#1.- Aplicacion del cliente
#   Una pagina web, aplicacion movil o interfaz grafica en python 
#   la soclicitud esta en http y respuesta en json

#2.- API
#Recibe, valida y procesa las solicitudes, tokens.

#3.- Lógica del sistema o base de datos
#Ejecuta los calculos, consulta información o utiliza un modelo de ia



# Permite crear un servidor HTTP.
from http.server import BaseHTTPRequestHandler, HTTPServer

# Permite convertir diccionarios de Python a formato JSON.
import json


# Definimos la clase que atenderá las solicitudes HTTP.
class MiAPI(BaseHTTPRequestHandler):

    # Este método se ejecuta cuando recibimos una petición GET.
    def do_GET(self):

        # Definimos la respuesta de nuestra API.
        if self.path == "/":
            respuesta = {
                "mensaje": "Bienvenido a mi API",
                "estado": "Funcionando"
            }

        elif self.path == "/saludo":
            respuesta = {
                "mensaje": "Hola, estamos aprendiendo a crear APIs"
            }

        else:
            # Si la ruta no existe, devolvemos un error 404.
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"error": "Ruta no encontrada"}
                ).encode("utf-8")
            )
            return

        # Convertimos el diccionario en una cadena JSON
        # codificada como bytes para enviarla por HTTP.
        contenido = json.dumps(
            respuesta,
            ensure_ascii=False
        ).encode("utf-8")

        # Indicamos que la solicitud fue exitosa.
        self.send_response(200)

        # Informamos que la respuesta contiene JSON.
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        # Indicamos el tamaño del contenido.
        self.send_header(
            "Content-Length",
            str(len(contenido))
        )

        # Finalizamos las cabeceras HTTP.
        self.end_headers()

        # Enviamos el contenido al cliente.
        self.wfile.write(contenido)

    # Este método se ejecuta cuando recibimos una petición POST.
    def do_POST(self):
        # Este ejemplo solo acepta POST en la ruta /saludo.
        if self.path != "/saludo":
            respuesta = {"error": "Ruta no encontrada"}
            estado = 404
        else:
            try:
                # Content-Length indica cuántos bytes tiene el cuerpo enviado.
                longitud = int(self.headers.get("Content-Length", "0"))
                # Rechazamos cuerpos vacíos o demasiado grandes.
                if longitud <= 0 or longitud > 1_000_000:
                    raise ValueError

                # Leemos el cuerpo, lo decodificamos y convertimos el JSON
                # recibido en un diccionario de Python.
                datos = json.loads(self.rfile.read(longitud).decode("utf-8"))

                # Obtenemos el nombre y quitamos espacios al inicio y al final.
                nombre = datos.get("nombre", "").strip()
                if not nombre:
                    raise ValueError

                # Preparamos una respuesta exitosa.
                respuesta = {"mensaje": f"Hola, {nombre}. Recibimos tu POST."}
                estado = 200
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                # Si el cuerpo no es JSON válido o falta el nombre, respondemos 400.
                respuesta = {
                    "error": "Envía un JSON válido con el campo 'nombre'."
                }
                estado = 400

        # Convertimos la respuesta de Python a JSON codificado en UTF-8.
        contenido = json.dumps(
            respuesta,
            ensure_ascii=False
        ).encode("utf-8")

        # Enviamos el código HTTP y las cabeceras de la respuesta.
        self.send_response(estado)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        # Indicamos el tamaño exacto del contenido enviado.
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()

        # Enviamos el JSON al cliente.
        self.wfile.write(contenido)


# ============================================================
# INICIAR EL SERVIDOR
# ============================================================

if __name__ == "__main__":

    # Creamos el servidor en el puerto 8000.
    servidor = HTTPServer(
        ("127.0.0.1", 8000),
        MiAPI
    )

    print("API disponible en http://127.0.0.1:8000")
    print("Presiona CTRL+C para detener el servidor.")

    # Mantenemos el servidor en funcionamiento.
    servidor.serve_forever()
