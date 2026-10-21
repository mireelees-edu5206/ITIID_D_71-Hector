import random
import math
from itertools import permutations
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# 1. Datos del problema: Almacén + Clientes con coordenadas (x, y)
ALMACEN = (0, 0)
clientes = {
    'A': (2, 6),
    'B': (5, 3),
    'C': (6, 8),
    'D': (8, 2),
    'E': (1, 1)
}

# 2. Distancia Euclidiana entre dos puntos
def dist_euclidiana(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Matriz de distancias (Almacén + clientes) para mostrar en pantalla
def construir_matriz():
    puntos = {'W': ALMACEN}
    puntos.update(clientes)
    nombres = list(puntos.keys())
    matriz = []
    for n1 in nombres:
        fila = {'nodo': n1, 'dist': {}}
        for n2 in nombres:
            fila['dist'][n2] = round(dist_euclidiana(puntos[n1], puntos[n2]), 2)
        matriz.append(fila)
    return nombres, matriz

# 3. Fitness: distancia TOTAL de la ruta  Almacén -> [orden clientes] -> Almacén
def distancia_ruta(orden):
    total = 0.0
    previo = ALMACEN
    tramos = []
    for c in orden:
        d = dist_euclidiana(previo, clientes[c])
        total += d
        tramos.append({'de': 'W' if previo == ALMACEN else _nombre_punto(previo),
                       'a': c, 'd': round(d, 2)})
        previo = clientes[c]
    d_regreso = dist_euclidiana(previo, ALMACEN)
    total += d_regreso
    tramos.append({'de': _nombre_punto(previo), 'a': 'W', 'd': round(d_regreso, 2)})
    return total, tramos

def _nombre_punto(punto):
    for nombre, coords in clientes.items():
        if coords == punto:
            return nombre
    return 'W'

# 4. Vecinos: intercambio (swap) de dos clientes dentro de la ruta
def obtener_vecinos(orden):
    vecinos = []
    for i in range(len(orden)):
        for j in range(i + 1, len(orden)):
            v = orden.copy()
            v[i], v[j] = v[j], v[i]
            vecinos.append((v, f"Swap: {orden[i]} ↔ {orden[j]}"))
    return vecinos

# 5. Hill Climbing para MINIMIZAR distancia total de la ruta
def hill_climbing_ruta(estado_inicial):
    actual = estado_inicial.copy()
    mejor_dist, _ = distancia_ruta(actual)
    historial = []
    movimiento = "Ruta Inicial"

    while True:
        historial.append({
            'ruta': actual.copy(),
            'distancia': round(mejor_dist, 2),
            'movimiento': movimiento
        })

        mejor_vecino = None
        mejor_mov = ""
        for vecino, desc in obtener_vecinos(actual):
            d_v, _ = distancia_ruta(vecino)
            if d_v < mejor_dist - 1e-9:
                mejor_dist = d_v
                mejor_vecino = vecino
                mejor_mov = desc

        if mejor_vecino is not None:
            actual = mejor_vecino
            movimiento = mejor_mov
        else:
            break

    historial.append({
        'ruta': actual.copy(),
        'distancia': round(mejor_dist, 2),
        'movimiento': "ÓPTIMO ALCANZADO (sin vecinos mejores)"
    })
    return actual, mejor_dist, historial

# 6. Óptimo global por fuerza bruta (5! = 120 rutas, trivial de calcular)
def optimo_global():
    mejor = float('inf')
    mejor_ruta = None
    for perm in permutations(clientes.keys()):
        d, _ = distancia_ruta(list(perm))
        if d < mejor:
            mejor = d
            mejor_ruta = list(perm)
    return mejor_ruta, mejor

# 6b. Ranking: las 120 rutas ordenadas de menor a mayor distancia (se calcula una vez)
_todas_las_rutas = None
def todas_las_rutas():
    global _todas_las_rutas
    if _todas_las_rutas is None:
        res = []
        for perm in permutations(clientes.keys()):
            d, _ = distancia_ruta(list(perm))
            res.append({'ruta': list(perm), 'dist': d})
        res.sort(key=lambda r: r['dist'])
        _todas_las_rutas = res
    return _todas_las_rutas

# Estado global de la ruta actual
ruta_actual = list(clientes.keys())          # A,B,C,D,E inicial
_, _, historial_inicial = hill_climbing_ruta(ruta_actual)
ruta_optima_hc, dist_optima_hc, historial_inicial = hill_climbing_ruta(ruta_actual)
ruta_actual = ruta_optima_hc.copy()
ruta_optima_global, dist_optima_global = optimo_global()
contador_ops = 1

def armar_respuesta(historial_custom=None, mensaje="Ruta actual"):
    dist_actual, tramos = distancia_ruta(ruta_actual)
    hist = historial_custom if historial_custom is not None else hill_climbing_ruta(ruta_actual)[2]
    nombres, matriz = construir_matriz()

    # Ranking de la ruta actual entre las 120 posibles
    todas = todas_las_rutas()
    mejores = sum(1 for r in todas if r['dist'] < dist_actual - 1e-9)
    peores = sum(1 for r in todas if r['dist'] > dist_actual + 1e-9)
    rank = mejores + 1
    pct_supera = round(peores / len(todas) * 100, 1)
    pct_top = round(rank / len(todas) * 100, 1)
    peor = todas[-1]

    detalles_clientes = [
        {'nombre': n, 'x': c[0], 'y': c[1],
         'dist_almacen': round(dist_euclidiana(ALMACEN, c), 2)}
        for n, c in clientes.items()
    ]

    return {
        'ruta': ruta_actual,
        'distancia': round(dist_actual, 2),
        'tramos': tramos,
        'historial': hist,
        'detalles_clientes': detalles_clientes,
        'almacen': ALMACEN,
        'optimo_global_ruta': ruta_optima_global,
        'optimo_global_dist': round(dist_optima_global, 2),
        'peor_ruta': peor['ruta'],
        'peor_dist': round(peor['dist'], 2),
        'rank': rank,
        'total_rutas': len(todas),
        'pct_supera': pct_supera,
        'pct_top': pct_top,
        'matriz_nombres': nombres,
        'matriz': matriz,
        'contador': contador_ops,
        'mensaje': mensaje
    }

# 7. Plantilla HTML Ultra 3D
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Repartidor 3D - Ruta Óptima (Euclidiana)</title>
    <link href="https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@400;700&family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-cyan: #00f3ff;
            --neon-pink: #ff007f;
            --neon-purple: #a855f7;
            --neon-green: #00ff9d;
            --neon-gold: #ffbe0b;
            --neon-red: #ff3366;
            --bg-deep: #030511;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Rajdhani', sans-serif;
            background: radial-gradient(circle at 50% 0%, #161d42 0%, #030511 75%);
            color: #eef6ff;
            min-height: 100vh;
            overflow-x: hidden;
            perspective: 1600px;
        }

        #bg-canvas {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            position: relative;
            z-index: 2;
            max-width: 1420px;
            margin: 0 auto;
            padding: 28px 24px 80px;
            transform-style: preserve-3d;
        }

        .hero {
            text-align: center;
            margin-bottom: 30px;
            transform-style: preserve-3d;
            animation: floatHero 6s ease-in-out infinite;
        }

        @keyframes floatHero {
            0%, 100% { transform: translateY(0px) rotateX(4deg); }
            50% { transform: translateY(-8px) rotateX(-3deg); }
        }

        .cyber-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 22px;
            border-radius: 999px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.76rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.45), inset 0 0 12px rgba(0, 243, 255, 0.25);
            margin-bottom: 12px;
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(1.9rem, 4vw, 3.3rem);
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: linear-gradient(90deg, #ffffff 0%, var(--neon-cyan) 45%, var(--neon-pink) 95%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 12px 28px rgba(0, 243, 255, 0.4));
        }

        .subtitle {
            color: #94a3b8;
            font-size: 1.15rem;
            margin-top: 6px;
            letter-spacing: 1px;
        }

        .card-3d {
            position: relative;
            background: linear-gradient(135deg, rgba(19, 28, 62, 0.84), rgba(8, 12, 30, 0.94));
            border: 1px solid rgba(0, 243, 255, 0.32);
            border-radius: 22px;
            padding: 24px;
            backdrop-filter: blur(18px);
            transform-style: preserve-3d;
            transition: transform 0.16s ease-out, box-shadow 0.3s ease, border-color 0.3s ease;
            box-shadow:
                0 28px 55px rgba(0, 0, 0, 0.8),
                0 0 28px rgba(0, 243, 255, 0.12),
                inset 0 1px 2px rgba(255, 255, 255, 0.22);
            overflow: hidden;
        }

        .card-3d::after {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at var(--glare-x, 50%) var(--glare-y, 50%), rgba(0, 243, 255, 0.16), transparent 55%);
            opacity: 0;
            transition: opacity 0.25s;
            pointer-events: none;
        }

        .card-3d:hover::after { opacity: 1; }
        .card-3d:hover { border-color: var(--neon-cyan); }

        .command-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 28px;
            padding: 20px 26px;
            border: 1px solid rgba(0, 255, 157, 0.45);
            background: linear-gradient(90deg, rgba(12, 26, 54, 0.92), rgba(22, 16, 52, 0.92));
            box-shadow: 0 0 35px rgba(0, 255, 157, 0.18);
        }

        .status-banner { display: flex; align-items: center; gap: 14px; }

        .rol-badge {
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            font-weight: 900;
            padding: 8px 16px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            color: #030511;
            box-shadow: 0 0 18px rgba(0, 243, 255, 0.6);
        }

        .action-buttons { display: flex; flex-wrap: wrap; gap: 12px; }

        .btn-3d {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            padding: 12px 18px;
            border-radius: 12px;
            cursor: pointer;
            border: 1px solid;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-azar {
            background: linear-gradient(135deg, rgba(255, 0, 127, 0.25), rgba(168, 85, 247, 0.15));
            border-color: var(--neon-pink);
            color: #fff;
            box-shadow: 0 6px 0 rgba(160, 0, 80, 0.7), 0 0 20px rgba(255, 0, 127, 0.35);
        }
        .btn-azar:hover { transform: translateY(-2px); background: var(--neon-pink); }
        .btn-azar:active { transform: translateY(4px); }

        .btn-optimizar {
            background: linear-gradient(135deg, rgba(0, 255, 157, 0.28), rgba(0, 255, 157, 0.1));
            border-color: var(--neon-green);
            color: #fff;
            box-shadow: 0 6px 0 rgba(0, 150, 90, 0.7), 0 0 22px rgba(0, 255, 157, 0.4);
        }
        .btn-optimizar:hover { transform: translateY(-2px); background: var(--neon-green); color: #030511; }

        .btn-optimal {
            background: linear-gradient(135deg, rgba(255, 190, 11, 0.3), rgba(255, 190, 11, 0.1));
            border-color: var(--neon-gold);
            color: #fff;
            box-shadow: 0 6px 0 rgba(160, 120, 0, 0.7), 0 0 22px rgba(255, 190, 11, 0.4);
        }
        .btn-optimal:hover { transform: translateY(-2px); background: var(--neon-gold); color: #030511; }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 22px;
            margin-bottom: 30px;
        }

        .kpi-label {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #94a3b8;
        }

        .kpi-val {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.2rem;
            font-weight: 900;
            margin: 8px 0;
        }

        .c-cyan { color: var(--neon-cyan); text-shadow: 0 0 22px rgba(0, 243, 255, 0.7); }
        .c-green { color: var(--neon-green); text-shadow: 0 0 22px rgba(0, 255, 157, 0.7); }
        .c-gold { color: var(--neon-gold); text-shadow: 0 0 22px rgba(255, 190, 11, 0.7); }
        .c-pink { color: var(--neon-pink); text-shadow: 0 0 22px rgba(255, 0, 127, 0.7); }

        .main-grid {
            display: grid;
            grid-template-columns: 1.25fr 1fr;
            gap: 26px;
            margin-bottom: 30px;
        }

        @media (max-width: 1080px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .section-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .pulse-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--neon-cyan);
            box-shadow: 0 0 16px var(--neon-cyan);
            animation: pulseGlow 1.6s infinite alternate;
        }

        @keyframes pulseGlow {
            from { transform: scale(0.85); opacity: 0.7; }
            to { transform: scale(1.25); opacity: 1; }
        }

        .cam-controls { display: flex; gap: 8px; flex-wrap: wrap; }

        .btn-cyber {
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.72rem;
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.2s;
        }

        .btn-cyber:hover {
            background: var(--neon-cyan);
            color: #030511;
            box-shadow: 0 0 18px var(--neon-cyan);
        }

        #mapa-2d-viewer {
            width: 100%;
            height: 480px;
            border-radius: 16px;
            background: radial-gradient(circle at center, rgba(20, 32, 80, 0.85), rgba(4, 6, 18, 0.96));
            border: 1px solid rgba(0, 243, 255, 0.35);
            box-shadow: inset 0 0 45px rgba(0, 243, 255, 0.16);
            position: relative;
            overflow: hidden;
        }

        #mapa-2d-canvas {
            width: 100%;
            height: 100%;
            display: block;
        }

        .viewer-overlay {
            position: absolute;
            bottom: 12px;
            left: 16px;
            right: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none;
            font-size: 0.82rem;
            color: #cbd5e1;
            flex-wrap: wrap;
            gap: 8px;
        }

        .legend-pill {
            background: rgba(3, 5, 17, 0.82);
            border: 1px solid rgba(0, 243, 255, 0.35);
            padding: 5px 12px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        /* Panel de ruta: lista ordenada de paradas */
        .route-track {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
        }

        .stop-node {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 74px;
            padding: 10px 8px;
            border-radius: 14px;
            background: rgba(11, 18, 42, 0.9);
            border: 1px solid rgba(0, 243, 255, 0.4);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5), 0 0 14px rgba(0, 243, 255, 0.2);
            transform-style: preserve-3d;
            transition: transform 0.2s;
        }

        .stop-node:hover { transform: translateY(-4px) translateZ(20px); }

        .stop-node.warehouse {
            border-color: var(--neon-gold);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5), 0 0 18px rgba(255, 190, 11, 0.35);
        }

        .stop-icon { font-size: 1.5rem; }
        .stop-name { font-family: 'Orbitron', sans-serif; font-weight: 800; font-size: 1rem; color: #fff; }
        .stop-coords { font-size: 0.75rem; color: #94a3b8; }

        .arrow-seg {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: var(--neon-cyan);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.72rem;
        }

        .arrow-line {
            font-size: 1.3rem;
            text-shadow: 0 0 12px var(--neon-cyan);
        }

        .table-3d {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 11px;
        }

        .table-3d thead th {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--neon-cyan);
            padding: 10px 14px;
            text-align: center;
            border-bottom: 1px solid rgba(0, 243, 255, 0.3);
        }

        .table-3d tbody tr {
            background: linear-gradient(90deg, rgba(20, 30, 66, 0.88), rgba(12, 18, 42, 0.94));
            transition: transform 0.22s ease, box-shadow 0.22s ease;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45);
        }

        .table-3d tbody tr:hover {
            transform: translateZ(20px) scale(1.01);
            box-shadow: 0 16px 32px rgba(0, 243, 255, 0.24);
        }

        .table-3d td {
            padding: 13px 14px;
            text-align: center;
            font-size: 1.02rem;
            font-weight: 600;
            border-top: 1px solid rgba(0, 243, 255, 0.2);
            border-bottom: 1px solid rgba(0, 243, 255, 0.2);
        }

        .table-3d td:first-child {
            border-left: 3px solid var(--neon-cyan);
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
        }

        .table-3d td:last-child {
            border-right: 1px solid rgba(0, 243, 255, 0.2);
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }

        .step-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 10px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            color: #030511;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        }

        .stop-chip {
            display: inline-block;
            margin: 2px 3px;
            padding: 4px 10px;
            border-radius: 8px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid rgba(0, 243, 255, 0.4);
            color: #fff;
        }

        .stop-chip.w {
            border-color: var(--neon-gold);
            color: var(--neon-gold);
            background: rgba(255, 190, 11, 0.12);
        }

        .row-winner {
            background: linear-gradient(90deg, rgba(0, 255, 157, 0.18), rgba(14, 22, 50, 0.95)) !important;
        }
        .row-winner td:first-child { border-left: 4px solid var(--neon-green); }

        .table-3d tfoot tr {
            background: linear-gradient(90deg, rgba(255, 190, 11, 0.22), rgba(20, 16, 44, 0.95)) !important;
        }
        .table-3d tfoot td {
            padding: 15px 14px;
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.15rem;
            font-weight: 900;
            color: var(--neon-gold);
            border-top: 2px solid var(--neon-gold);
            border-bottom: 1px solid rgba(255, 190, 11, 0.4);
            text-shadow: 0 0 14px rgba(255, 190, 11, 0.5);
        }
        .table-3d tfoot td:first-child {
            border-left: 4px solid var(--neon-gold);
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
        }
        .table-3d tfoot td:last-child {
            border-right: 1px solid rgba(255, 190, 11, 0.4);
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }

        /* Constructor de ruta: botones de clientes clicables */
        .builder-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 28px;
            padding: 18px 26px;
            border: 1px solid rgba(0, 243, 255, 0.45);
            background: linear-gradient(90deg, rgba(12, 26, 54, 0.92), rgba(16, 22, 58, 0.92));
        }

        .client-btns {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .client-btn {
            position: relative;
            width: 66px;
            height: 66px;
            border-radius: 14px;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.25rem;
            font-weight: 900;
            background: rgba(0, 243, 255, 0.12);
            border: 2px solid var(--neon-cyan);
            color: #fff;
            cursor: pointer;
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 5px 0 rgba(0, 140, 180, 0.6), 0 0 16px rgba(0, 243, 255, 0.3);
            transition: all 0.15s;
        }

        .client-btn:hover {
            transform: translateY(-3px);
            background: var(--neon-cyan);
            color: #030511;
        }

        .client-btn:active { transform: translateY(2px); }

        .client-btn.used {
            opacity: 0.35;
            pointer-events: none;
            background: rgba(0, 255, 157, 0.15);
            border-color: var(--neon-green);
        }

        .cb-coords {
            font-size: 0.62rem;
            color: #94a3b8;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
        }

        .client-btn:hover .cb-coords { color: #030511; }

        .pick-order {
            position: absolute;
            top: -9px;
            right: -9px;
            width: 23px;
            height: 23px;
            border-radius: 50%;
            background: var(--neon-green);
            color: #030511;
            font-size: 0.75rem;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px var(--neon-green);
        }

        .preview-ruta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            color: #cbd5e1;
        }

        .builder-actions { display: flex; gap: 8px; }

        /* Barra con la fórmula de la suma total */
        .suma-formula {
            margin-top: 16px;
            padding: 14px 18px;
            border-radius: 14px;
            background: linear-gradient(90deg, rgba(0, 255, 157, 0.14), rgba(0, 243, 255, 0.08));
            border: 1px solid var(--neon-green);
            box-shadow: 0 0 22px rgba(0, 255, 157, 0.25), inset 0 0 14px rgba(0, 255, 157, 0.1);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.98rem;
            font-weight: 700;
            text-align: center;
            line-height: 2;
            word-break: break-word;
        }
        .suma-formula .term { color: #8fb8ff; }
        .suma-formula .total { color: var(--neon-green); font-size: 1.25rem; text-shadow: 0 0 16px rgba(0,255,157,0.6); }

        .matrix-mini td, .matrix-mini th {
            font-size: 0.9rem !important;
            padding: 9px 8px !important;
        }

        /* ============================================================
           🎄 NAVIDAD EXCESIVA — Overrides globales 🎄
           Glassmorphism + Neumorfismo + Claymorphism navideño
           ============================================================ */
        :root {
            --neon-cyan: #f7c948;
            --neon-pink: #d42426;
            --neon-purple: #8fd3ff;
            --neon-green: #25b04f;
            --neon-gold: #f7c948;
            --neon-red: #d42426;
            --nieve: #f4fbff;
            --rojo: #d42426;
            --verde: #1fa34a;
            --hielo: #8fd3ff;
            --noche: #0b1f33;
        }

        body {
            background:
                radial-gradient(ellipse at 50% -10%, #1d4a6b 0%, #0b1f33 55%),
                linear-gradient(180deg, #0b1f33 0%, #071224 100%);
            color: var(--nieve);
            overflow-x: hidden;
        }

        h1 {
            font-family: 'Mountains of Christmas', cursive !important;
            font-weight: 700;
            letter-spacing: 4px;
            background: linear-gradient(90deg, #ffffff 0%, #ffd76e 40%, #ff6b6b 75%, #7bffab 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 4px 18px rgba(255, 215, 110, 0.5)) drop-shadow(0 0 35px rgba(37, 176, 79, 0.4));
        }

        .cyber-badge {
            font-family: 'Orbitron', sans-serif;
            background: rgba(212, 36, 38, 0.16);
            border: 1px solid #ff6b6b;
            color: #ffd0d0;
            box-shadow: 0 0 25px rgba(212, 36, 38, 0.5), inset 0 0 12px rgba(255, 255, 255, 0.2);
        }

        .subtitle { color: #bfd8ee; }

        /* === GLASSMORPHISM: tarjetas de vidrio helado === */
        .card-3d {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.10), rgba(180, 220, 255, 0.05)) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.35) !important;
            border-radius: 26px !important;
            backdrop-filter: blur(22px) saturate(140%) !important;
            -webkit-backdrop-filter: blur(22px) saturate(140%) !important;
            box-shadow:
                0 24px 50px rgba(0, 0, 0, 0.55),
                inset 0 1px 3px rgba(255, 255, 255, 0.5),
                inset 0 -6px 18px rgba(143, 211, 255, 0.12) !important;
        }
        .card-3d::after {
            background: radial-gradient(circle at var(--glare-x, 50%) var(--glare-y, 50%), rgba(255, 255, 255, 0.22), transparent 55%) !important;
        }
        .card-3d:hover {
            border-color: #ffd76e !important;
            box-shadow:
                0 30px 60px rgba(0, 0, 0, 0.65),
                0 0 35px rgba(247, 201, 72, 0.28),
                inset 0 1px 3px rgba(255, 255, 255, 0.5) !important;
        }

        /* === NEUMORFISMO: KPIs y chips hundidos === */
        .kpi-label { color: #a8c4dd !important; }
        .kpi-val { text-shadow: 0 2px 4px rgba(0,0,0,0.6), 0 0 24px currentColor !important; }
        .c-cyan { color: var(--hielo) !important; text-shadow: 0 0 22px rgba(143, 211, 255, 0.8) !important; }
        .c-green { color: #4be07a !important; text-shadow: 0 0 22px rgba(37, 176, 79, 0.8) !important; }
        .c-gold { color: var(--neon-gold) !important; }
        .c-pink { color: #ff8085 !important; }

        .energy-bar {
            background: rgba(7, 18, 36, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: inset 4px 4px 8px rgba(0,0,0,0.6), inset -3px -3px 6px rgba(143,211,255,0.15) !important;
        }
        .energy-fill {
            background: repeating-linear-gradient(45deg, #d42426, #d42426 12px, #f4fbff 12px, #f4fbff 24px) !important;
            box-shadow: 0 0 18px rgba(212, 36, 38, 0.7) !important;
        }

        .command-bar, .builder-bar {
            border: 1.5px solid rgba(255, 215, 110, 0.5) !important;
            background: linear-gradient(90deg, rgba(212, 36, 38, 0.14), rgba(31, 163, 74, 0.12)) !important;
        }

        .rol-badge {
            background: linear-gradient(135deg, #d42426, #f7c948) !important;
            color: #fff !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
            box-shadow:
                0 0 22px rgba(247, 201, 72, 0.6),
                inset -3px -4px 8px rgba(0,0,0,0.35),
                inset 3px 4px 8px rgba(255,255,255,0.4) !important;
        }

        /* === CLAYMORPHISM: botones gorditos de plastilina === */
        .btn-3d {
            border-radius: 20px !important;
            border: 2px solid rgba(255, 255, 255, 0.35) !important;
            font-family: 'Orbitron', sans-serif;
            box-shadow:
                0 8px 0 rgba(0, 0, 0, 0.4),
                inset 3px 4px 10px rgba(255, 255, 255, 0.4),
                inset -4px -6px 12px rgba(0, 0, 0, 0.35) !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.4);
        }
        .btn-azar {
            background: linear-gradient(135deg, #ff5b5b, #d42426) !important;
            border-color: #ffb3b3 !important;
            box-shadow: 0 8px 0 #7a0e0e, inset 3px 4px 10px rgba(255,255,255,0.45), inset -4px -6px 12px rgba(0,0,0,0.3), 0 0 24px rgba(212,36,38,0.5) !important;
        }
        .btn-azar:hover { background: linear-gradient(135deg, #ff7b7b, #e32) !important; transform: translateY(-3px) scale(1.04) !important; }
        .btn-optimizar {
            background: linear-gradient(135deg, #3ecb6b, #178a3d) !important;
            border-color: #9fffc4 !important;
            box-shadow: 0 8px 0 #0b4d22, inset 3px 4px 10px rgba(255,255,255,0.45), inset -4px -6px 12px rgba(0,0,0,0.3), 0 0 24px rgba(37,176,79,0.5) !important;
        }
        .btn-optimizar:hover { background: linear-gradient(135deg, #55e584, #1fa34a) !important; transform: translateY(-3px) scale(1.04) !important; }
        .btn-optimal {
            background: linear-gradient(135deg, #ffd76e, #d9a414) !important;
            border-color: #fff3c4 !important;
            color: #4a2e00 !important;
            box-shadow: 0 8px 0 #8a6200, inset 3px 4px 10px rgba(255,255,255,0.5), inset -4px -6px 12px rgba(0,0,0,0.25), 0 0 24px rgba(247,201,72,0.55) !important;
        }
        .btn-optimal:hover { transform: translateY(-3px) scale(1.04) !important; }

        .btn-cyber {
            background: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            color: var(--nieve) !important;
            border-radius: 14px !important;
            box-shadow: inset 2px 2px 6px rgba(255,255,255,0.25), inset -2px -3px 6px rgba(0,0,0,0.3) !important;
        }
        .btn-cyber:hover { background: #f7c948 !important; color: #4a2e00 !important; }

        .client-btn {
            border-radius: 20px !important;
            background: linear-gradient(145deg, rgba(255,255,255,0.16), rgba(143,211,255,0.08)) !important;
            border: 2px solid rgba(143, 211, 255, 0.6) !important;
            color: var(--nieve);
            box-shadow:
                0 6px 0 rgba(10, 40, 70, 0.8),
                inset 3px 4px 9px rgba(255,255,255,0.35),
                inset -3px -5px 10px rgba(0,0,0,0.3),
                0 0 18px rgba(143,211,255,0.35) !important;
        }
        .client-btn:hover { background: #f7c948 !important; color: #4a2e00 !important; border-color: #fff3c4 !important; }
        .client-btn.used { opacity: 0.4; background: rgba(37,176,79,0.25) !important; border-color: #4be07a !important; }
        .pick-order { background: #d42426 !important; color: #fff; box-shadow: 0 0 12px rgba(212,36,38,0.8); }

        /* Visor del mapa estilo ventana helada */
        #mapa-2d-viewer {
            background: radial-gradient(circle at center, rgba(20, 45, 75, 0.85), rgba(7, 18, 36, 0.95)) !important;
            border: 2px solid rgba(143, 211, 255, 0.5) !important;
            box-shadow: inset 0 0 50px rgba(143, 211, 255, 0.2), 0 0 30px rgba(143, 211, 255, 0.15) !important;
        }

        .section-title { color: #ffe9b8 !important; }
        .pulse-dot { background: var(--hielo) !important; box-shadow: 0 0 16px var(--hielo) !important; }

        /* Tablas estilo papel de regalo */
        .table-3d thead th { color: #ffd76e !important; border-bottom-color: rgba(255, 215, 110, 0.4) !important; }
        .table-3d tbody tr {
            background: linear-gradient(90deg, rgba(255,255,255,0.10), rgba(143,211,255,0.06)) !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
        }
        .table-3d td { border-top-color: rgba(255,255,255,0.2) !important; border-bottom-color: rgba(255,255,255,0.2) !important; }
        .table-3d td:first-child { border-left: 3px solid var(--hielo) !important; }
        .table-3d td:last-child { border-right: 1px solid rgba(255,255,255,0.2) !important; }
        .table-3d tfoot td { border-top: 2px solid var(--neon-gold) !important; }

        .stop-chip {
            background: rgba(37, 176, 79, 0.18) !important;
            border: 1px solid rgba(75, 224, 122, 0.5) !important;
            color: #d6ffd9 !important;
        }
        .stop-chip.w { border-color: var(--neon-gold) !important; color: var(--neon-gold) !important; background: rgba(247, 201, 72, 0.14) !important; }
        .stop-node { background: rgba(10, 30, 55, 0.9) !important; border-color: rgba(143, 211, 255, 0.5) !important; }
        .stop-node.warehouse { border-color: var(--neon-gold) !important; }
        .step-num { background: linear-gradient(135deg, #d42426, #f7c948) !important; color: #fff !important; }
        .arrow-seg { color: var(--hielo) !important; }
        .row-winner { background: linear-gradient(90deg, rgba(37,176,79,0.25), rgba(20,45,75,0.95)) !important; }

        .suma-formula {
            background: linear-gradient(90deg, rgba(37,176,79,0.18), rgba(212,36,38,0.12)) !important;
            border: 1.5px solid #4be07a !important;
            box-shadow: 0 0 22px rgba(37,176,79,0.3), inset 0 0 14px rgba(255,255,255,0.1) !important;
        }
        .suma-formula .term { color: #a8c4dd !important; }
        .suma-formula .total { color: #4be07a !important; }

        .legend-pill { border-color: rgba(255,255,255,0.35) !important; background: rgba(7, 18, 36, 0.85) !important; }

        /* ===== EL "67" FELIZ CON GORRO NAVIDEÑO ===== */
        .happy-67 {
            position: fixed;
            top: 48%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Mountains of Christmas', cursive;
            font-size: 42vw;
            color: rgba(212, 36, 38, 0.13);
            -webkit-text-stroke: 3px rgba(37, 176, 79, 0.16);
            text-shadow:
                0 0 60px rgba(212, 36, 38, 0.5),
                0 0 140px rgba(37, 176, 79, 0.4),
                0 0 260px rgba(247, 201, 72, 0.35);
            z-index: 0;
            pointer-events: none;
            user-select: none;
            animation: bounce67 2.8s ease-in-out infinite;
        }
        @keyframes bounce67 {
            0%, 100% { transform: translate(-50%, -50%) scale(1) rotate(-2deg); }
            50% { transform: translate(-50%, -53%) scale(1.03) rotate(2deg); }
        }
        .gorro-67 {
            position: fixed;
            top: calc(48% - 24vw);
            left: calc(50% + 9vw);
            width: 12vw;
            z-index: 1;
            pointer-events: none;
            animation: bounce67 2.8s ease-in-out infinite;
            filter: drop-shadow(0 6px 14px rgba(0,0,0,0.5));
        }

        /* ===== LUCES DE NAVIDAD PARPADEANTES ARRIBA ===== */
        .luces {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 26px;
            z-index: 6;
            display: flex;
            justify-content: space-around;
            pointer-events: none;
        }
        .foco {
            width: 14px; height: 14px;
            border-radius: 50%;
            animation: parpadear 1.4s infinite;
        }
        .foco::before {
            content: '';
            position: absolute;
            top: -6px; left: 5px;
            width: 4px; height: 6px;
            background: #5b3b1e;
            border-radius: 2px;
        }
        @keyframes parpadear {
            0%, 100% { box-shadow: 0 0 14px currentColor; opacity: 1; }
            50% { opacity: 0.35; box-shadow: 0 0 4px currentColor; }
        }

        /* ===== SANTA EN TRINEO VOLANDO POR EL CIELO ===== */
        .santa-vuelo {
            position: fixed;
            top: 8%;
            left: -320px;
            width: 300px;
            z-index: 4;
            pointer-events: none;
            animation: volarSanta 22s linear infinite;
            filter: drop-shadow(0 0 20px rgba(255,255,255,0.35));
        }
        @keyframes volarSanta {
            0% { transform: translateX(0) translateY(0) rotate(-3deg); }
            15% { transform: translateX(30vw) translateY(3vh) rotate(2deg); }
            35% { transform: translateX(60vw) translateY(-2vh) rotate(-4deg); }
            55% { transform: translateX(90vw) translateY(2vh) rotate(2deg); }
            75% { transform: translateX(120vw) translateY(-1vh); }
            100% { transform: translateX(150vw) translateY(0); }
        }

        /* ===== EL GRINCH ESPIANDO DESDE ABAJO ===== */
        .grinch {
            position: fixed;
            bottom: -52px;
            right: 4%;
            width: 170px;
            z-index: 4;
            pointer-events: none;
            animation: espiarGrinch 6s ease-in-out infinite;
            filter: drop-shadow(0 0 22px rgba(80, 160, 40, 0.6));
        }
        @keyframes espiarGrinch {
            0%, 100% { transform: translateY(0); }
            45%, 55% { transform: translateY(-34px); }
        }

        /* ===== REGALOS FLOTANDO ===== */
        .regalo {
            position: fixed;
            z-index: 1;
            pointer-events: none;
            user-select: none;
            animation: flotarRegalo var(--dur, 8s) ease-in-out infinite;
            filter: drop-shadow(0 0 14px rgba(255, 215, 110, 0.5));
        }
        @keyframes flotarRegalo {
            0%, 100% { transform: translateY(0) rotate(-8deg); }
            50% { transform: translateY(-20px) rotate(9deg); }
        }

        /* ===== DUENDES ===== */
        .duende {
            position: fixed;
            z-index: 1;
            font-size: 2rem;
            pointer-events: none;
            user-select: none;
            animation: duendeBaila var(--dur, 4s) ease-in-out infinite;
            filter: drop-shadow(0 0 10px rgba(75, 224, 122, 0.5));
        }
        @keyframes duendeBaila {
            0%, 100% { transform: rotate(-10deg) translateY(0); }
            50% { transform: rotate(10deg) translateY(-10px); }
        }

        /* ===== NIEVE ===== */
        #bg-canvas {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            z-index: 1;
            pointer-events: none;
        }
        .container { padding-top: 46px !important; }
    </style>
</head>
<body>
    <!-- 🎄 Luces navideñas parpadeantes -->
    <div class="luces" id="luces"></div>

    <canvas id="bg-canvas"></canvas>

    <!-- 🎅 El 67 feliz con su gorro navideño -->
    <div class="happy-67">67</div>
    <svg class="gorro-67" viewBox="0 0 100 70">
        <path d="M10 52 Q30 10 78 14 Q92 16 84 34 Q80 20 66 24 Q40 30 30 52 Z" fill="#d42426" stroke="#8f1212" stroke-width="2"/>
        <circle cx="86" cy="30" r="10" fill="#fff"/>
        <rect x="4" y="48" width="58" height="16" rx="8" fill="#fff" stroke="#d9d9d9" stroke-width="2"/>
    </svg>

    <!-- 🎅 Santa en trineo con Rodolfo volando -->
    <svg class="santa-vuelo" viewBox="0 0 320 120">
        <!-- Rodolfo -->
        <g>
            <path d="M255 60 q14 -18 34 -14 q10 2 12 14 q2 14 -10 18 q-16 5 -30 -4 q-8 -7 -6 -14 Z" fill="#8b5a2b"/>
            <path d="M282 44 q2 -14 -6 -20 M288 46 q8 -12 18 -16 M284 48 q-2 -16 -14 -22" stroke="#6b4423" stroke-width="4" fill="none" stroke-linecap="round"/>
            <circle cx="296" cy="62" r="7" fill="#ff1a1a">
                <animate attributeName="r" values="6;8;6" dur="1s" repeatCount="indefinite"/>
            </circle>
            <circle cx="296" cy="62" r="11" fill="#ff1a1a" opacity="0.35">
                <animate attributeName="opacity" values="0.5;0.15;0.5" dur="1s" repeatCount="indefinite"/>
            </circle>
            <circle cx="282" cy="54" r="3" fill="#1a1a1a"/>
        </g>
        <!-- Cuerda -->
        <path d="M246 66 L205 72" stroke="#c9a35a" stroke-width="3" fill="none"/>
        <!-- Trineo -->
        <g>
            <path d="M140 88 h70 q14 0 20 -12 l8 -4" fill="none" stroke="#d42426" stroke-width="6" stroke-linecap="round"/>
            <path d="M150 72 q-8 14 4 16 h56 q14 -2 12 -16 Z" fill="#a11212" stroke="#d42426" stroke-width="3"/>
            <path d="M150 72 q30 6 60 0" stroke="#f7c948" stroke-width="3" fill="none"/>
        </g>
        <!-- Santa -->
        <g>
            <circle cx="185" cy="38" r="15" fill="#ffd9b3"/>
            <path d="M170 40 q15 22 30 0 q-2 18 -15 18 q-13 0 -15 -18Z" fill="#fff"/>
            <path d="M168 34 q-2 -20 18 -20 q18 0 16 22" fill="#d42426"/>
            <circle cx="204" cy="16" r="6" fill="#fff"/>
            <circle cx="179" cy="34" r="2.4" fill="#222"/>
            <circle cx="191" cy="34" r="2.4" fill="#222"/>
            <rect x="164" y="52" width="44" height="24" rx="10" fill="#d42426"/>
            <rect x="162" y="62" width="48" height="7" fill="#1a1a1a"/>
            <rect x="181" y="62" width="10" height="7" fill="#f7c948"/>
        </g>
    </svg>

    <!-- 🟢 El Grinch espiando desde abajo a la orilla -->
    <svg class="grinch" viewBox="0 0 160 120">
        <path d="M30 118 q-4 -60 50 -62 q54 -2 50 62 Z" fill="#6fbf2e"/>
        <path d="M46 118 q0 -52 34 -52 q34 0 34 52" fill="#57a023" opacity="0.55"/>
        <path d="M56 30 q6 -22 26 -22 q20 0 24 22 l-6 8 q-20 -12 -38 0 Z" fill="#d42426"/>
        <circle cx="104" cy="12" r="8" fill="#fff"/>
        <rect x="52" y="36" width="58" height="12" rx="6" fill="#fff"/>
        <ellipse cx="66" cy="66" rx="13" ry="10" fill="#f4e04a"/>
        <ellipse cx="96" cy="66" rx="13" ry="10" fill="#f4e04a"/>
        <ellipse cx="66" cy="68" rx="5" ry="6" fill="#b3201f"/>
        <ellipse cx="96" cy="68" rx="5" ry="6" fill="#b3201f"/>
        <path d="M52 56 q14 -10 26 -2 M84 54 q14 -8 24 4" stroke="#2e4d0f" stroke-width="5" fill="none" stroke-linecap="round"/>
        <path d="M66 96 q15 -8 30 0" stroke="#2e4d0f" stroke-width="4" fill="none" stroke-linecap="round"/>
    </svg>

    <div class="container">
        <header class="hero">
            <div class="cyber-badge">🎄 IA • TSP • Distancia Euclidiana • Hill Climbing • Edición Navidad 🎅</div>
            <h1>🎅 Santa-Bot Repartidor: Ruta Óptima 🎁</h1>
            <p class="subtitle">Entregar los 5 regalos y regresar al taller W recorriendo la menor distancia euclidiana — ¡con nieve, duendes y el Grinch espiando!</p>
        </header>

        <!-- Barra de control -->
        <div class="card-3d command-bar">
            <div class="status-banner">
                <span class="rol-badge" id="ops-counter">RUTA #{{ estado_inicial.contador }}</span>
                <div>
                    <div style="font-family:'Orbitron',sans-serif; font-size:0.95rem; color:var(--neon-green);" id="action-status">
                        {{ estado_inicial.mensaje }}
                    </div>
                    <div style="font-size:0.9rem; color:#94a3b8;">
                        Inicio y regreso: Almacén W(0,0) • Métrica: distancia euclidiana √((x₂-x₁)² + (y₂-y₁)²)
                    </div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn-3d btn-azar" onclick="rutaAzar()">🎲 Ruta al Azar</button>
                <button class="btn-3d btn-optimizar" onclick="optimizar()">🚀 Optimizar (Hill Climbing)</button>
                <button class="btn-3d btn-optimal" onclick="cargarOptimo()">⭐ Óptimo Global (Fuerza Bruta)</button>
            </div>
        </div>

        <!-- Constructor de ruta personalizada -->
        <div class="card-3d builder-bar">
            <div>
                <div style="font-family:'Orbitron',sans-serif; font-size:0.95rem; color:var(--neon-cyan);">
                    🧭 Constructor de Ruta
                </div>
                <div style="font-size:0.9rem; color:#94a3b8;">
                    Haz clic en los clientes en el orden que quieras — ej. empieza en <strong>A</strong> y termina en <strong>E</strong>, y de ahí vuelve al almacén
                </div>
            </div>
            <div class="client-btns" id="client-btns"></div>
            <div class="preview-ruta" id="preview-ruta"></div>
            <div class="builder-actions">
                <button class="btn-cyber" onclick="undoPick()">↩ Deshacer</button>
                <button class="btn-cyber" onclick="clearPick()">✖ Limpiar</button>
            </div>
        </div>

        <!-- KPIs -->
        <section class="kpi-grid">
            <div class="card-3d tilt-card">
                <div class="kpi-label">Distancia Total de la Ruta Actual</div>
                <div class="kpi-val c-green"><span id="kpi-dist">{{ estado_inicial.distancia }}</span> u</div>
                <div style="color:#94a3b8; font-size:0.92rem;">W → <span id="kpi-ruta-mini">{{ estado_inicial.ruta | join(' → ') }}</span> → W</div>
            </div>
            <div class="card-3d tilt-card">
                <div class="kpi-label">Óptimo Global Real (Fuerza Bruta 5!)</div>
                <div class="kpi-val c-gold">{{ estado_inicial.optimo_global_dist }} u</div>
                <div style="color:#94a3b8; font-size:0.92rem;">W → {{ estado_inicial.optimo_global_ruta | join(' → ') }} → W</div>
            </div>
            <div class="card-3d tilt-card">
                <div class="kpi-label">Ranking entre las 120 Rutas Posibles</div>
                <div class="kpi-val c-pink">
                    <span id="kpi-rank">#{{ estado_inicial.rank }}</span>
                    <span style="font-size:1.05rem; color:#94a3b8;">de {{ estado_inicial.total_rutas }}</span>
                </div>
                <div class="energy-bar">
                    <div class="energy-fill" id="kpi-rank-barra" style="width: {{ estado_inicial.pct_supera }}%;"></div>
                </div>
                <div style="color:#94a3b8; font-size:0.92rem; margin-top:8px;" id="kpi-rank-detalle">
                    Top {{ estado_inicial.pct_top }}% • supera al {{ estado_inicial.pct_supera }}% de las rutas
                </div>
            </div>
            <div class="card-3d tilt-card">
                <div class="kpi-label">Peor Ruta Posible (máxima distancia)</div>
                <div class="kpi-val c-cyan">{{ estado_inicial.peor_dist }} u</div>
                <div style="color:#94a3b8; font-size:0.92rem;">W → {{ estado_inicial.peor_ruta | join(' → ') }} → W</div>
            </div>
            <div class="card-3d tilt-card">
                <div class="kpi-label">Pasos de Escalada Hill Climbing</div>
                <div class="kpi-val c-cyan" id="kpi-pasos">{{ estado_inicial.historial | length }} iter.</div>
                <div style="color:#94a3b8; font-size:0.92rem;">Vecinos por intercambio de pares (Swap)</div>
            </div>
        </section>

        <!-- Mapa 3D + Ruta en orden -->
        <div class="main-grid">
            <div class="card-3d tilt-card">
                <div class="section-header">
                    <div class="section-title">
                        <span class="pulse-dot"></span> Mapa 2D: Almacén, Clientes, Coordenadas y Distancias
                    </div>
                    <div class="cam-controls">
                        <button class="btn-cyber" onclick="toggleRobot()">⏯ Robot</button>
                    </div>
                </div>
                <div id="mapa-2d-viewer">
                    <canvas id="mapa-2d-canvas"></canvas>
                    <div class="viewer-overlay">
                        <div class="legend-pill">
                            <span style="color:var(--neon-gold);">▣ Almacén W(0,0)</span>
                            <span style="color:var(--neon-cyan);">● Clientes con coordenadas</span>
                            <span style="color:var(--neon-green);">─ Ruta con distancia por tramo</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Secuencia de paradas + tramos con distancias -->
            <div class="card-3d">
                <div class="section-header">
                    <div class="section-title">
                        <span class="pulse-dot" style="background:var(--neon-green); box-shadow:0 0 16px var(--neon-green);"></span>
                        Secuencia de Entrega & Tramos
                    </div>
                </div>
                <div class="route-track" id="route-track"></div>
                <table class="table-3d" style="margin-top:12px;">
                    <thead>
                        <tr><th>Tramo</th><th>Distancia Euclidiana</th></tr>
                    </thead>
                    <tbody id="tabla-tramos-body"></tbody>
                    <tfoot id="tabla-tramos-foot"></tfoot>
                </table>
                <div class="suma-formula" id="suma-formula"></div>
            </div>
        </div>

        <!-- Matriz de distancias euclidianas -->
        <div class="card-3d" style="margin-bottom:30px;">
            <div class="section-header">
                <div class="section-title">
                    <span class="pulse-dot" style="background:var(--neon-purple); box-shadow:0 0 16px var(--neon-purple);"></span>
                    Matriz de Distancias Euclidianas (W = Almacén)
                </div>
            </div>
            <table class="table-3d matrix-mini">
                <thead>
                    <tr>
                        <th>Nodo</th>
                        {% for n in estado_inicial.matriz_nombres %}<th>{{ n }}</th>{% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for fila in estado_inicial.matriz %}
                    <tr>
                        <td style="font-family:'Orbitron',sans-serif; color:var(--neon-cyan);">{{ fila.nodo }}</td>
                        {% for n in estado_inicial.matriz_nombres %}
                        <td>{{ fila.dist[n] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Historial Hill Climbing -->
        <div class="card-3d">
            <div class="section-header">
                <div class="section-title">
                    <span class="pulse-dot" style="background:var(--neon-pink); box-shadow:0 0 16px var(--neon-pink);"></span>
                    Ruta de Optimización Hill Climbing (paso a paso)
                </div>
            </div>
            <table class="table-3d">
                <thead>
                    <tr>
                        <th>Paso</th>
                        <th>Movimiento</th>
                        <th>Ruta Completa (W → ... → W)</th>
                        <th>Distancia Total</th>
                    </tr>
                </thead>
                <tbody id="tabla-historial-body"></tbody>
            </table>
        </div>
    </div>

    <script>
        let estadoApp = {{ estado_inicial | tojson }};
        const COORDS = {
            'W': [{{ estado_inicial.almacen[0] }}, {{ estado_inicial.almacen[1] }}],
            {% for n, c in clientes.items() %}'{{ n }}': [{{ c[0] }}, {{ c[1] }}],{% endfor %}
        };

        // 1. Tilt 3D en tarjetas
        document.querySelectorAll('.tilt-card').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.transform = `perspective(1200px) rotateX(${((y/rect.height)-0.5)*-10}deg) rotateY(${((x/rect.width)-0.5)*10}deg) translateZ(6px)`;
                card.style.setProperty('--glare-x', `${(x/rect.width)*100}%`);
                card.style.setProperty('--glare-y', `${(y/rect.height)*100}%`);
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
            });
        });

        // 2. Fondo navideño: nieve cayendo + luces + regalos + duendes
        const bgCanvas = document.getElementById('bg-canvas');
        const bgCtx = bgCanvas.getContext('2d');
        let flakes = [];
        function resizeBg() {
            bgCanvas.width = window.innerWidth;
            bgCanvas.height = window.innerHeight;
            flakes = Array.from({length: 160}, () => ({
                x: Math.random() * bgCanvas.width,
                y: Math.random() * bgCanvas.height,
                r: 1 + Math.random() * 3.2,
                v: 0.6 + Math.random() * 1.8,
                sway: Math.random() * Math.PI * 2,
                swayV: 0.008 + Math.random() * 0.02
            }));
        }
        resizeBg();
        function animateBg() {
            requestAnimationFrame(animateBg);
            bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
            bgCtx.fillStyle = '#ffffff';
            for (const f of flakes) {
                f.y += f.v;
                f.sway += f.swayV;
                f.x += Math.sin(f.sway) * 0.7;
                if (f.y > bgCanvas.height + 6) { f.y = -6; f.x = Math.random() * bgCanvas.width; }
                bgCtx.globalAlpha = 0.45 + f.r * 0.15;
                bgCtx.beginPath();
                bgCtx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
                bgCtx.fill();
            }
            bgCtx.globalAlpha = 1;
        }
        animateBg();

        // Luces navideñas parpadeantes
        const coloresLuz = ['#ff4b4b', '#ffd76e', '#4be07a', '#8fd3ff', '#ff9de2'];
        const luces = document.getElementById('luces');
        for (let i = 0; i < 26; i++) {
            const f = document.createElement('div');
            f.className = 'foco';
            f.style.color = coloresLuz[i % coloresLuz.length];
            f.style.background = coloresLuz[i % coloresLuz.length];
            f.style.animationDelay = (Math.random() * 1.4) + 's';
            luces.appendChild(f);
        }

        // Regalos flotando por toda la pantalla
        const emojisRegalo = ['🎁', '🎄', '⭐', '❄️', '🔔', '🕯️', '🍪'];
        for (let i = 0; i < 22; i++) {
            const r = document.createElement('div');
            r.className = 'regalo';
            r.textContent = emojisRegalo[i % emojisRegalo.length];
            r.style.left = (2 + Math.random() * 94) + 'vw';
            r.style.top = (4 + Math.random() * 88) + 'vh';
            r.style.fontSize = (1.2 + Math.random() * 1.8) + 'rem';
            r.style.setProperty('--dur', (5 + Math.random() * 7) + 's');
            r.style.animationDelay = (Math.random() * 6) + 's';
            document.body.appendChild(r);
        }

        // Muchos duendes bailando
        const emojisDuende = ['🧝', '🧝‍♂️', '🧝‍♀️'];
        for (let i = 0; i < 14; i++) {
            const d = document.createElement('div');
            d.className = 'duende';
            d.textContent = emojisDuende[i % emojisDuende.length];
            d.style.left = (3 + Math.random() * 92) + 'vw';
            d.style.top = (8 + Math.random() * 80) + 'vh';
            d.style.fontSize = (1.4 + Math.random() * 1.4) + 'rem';
            d.style.setProperty('--dur', (2.5 + Math.random() * 3.5) + 's');
            d.style.animationDelay = (Math.random() * 4) + 's';
            document.body.appendChild(d);
        }

        // 3. Mapa 2D en Canvas: plano cartesiano con coordenadas, distancias y robot
        const viewer = document.getElementById('mapa-2d-viewer');
        const mapaCanvas = document.getElementById('mapa-2d-canvas');
        const mctx = mapaCanvas.getContext('2d');

        const MARGEN = { izq: 52, der: 28, sup: 30, inf: 52 };
        let rutaActual = [];
        let tramosActuales = [];
        let robotT = 0;
        let robotOn = true;

        function ajustarCanvas() {
            const dpr = window.devicePixelRatio || 1;
            mapaCanvas.width = viewer.clientWidth * dpr;
            mapaCanvas.height = viewer.clientHeight * dpr;
            mctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }
        ajustarCanvas();

        // Convierte coordenada de datos (0..8) a píxel del canvas
        function aPixel(x, y) {
            const w = viewer.clientWidth - MARGEN.izq - MARGEN.der;
            const h = viewer.clientHeight - MARGEN.sup - MARGEN.inf;
            const lado = Math.min(w, h);
            const ox = MARGEN.izq + (w - lado) / 2;
            const oy = MARGEN.sup + (h - lado) / 2;
            return {
                x: ox + (x / 8) * lado,
                y: oy + (1 - y / 8) * lado   // Y crece hacia arriba
            };
        }

        function dibujarMapa() {
            const W = viewer.clientWidth;
            const H = viewer.clientHeight;
            mctx.clearRect(0, 0, W, H);

            // Fondo del plano
            const p00 = aPixel(0, 0), p88 = aPixel(8, 8);
            mctx.fillStyle = 'rgba(8, 14, 34, 0.75)';
            mctx.fillRect(p88.x, p88.y, p00.x - p88.x, p00.y - p88.y);

            // Cuadrícula 0..8 con números de coordenadas en los ejes
            for (let c = 0; c <= 8; c++) {
                const pv = aPixel(c, 0), pv2 = aPixel(c, 8);
                const ph = aPixel(0, c), ph2 = aPixel(8, c);

                mctx.strokeStyle = c === 0 ? 'rgba(143, 211, 255, 0.7)' : 'rgba(143, 211, 255, 0.16)';
                mctx.lineWidth = c === 0 ? 2 : 1;
                mctx.beginPath();
                mctx.moveTo(pv.x, pv2.y); mctx.lineTo(pv.x, pv.y); mctx.stroke();   // vertical
                mctx.beginPath();
                mctx.moveTo(ph.x, ph.y); mctx.lineTo(ph2.x, ph.y); mctx.stroke();   // horizontal

                // Números eje X (abajo) y eje Y (izquierda)
                mctx.font = 'bold 13px Orbitron, sans-serif';
                mctx.fillStyle = '#ffe9b8';
                mctx.textAlign = 'center';
                mctx.fillText(c, pv.x, pv.y + 22);
                mctx.textAlign = 'right';
                mctx.fillText(c, ph.x - 10, ph.y + 4);
            }

            // Etiquetas de los ejes
            mctx.font = 'bold 14px Orbitron, sans-serif';
            mctx.fillStyle = '#8fd3ff';
            mctx.textAlign = 'center';
            mctx.fillText('EJE X', p00.x + (p88.x - p00.x) / 2, p00.y + 42);
            mctx.save();
            mctx.translate(p88.x - 34, p00.y + (p88.y - p00.y) / 2);
            mctx.rotate(-Math.PI / 2);
            mctx.fillText('EJE Y', 0, 0);
            mctx.restore();

            // Ruta: línea verde con flechas y distancia por tramo
            const secuencia = ['W', ...rutaActual, 'W'];
            const pts = secuencia.map(n => aPixel(COORDS[n][0], COORDS[n][1]));

            mctx.strokeStyle = '#ff5b5b';
            mctx.lineWidth = 3;
            mctx.shadowColor = '#ff5b5b';
            mctx.shadowBlur = 10;
            mctx.beginPath();
            pts.forEach((p, i) => i === 0 ? mctx.moveTo(p.x, p.y) : mctx.lineTo(p.x, p.y));
            mctx.stroke();
            mctx.shadowBlur = 0;

            // Flechas de dirección + etiqueta de distancia en el punto medio
            for (let i = 0; i < pts.length - 1; i++) {
                const a = pts[i], b = pts[i + 1];
                const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
                const ang = Math.atan2(b.y - a.y, b.x - a.x);

                // Punta de flecha en el medio del tramo
                mctx.save();
                mctx.translate(mx, my);
                mctx.rotate(ang);
                mctx.fillStyle = '#ff5b5b';
                mctx.beginPath();
                mctx.moveTo(9, 0); mctx.lineTo(-5, -6); mctx.lineTo(-5, 6);
                mctx.closePath(); mctx.fill();
                mctx.restore();

                // Etiqueta de distancia desplazada perpendicular a la línea
                if (tramosActuales[i]) {
                    const nx = -Math.sin(ang) * 16, ny = Math.cos(ang) * 16;
                    const txt = `${tramosActuales[i].de}→${tramosActuales[i].a}: ${tramosActuales[i].d}`;
                    mctx.font = 'bold 11.5px Orbitron, sans-serif';
                    const tw = mctx.measureText(txt).width + 14;
                    mctx.fillStyle = 'rgba(10, 30, 55, 0.92)';
                    mctx.strokeStyle = 'rgba(255, 91, 91, 0.75)';
                    mctx.lineWidth = 1.2;
                    mctx.beginPath();
                    mctx.roundRect(mx + nx - tw / 2, my + ny - 11, tw, 22, 8);
                    mctx.fill(); mctx.stroke();
                    mctx.fillStyle = '#ff5b5b';
                    mctx.textAlign = 'center';
                    mctx.fillText(txt, mx + nx, my + ny + 4);
                }
            }

            // Almacén W: cuadrado dorado
            const wp = aPixel(0, 0);
            mctx.fillStyle = '#ffbe0b';
            mctx.shadowColor = '#ffbe0b';
            mctx.shadowBlur = 16;
            mctx.fillRect(wp.x - 11, wp.y - 11, 22, 22);
            mctx.shadowBlur = 0;
            mctx.strokeStyle = '#fff2c0';
            mctx.lineWidth = 2;
            mctx.strokeRect(wp.x - 11, wp.y - 11, 22, 22);
            mctx.font = 'bold 13px Orbitron, sans-serif';
            mctx.fillStyle = '#ffbe0b';
            mctx.textAlign = 'center';
            mctx.fillText('W (0,0)', wp.x + 34, wp.y + 16);

            // Clientes: círculos cian con letra y coordenadas
            Object.entries(COORDS).forEach(([n, c]) => {
                if (n === 'W') return;
                const p = aPixel(c[0], c[1]);
                mctx.fillStyle = '#4be07a';
                mctx.shadowColor = '#4be07a';
                mctx.shadowBlur = 14;
                mctx.beginPath();
                mctx.arc(p.x, p.y, 10, 0, Math.PI * 2);
                mctx.fill();
                mctx.shadowBlur = 0;
                mctx.strokeStyle = '#d6ffd9';
                mctx.lineWidth = 2;
                mctx.stroke();
                mctx.fillStyle = '#030511';
                mctx.font = 'bold 12px Orbitron, sans-serif';
                mctx.textAlign = 'center';
                mctx.fillText(n, p.x, p.y + 4);
                // Coordenadas del cliente
                mctx.fillStyle = '#ffe9b8';
                mctx.font = 'bold 11px Orbitron, sans-serif';
                mctx.fillText(`(${c[0]}, ${c[1]})`, p.x, p.y - 16);
            });

            // Robot animado recorriendo la ruta
            if (robotOn && pts.length > 1) {
                robotT = (robotT + 0.0022) % 1;
                const totalSegs = pts.length - 1;
                const pos = robotT * totalSegs;
                const seg = Math.min(totalSegs - 1, Math.floor(pos));
                const t = pos - seg;
                const rx = pts[seg].x + (pts[seg + 1].x - pts[seg].x) * t;
                const ry = pts[seg].y + (pts[seg + 1].y - pts[seg].y) * t;
                mctx.fillStyle = '#ffffff';
                mctx.shadowColor = '#ff5b5b';
                mctx.shadowBlur = 18;
                mctx.beginPath();
                mctx.arc(rx, ry, 7, 0, Math.PI * 2);
                mctx.fill();
                mctx.shadowBlur = 0;
                mctx.font = 'bold 11px Orbitron, sans-serif';
                mctx.fillStyle = '#ffffff';
                mctx.textAlign = 'center';
                mctx.fillText('🤖', rx, ry - 12);
            }
        }

        window.toggleRobot = function() { robotOn = !robotOn; };

        function reconstruirRuta(ruta, tramos) {
            rutaActual = ruta;
            tramosActuales = tramos || [];
        }

        function animarMapa() {
            requestAnimationFrame(animarMapa);
            dibujarMapa();
        }
        animarMapa();

        // 4. Render de UI
        const NOMBRES = {'W':'🏭 W'};
        function chipsDeRuta(ruta) {
            const seq = ['W', ...ruta, 'W'];
            return seq.map(n => `<span class="stop-chip ${n === 'W' ? 'w' : ''}">${n}</span>`).join(' → ');
        }

        function renderizarUI(data) {
            estadoApp = data;
            document.getElementById('ops-counter').textContent = `RUTA #${data.contador}`;
            document.getElementById('action-status').textContent = data.mensaje;
            document.getElementById('kpi-dist').textContent = data.distancia;
            document.getElementById('kpi-ruta-mini').textContent = data.ruta.join(' → ');
            document.getElementById('kpi-pasos').textContent = `${data.historial.length} iter.`;
            document.getElementById('kpi-rank').textContent = `#${data.rank}`;
            document.getElementById('kpi-rank-barra').style.width = `${data.pct_supera}%`;
            document.getElementById('kpi-rank-detalle').textContent =
                `Top ${data.pct_top}% • supera al ${data.pct_supera}% de las ${data.total_rutas} rutas`;

            // Secuencia de paradas con flechas y distancias
            const seq = ['W', ...data.ruta, 'W'];
            document.getElementById('route-track').innerHTML = seq.map((n, i) => {
                const esW = n === 'W';
                const coords = COORDS[n];
                const icono = esW ? '🏭' : '📦';
                const dist = i > 0 && data.tramos[i-1] ? data.tramos[i-1].d : '';
                const flecha = i > 0 ? `<div class="arrow-seg"><span class="arrow-line">⟶</span><span>${dist} u</span></div>` : '';
                return `${flecha}<div class="stop-node ${esW ? 'warehouse' : ''}">
                    <span class="stop-icon">${icono}</span>
                    <span class="stop-name">${n}</span>
                    <span class="stop-coords">(${coords[0]}, ${coords[1]})</span>
                </div>`;
            }).join('');

            // Tabla de tramos + fila del TOTAL (salida del almacén, entregas y regreso)
            document.getElementById('tabla-tramos-body').innerHTML = data.tramos.map((t, i) => `
                <tr>
                    <td><span class="stop-chip ${t.de==='W'?'w':''}">${t.de}</span> ⟶ <span class="stop-chip ${t.a==='W'?'w':''}">${t.a}</span></td>
                    <td style="font-family:'Orbitron',sans-serif; color:var(--neon-green);">${t.d} u</td>
                </tr>
            `).join('');

            document.getElementById('tabla-tramos-foot').innerHTML = `
                <tr>
                    <td>Σ TOTAL (W → entregas → W)</td>
                    <td>${data.distancia} u</td>
                </tr>
            `;

            // Fórmula de la suma desglosada: salida + cada entrega + regreso
            const terminos = data.tramos.map(t => `${t.d}`).join(' + ');
            document.getElementById('suma-formula').innerHTML =
                `Σ = <span class="term">${terminos}</span> = <span class="total">${data.distancia} u</span>`;

            // Historial
            document.getElementById('tabla-historial-body').innerHTML = data.historial.map((p, i) => `
                <tr class="${i === data.historial.length - 1 ? 'row-winner' : ''}">
                    <td><span class="step-num">${i + 1}</span></td>
                    <td style="color:var(--neon-gold); font-family:'Orbitron',sans-serif; font-size:0.85rem;">${p.movimiento}</td>
                    <td>${chipsDeRuta(p.ruta)}</td>
                    <td style="font-family:'Orbitron',sans-serif; font-size:1.15rem; color:var(--neon-green);">${p.distancia} u</td>
                </tr>
            `).join('');

            reconstruirRuta(data.ruta, data.tramos);
        }

        async function enviarAccion(url, payload) {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            renderizarUI(await res.json());
        }

        window.rutaAzar = () => enviarAccion('/api/azar', {});
        window.optimizar = () => enviarAccion('/api/optimizar', {});
        window.cargarOptimo = () => enviarAccion('/api/optimo', {});

        // ===== Constructor de ruta personalizada =====
        const CLIENTES_ORDEN = ['A', 'B', 'C', 'D', 'E'];
        let seleccionRuta = [];

        function renderConstructor() {
            document.getElementById('client-btns').innerHTML = CLIENTES_ORDEN.map(n => {
                const idx = seleccionRuta.indexOf(n);
                const usado = idx >= 0;
                return `<button class="client-btn ${usado ? 'used' : ''}" onclick="pickCliente('${n}')">
                    ${n}
                    ${usado ? `<span class="pick-order">${idx + 1}</span>` : ''}
                    <span class="cb-coords">(${COORDS[n][0]}, ${COORDS[n][1]})</span>
                </button>`;
            }).join('');

            const seq = ['W', ...seleccionRuta, 'W'];
            document.getElementById('preview-ruta').innerHTML =
                `<span style="color:#94a3b8; font-size:0.8rem;">PREVIEW:</span> ` +
                seq.map(n => `<span class="stop-chip ${n === 'W' ? 'w' : ''}">${n}</span>`).join(' → ');
        }

        window.pickCliente = function(n) {
            if (seleccionRuta.includes(n)) return;
            seleccionRuta.push(n);
            renderConstructor();
            // Cuando ya elegiste los 5 clientes, aplicamos tu ruta
            if (seleccionRuta.length === CLIENTES_ORDEN.length) {
                const orden = seleccionRuta.slice();
                seleccionRuta = [];
                enviarAccion('/api/ruta_manual', { orden });
            }
        };

        window.undoPick = function() { seleccionRuta.pop(); renderConstructor(); };
        window.clearPick = function() { seleccionRuta = []; renderConstructor(); };

        renderizarUI(estadoApp);
        renderConstructor();

        window.addEventListener('resize', () => {
            resizeBg();
            ajustarCanvas();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        estado_inicial=armar_respuesta(
            historial_custom=historial_inicial,
            mensaje="Ruta óptima encontrada con Hill Climbing (desde A→B→C→D→E)"
        ),
        clientes=clientes
    )

@app.route('/api/azar', methods=['POST'])
def api_azar():
    global ruta_actual, contador_ops
    ruta_actual = list(clientes.keys())
    random.shuffle(ruta_actual)
    contador_ops += 1
    return jsonify(armar_respuesta(mensaje="Ruta aleatoria generada — presiona Optimizar para mejorarla"))

@app.route('/api/optimizar', methods=['POST'])
def api_optimizar():
    global ruta_actual, contador_ops
    ruta_actual, dist, historial = hill_climbing_ruta(ruta_actual)
    contador_ops += 1
    return jsonify(armar_respuesta(
        historial_custom=historial,
        mensaje=f"Optimizado con Hill Climbing: {round(dist, 2)} u en {len(historial)-1} mejora(s)"
    ))

@app.route('/api/ruta_manual', methods=['POST'])
def api_ruta_manual():
    global ruta_actual, contador_ops
    datos = request.get_json() or {}
    orden = datos.get('orden', [])
    # Validar que sea una permutación válida de los 5 clientes
    if sorted(orden) == sorted(clientes.keys()):
        ruta_actual = orden.copy()
        contador_ops += 1
        return jsonify(armar_respuesta(
            mensaje=f"Ruta personalizada aplicada: W → {' → '.join(orden)} → W"
        ))
    return jsonify(armar_respuesta(mensaje="Ruta inválida — debes elegir los 5 clientes"))

@app.route('/api/optimo', methods=['POST'])
def api_optimo():
    global ruta_actual, contador_ops
    ruta_actual = ruta_optima_global.copy()
    contador_ops += 1
    return jsonify(armar_respuesta(
        mensaje=f"Óptimo global garantizado (fuerza bruta sobre 120 rutas): {round(dist_optima_global, 2)} u"
    ))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
