# ============================================================
# BÚSQUEDA CIEGA - DEPTH FIRST SEARCH (DFS)
# ============================================================
#
# DFS = Depth First Search
#      Búsqueda en Profundidad
#
# IDEA PRINCIPAL:
# DFS intenta avanzar lo más profundo posible por un camino
# antes de regresar y probar otro camino.
#
# Es una búsqueda CIEGA porque NO utiliza información adicional
# que indique qué tan cerca estamos del objetivo.
# ============================================================

# DFS conceptualmente utiliza una estructura tipo pila:

#          ┌─────┐
#entra →   │  A  │
#          │  B  │
#          │  D  │ ← sale primero
#          └─────┘
#            LIFO

# ------------------------------------------------------------
# 1. DEFINIMOS EL ESPACIO DE BÚSQUEDA
# ------------------------------------------------------------
#
# El diccionario representa un grafo.
#
# Cada clave representa un estado.
# La lista asociada contiene los estados vecinos
# a los que podemos desplazarnos.
#
# Visualmente podemos imaginar:
#
#              A
#             / \
#            B   C
#           / \   \
#          D   E   F
#
# DFS comenzará en A y buscará llegar a F.
# ------------------------------------------------------------

grafo = {

    "A": ["B", "C"],

    "B": ["D", "E"],

    "C": ["F"],

    "D": [],

    "E": [],

    "F": []
}


# ------------------------------------------------------------
# 2. FUNCIÓN DFS
# ------------------------------------------------------------

def dfs(actual, objetivo, visitados=None, camino=None):

    # --------------------------------------------------------
    # Crear las estructuras en la primera llamada
    # --------------------------------------------------------
    #
    # visitados:
    # Guarda los estados que ya hemos explorado.
    #
    # camino:
    # Guarda la ruta que estamos siguiendo actualmente.
    # --------------------------------------------------------

    if visitados is None:
        visitados = set()

    if camino is None:
        camino = []


    # --------------------------------------------------------
    # 3. MARCAR EL ESTADO ACTUAL COMO VISITADO
    # --------------------------------------------------------

    visitados.add(actual)

    # Agregamos el estado al camino actual.
    camino.append(actual)


    # Mostramos qué estado estamos explorando.
    print("Visitando:", actual)


    # --------------------------------------------------------
    # 4. COMPROBAR SI ENCONTRAMOS EL OBJETIVO
    # --------------------------------------------------------

    if actual == objetivo:

        # copy() es importante porque camino seguirá
        # modificándose durante el proceso.
        return camino.copy()


    # --------------------------------------------------------
    # 5. EXPLORAR LOS VECINOS
    # --------------------------------------------------------
    #
    # DFS toma un vecino y profundiza en él.
    # --------------------------------------------------------

    for vecino in grafo[actual]:

        # Solo exploramos estados que todavía
        # no hayan sido visitados.

        if vecino not in visitados:

            # Llamamos nuevamente a DFS.
            #
            # Esto es una llamada RECURSIVA.
            resultado = dfs(
                vecino,
                objetivo,
                visitados,
                camino
            )


            # ------------------------------------------------
            # 6. ¿SE ENCONTRÓ EL OBJETIVO?
            # ------------------------------------------------

            if resultado:

                return resultado


    # --------------------------------------------------------
    # 7. RETROCESO (BACKTRACKING)
    # --------------------------------------------------------
    #
    # Si llegamos aquí significa que desde "actual"
    # no encontramos el objetivo.
    #
    # Entonces eliminamos este estado del camino
    # y regresamos al estado anterior.
    # --------------------------------------------------------

    camino.pop()

    return None


# ============================================================
# 8. EJECUTAR LA BÚSQUEDA
# ============================================================

ruta = dfs("A", "F")


# ============================================================
# 9. MOSTRAR EL RESULTADO
# ============================================================

print("\nRuta encontrada:")

if ruta:

    print(" -> ".join(ruta))

else:

    print("No se encontró una ruta.")

#¿Qué significa "ciega"?
#No significa que el algoritmo no tenga información del problema.
#Significa que no utiliza una heurística que le diga qué tan prometedor es un estado.
#DFS solamente sabe:
#"Estoy en A y desde A puedo ir a B o C."
#No sabe:
#"C está más cerca de F que B."


#DFS significa "profundizar"
#La regla mental es: "Primero bajo todo lo posible; si no funciona, regreso."

#¿Encontré el objetivo?
 
#Sí regreso la ruta
#No continúo buscando