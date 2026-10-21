# ============================================================
# PROBLEMA DE BÚSQUEDA
# ============================================================

# Definición formal de un problema de búsqueda

# En Inteligencia Artificial, 
# un problema de búsqueda consiste en determinar 
# una secuencia de acciones que permita a un agente 
# pasar de un estado inicial a un estado objetivo, 
# utilizando las acciones disponibles y respetando las restricciones del problema.

# Formalmente, un problema de búsqueda puede representarse como una tupla de cinco elementos:

# P=(S,A,s0,G,C)

# donde:

# Elemento	Significado
# (S)	    Conjunto de todos los estados posibles
# (A)	    Conjunto de acciones que el agente puede realizar
# (s0)	    Estado inicial
# (G)	    Conjunto de estados objetivo
# (C)	    Costo asociado a las acciones o caminos

# 1. CONJUNTO DE ESTADOS (S)
# ------------------------------------------------------------
# Cada letra representa una posición posible del agente. Estados 
# Representan todas las situaciones en las que puede encontrarse el agente.
# Por ejemplo, para un robot que se mueve en un mapa:
# Cada letra representa una posición posible.

estados = {"A", "B", "C", "D", "E", "F"}


# 2. ACCIONES / CONEXIONES (A)
# ------------------------------------------------------------
# Diccionario que indica a qué estados puede desplazarse
# el agente desde cada estado izquierda o derecha

acciones = {
    "A": ["B", "D"],
    "B": ["A", "C"],
    "C": ["B", "F"],
    "D": ["A", "E"],
    "E": ["D", "F"],
    "F": ["C", "E"]
}


# 3. ESTADO INICIAL (s0)
# ------------------------------------------------------------
# El agente comienza en A.

estado_inicial = "A"


# 4. ESTADO OBJETIVO (G)
# ------------------------------------------------------------
# El objetivo consiste en llegar a F.

estado_objetivo = "F"


# ============================================================
# ALGORITMO DE BÚSQUEDA EN ANCHURA (BFS)
# ============================================================

def busqueda_anchura(inicio, objetivo):
    """
    Busca un camino desde el estado inicial
    hasta el estado objetivo utilizando BFS.
    """

    # Cola de estados pendientes por explorar.
    cola = [[inicio]]

    # Estados que ya fueron visitados.
    visitados = set()

    # Mientras existan caminos pendientes...
    while cola:

        # Extraemos el primer camino de la cola.
        camino = cola.pop(0)

        # El último estado del camino es el estado actual.
        estado_actual = camino[-1]

        # Si ya visitamos este estado, lo ignoramos.
        if estado_actual in visitados:
            continue

        # Registramos el estado como visitado.
        visitados.add(estado_actual)

        # Mostramos el estado que estamos explorando.
        print("Explorando:", estado_actual)

        # Comprobamos si encontramos el objetivo.
        if estado_actual == objetivo:
            return camino

        # Obtenemos los estados vecinos.
        for vecino in acciones[estado_actual]:

            # Si todavía no hemos visitado el vecino...
            if vecino not in visitados:

                # Creamos un nuevo camino.
                nuevo_camino = camino + [vecino]

                # Lo agregamos a la cola.
                cola.append(nuevo_camino)

    # Si no existe una solución...
    return None


# ============================================================
# EJECUTAR LA BÚSQUEDA
# ============================================================

solucion = busqueda_anchura(
    estado_inicial,
    estado_objetivo
)


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

if solucion:

    print("\n¡Objetivo encontrado!")

    print("Ruta encontrada:")

    print(" -> ".join(solucion))

    print("\nNúmero de movimientos:", len(solucion) - 1)

else:

    print("\nNo se encontró una solución.")