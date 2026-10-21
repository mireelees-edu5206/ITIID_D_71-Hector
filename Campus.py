import math
import random
import heapq
from collections import deque
from itertools import permutations
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# =====================================================================
# 1. MODELO DEL CAMPUS: Grafo de 9 nodos (Base + 8 edificios)
#    Coordenadas (x, y). Las aristas son los caminos reales del campus
#    y su costo es la distancia euclidiana entre los edificios.
# =====================================================================
nodos = {
    'BASE':        (0, 0),   # Estación de robots / almacén
    'Biblioteca':  (2, 7),
    'Ingenieria':  (3, 5),
    'Laboratorio': (7, 8),
    'Auditorio':   (8, 5),
    'Cafeteria':   (5, 4),
    'Rectoria':    (5, 1),
    'Gimnasio':    (9, 2),
    'Dormitorios': (2, 2),
}

# Caminos físicos del campus (aristas del grafo)
aristas = [
    ('BASE', 'Dormitorios'), ('BASE', 'Rectoria'),
    ('Dormitorios', 'Biblioteca'), ('Dormitorios', 'Ingenieria'), ('Dormitorios', 'Rectoria'),
    ('Rectoria', 'Cafeteria'), ('Rectoria', 'Gimnasio'),
    ('Biblioteca', 'Ingenieria'), ('Biblioteca', 'Laboratorio'),
    ('Ingenieria', 'Cafeteria'), ('Ingenieria', 'Laboratorio'),
    ('Cafeteria', 'Auditorio'), ('Cafeteria', 'Laboratorio'), ('Cafeteria', 'Gimnasio'),
    ('Auditorio', 'Laboratorio'), ('Auditorio', 'Gimnasio'),
]

EDIFICIOS = [n for n in nodos if n != 'BASE']

def dist_euclidiana(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# Grafo con pesos (diccionario de adyacencia)
grafo = {n: {} for n in nodos}
for a, b in aristas:
    w = dist_euclidiana(nodos[a], nodos[b])
    grafo[a][b] = w
    grafo[b][a] = w

# =====================================================================
# 2. BFS — Breadth-First Search: camino con MENOS SALTOS (ignora costos)
# =====================================================================
def bfs(origen, destino):
    visitados = {origen}
    cola = deque([[origen]])
    expandidos = 0
    while cola:
        camino = cola.popleft()
        expandidos += 1
        nodo = camino[-1]
        if nodo == destino:
            return camino, expandidos
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(camino + [vecino])
    return None, expandidos

# =====================================================================
# 3. UCS — Uniform Cost Search (Dijkstra): camino de MENOR COSTO
# =====================================================================
def ucs(origen, destino):
    heap = [(0.0, origen, [origen])]
    mejor_costo = {origen: 0.0}
    expandidos = 0
    while heap:
        costo, nodo, camino = heapq.heappop(heap)
        expandidos += 1
        if nodo == destino:
            return camino, costo, expandidos
        if costo > mejor_costo.get(nodo, float('inf')):
            continue
        for vecino, peso in grafo[nodo].items():
            nuevo = costo + peso
            if nuevo < mejor_costo.get(vecino, float('inf')):
                mejor_costo[vecino] = nuevo
                heapq.heappush(heap, (nuevo, vecino, camino + [vecino]))
    return None, float('inf'), expandidos

def costo_camino(camino):
    return sum(grafo[camino[i]][camino[i + 1]] for i in range(len(camino) - 1))

# =====================================================================
# 4. ORDEN DE ENTREGAS (TSP): visitar los 8 edificios y volver a BASE.
#    Distancia directa euclidiana entre entregas consecutivas.
# =====================================================================
def distancia_orden(orden):
    total = dist_euclidiana(nodos['BASE'], nodos[orden[0]])
    for i in range(len(orden) - 1):
        total += dist_euclidiana(nodos[orden[i]], nodos[orden[i + 1]])
    total += dist_euclidiana(nodos[orden[-1]], nodos['BASE'])
    return total

# --- Hill Climbing (vecinos por swap) ---
def hill_climbing_ruta(orden_inicial):
    evals = 0
    actual = orden_inicial.copy()
    mejor = distancia_orden(actual)
    evals += 1
    historial = []
    movimiento = "Orden inicial"
    while True:
        historial.append({'orden': actual.copy(), 'dist': round(mejor, 2), 'mov': movimiento})
        mejor_vecino, mejor_mov = None, ""
        for i in range(len(actual)):
            for j in range(i + 1, len(actual)):
                v = actual.copy()
                v[i], v[j] = v[j], v[i]
                dv = distancia_orden(v)
                evals += 1
                if dv < mejor - 1e-9:
                    mejor, mejor_vecino, mejor_mov = dv, v, f"Swap {v[i]} ↔ {v[j]}"
        if mejor_vecino is None:
            break
        actual = mejor_vecino
        movimiento = mejor_mov
    historial.append({'orden': actual.copy(), 'dist': round(mejor, 2), 'mov': "ÓPTIMO (máximo local)"})
    return actual, mejor, historial, evals

# --- Algoritmo Genético ---
def algoritmo_genetico(semilla=42, poblacion_n=80, generaciones=150, prob_mut=0.15, elite=2):
    rng = random.Random(semilla)
    evals = [0]

    def fitness(o):
        evals[0] += 1
        return distancia_orden(o)

    poblacion = [rng.sample(EDIFICIOS, len(EDIFICIOS)) for _ in range(poblacion_n)]
    convergencia = []

    def torneo(rng, pob, k=3):
        return min((rng.choice(pob) for _ in range(k)), key=fitness)

    def cruce_OX(p1, p2):
        n = len(p1)
        a, b = sorted(rng.sample(range(n), 2))
        hijo = [None] * n
        hijo[a:b + 1] = p1[a:b + 1]
        pos = (b + 1) % n
        for g in p2:
            if g not in hijo:
                hijo[pos] = g
                pos = (pos + 1) % n
        return hijo

    def mutar(ind):
        if rng.random() < prob_mut:
            i, j = rng.sample(range(len(ind)), 2)
            ind[i], ind[j] = ind[j], ind[i]
        return ind

    for gen in range(generaciones):
        poblacion.sort(key=fitness)
        convergencia.append(round(fitness(poblacion[0]), 2))
        nueva = poblacion[:elite]
        while len(nueva) < poblacion_n:
            hijo = mutar(cruce_OX(torneo(rng, poblacion), torneo(rng, poblacion)))
            nueva.append(hijo)
        poblacion = nueva

    poblacion.sort(key=fitness)
    evals[0] += 1
    return poblacion[0], distancia_orden(poblacion[0]), convergencia, evals[0]

# --- Óptimo global por fuerza bruta (8! = 40320) ---
def optimo_global():
    mejor, mejor_orden, evals = float('inf'), None, 0
    for perm in permutations(EDIFICIOS):
        evals += 1
        d = distancia_orden(list(perm))
        if d < mejor:
            mejor, mejor_orden = d, list(perm)
    return mejor_orden, mejor, evals

# =====================================================================
# 5. Ejecutar todo y armar respuesta
# =====================================================================
semilla_ga = 42
orden_azul = EDIFICIOS.copy()
random.Random(7).shuffle(orden_azul)

def ejecutar_todo(destino='Laboratorio', semilla=None):
    global semilla_ga
    if semilla is not None:
        semilla_ga = semilla

    # --- Parte A: Búsqueda en grafo BASE -> destino ---
    camino_bfs, bfs_exp = bfs('BASE', destino)
    camino_ucs, costo_ucs, ucs_exp = ucs('BASE', destino)
    costo_bfs = costo_camino(camino_bfs)

    # --- Parte B: Orden de entregas (TSP) ---
    hc_orden, hc_dist, hc_hist, hc_evals = hill_climbing_ruta(orden_azul)
    ga_orden, ga_dist, ga_conv, ga_evals = algoritmo_genetico(semilla=semilla_ga)
    opt_orden, opt_dist, opt_evals = optimo_global()
    factorial_8 = math.factorial(len(EDIFICIOS))  # 8! = 40,320

    # --- Veredictos de comparación ---
    mismo_bfs_ucs = camino_bfs == camino_ucs
    mismo_hc_ga = hc_orden == ga_orden
    hc_es_optimo = abs(hc_dist - opt_dist) < 1e-6
    ga_es_optimo = abs(ga_dist - opt_dist) < 1e-6

    return {
        'destino': destino,
        'bfs_camino': camino_bfs,
        'bfs_saltos': len(camino_bfs) - 1,
        'bfs_costo': round(costo_bfs, 2),
        'bfs_exp': bfs_exp,
        'ucs_camino': camino_ucs,
        'ucs_costo': round(costo_ucs, 2),
        'ucs_exp': ucs_exp,
        'mismo_bfs_ucs': mismo_bfs_ucs,
        'hc_orden': hc_orden,
        'hc_dist': round(hc_dist, 2),
        'hc_hist': hc_hist,
        'hc_evals': hc_evals,
        'hc_es_optimo': hc_es_optimo,
        'ga_orden': ga_orden,
        'ga_dist': round(ga_dist, 2),
        'ga_conv': ga_conv[:: max(1, len(ga_conv) // 60)],
        'ga_gens': len(ga_conv),
        'ga_semilla': semilla_ga,
        'ga_evals': ga_evals,
        'ga_es_optimo': ga_es_optimo,
        'mismo_hc_ga': mismo_hc_ga,
        'opt_orden': opt_orden,
        'opt_dist': round(opt_dist, 2),
        'opt_evals': opt_evals,
        'factorial_8': factorial_8,
    }

estado_inicial = ejecutar_todo()

# =====================================================================
# 6. PLANTILLA HTML — Tema: Día de Muertos Diabólico
# =====================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 Ruta Verde Logística — Campus de los Muertos</title>
    <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --marigold: #ff7518;
            --magenta: #ff2d95;
            --purple: #a855f7;
            --bone: #f5f0e6;
            --blood: #d90429;
            --green: #39ff88;
            --bg: #0a0512;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Rajdhani', sans-serif;
            background:
                radial-gradient(ellipse at 50% -10%, #2a1140 0%, #0a0512 60%),
                #0a0512;
            color: var(--bone);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ===== EL "67" MALIGNO DE FONDO ===== */
        .evil-67 {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Creepster', cursive;
            font-size: 46vw;
            color: rgba(217, 4, 41, 0.10);
            text-shadow:
                0 0 60px rgba(217, 4, 41, 0.55),
                0 0 160px rgba(217, 4, 41, 0.4),
                0 0 300px rgba(217, 4, 41, 0.3);
            z-index: 0;
            pointer-events: none;
            user-select: none;
            animation: flicker67 3.7s infinite;
        }

        @keyframes flicker67 {
            0%, 100% { opacity: 1; }
            41% { opacity: 1; }
            42% { opacity: 0.55; }
            43% { opacity: 1; }
            77% { opacity: 1; }
            78% { opacity: 0.4; }
            79% { opacity: 1; }
            80% { opacity: 0.85; }
        }

        /* ===== CALAVERAS CON AURA BLANCA ===== */
        .skull {
            position: fixed;
            z-index: 1;
            font-size: 1.6rem;
            pointer-events: none;
            user-select: none;
            text-shadow:
                0 0 12px #fff,
                0 0 28px rgba(255, 255, 255, 0.9),
                0 0 55px rgba(255, 255, 255, 0.6);
            animation: skullFloat var(--dur, 7s) ease-in-out infinite;
            opacity: 0.9;
        }

        @keyframes skullFloat {
            0%, 100% { transform: translateY(0) rotate(-6deg); }
            50% { transform: translateY(-16px) rotate(7deg); }
        }

        /* ===== MINI "67" MALIGNOS FLOTANDO ===== */
        .mini-67 {
            position: fixed;
            z-index: 1;
            font-family: 'Creepster', cursive;
            color: rgba(217, 4, 41, 0.7);
            text-shadow:
                0 0 14px rgba(217, 4, 41, 0.95),
                0 0 40px rgba(217, 4, 41, 0.65),
                0 0 80px rgba(217, 4, 41, 0.4);
            pointer-events: none;
            user-select: none;
            animation:
                mini67Float var(--dur, 9s) ease-in-out infinite,
                flickerMini67 4.5s infinite;
        }

        @keyframes mini67Float {
            0%, 100% { transform: translateY(0) rotate(-9deg) scale(1); }
            50% { transform: translateY(-26px) rotate(10deg) scale(1.08); }
        }

        @keyframes flickerMini67 {
            0%, 100% { opacity: 0.85; }
            31% { opacity: 0.85; }
            32% { opacity: 0.35; }
            33% { opacity: 0.85; }
            68% { opacity: 0.85; }
            69% { opacity: 0.45; }
            70% { opacity: 0.85; }
        }

        /* ===== CATRÍN Y CATRINA ===== */
        .figura {
            position: fixed;
            bottom: 40px;
            z-index: 1;
            width: 210px;
            pointer-events: none;
            filter:
                drop-shadow(0 0 18px rgba(255, 255, 255, 0.35))
                drop-shadow(0 0 40px rgba(168, 85, 247, 0.35));
            animation: floatFigura 7s ease-in-out infinite;
            opacity: 0.92;
        }
        .catrin { left: 1.5%; }
        .catrina { right: 1.5%; animation-delay: -3.5s; }

        @keyframes floatFigura {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-14px); }
        }

        @media (max-width: 900px) {
            .figura { width: 120px; opacity: 0.5; }
        }

        /* ===== TUMBAS Y BRUMA ===== */
        .cementerio {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 90px;
            z-index: 1;
            pointer-events: none;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
        }

        .tumba {
            width: 52px;
            height: 62px;
            background: linear-gradient(180deg, #4a4a5a, #2c2c3a);
            border-radius: 26px 26px 4px 4px;
            border: 2px solid #5b5b70;
            position: relative;
            box-shadow: 0 6px 18px rgba(0,0,0,0.8);
        }
        .tumba::before {
            content: '✝';
            position: absolute;
            top: 8px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 1.3rem;
            color: #8b8ba0;
        }
        .tumba::after {
            content: '';
            position: absolute;
            bottom: -4px;
            left: -10px;
            right: -10px;
            height: 10px;
            background: #14101f;
            border-radius: 50%;
        }

        .bruma {
            position: fixed;
            bottom: 0;
            left: -50%;
            width: 200%;
            height: 120px;
            z-index: 2;
            pointer-events: none;
            background: linear-gradient(90deg,
                transparent, rgba(200, 180, 255, 0.07) 25%,
                rgba(200, 180, 255, 0.12) 50%,
                rgba(200, 180, 255, 0.07) 75%, transparent);
            animation: brumaMover 18s linear infinite;
        }
        @keyframes brumaMover {
            from { transform: translateX(-25%); }
            to { transform: translateX(25%); }
        }

        /* ===== CONTENIDO ===== */
        .container {
            position: relative;
            z-index: 5;
            max-width: 1340px;
            margin: 0 auto;
            padding: 30px 24px 160px;
        }

        .hero { text-align: center; margin-bottom: 28px; }

        .badge {
            display: inline-block;
            padding: 6px 20px;
            border-radius: 999px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.72rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(255, 117, 24, 0.12);
            border: 1px solid var(--marigold);
            color: var(--marigold);
            box-shadow: 0 0 22px rgba(255, 117, 24, 0.45);
            margin-bottom: 12px;
        }

        h1 {
            font-family: 'Creepster', cursive;
            font-size: clamp(2.6rem, 5.5vw, 4.6rem);
            letter-spacing: 5px;
            color: var(--bone);
            text-shadow:
                0 0 14px rgba(255, 255, 255, 0.55),
                0 0 40px rgba(255, 117, 24, 0.7),
                0 0 80px rgba(217, 4, 41, 0.6);
        }

        .subtitle { color: #c9b8e8; font-size: 1.15rem; margin-top: 8px; }

        /* ===== TARJETAS ALTAR ===== */
        .card {
            position: relative;
            background: linear-gradient(145deg, rgba(30, 18, 48, 0.92), rgba(14, 8, 26, 0.95));
            border: 1px solid rgba(255, 117, 24, 0.4);
            border-radius: 20px;
            padding: 24px;
            backdrop-filter: blur(14px);
            box-shadow:
                0 24px 50px rgba(0, 0, 0, 0.8),
                0 0 25px rgba(255, 117, 24, 0.1),
                inset 0 1px 2px rgba(255, 255, 255, 0.15);
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: -60px; left: -60px;
            width: 160px; height: 160px;
            background: radial-gradient(circle, rgba(255, 117, 24, 0.16), transparent 70%);
            pointer-events: none;
        }

        .command-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 26px;
            border-color: rgba(255, 45, 149, 0.5);
        }

        .btn {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            padding: 11px 18px;
            border-radius: 12px;
            cursor: pointer;
            border: 1px solid;
            transition: all 0.2s;
        }

        .btn-run {
            background: rgba(57, 255, 136, 0.14);
            border-color: var(--green);
            color: var(--green);
            box-shadow: 0 0 18px rgba(57, 255, 136, 0.3);
        }
        .btn-run:hover { background: var(--green); color: #0a0512; }

        .btn-seed {
            background: rgba(168, 85, 247, 0.15);
            border-color: var(--purple);
            color: #d6b8ff;
            box-shadow: 0 0 18px rgba(168, 85, 247, 0.3);
        }
        .btn-seed:hover { background: var(--purple); color: #fff; }

        .select-destino {
            padding: 10px 14px;
            border-radius: 10px;
            background: rgba(10, 5, 18, 0.95);
            border: 1px solid var(--marigold);
            color: var(--bone);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 26px;
        }

        .kpi-label {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.78rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #b8a8d8;
        }

        .kpi-val {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.1rem;
            font-weight: 900;
            margin: 8px 0 4px;
        }

        .c-magenta { color: var(--magenta); text-shadow: 0 0 20px rgba(255,45,149,0.7); }
        .c-marigold { color: var(--marigold); text-shadow: 0 0 20px rgba(255,117,24,0.7); }
        .c-purple { color: var(--purple); text-shadow: 0 0 20px rgba(168,85,247,0.7); }
        .c-green { color: var(--green); text-shadow: 0 0 20px rgba(57,255,136,0.7); }

        .main-grid {
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            gap: 24px;
            margin-bottom: 26px;
        }
        @media (max-width: 1000px) { .main-grid { grid-template-columns: 1fr; } }

        .section-title {
            font-family: 'Creepster', cursive;
            font-size: 1.5rem;
            letter-spacing: 2.5px;
            color: var(--bone);
            margin-bottom: 14px;
            text-shadow: 0 0 16px rgba(255, 117, 24, 0.6);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        #mapa-viewer {
            width: 100%;
            height: 470px;
            border-radius: 16px;
            background: radial-gradient(circle at center, rgba(30, 18, 55, 0.9), rgba(8, 4, 16, 0.97));
            border: 1px solid rgba(255, 117, 24, 0.4);
            box-shadow: inset 0 0 45px rgba(168, 85, 247, 0.15);
            position: relative;
            overflow: hidden;
        }

        #mapa-canvas { width: 100%; height: 100%; display: block; }

        .viewer-overlay {
            position: absolute;
            bottom: 10px; left: 14px; right: 14px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            pointer-events: none;
            font-size: 0.8rem;
        }

        .legend-pill {
            background: rgba(10, 5, 18, 0.88);
            border: 1px solid rgba(255, 117, 24, 0.4);
            padding: 5px 12px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 9px;
            color: #d8ccff;
        }

        .modo-btns { display: flex; gap: 8px; flex-wrap: wrap; }

        .btn-modo {
            background: rgba(255, 117, 24, 0.12);
            border: 1px solid var(--marigold);
            color: var(--marigold);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.7rem;
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .btn-modo:hover, .btn-modo.activo { background: var(--marigold); color: #0a0512; }

        /* ===== TABLAS ===== */
        .table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px;
        }

        .table thead th {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--marigold);
            padding: 8px 12px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 117, 24, 0.35);
        }

        .table tbody tr {
            background: linear-gradient(90deg, rgba(40, 24, 66, 0.9), rgba(20, 12, 36, 0.95));
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 8px 20px rgba(0,0,0,0.45);
        }
        .table tbody tr:hover { transform: scale(1.012); box-shadow: 0 12px 28px rgba(255,117,24,0.2); }

        .table td {
            padding: 12px 12px;
            text-align: center;
            font-size: 0.98rem;
            font-weight: 600;
            border-top: 1px solid rgba(255, 117, 24, 0.25);
            border-bottom: 1px solid rgba(255, 117, 24, 0.25);
        }
        .table td:first-child { border-left: 3px solid var(--marigold); border-radius: 10px 0 0 10px; }
        .table td:last-child { border-right: 1px solid rgba(255, 117, 24, 0.25); border-radius: 0 10px 10px 0; }

        .node-chip {
            display: inline-block;
            margin: 2px;
            padding: 3px 9px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            background: rgba(255, 117, 24, 0.14);
            border: 1px solid rgba(255, 117, 24, 0.45);
            color: var(--bone);
        }
        .node-chip.base { border-color: var(--marigold); color: var(--marigold); }

        .veredicto {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 16px;
            border-radius: 14px;
            margin-bottom: 14px;
            background: rgba(20, 12, 36, 0.9);
            border: 1px solid rgba(168, 85, 247, 0.35);
        }
        .veredicto .icono { font-size: 1.8rem; }
        .veredicto h4 {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.95rem;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .veredicto p { font-size: 0.95rem; color: #d8ccff; line-height: 1.45; }
        .v-si { border-left: 4px solid var(--green); }
        .v-no { border-left: 4px solid var(--blood); }

        .convergencia-canvas {
            width: 100%;
            height: 90px;
            border-radius: 12px;
            background: rgba(8, 4, 16, 0.85);
            border: 1px solid rgba(168, 85, 247, 0.35);
        }

        .tag-algo {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 8px;
            display: inline-block;
        }
        .tag-bfs { background: rgba(255,45,149,0.2); color: var(--magenta); border: 1px solid var(--magenta); }
        .tag-ucs { background: rgba(255,117,24,0.2); color: var(--marigold); border: 1px solid var(--marigold); }
        .tag-hc { background: rgba(168,85,247,0.2); color: #d6b8ff; border: 1px solid var(--purple); }
        .tag-ga { background: rgba(57,255,136,0.15); color: var(--green); border: 1px solid var(--green); }
        .tag-opt { background: rgba(255,255,255,0.12); color: #fff; border: 1px solid #fff; }
    </style>
</head>
<body>
    <!-- EL 67 MALIGNO -->
    <div class="evil-67">67</div>

    <!-- CALAVERAS CON AURA BLANCA (generadas por JS) -->
    <div id="skulls"></div>

    <!-- CATRÍN Y CATRINA -->
    <svg class="figura catrin" viewBox="0 0 200 320">
        <!-- Sombrero de copa -->
        <rect x="62" y="8" width="76" height="60" rx="6" fill="#1a1a26" stroke="#5b5b70" stroke-width="3"/>
        <rect x="48" y="62" width="104" height="14" rx="7" fill="#1a1a26" stroke="#5b5b70" stroke-width="3"/>
        <rect x="62" y="50" width="76" height="14" fill="#d90429"/>
        <!-- Cráneo -->
        <circle cx="100" cy="105" r="32" fill="#f5f0e6"/>
        <circle cx="88" cy="98" r="7" fill="#1a1a26"/>
        <circle cx="112" cy="98" r="7" fill="#1a1a26"/>
        <polygon points="100,108 94,120 106,120" fill="#1a1a26"/>
        <rect x="86" y="126" width="28" height="7" rx="3" fill="#1a1a26"/>
        <line x1="94" y1="126" x2="94" y2="133" stroke="#f5f0e6" stroke-width="2"/>
        <line x1="100" y1="126" x2="100" y2="133" stroke="#f5f0e6" stroke-width="2"/>
        <line x1="106" y1="126" x2="106" y2="133" stroke="#f5f0e6" stroke-width="2"/>
        <!-- Traje -->
        <rect x="72" y="140" width="56" height="100" rx="14" fill="#1a1a26" stroke="#5b5b70" stroke-width="3"/>
        <polygon points="100,150 90,142 110,142" fill="#f5f0e6"/>
        <rect x="96" y="142" width="8" height="34" fill="#d90429"/>
        <line x1="80" y1="240" x2="80" y2="300" stroke="#1a1a26" stroke-width="12" stroke-linecap="round"/>
        <line x1="120" y1="240" x2="120" y2="300" stroke="#1a1a26" stroke-width="12" stroke-linecap="round"/>
        <line x1="72" y1="160" x2="46" y2="210" stroke="#1a1a26" stroke-width="10" stroke-linecap="round"/>
        <line x1="128" y1="160" x2="154" y2="210" stroke="#1a1a26" stroke-width="10" stroke-linecap="round"/>
        <circle cx="46" cy="214" r="7" fill="#f5f0e6"/>
        <circle cx="154" cy="214" r="7" fill="#f5f0e6"/>
    </svg>

    <svg class="figura catrina" viewBox="0 0 200 320">
        <!-- Sombrero ancho con flores -->
        <ellipse cx="100" cy="70" rx="86" ry="16" fill="#2a1140" stroke="#a855f7" stroke-width="3"/>
        <path d="M 62 70 Q 62 18 100 18 Q 138 18 138 70 Z" fill="#2a1140" stroke="#a855f7" stroke-width="3"/>
        <circle cx="70" cy="52" r="10" fill="#ff7518"/>
        <circle cx="100" cy="42" r="11" fill="#ff2d95"/>
        <circle cx="130" cy="52" r="10" fill="#ffbe0b"/>
        <!-- Cráneo -->
        <circle cx="100" cy="105" r="32" fill="#f5f0e6"/>
        <circle cx="88" cy="98" r="7" fill="#1a1a26"/>
        <circle cx="112" cy="98" r="7" fill="#1a1a26"/>
        <circle cx="88" cy="98" r="10" fill="none" stroke="#ff2d95" stroke-width="2"/>
        <circle cx="112" cy="98" r="10" fill="none" stroke="#ff2d95" stroke-width="2"/>
        <polygon points="100,108 94,120 106,120" fill="#1a1a26"/>
        <rect x="86" y="126" width="28" height="7" rx="3" fill="#1a1a26"/>
        <!-- Vestido -->
        <path d="M 72 140 L 128 140 L 160 300 L 40 300 Z" fill="#3d1a5e" stroke="#a855f7" stroke-width="3"/>
        <line x1="72" y1="150" x2="40" y2="200" stroke="#3d1a5e" stroke-width="10" stroke-linecap="round"/>
        <line x1="128" y1="150" x2="160" y2="200" stroke="#3d1a5e" stroke-width="10" stroke-linecap="round"/>
        <circle cx="40" cy="204" r="7" fill="#f5f0e6"/>
        <circle cx="160" cy="204" r="7" fill="#f5f0e6"/>
        <!-- Flores en el vestido -->
        <circle cx="100" cy="190" r="8" fill="#ff7518"/>
        <circle cx="80" cy="230" r="7" fill="#ff2d95"/>
        <circle cx="120" cy="230" r="7" fill="#ffbe0b"/>
        <circle cx="100" cy="270" r="8" fill="#ff7518"/>
    </svg>

    <!-- TUMBAS + BRUMA -->
    <div class="cementerio" id="cementerio"></div>
    <div class="bruma"></div>

    <!-- ================= CONTENIDO ================= -->
    <div class="container">
        <header class="hero">
            <div class="badge">💀 Informe Técnico • Sistemas Inteligentes • BFS • UCS • HC • GA</div>
            <h1>🕯️ Ruta Verde Logística 🕯️</h1>
            <p class="subtitle">Campus Universitario como grafo (9 nodos) — comparación de algoritmos de búsqueda y optimización</p>
        </header>

        <!-- Panel de control -->
        <div class="card command-bar">
            <div>
                <div style="font-family:'Orbitron',sans-serif; font-size:0.95rem; color:var(--marigold);">
                    ⚙️ Panel del Cementerio Logístico
                </div>
                <div style="font-size:0.9rem; color:#b8a8d8;">
                    Destino BFS/UCS:
                    <select class="select-destino" id="destino-select" onchange="cambiarDestino(this.value)">
                        {% for n in edificios %}
                        <option value="{{ n }}" {{ 'selected' if n == 'Laboratorio' }}>{{ n }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn btn-run" onclick="reEjecutar()">🚀 Ejecutar Todo</button>
                <button class="btn btn-seed" onclick="nuevaSemilla()">🧬 GA Nueva Semilla</button>
            </div>
        </div>

        <!-- KPIs -->
        <section class="kpi-grid">
            <div class="card">
                <div class="kpi-label">Nodos del Campus (Grafo)</div>
                <div class="kpi-val c-marigold">9 <span style="font-size:1rem; color:#b8a8d8;">base + 8 edificios</span></div>
                <div style="font-size:0.9rem; color:#b8a8d8;">{{ aristas | length }} caminos con costo euclidiano</div>
            </div>
            <div class="card">
                <div class="kpi-label">Factorial del Problema</div>
                <div class="kpi-val c-purple">8! = 40,320</div>
                <div style="font-size:0.9rem; color:#b8a8d8;">órdenes de entrega posibles (permutaciones)</div>
            </div>
            <div class="card">
                <div class="kpi-label">Mejor Ruta de Entrega (Óptimo)</div>
                <div class="kpi-val c-green" id="kpi-opt">{{ estado_inicial.opt_dist }} u</div>
                <div style="font-size:0.85rem; color:#b8a8d8;" id="kpi-opt-ruta">8! = 40,320 rutas evaluadas</div>
            </div>
            <div class="card">
                <div class="kpi-label">¿BFS y UCS llegan igual?</div>
                <div class="kpi-val {{ 'c-green' if estado_inicial.mismo_bfs_ucs else 'c-magenta' }}" id="kpi-bufs">
                    {{ 'SÍ ✔' if estado_inicial.mismo_bfs_ucs else 'NO ✗' }}
                </div>
                <div style="font-size:0.85rem; color:#b8a8d8;" id="kpi-bufs-det"></div>
            </div>
            <div class="card">
                <div class="kpi-label">¿HC y GA llegan igual?</div>
                <div class="kpi-val {{ 'c-green' if estado_inicial.mismo_hc_ga else 'c-magenta' }}" id="kpi-hcga">
                    {{ 'SÍ ✔' if estado_inicial.mismo_hc_ga else 'NO ✗' }}
                </div>
                <div style="font-size:0.85rem; color:#b8a8d8;" id="kpi-hcga-det"></div>
            </div>
        </section>

        <!-- Mapa + Resultados de algoritmos -->
        <div class="main-grid">
            <div class="card">
                <div class="section-title">
                    🪦 Mapa del Campus Maldito
                    <span style="margin-left:auto; font-family:'Orbitron',sans-serif;" class="modo-btns">
                        <button class="btn-modo activo" id="modo-orden" onclick="setModo('orden')">Ruta de Entregas (HC vs GA)</button>
                        <button class="btn-modo" id="modo-path" onclick="setModo('path')">Camino BASE→Destino (BFS vs UCS)</button>
                    </span>
                </div>
                <div id="mapa-viewer">
                    <canvas id="mapa-canvas"></canvas>
                    <div class="viewer-overlay">
                        <div class="legend-pill" id="legend-modo">
                            <span style="color:var(--purple);">━ HC</span>
                            <span style="color:var(--green);">━ GA</span>
                        </div>
                        <div class="legend-pill">◆ Caminos del campus • ● Edificios</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="section-title">⚰️ Resultados por Algoritmo</div>
                <table class="table">
                    <thead>
                        <tr><th>Algoritmo</th><th>Resultado</th><th>Costo</th><th>Evaluaciones</th></tr>
                    </thead>
                    <tbody id="tabla-algos"></tbody>
                </table>
                <div class="section-title" style="margin-top:22px;">🧬 Convergencia del Genético</div>
                <canvas class="convergencia-canvas" id="conv-canvas"></canvas>
                <div id="ga-info" style="font-size:0.85rem; color:#b8a8d8; margin-top:8px;"></div>
            </div>
        </div>

        <!-- Espacio de búsqueda: factorial y combinaciones evaluadas -->
        <div class="card" style="margin-bottom:26px;">
            <div class="section-title">🔢 Espacio de Búsqueda: 8! = 40,320 combinaciones</div>
            <p style="color:#b8a8d8; font-size:0.95rem; margin-bottom:14px;">
                Con 8 edificios hay <strong>8! = 8 × 7 × 6 × 5 × 4 × 3 × 2 × 1 = 40,320</strong> órdenes de entrega posibles.
                Cada algoritmo explora una porción distinta del espacio:
            </p>
            <div id="espacio-barras"></div>
        </div>

        <!-- Comparación: ¿llegan a la misma ruta? -->
        <div class="card" style="margin-bottom:26px;">
            <div class="section-title">💀 ¿Por qué llegan o NO llegan a la misma ruta?</div>

            <div class="veredicto" id="veredicto-bfsucs"></div>
            <div class="veredicto" id="veredicto-hcga"></div>
            <div class="veredicto" id="veredicto-optimo"></div>
            <div class="veredicto" id="veredicto-natural"></div>
        </div>

        <!-- Historial Hill Climbing -->
        <div class="card">
            <div class="section-title">🕯️ Pasos del Hill Climbing (desde orden aleatorio)</div>
            <table class="table">
                <thead>
                    <tr><th>Paso</th><th>Movimiento</th><th>Orden de Entregas</th><th>Distancia</th></tr>
                </thead>
                <tbody id="tabla-historial"></tbody>
            </table>
        </div>
    </div>

    <script>
        const NODOS = {{ nodos | tojson }};
        const ARISTAS = {{ aristas | tojson }};
        let estado = {{ estado_inicial | tojson }};
        let modo = 'orden';

        // ===== Calaveras con aura blanca flotando por toda la pantalla =====
        const skullsDiv = document.getElementById('skulls');
        for (let i = 0; i < 26; i++) {
            const s = document.createElement('span');
            s.className = 'skull';
            s.textContent = '💀';
            s.style.left = Math.random() * 97 + 'vw';
            s.style.top = Math.random() * 92 + 'vh';
            s.style.fontSize = (1 + Math.random() * 1.6) + 'rem';
            s.style.setProperty('--dur', (5 + Math.random() * 7) + 's');
            s.style.animationDelay = (-Math.random() * 8) + 's';
            s.style.opacity = 0.5 + Math.random() * 0.5;
            skullsDiv.appendChild(s);
        }

        // ===== Mini "67" malignos flotando por toda la pantalla =====
        for (let i = 0; i < 14; i++) {
            const e67 = document.createElement('span');
            e67.className = 'mini-67';
            e67.textContent = '67';
            e67.style.left = Math.random() * 93 + 'vw';
            e67.style.top = Math.random() * 88 + 'vh';
            e67.style.fontSize = (1.6 + Math.random() * 3.4) + 'rem';
            e67.style.setProperty('--dur', (6 + Math.random() * 8) + 's');
            e67.style.animationDelay = (-Math.random() * 9) + 's, ' + (-Math.random() * 4.5) + 's';
            skullsDiv.appendChild(e67);
        }

        // ===== Tumbas en la parte inferior =====
        const cem = document.getElementById('cementerio');
        for (let i = 0; i < 16; i++) {
            const t = document.createElement('div');
            t.className = 'tumba';
            const escala = 0.7 + Math.random() * 0.7;
            t.style.transform = `scale(${escala})`;
            t.style.opacity = 0.55 + Math.random() * 0.45;
            cem.appendChild(t);
        }

        // ===== MAPA 2D =====
        const canvas = document.getElementById('mapa-canvas');
        const ctx = canvas.getContext('2d');
        const viewerEl = document.getElementById('mapa-viewer');
        const M = { izq: 46, der: 26, sup: 26, inf: 40 };

        function aPixel(x, y) {
            const w = viewerEl.clientWidth - M.izq - M.der;
            const h = viewerEl.clientHeight - M.sup - M.inf;
            const lado = Math.min(w, h);
            const ox = M.izq + (w - lado) / 2, oy = M.sup + (h - lado) / 2;
            return { x: ox + (x / 9) * lado, y: oy + (1 - y / 9) * lado };
        }

        function ajustar() {
            const dpr = window.devicePixelRatio || 1;
            canvas.width = viewerEl.clientWidth * dpr;
            canvas.height = viewerEl.clientHeight * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }
        ajustar();

        function dibujarCamino(secuencia, color, desplazar = 0, punteado = false) {
            const pts = secuencia.map(n => aPixel(...NODOS[n]));
            ctx.save();
            if (punteado) ctx.setLineDash([10, 7]);
            ctx.strokeStyle = color;
            ctx.lineWidth = 3.5;
            ctx.shadowColor = color;
            ctx.shadowBlur = 12;
            ctx.beginPath();
            pts.forEach((p, i) => {
                const dx = desplazar * Math.sin(i * 2.4), dy = desplazar * Math.cos(i * 2.4);
                i === 0 ? ctx.moveTo(p.x + dx, p.y + dy) : ctx.lineTo(p.x + dx, p.y + dy);
            });
            ctx.stroke();
            ctx.restore();

            // flechas
            ctx.fillStyle = color;
            for (let i = 0; i < pts.length - 1; i++) {
                const a = pts[i], b = pts[i + 1];
                const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
                const ang = Math.atan2(b.y - a.y, b.x - a.x);
                ctx.save();
                ctx.translate(mx, my); ctx.rotate(ang);
                ctx.beginPath();
                ctx.moveTo(8, 0); ctx.lineTo(-4, -5); ctx.lineTo(-4, 5);
                ctx.closePath(); ctx.fill();
                ctx.restore();
            }
        }

        function dibujar() {
            const W = viewerEl.clientWidth, H = viewerEl.clientHeight;
            ctx.clearRect(0, 0, W, H);

            // rejilla tenue
            for (let c = 0; c <= 9; c++) {
                const a = aPixel(c, 0), b = aPixel(c, 9);
                const d = aPixel(0, c), e = aPixel(9, c);
                ctx.strokeStyle = 'rgba(168,85,247,0.10)';
                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.moveTo(a.x, b.y); ctx.lineTo(a.x, a.y); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(e.x, e.y); ctx.stroke();
            }

            // aristas del campus (caminos)
            ARISTAS.forEach(([a, b]) => {
                const p1 = aPixel(...NODOS[a]), p2 = aPixel(...NODOS[b]);
                ctx.strokeStyle = 'rgba(255,117,24,0.28)';
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
            });

            // rutas según modo
            if (modo === 'path') {
                dibujarCamino(estado.bfs_camino, '#ff2d95', 3, true);
                dibujarCamino(estado.ucs_camino, '#ff7518', -3, false);
            } else {
                dibujarCamino(['BASE', ...estado.hc_orden, 'BASE'], '#a855f7', 3, true);
                dibujarCamino(['BASE', ...estado.ga_orden, 'BASE'], '#39ff88', -3, false);
            }

            // nodos
            Object.entries(NODOS).forEach(([n, c]) => {
                const p = aPixel(c[0], c[1]);
                const esBase = n === 'BASE';
                ctx.fillStyle = esBase ? '#ff7518' : '#f5f0e6';
                ctx.shadowColor = esBase ? '#ff7518' : '#ffffff';
                ctx.shadowBlur = 14;
                ctx.beginPath();
                ctx.arc(p.x, p.y, esBase ? 12 : 9, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.strokeStyle = esBase ? '#ffd8a8' : '#a855f7';
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.fillStyle = esBase ? '#ffbe0b' : '#d8ccff';
                ctx.font = 'bold 11.5px Orbitron, sans-serif';
                ctx.textAlign = 'center';
                const etiqueta = esBase ? `🏭 BASE (${c[0]},${c[1]})` : `${n} (${c[0]},${c[1]})`;
                ctx.fillText(etiqueta, p.x, p.y - 15);
            });
        }

        window.setModo = function(m) {
            modo = m;
            document.getElementById('modo-orden').classList.toggle('activo', m === 'orden');
            document.getElementById('modo-path').classList.toggle('activo', m === 'path');
            document.getElementById('legend-modo').innerHTML = m === 'path'
                ? '<span style="color:var(--magenta);">┄ BFS</span><span style="color:var(--marigold);">━ UCS</span>'
                : '<span style="color:var(--purple);">┄ Hill Climbing</span><span style="color:var(--green);">━ Genético</span>';
            dibujar();
        };

        function animar() { requestAnimationFrame(animar); dibujar(); }
        animar();

        // ===== Convergencia GA (mini gráfica) =====
        function dibujarConvergencia(conv) {
            const cv = document.getElementById('conv-canvas');
            const dpr = window.devicePixelRatio || 1;
            cv.width = cv.clientWidth * dpr; cv.height = cv.clientHeight * dpr;
            const c2 = cv.getContext('2d');
            c2.setTransform(dpr, 0, 0, dpr, 0, 0);
            const w = cv.clientWidth, h = cv.clientHeight;
            const min = Math.min(...conv), max = Math.max(...conv);
            const rango = max - min || 1;
            c2.strokeStyle = '#39ff88';
            c2.lineWidth = 2.5;
            c2.shadowColor = '#39ff88'; c2.shadowBlur = 8;
            c2.beginPath();
            conv.forEach((v, i) => {
                const x = 8 + (i / (conv.length - 1)) * (w - 16);
                const y = h - 10 - ((v - min) / rango) * (h - 24);
                i === 0 ? c2.moveTo(x, y) : c2.lineTo(x, y);
            });
            c2.stroke();
            c2.shadowBlur = 0;
            c2.fillStyle = '#b8a8d8';
            c2.font = '11px Orbitron, sans-serif';
            c2.textAlign = 'left';
            c2.fillText(`${conv[0]}u`, 10, 14);
            c2.textAlign = 'right';
            c2.fillText(`${conv[conv.length - 1]}u`, w - 10, 14);
        }

        // ===== Render =====
        function chips(sec) {
            return sec.map(n => `<span class="node-chip ${n === 'BASE' ? 'base' : ''}">${n}</span>`).join(' → ');
        }

        function renderizar(d) {
            estado = d;
            document.getElementById('kpi-opt').textContent = d.opt_dist + ' u';
            document.getElementById('kpi-bufs').textContent = d.mismo_bfs_ucs ? 'SÍ ✔' : 'NO ✗';
            document.getElementById('kpi-bufs').className = 'kpi-val ' + (d.mismo_bfs_ucs ? 'c-green' : 'c-magenta');
            document.getElementById('kpi-bufs-det').textContent =
                `BFS: ${d.bfs_saltos} saltos / ${d.bfs_costo}u • UCS: ${d.ucs_costo}u`;
            document.getElementById('kpi-hcga').textContent = d.mismo_hc_ga ? 'SÍ ✔' : 'NO ✗';
            document.getElementById('kpi-hcga').className = 'kpi-val ' + (d.mismo_hc_ga ? 'c-green' : 'c-magenta');
            document.getElementById('kpi-hcga-det').textContent =
                `HC: ${d.hc_dist}u • GA: ${d.ga_dist}u • Óptimo: ${d.opt_dist}u`;

            // Tabla de algoritmos (con evaluaciones de cada uno)
            const filas = [
                { tag: 'tag-bfs', nombre: 'BFS', res: chips(d.bfs_camino), costo: `${d.bfs_saltos} saltos / ${d.bfs_costo} u`, evals: `${d.bfs_exp} nodos` },
                { tag: 'tag-ucs', nombre: 'UCS', res: chips(d.ucs_camino), costo: `${d.ucs_costo} u`, evals: `${d.ucs_exp} nodos` },
                { tag: 'tag-hc', nombre: 'Hill Climbing', res: chips(['BASE', ...d.hc_orden, 'BASE']), costo: `${d.hc_dist} u ${d.hc_es_optimo ? '⭐ óptimo' : ''}`, evals: `${d.hc_evals} órdenes` },
                { tag: 'tag-ga', nombre: 'Genético', res: chips(['BASE', ...d.ga_orden, 'BASE']), costo: `${d.ga_dist} u ${d.ga_es_optimo ? '⭐ óptimo' : ''}`, evals: `${d.ga_evals.toLocaleString()} órdenes` },
                { tag: 'tag-opt', nombre: 'Óptimo (bruta)', res: chips(['BASE', ...d.opt_orden, 'BASE']), costo: `${d.opt_dist} u`, evals: `${d.opt_evals.toLocaleString()} órdenes` },
            ];
            document.getElementById('tabla-algos').innerHTML = filas.map(f =>
                `<tr><td><span class="tag-algo ${f.tag}">${f.nombre}</span></td><td>${f.res}</td>
                 <td style="font-family:'Orbitron',sans-serif; color:var(--green);">${f.costo}</td>
                 <td style="font-family:'Orbitron',sans-serif; color:var(--purple); font-size:0.85rem;">${f.evals}</td></tr>`
            ).join('');

            // Barras del espacio de búsqueda (cuántas combinaciones evalúa cada algoritmo)
            const espacio = [
                { nombre: 'BFS', evals: d.bfs_exp, tipo: 'nodos expandidos en el grafo', color: '#ff2d95' },
                { nombre: 'UCS', evals: d.ucs_exp, tipo: 'nodos expandidos en el grafo', color: '#ff7518' },
                { nombre: 'Hill Climbing', evals: d.hc_evals, tipo: 'órdenes evaluadas', color: '#a855f7' },
                { nombre: 'Genético', evals: d.ga_evals, tipo: 'órdenes evaluadas', color: '#39ff88' },
                { nombre: 'Fuerza Bruta', evals: d.opt_evals, tipo: 'órdenes evaluadas (100% del espacio)', color: '#f5f0e6' },
            ];
            document.getElementById('espacio-barras').innerHTML = espacio.map(a => {
                const pct = Math.min(100, (a.evals / d.factorial_8) * 100);
                return `
                <div style="margin-bottom:13px;">
                    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px;">
                        <span style="font-family:'Orbitron',sans-serif; font-size:0.85rem; color:${a.color};">${a.nombre}</span>
                        <span style="font-size:0.85rem; color:#b8a8d8;">
                            <strong style="color:${a.color};">${a.evals.toLocaleString()}</strong> ${a.tipo}
                            — ${a.nombre === 'BFS' || a.nombre === 'UCS' ? 'espacio distinto' : pct.toFixed(1) + '% del espacio'}
                        </span>
                    </div>
                    <div style="height:10px; background:rgba(255,255,255,0.07); border-radius:8px; border:1px solid rgba(255,255,255,0.12); overflow:hidden;">
                        <div style="height:100%; width:${Math.max(pct, 1.5)}%; background:${a.color}; border-radius:8px; box-shadow:0 0 14px ${a.color};"></div>
                    </div>
                </div>`;
            }).join('');

            // Veredictos
            const v = document.getElementById('veredicto-bfsucs');
            v.className = 'veredicto ' + (d.mismo_bfs_ucs ? 'v-si' : 'v-no');
            v.innerHTML = `<div class="icono">${d.mismo_bfs_ucs ? '😇' : '😈'}</div><div>
                <h4>1. ¿BFS y UCS llegan a la misma ruta? ${d.mismo_bfs_ucs ? 'SÍ' : 'NO'}</h4>
                <p>BFS minimiza <strong>número de saltos</strong> y <strong>ignora los costos</strong> de las aristas;
                UCS minimiza el <strong>costo acumulado real</strong>. Aquí BFS dio <strong>${d.bfs_saltos} saltos con ${d.bfs_costo}u</strong>
                y UCS encontró <strong>${d.ucs_costo}u</strong>.
                ${d.mismo_bfs_ucs
                    ? 'Coincidieron porque el camino con menos aristas TAMBIÉN era el de menor costo en este grafo.'
                    : 'Difieren porque el camino con menos aristas NO es el más barato: BFS no "ve" las distancias.'}
                Solo coinciden cuando el grafo tiene pesos uniformes o por casualidad.</p></div>`;

            const v2 = document.getElementById('veredicto-hcga');
            v2.className = 'veredicto ' + (d.mismo_hc_ga ? 'v-si' : 'v-no');
            v2.innerHTML = `<div class="icono">${d.mismo_hc_ga ? '😇' : '😈'}</div><div>
                <h4>2. ¿Hill Climbing y Genético llegan a la misma ruta? ${d.mismo_hc_ga ? 'SÍ' : 'NO'}</h4>
                <p>HC: <strong>${d.hc_dist}u</strong> ${d.hc_es_optimo ? '(óptimo ⭐)' : '(óptimo local)'} •
                GA: <strong>${d.ga_dist}u</strong> ${d.ga_es_optimo ? '(óptimo ⭐)' : ''} •
                Óptimo real: <strong>${d.opt_dist}u</strong>.
                Hill Climbing solo acepta mejoras inmediatas → puede quedarse atrapado en un óptimo local.
                El Genético mantiene una población y explora con cruza + mutación → escapa de óptimos locales y
                converge al global con alta probabilidad. ${d.mismo_hc_ga ? 'Aquí coincidieron: el paisaje fue amable con HC.' : 'Aquí difirieron: HC quedó atrapado.'}</p></div>`;

            const v3 = document.getElementById('veredicto-optimo');
            v3.className = 'veredicto v-si';
            v3.innerHTML = `<div class="icono">📜</div><div>
                <h4>3. ¿Por qué comparar es distinto a comparar rutas?</h4>
                <p>BFS/UCS resuelven <strong>¿cómo llego de A a B?</strong> (una sola entrega).
                HC/GA resuelven <strong>¿en qué orden hago todas las entregas?</strong> (TSP).
                Son problemas diferentes, por eso sus "rutas" no se comparan directamente:
                el robot usa BFS/UCS para NAVEGAR cada tramo, y HC/GA para ORDENAR las entregas.</p></div>`;

            const v4 = document.getElementById('veredicto-natural');
            v4.className = 'veredicto v-si';
            v4.innerHTML = `<div class="icono">💀</div><div>
                <h4>4. Conclusión del informe técnico</h4>
                <p>• BFS solo garantiza pocos saltos (sirve si el costo no importa o es uniforme).<br>
                • UCS garantiza el camino más barato entre dos puntos — óptimo para navegación.<br>
                • Hill Climbing es rápido pero puede no hallar el óptimo global (depende del punto de partida).<br>
                • El Genético es más costoso en cómputo pero más robusto para órdenes de entrega complejos.<br>
                • Recomendación para Ruta Verde: <strong>ordenar con GA + navegar con UCS</strong>.</p></div>`;

            // Historial HC
            document.getElementById('tabla-historial').innerHTML = d.hc_hist.map((p, i) => `
                <tr class="${i === d.hc_hist.length - 1 ? 'row-win' : ''}">
                    <td>${i + 1}</td>
                    <td style="color:var(--marigold); font-family:'Orbitron',sans-serif; font-size:0.82rem;">${p.mov}</td>
                    <td>${chips(p.orden)}</td>
                    <td style="font-family:'Orbitron',sans-serif; color:var(--green);">${p.dist} u</td>
                </tr>`).join('');

            document.getElementById('ga-info').textContent =
                `GA: población 80, ${d.ga_gens} generaciones, elitismo 2, mutación 15%, semilla ${d.ga_semilla} → mejor ${d.ga_dist}u`;
            dibujarConvergencia(d.ga_conv);
            dibujar();
        }

        async function post(url, payload) {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            renderizar(await res.json());
        }

        window.reEjecutar = () => post('/api/ejecutar', { destino: estado.destino });
        window.nuevaSemilla = () => post('/api/nueva_semilla', { destino: estado.destino });
        window.cambiarDestino = (d) => post('/api/destino', { destino: d });

        renderizar(estado);
        window.addEventListener('resize', () => { ajustar(); dibujar(); });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        estado_inicial=estado_inicial,
        nodos=nodos,
        aristas=aristas,
        edificios=EDIFICIOS
    )

@app.route('/api/ejecutar', methods=['POST'])
def api_ejecutar():
    destino = (request.get_json() or {}).get('destino', 'Laboratorio')
    return jsonify(ejecutar_todo(destino))

@app.route('/api/destino', methods=['POST'])
def api_destino():
    destino = (request.get_json() or {}).get('destino', 'Laboratorio')
    return jsonify(ejecutar_todo(destino))

@app.route('/api/nueva_semilla', methods=['POST'])
def api_nueva_semilla():
    destino = (request.get_json() or {}).get('destino', 'Laboratorio')
    return jsonify(ejecutar_todo(destino, semilla=random.randint(1, 9999)))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
