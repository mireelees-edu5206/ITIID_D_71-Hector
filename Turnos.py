import random
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# 1. Definición de Empleados, Preferencias y Turnos disponibles
empleados = ['Ana', 'Luis', 'Carlos', 'Maria']

# Estado global editable desde la interfaz 3D
preferencias_actuales = {
    'Ana': 'Matutino',
    'Luis': 'Vespertino',
    'Carlos': 'Nocturno',
    'Maria': 'Matutino'
}

turnos_disponibles = ['Mañana (Matutino)', 'Tarde (Vespertino)', 'Noche (Nocturno)', 'Mixto']
preferencias_disponibles = ['Matutino', 'Vespertino', 'Nocturno', 'Mixto']

equivalencia_turno = {
    'Mañana (Matutino)': 'Matutino',
    'Tarde (Vespertino)': 'Vespertino',
    'Noche (Nocturno)': 'Nocturno',
    'Mixto': 'Mixto'
}

# Estado actual de quién está en qué turno (se puede rolar, modificar manualmente o con Hill Climbing)
asignacion_actual_global = {
    'Ana': 'Mañana (Matutino)',
    'Luis': 'Tarde (Vespertino)',
    'Carlos': 'Noche (Nocturno)',
    'Maria': 'Mixto'
}

contador_rol = 1

# 2. Función de Evaluación (Fitness)
# +100 pts si recibe su turno preferido exacto
# +60 pts si recibe el turno 'Mixto' (comodín adaptable)
# +20 pts si recibe un turno diferente a su preferencia
def evaluar_empleado(empleado, turno, prefs=None):
    if prefs is None:
        prefs = preferencias_actuales
    pref = prefs[empleado]
    tipo_turno = equivalencia_turno[turno]
    if tipo_turno == pref:
        return 100
    elif tipo_turno == 'Mixto':
        return 60
    else:
        return 20

def evaluar(estado, prefs=None):
    if prefs is None:
        prefs = preferencias_actuales
    satisfaccion_total = sum(evaluar_empleado(emp, turno, prefs) for emp, turno in estado.items())
    coincidencias_exactas = sum(
        1 for emp, turno in estado.items() if equivalencia_turno[turno] == prefs[emp]
    )
    return satisfaccion_total, coincidencias_exactas

# 3. Generación de Vecinos (intercambiando los turnos entre pares de empleados)
def obtener_vecinos(estado):
    vecinos = []
    lista_emp = list(estado.keys())
    for i in range(len(lista_emp)):
        for j in range(i + 1, len(lista_emp)):
            vecino = estado.copy()
            emp1, emp2 = lista_emp[i], lista_emp[j]
            vecino[emp1], vecino[emp2] = vecino[emp2], vecino[emp1]
            vecinos.append((vecino, f"Intercambio: {emp1} ↔ {emp2}"))
    return vecinos

# 4. Algoritmo Hill Climbing desde cualquier estado inicial
def hill_climbing_turnos(estado_inicial=None, prefs=None):
    if prefs is None:
        prefs = preferencias_actuales
    if estado_inicial is None:
        estado_actual = {
            'Ana': 'Noche (Nocturno)',
            'Luis': 'Mañana (Matutino)',
            'Carlos': 'Mixto',
            'Maria': 'Tarde (Vespertino)'
        }
    else:
        estado_actual = estado_inicial.copy()

    puntaje_actual, exactas_actual = evaluar(estado_actual, prefs)
    historial = []
    movimiento = "Estado Inicial de Partida"

    while True:
        historial.append({
            'asignacion': estado_actual.copy(),
            'puntaje': puntaje_actual,
            'exactas': exactas_actual,
            'movimiento': movimiento
        })

        vecinos = obtener_vecinos(estado_actual)
        mejor_vecino = None
        mejor_puntaje = puntaje_actual
        mejor_exactas = exactas_actual
        mejor_movimiento = ""

        for vecino, desc_mov in vecinos:
            puntaje_v, exactas_v = evaluar(vecino, prefs)
            if puntaje_v > mejor_puntaje:
                mejor_puntaje = puntaje_v
                mejor_exactas = exactas_v
                mejor_vecino = vecino
                mejor_movimiento = desc_mov

        if mejor_vecino is not None and mejor_puntaje > puntaje_actual:
            estado_actual = mejor_vecino
            puntaje_actual = mejor_puntaje
            exactas_actual = mejor_exactas
            movimiento = mejor_movimiento
        else:
            break

    return estado_actual, puntaje_actual, exactas_actual, historial

def armar_respuesta_estado(historial_custom=None, mensaje_accion="Estado Actual"):
    puntaje_actual, exactas_actual = evaluar(asignacion_actual_global, preferencias_actuales)
    if historial_custom is None:
        _, _, _, historial_hc = hill_climbing_turnos(asignacion_actual_global, preferencias_actuales)
    else:
        historial_hc = historial_custom

    detalles_empleados = []
    for emp in empleados:
        turno_asignado = asignacion_actual_global[emp]
        puntos = evaluar_empleado(emp, turno_asignado, preferencias_actuales)
        es_exacto = equivalencia_turno[turno_asignado] == preferencias_actuales[emp]
        es_mixto = equivalencia_turno[turno_asignado] == 'Mixto' and not es_exacto
        detalles_empleados.append({
            'nombre': emp,
            'preferencia': preferencias_actuales[emp],
            'turno': turno_asignado,
            'turno_corto': turno_asignado.split(' ')[0],
            'puntos': puntos,
            'estado_tipo': 'exacto' if es_exacto else ('mixto' if es_mixto else 'conflicto')
        })

    # Generar calendario de rotación de 4 semanas a partir de la asignación actual
    lista_turnos_actual = [asignacion_actual_global[e] for e in empleados]
    calendario_roles = []
    for semana in range(1, 5):
        desplazamiento = (semana - 1) % len(empleados)
        turnos_rotados = lista_turnos_actual[-desplazamiento:] + lista_turnos_actual[:-desplazamiento]
        asig_semana = {empleados[i]: turnos_rotados[i] for i in range(len(empleados))}
        pts_sem, ex_sem = evaluar(asig_semana, preferencias_actuales)
        calendario_roles.append({
            'semana': f"Rol / Semana {semana}",
            'asignacion': asig_semana,
            'puntaje': pts_sem,
            'exactas': ex_sem
        })

    return {
        'detalles_empleados': detalles_empleados,
        'puntaje_final': puntaje_actual,
        'exactas_final': exactas_actual,
        'historial': historial_hc,
        'calendario_roles': calendario_roles,
        'contador_rol': contador_rol,
        'mensaje_accion': mensaje_accion
    }

# Inicializamos con el óptimo de Hill Climbing al arrancar
asignacion_optima_init, _, _, historial_inicial = hill_climbing_turnos()
asignacion_actual_global = asignacion_optima_init.copy()

# 5. Plantilla HTML Ultra 3D Cyberpunk con Control de Roles y Asignación Manual
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus 3D - Control y Rol de Turnos (Hill Climbing)</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
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

        /* Tarjetas 3D */
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

        .card-3d:hover {
            border-color: var(--neon-cyan);
            box-shadow:
                0 35px 70px rgba(0, 0, 0, 0.9),
                0 0 42px rgba(0, 243, 255, 0.32);
        }

        /* Panel de Comando: Rolar Turnos y Acciones Rápidas */
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

        .status-banner {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .rol-badge {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.05rem;
            font-weight: 900;
            padding: 8px 16px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            color: #030511;
            box-shadow: 0 0 18px rgba(0, 243, 255, 0.6);
        }

        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }

        .btn-3d {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            padding: 12px 20px;
            border-radius: 12px;
            cursor: pointer;
            border: 1px solid;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-rolar {
            background: linear-gradient(135deg, rgba(0, 243, 255, 0.22), rgba(0, 243, 255, 0.08));
            border-color: var(--neon-cyan);
            color: #fff;
            box-shadow: 0 6px 0 rgba(0, 140, 180, 0.7), 0 0 20px rgba(0, 243, 255, 0.35);
        }

        .btn-rolar:hover {
            transform: translateY(-2px);
            background: var(--neon-cyan);
            color: #030511;
            box-shadow: 0 8px 0 rgba(0, 140, 180, 0.9), 0 0 30px var(--neon-cyan);
        }

        .btn-rolar:active {
            transform: translateY(4px);
            box-shadow: 0 2px 0 rgba(0, 140, 180, 0.7);
        }

        .btn-optimizar {
            background: linear-gradient(135deg, rgba(0, 255, 157, 0.28), rgba(0, 255, 157, 0.1));
            border-color: var(--neon-green);
            color: #fff;
            box-shadow: 0 6px 0 rgba(0, 150, 90, 0.7), 0 0 22px rgba(0, 255, 157, 0.4);
        }

        .btn-optimizar:hover {
            transform: translateY(-2px);
            background: var(--neon-green);
            color: #030511;
            box-shadow: 0 8px 0 rgba(0, 150, 90, 0.9), 0 0 32px var(--neon-green);
        }

        .btn-azar {
            background: linear-gradient(135deg, rgba(255, 0, 127, 0.25), rgba(168, 85, 247, 0.15));
            border-color: var(--neon-pink);
            color: #fff;
            box-shadow: 0 6px 0 rgba(160, 0, 80, 0.7), 0 0 20px rgba(255, 0, 127, 0.35);
        }

        .btn-azar:hover {
            transform: translateY(-2px);
            background: var(--neon-pink);
            color: #fff;
            box-shadow: 0 8px 0 rgba(160, 0, 80, 0.9), 0 0 30px var(--neon-pink);
        }

        /* KPIs */
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
            font-size: 2.35rem;
            font-weight: 900;
            margin: 8px 0;
        }

        .c-cyan { color: var(--neon-cyan); text-shadow: 0 0 22px rgba(0, 243, 255, 0.7); }
        .c-green { color: var(--neon-green); text-shadow: 0 0 22px rgba(0, 255, 157, 0.7); }
        .c-gold { color: var(--neon-gold); text-shadow: 0 0 22px rgba(255, 190, 11, 0.7); }

        .energy-bar {
            height: 11px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.14);
            margin-top: 8px;
        }

        .energy-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-green));
            box-shadow: 0 0 18px var(--neon-green);
            border-radius: 999px;
            transition: width 0.5s ease;
        }

        /* Grid principal */
        .main-grid {
            display: grid;
            grid-template-columns: 1.2fr 1.05fr;
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

        .cam-controls { display: flex; gap: 8px; }

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

        /* Visor 3D */
        #nexus-3d-viewer {
            width: 100%;
            height: 460px;
            border-radius: 16px;
            background: radial-gradient(circle at center, rgba(20, 32, 80, 0.85), rgba(4, 6, 18, 0.96));
            border: 1px solid rgba(0, 243, 255, 0.35);
            box-shadow: inset 0 0 45px rgba(0, 243, 255, 0.16);
            position: relative;
            overflow: hidden;
            cursor: grab;
        }

        #nexus-3d-viewer:active { cursor: grabbing; }

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

        /* Tarjetas / Cubos Interactivos para Modificar Empleado y Turno */
        .cubes-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }

        @media (max-width: 600px) {
            .cubes-grid { grid-template-columns: 1fr; }
        }

        .emp-pod {
            background: rgba(11, 18, 42, 0.85);
            border: 1px solid rgba(0, 243, 255, 0.28);
            border-radius: 16px;
            padding: 16px 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            transition: transform 0.25s ease, border-color 0.25s ease;
        }

        .emp-pod:hover {
            transform: translateY(-4px);
            border-color: var(--neon-cyan);
            box-shadow: 0 12px 28px rgba(0, 243, 255, 0.22);
        }

        .cube-scene {
            width: 78px;
            height: 78px;
            perspective: 600px;
            margin: 8px 0 14px;
        }

        .cube-3d {
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            animation: rotateCube 8s infinite linear;
        }

        @keyframes rotateCube {
            0%   { transform: rotateX(-20deg) rotateY(0deg); }
            100% { transform: rotateX(-20deg) rotateY(360deg); }
        }

        .face {
            position: absolute;
            width: 78px;
            height: 78px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            border: 2px solid;
            backdrop-filter: blur(5px);
        }

        .match-exacto .face {
            background: rgba(0, 255, 157, 0.18);
            border-color: var(--neon-green);
            color: #ffffff;
            box-shadow: 0 0 20px rgba(0, 255, 157, 0.45), inset 0 0 12px rgba(0, 255, 157, 0.25);
        }

        .match-mixto .face {
            background: rgba(255, 190, 11, 0.18);
            border-color: var(--neon-gold);
            color: #ffffff;
            box-shadow: 0 0 20px rgba(255, 190, 11, 0.45), inset 0 0 12px rgba(255, 190, 11, 0.25);
        }

        .match-conflicto .face {
            background: rgba(255, 51, 102, 0.18);
            border-color: var(--neon-red);
            color: #ffffff;
            box-shadow: 0 0 20px rgba(255, 51, 102, 0.45), inset 0 0 12px rgba(255, 51, 102, 0.25);
        }

        .f-front  { transform: rotateY(  0deg) translateZ(39px); }
        .f-back   { transform: rotateY(180deg) translateZ(39px); }
        .f-right  { transform: rotateY( 90deg) translateZ(39px); }
        .f-left   { transform: rotateY(-90deg) translateZ(39px); }
        .f-top    { transform: rotateX( 90deg) translateZ(39px); }
        .f-bottom { transform: rotateX(-90deg) translateZ(39px); }

        .emp-name {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.15rem;
            color: #fff;
            letter-spacing: 1px;
        }

        /* Selectores Cyberpunk para modificar turno y preferencia */
        .control-group {
            width: 100%;
            margin-top: 6px;
            text-align: left;
        }

        .control-label {
            font-size: 0.75rem;
            font-family: 'Orbitron', sans-serif;
            color: #94a3b8;
            letter-spacing: 1px;
            text-transform: uppercase;
            display: block;
            margin-bottom: 3px;
        }

        .cyber-select {
            width: 100%;
            padding: 7px 10px;
            border-radius: 9px;
            background: rgba(5, 10, 28, 0.92);
            border: 1px solid rgba(0, 243, 255, 0.45);
            color: #eef6ff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.98rem;
            font-weight: 700;
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .cyber-select:focus, .cyber-select:hover {
            border-color: var(--neon-green);
            box-shadow: 0 0 14px rgba(0, 255, 157, 0.35);
        }

        .pts-pill {
            margin-top: 8px;
            padding: 4px 12px;
            border-radius: 20px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.76rem;
            font-weight: 800;
        }

        .pill-exacto {
            background: rgba(0, 255, 157, 0.18);
            color: var(--neon-green);
            border: 1px solid var(--neon-green);
        }

        .pill-mixto {
            background: rgba(255, 190, 11, 0.18);
            color: var(--neon-gold);
            border: 1px solid var(--neon-gold);
        }

        .pill-conflicto {
            background: rgba(255, 51, 102, 0.18);
            color: var(--neon-red);
            border: 1px solid var(--neon-red);
        }

        /* Tablas 3D */
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
            padding: 14px 14px;
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

        .assign-chip {
            display: inline-block;
            margin: 3px 4px;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.88rem;
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid rgba(0, 243, 255, 0.35);
        }

        .assign-chip strong {
            color: var(--neon-cyan);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
        }

        .row-winner {
            background: linear-gradient(90deg, rgba(0, 255, 157, 0.18), rgba(14, 22, 50, 0.95)) !important;
        }
        .row-winner td:first-child {
            border-left: 4px solid var(--neon-green);
        }
    </style>
</head>
<body>
    <canvas id="bg-canvas"></canvas>

    <div class="container">
        <header class="hero">
            <div class="cyber-badge">
                <span>⚡</span> IA • Rol de Turnos & Optimización Hill Climbing • WebGL 3D
            </div>
            <h1>Nexus 3D: Gestor y Rol de Turnos</h1>
            <p class="subtitle">Rola los turnos, asigna manualmente quién va a cada turno o deja que Hill Climbing optimice la satisfacción</p>
        </header>

        <!-- Barra de Control Interactiva para Rolar y Optimizar -->
        <div class="card-3d command-bar">
            <div class="status-banner">
                <span class="rol-badge" id="rol-counter">ROL #{{ estado_inicial.contador_rol }}</span>
                <div>
                    <div style="font-family:'Orbitron',sans-serif; font-size:0.95rem; color:var(--neon-green);" id="action-status">
                        {{ estado_inicial.mensaje_accion }}
                    </div>
                    <div style="font-size:0.9rem; color:#94a3b8;">
                        Al cambiar el turno de un empleado se intercambia automáticamente con quien lo ocupaba
                    </div>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn-3d btn-rolar" onclick="rolarTurnos(1)">
                    🔄 Rolar Turnos (+1)
                </button>
                <button class="btn-3d btn-rolar" onclick="rolarTurnos(-1)">
                    ⏪ Rolar Atrás (-1)
                </button>
                <button class="btn-3d btn-azar" onclick="rolarAzar()">
                    🎲 Rolar al Azar
                </button>
                <button class="btn-3d btn-optimizar" onclick="optimizarHillClimbing()">
                    🚀 Optimizar (Hill Climbing)
                </button>
            </div>
        </div>

        <!-- KPIs -->
        <section class="kpi-grid">
            <div class="card-3d tilt-card">
                <div class="kpi-label">Satisfacción del Rol Actual</div>
                <div class="kpi-val c-green">
                    <span id="kpi-puntaje">{{ estado_inicial.puntaje_final }}</span>
                    <span style="font-size:1.1rem; color:#94a3b8;">/ 360 PTS</span>
                </div>
                <div class="energy-bar">
                    <div class="energy-fill" id="kpi-barra" style="width: {{ (estado_inicial.puntaje_final / 360 * 100) | int }}%;"></div>
                </div>
            </div>

            <div class="card-3d tilt-card">
                <div class="kpi-label">Preferencias Exactas Cumplidas</div>
                <div class="kpi-val c-cyan" id="kpi-exactas">{{ estado_inicial.exactas_final }} de 4</div>
                <div style="color:#94a3b8; font-size:0.92rem;">
                    +100 pts turno exacto • +60 pts Mixto • +20 pts otro
                </div>
            </div>

            <div class="card-3d tilt-card">
                <div class="kpi-label">Pasos requeridos hacia el Óptimo</div>
                <div class="kpi-val c-gold" id="kpi-pasos">{{ estado_inicial.historial | length }} pasos</div>
                <div style="color:#94a3b8; font-size:0.92rem;">
                    Calculado en vivo desde la asignación actual
                </div>
            </div>
        </section>

        <!-- Escena 3D + Panel para Modificar Quién va a cada Turno -->
        <div class="main-grid">
            <div class="card-3d tilt-card">
                <div class="section-header">
                    <div class="section-title">
                        <span class="pulse-dot"></span> Gráfica 3D: Reloj de Turnos 24h & Barras de Satisfacción
                    </div>
                    <div class="cam-controls">
                        <button class="btn-cyber" onclick="setCameraView('iso')">Vista 3D</button>
                        <button class="btn-cyber" onclick="setCameraView('front')">Barras</button>
                        <button class="btn-cyber" onclick="setCameraView('top')">Reloj 24h</button>
                    </div>
                </div>
                <div id="nexus-3d-viewer">
                    <div class="viewer-overlay">
                        <div class="legend-pill">
                            <span style="color:var(--neon-green);">█ Barra 100 pts (Turno Ideal)</span>
                            <span style="color:var(--neon-gold);">█ Barra 60 pts (Mixto)</span>
                            <span style="color:var(--neon-red);">█ Barra 20 pts (Conflicto)</span>
                        </div>
                        <div class="legend-pill">Arrastra para rotar el Reloj 3D de Turnos</div>
                    </div>
                </div>
            </div>

            <!-- Control Individual por Empleado -->
            <div class="card-3d">
                <div class="section-header">
                    <div class="section-title">
                        <span class="pulse-dot" style="background:var(--neon-green); box-shadow:0 0 16px var(--neon-green);"></span>
                        Control Manual: ¿Quién va a cada Turno?
                    </div>
                </div>
                <div class="cubes-grid" id="empleados-pods-container">
                    <!-- Renderizado dinámico por JS -->
                </div>
            </div>
        </div>

        <!-- Calendario de Rotación de 4 Semanas / Roles -->
        <div class="card-3d" style="margin-bottom: 30px;">
            <div class="section-header">
                <div class="section-title">
                    <span class="pulse-dot" style="background:var(--neon-gold); box-shadow:0 0 16px var(--neon-gold);"></span>
                    Proyección de Rol de Turnos (Rotación de 4 Semanas)
                </div>
            </div>
            <table class="table-3d">
                <thead>
                    <tr>
                        <th>Ciclo</th>
                        <th>Ana</th>
                        <th>Luis</th>
                        <th>Carlos</th>
                        <th>Maria</th>
                        <th>Satisfacción del Rol</th>
                        <th>Aplicar</th>
                    </tr>
                </thead>
                <tbody id="tabla-calendario-body">
                </tbody>
            </table>
        </div>

        <!-- Historial Paso a Paso de Hill Climbing -->
        <div class="card-3d">
            <div class="section-header">
                <div class="section-title">
                    <span class="pulse-dot" style="background:var(--neon-pink); box-shadow:0 0 16px var(--neon-pink);"></span>
                    Ruta de Optimización Hill Climbing (Desde el estado actual)
                </div>
            </div>
            <table class="table-3d">
                <thead>
                    <tr>
                        <th>Paso</th>
                        <th>Operación (Swap)</th>
                        <th>Asignación de Turnos</th>
                        <th>Exactas</th>
                        <th>Satisfacción</th>
                    </tr>
                </thead>
                <tbody id="tabla-historial-body">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const TURNOS_DISPONIBLES = {{ turnos_disponibles | tojson }};
        const PREFS_DISPONIBLES = {{ preferencias_disponibles | tojson }};
        let estadoApp = {{ estado_inicial | tojson }};

        // 1. Efecto Tilt 3D en tarjetas
        document.querySelectorAll('.tilt-card').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const rotateY = ((x / rect.width) - 0.5) * 10;
                const rotateX = ((y / rect.height) - 0.5) * -10;
                card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(6px)`;
                card.style.setProperty('--glare-x', `${(x / rect.width) * 100}%`);
                card.style.setProperty('--glare-y', `${(y / rect.height) * 100}%`);
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
            });
        });

        // 2. Fondo 3D Synthwave
        const bgCanvas = document.getElementById('bg-canvas');
        const bgScene = new THREE.Scene();
        const bgCamera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        const bgRenderer = new THREE.WebGLRenderer({ canvas: bgCanvas, alpha: true, antialias: true });
        bgRenderer.setSize(window.innerWidth, window.innerHeight);

        const gridHelper = new THREE.GridHelper(160, 45, 0x00f3ff, 0xff007f);
        gridHelper.position.y = -18;
        gridHelper.material.transparent = true;
        gridHelper.material.opacity = 0.25;
        bgScene.add(gridHelper);

        const starsGeo = new THREE.BufferGeometry();
        const starPositions = new Float32Array(850 * 3);
        for (let i = 0; i < 850 * 3; i++) {
            starPositions[i] = (Math.random() - 0.5) * 160;
        }
        starsGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        const starsMat = new THREE.PointsMaterial({ color: 0x00f3ff, size: 0.38, transparent: true, opacity: 0.7 });
        const starField = new THREE.Points(starsGeo, starsMat);
        bgScene.add(starField);
        bgCamera.position.set(0, 2, 42);

        function animateBackground() {
            requestAnimationFrame(animateBackground);
            starField.rotation.y += 0.0009;
            gridHelper.position.z = (gridHelper.position.z + 0.08) % 3.5;
            bgRenderer.render(bgScene, bgCamera);
        }
        animateBackground();

        // 3. Gráfica 3D: Reloj de Turnos 24h + Barras 3D de Satisfacción Laboral
        const viewer = document.getElementById('nexus-3d-viewer');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(46, viewer.clientWidth / viewer.clientHeight, 0.1, 500);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(viewer.clientWidth, viewer.clientHeight);
        viewer.appendChild(renderer.domElement);

        // Iluminación para dar volumen real 3D a las barras y al reloj
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0x00f3ff, 1.1);
        dirLight.position.set(10, 18, 12);
        scene.add(dirLight);
        const pinkLight = new THREE.PointLight(0xff007f, 0.9, 30);
        pinkLight.position.set(-10, 8, -10);
        scene.add(pinkLight);

        const worldGroup = new THREE.Group();
        scene.add(worldGroup);

        const chartGroup = new THREE.Group();
        worldGroup.add(chartGroup);

        // Crear el Disco de Reloj de 24 Horas en la base con 4 sectores de Turno
        function crearTexturaReloj24h() {
            const canvas = document.createElement('canvas');
            canvas.width = 1024;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');
            const cx = 512, cy = 512, r = 470;

            // Fondo oscuro circular
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(6, 11, 30, 0.94)';
            ctx.fill();
            ctx.lineWidth = 8;
            ctx.strokeStyle = '#00f3ff';
            ctx.stroke();

            // 4 Cuadrantes de Turnos: Mañana, Tarde, Noche, Mixto
            const sectores = [
                { ini: -Math.PI / 4, fin: Math.PI / 4, color: 'rgba(255, 190, 11, 0.22)', borde: '#ffbe0b', titulo: '☀️ MAÑANA (06-14h)' },
                { ini: Math.PI / 4, fin: 3 * Math.PI / 4, color: 'rgba(0, 243, 255, 0.22)', borde: '#00f3ff', titulo: '🌅 TARDE (14-22h)' },
                { ini: 3 * Math.PI / 4, fin: 5 * Math.PI / 4, color: 'rgba(168, 85, 247, 0.25)', borde: '#a855f7', titulo: '🌙 NOCHE (22-06h)' },
                { ini: 5 * Math.PI / 4, fin: 7 * Math.PI / 4, color: 'rgba(255, 0, 127, 0.22)', borde: '#ff007f', titulo: '⚡ MIXTO (ROTATIVO)' }
            ];

            sectores.forEach(s => {
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.arc(cx, cy, r - 12, s.ini, s.fin);
                ctx.closePath();
                ctx.fillStyle = s.color;
                ctx.fill();
                ctx.lineWidth = 4;
                ctx.strokeStyle = s.borde;
                ctx.stroke();

                // Etiqueta del sector en el borde del reloj
                const midAngle = (s.ini + s.fin) / 2;
                const tx = cx + Math.cos(midAngle) * 365;
                const ty = cy + Math.sin(midAngle) * 365;
                ctx.save();
                ctx.translate(tx, ty);
                ctx.font = 'bold 28px Orbitron, sans-serif';
                ctx.fillStyle = '#ffffff';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(s.titulo, 0, 0);
                ctx.restore();
            });

            // Marcas de 24 horas alrededor del reloj
            for (let h = 0; h < 24; h++) {
                const ang = (h / 24) * Math.PI * 2 - Math.PI / 2;
                const x1 = cx + Math.cos(ang) * (r - 35);
                const y1 = cy + Math.sin(ang) * (r - 35);
                const x2 = cx + Math.cos(ang) * (r - 10);
                const y2 = cy + Math.sin(ang) * (r - 10);
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.lineWidth = h % 6 === 0 ? 5 : 2;
                ctx.strokeStyle = h % 6 === 0 ? '#00ff9d' : 'rgba(255,255,255,0.4)';
                ctx.stroke();
            }

            // Círculo central del reloj
            ctx.beginPath();
            ctx.arc(cx, cy, 85, 0, Math.PI * 2);
            ctx.fillStyle = '#050a1f';
            ctx.fill();
            ctx.lineWidth = 5;
            ctx.strokeStyle = '#00ff9d';
            ctx.stroke();

            ctx.font = 'bold 26px Orbitron, sans-serif';
            ctx.fillStyle = '#00ff9d';
            ctx.textAlign = 'center';
            ctx.fillText('ROL 24H', cx, cy + 8);

            return new THREE.CanvasTexture(canvas);
        }

        const clockGeo = new THREE.CylinderGeometry(7.2, 7.2, 0.35, 64);
        const clockMat = [
            new THREE.MeshBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.45 }),
            new THREE.MeshBasicMaterial({ map: crearTexturaReloj24h() }),
            new THREE.MeshBasicMaterial({ color: 0x050816 })
        ];
        const clockBase = new THREE.Mesh(clockGeo, clockMat);
        clockBase.position.y = -2.4;
        worldGroup.add(clockBase);

        // Manecilla / Aguja 3D giratoria del reloj de turnos
        const handGroup = new THREE.Group();
        handGroup.position.y = -2.15;
        const handGeo = new THREE.BoxGeometry(4.8, 0.12, 0.18);
        handGeo.translate(2.4, 0, 0);
        const handMat = new THREE.MeshBasicMaterial({ color: 0x00ff9d });
        const clockHand = new THREE.Mesh(handGeo, handMat);
        handGroup.add(clockHand);
        worldGroup.add(handGroup);

        let animatedBars = [];

        function crearEtiqueta3D(linea1, linea2, colorHex) {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 170;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = 'rgba(4, 9, 26, 0.92)';
            ctx.strokeStyle = colorHex;
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.roundRect(14, 14, 484, 142, 24);
            ctx.fill();
            ctx.stroke();

            ctx.font = 'bold 38px Orbitron, sans-serif';
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.fillText(linea1, 256, 68);

            ctx.font = 'bold 30px Rajdhani, sans-serif';
            ctx.fillStyle = colorHex;
            ctx.fillText(linea2, 256, 120);

            const tex = new THREE.CanvasTexture(canvas);
            const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
            const sprite = new THREE.Sprite(mat);
            sprite.scale.set(4.1, 1.35, 1);
            return sprite;
        }

        // Posición fija en el reloj 24h para cada uno de los 4 turnos
        const POSICION_POR_TURNO = {
            'Mañana (Matutino)':  { angle: 0,               icono: '☀️ MAÑANA' },
            'Tarde (Vespertino)': { angle: Math.PI / 2,     icono: '🌅 TARDE' },
            'Noche (Nocturno)':   { angle: Math.PI,         icono: '🌙 NOCHE' },
            'Mixto':              { angle: 3 * Math.PI / 2, icono: '⚡ MIXTO' }
        };

        function reconstruirEscena3D(detalles) {
            while (chartGroup.children.length > 0) {
                chartGroup.remove(chartGroup.children[0]);
            }
            animatedBars = [];

            const radius = 4.25;
            const maxBarHeight = 5.2; // 100 pts = 5.2 unidades de altura 3D

            detalles.forEach((emp) => {
                const infoTurno = POSICION_POR_TURNO[emp.turno] || { angle: 0, icono: emp.turno_corto };
                const x = Math.cos(infoTurno.angle) * radius;
                const z = Math.sin(infoTurno.angle) * radius;

                let colorHex = '#00ff9d';
                let colorNum = 0x00ff9d;
                if (emp.estado_tipo === 'mixto') {
                    colorHex = '#ffbe0b';
                    colorNum = 0xffbe0b;
                } else if (emp.estado_tipo === 'conflicto') {
                    colorHex = '#ff3366';
                    colorNum = 0xff3366;
                }

                // 1. Jaula Wireframe 3D de Meta Máxima (100 pts)
                const goalGeo = new THREE.BoxGeometry(1.45, maxBarHeight, 1.45);
                const goalEdges = new THREE.EdgesGeometry(goalGeo);
                const goalLine = new THREE.LineSegments(
                    goalEdges,
                    new THREE.LineBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.28 })
                );
                goalLine.position.set(x, -2.2 + maxBarHeight / 2, z);
                chartGroup.add(goalLine);

                // 2. Barra / Columna 3D de Satisfacción Real del Empleado en ese Turno
                const targetHeight = Math.max(0.6, (emp.puntos / 100) * maxBarHeight);
                const barGeo = new THREE.CylinderGeometry(0.68, 0.68, 1, 6); // Prisma hexagonal 3D
                const barMat = new THREE.MeshPhongMaterial({
                    color: colorNum,
                    emissive: colorNum,
                    emissiveIntensity: 0.35,
                    shininess: 90,
                    transparent: true,
                    opacity: 0.9
                });
                const barMesh = new THREE.Mesh(barGeo, barMat);
                barMesh.position.set(x, -2.2 + 0.05, z);
                barMesh.scale.y = 0.1;
                chartGroup.add(barMesh);

                // Anillo de energía en la base de la columna
                const pedestalGeo = new THREE.RingGeometry(0.8, 1.05, 32);
                const pedestalMat = new THREE.MeshBasicMaterial({ color: colorNum, side: THREE.DoubleSide });
                const pedestal = new THREE.Mesh(pedestalGeo, pedestalMat);
                pedestal.rotation.x = Math.PI / 2;
                pedestal.position.set(x, -2.18, z);
                chartGroup.add(pedestal);

                // 3. Etiqueta 3D flotante encima de la barra con Empleado + Turno + Puntos
                const label = crearEtiqueta3D(
                    `👤 ${emp.nombre} → ${emp.turno_corto}`,
                    `Pref: ${emp.preferencia} | +${emp.puntos} PTS`,
                    colorHex
                );
                label.position.set(x, -2.2 + targetHeight + 1.35, z);
                chartGroup.add(label);

                animatedBars.push({ barMesh, targetHeight, baseY: -2.2, currentH: 0.1 });
            });
        }

        camera.position.set(0, 8.8, 15.8);
        camera.lookAt(0, 0.3, 0);

        let dragging = false, px = 0, py = 0;
        viewer.addEventListener('mousedown', e => { dragging = true; px = e.clientX; py = e.clientY; });
        window.addEventListener('mouseup', () => { dragging = false; });
        window.addEventListener('mousemove', e => {
            if (!dragging) return;
            worldGroup.rotation.y += (e.clientX - px) * 0.01;
            worldGroup.rotation.x = Math.max(-0.45, Math.min(0.65, worldGroup.rotation.x + (e.clientY - py) * 0.008));
            px = e.clientX;
            py = e.clientY;
        });

        window.setCameraView = function(mode) {
            if (mode === 'iso') {
                worldGroup.rotation.set(0, 0, 0);
                camera.position.set(0, 8.8, 15.8);
            } else if (mode === 'front') {
                worldGroup.rotation.set(0, 0, 0);
                camera.position.set(0, 3.2, 16.5);
            } else if (mode === 'top') {
                worldGroup.rotation.set(0, 0, 0);
                camera.position.set(0, 17.5, 2.5);
            }
            camera.lookAt(0, 0.3, 0);
        };

        window.triggerPulse = function() {
            animatedBars.forEach(b => { b.currentH = 0.15; });
        };

        function animateNexus() {
            requestAnimationFrame(animateNexus);
            if (!dragging) {
                worldGroup.rotation.y += 0.0035;
            }
            // Aguja del reloj 24h girando continuamente
            handGroup.rotation.y -= 0.015;

            // Animación suave de crecimiento de las barras 3D de satisfacción
            animatedBars.forEach(b => {
                b.currentH += (b.targetHeight - b.currentH) * 0.1;
                b.barMesh.scale.y = b.currentH;
                b.barMesh.position.y = b.baseY + b.currentH / 2;
                b.barMesh.rotation.y += 0.01;
            });

            renderer.render(scene, camera);
        }
        animateNexus();

        // 4. Renderizar interfaz completa cada vez que se rolan o modifican turnos
        function renderizarUI(data) {
            estadoApp = data;
            document.getElementById('rol-counter').textContent = `ROL #${data.contador_rol}`;
            document.getElementById('action-status').textContent = data.mensaje_accion;
            document.getElementById('kpi-puntaje').textContent = data.puntaje_final;
            document.getElementById('kpi-barra').style.width = `${Math.min(100, Math.round(data.puntaje_final / 360 * 100))}%`;
            document.getElementById('kpi-exactas').textContent = `${data.exactas_final} de 4`;
            document.getElementById('kpi-pasos').textContent = `${data.historial.length} pasos`;

            // Renderizar pods de empleados con selectores interactivos
            const podsContainer = document.getElementById('empleados-pods-container');
            podsContainer.innerHTML = data.detalles_empleados.map(emp => {
                const opcionesTurno = TURNOS_DISPONIBLES.map(t =>
                    `<option value="${t}" ${t === emp.turno ? 'selected' : ''}>${t}</option>`
                ).join('');

                const opcionesPref = PREFS_DISPONIBLES.map(p =>
                    `<option value="${p}" ${p === emp.preferencia ? 'selected' : ''}>${p}</option>`
                ).join('');

                const etiquetaEstado = emp.estado_tipo === 'exacto'
                    ? `★ PREFERENCIA EXACTA (+${emp.puntos})`
                    : (emp.estado_tipo === 'mixto' ? `⚡ TURNO MIXTO (+${emp.puntos})` : `⚠ NO PREFERIDO (+${emp.puntos})`);

                return `
                    <div class="emp-pod">
                        <div class="emp-name">${emp.nombre}</div>
                        <div class="cube-scene">
                            <div class="cube-3d match-${emp.estado_tipo}">
                                <div class="face f-front">
                                    <span style="font-size:1.25rem;">${emp.nombre.slice(0,3).toUpperCase()}</span>
                                    <span style="font-size:0.68rem;">+${emp.puntos} PTS</span>
                                </div>
                                <div class="face f-back">
                                    <span style="font-size:0.7rem;">TURNO</span>
                                    <span style="font-size:0.8rem;">${emp.turno_corto}</span>
                                </div>
                                <div class="face f-right">
                                    <span style="font-size:0.68rem;">PREF</span>
                                    <span style="font-size:0.78rem;">${emp.preferencia.slice(0,6)}</span>
                                </div>
                                <div class="face f-left">
                                    <span style="font-size:1rem;">+${emp.puntos}</span>
                                </div>
                                <div class="face f-top"><span>★</span></div>
                                <div class="face f-bottom"><span>3D</span></div>
                            </div>
                        </div>

                        <div class="control-group">
                            <label class="control-label">Turno Asignado (Swap auto):</label>
                            <select class="cyber-select" onchange="cambiarTurnoEmpleado('${emp.nombre}', this.value)">
                                ${opcionesTurno}
                            </select>
                        </div>

                        <div class="control-group">
                            <label class="control-label">Preferencia del Empleado:</label>
                            <select class="cyber-select" onchange="cambiarPreferenciaEmpleado('${emp.nombre}', this.value)">
                                ${opcionesPref}
                            </select>
                        </div>

                        <div class="pts-pill pill-${emp.estado_tipo}">
                            ${etiquetaEstado}
                        </div>
                    </div>
                `;
            }).join('');

            // Renderizar tabla de rotación de 4 semanas
            const calBody = document.getElementById('tabla-calendario-body');
            calBody.innerHTML = data.calendario_roles.map((sem, idx) => `
                <tr class="${idx === 0 ? 'row-winner' : ''}">
                    <td style="font-family:'Orbitron',sans-serif; color:var(--neon-cyan);">${sem.semana} ${idx === 0 ? '(ACTUAL)' : ''}</td>
                    <td>${sem.asignacion['Ana']}</td>
                    <td>${sem.asignacion['Luis']}</td>
                    <td>${sem.asignacion['Carlos']}</td>
                    <td>${sem.asignacion['Maria']}</td>
                    <td style="font-family:'Orbitron',sans-serif; color:var(--neon-green);">${sem.puntaje} pts (${sem.exactas}/4)</td>
                    <td>
                        <button class="btn-cyber" onclick="rolarTurnos(${idx})">Cargar este Rol</button>
                    </td>
                </tr>
            `).join('');

            // Renderizar historial Hill Climbing
            const histBody = document.getElementById('tabla-historial-body');
            histBody.innerHTML = data.historial.map((paso, idx) => {
                const chips = Object.entries(paso.asignacion).map(([e, t]) =>
                    `<span class="assign-chip"><strong>${e}:</strong> ${t}</span>`
                ).join('');
                const isLast = idx === data.historial.length - 1;
                return `
                    <tr class="${isLast ? 'row-winner' : ''}">
                        <td><span class="step-num">${idx + 1}</span></td>
                        <td style="color:var(--neon-gold); font-family:'Orbitron',sans-serif; font-size:0.88rem;">${paso.movimiento}</td>
                        <td>${chips}</td>
                        <td style="font-family:'Orbitron',sans-serif; color:var(--neon-cyan);">${paso.exactas} / 4</td>
                        <td style="font-family:'Orbitron',sans-serif; font-size:1.18rem; color:var(--neon-green);">${paso.puntaje} pts</td>
                    </tr>
                `;
            }).join('');

            reconstruirEscena3D(data.detalles_empleados);
            triggerPulse();
        }

        // 5. Funciones AJAX para rolar, cambiar turno manualmente y optimizar
        async function enviarAccion(url, payload) {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            renderizarUI(data);
        }

        window.rolarTurnos = function(pasos) {
            enviarAccion('/api/rolar', { pasos });
        };

        window.rolarAzar = function() {
            enviarAccion('/api/azar', {});
        };

        window.cambiarTurnoEmpleado = function(empleado, nuevo_turno) {
            enviarAccion('/api/asignar_turno', { empleado, nuevo_turno });
        };

        window.cambiarPreferenciaEmpleado = function(empleado, nueva_preferencia) {
            enviarAccion('/api/cambiar_preferencia', { empleado, nueva_preferencia });
        };

        window.optimizarHillClimbing = function() {
            enviarAccion('/api/optimizar', {});
        };

        // Inicializar al cargar
        renderizarUI(estadoApp);

        window.addEventListener('resize', () => {
            bgCamera.aspect = window.innerWidth / window.innerHeight;
            bgCamera.updateProjectionMatrix();
            bgRenderer.setSize(window.innerWidth, window.innerHeight);

            camera.aspect = viewer.clientWidth / viewer.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(viewer.clientWidth, viewer.clientHeight);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    estado_inicial = armar_respuesta_estado(
        historial_custom=historial_inicial,
        mensaje_accion="Asignación Óptima Inicial (Hill Climbing)"
    )
    return render_template_string(
        HTML_TEMPLATE,
        estado_inicial=estado_inicial,
        turnos_disponibles=turnos_disponibles,
        preferencias_disponibles=preferencias_disponibles
    )

@app.route('/api/rolar', methods=['POST'])
def api_rolar():
    global asignacion_actual_global, contador_rol
    datos = request.get_json() or {}
    pasos = int(datos.get('pasos', 1))
    if pasos == 0:
        return jsonify(armar_respuesta_estado(mensaje_accion="Rol actual mantenido"))

    lista_turnos = [asignacion_actual_global[e] for e in empleados]
    desplazamiento = pasos % len(empleados)
    turnos_rotados = lista_turnos[-desplazamiento:] + lista_turnos[:-desplazamiento]
    asignacion_actual_global = {empleados[i]: turnos_rotados[i] for i in range(len(empleados))}
    contador_rol += 1

    sentido = f"+{pasos}" if pasos > 0 else str(pasos)
    return jsonify(armar_respuesta_estado(
        mensaje_accion=f"Turnos rolados ({sentido} posición): cada empleado pasó al siguiente turno"
    ))

@app.route('/api/azar', methods=['POST'])
def api_azar():
    global asignacion_actual_global, contador_rol
    copia_turnos = turnos_disponibles.copy()
    random.shuffle(copia_turnos)
    asignacion_actual_global = {empleados[i]: copia_turnos[i] for i in range(len(empleados))}
    contador_rol += 1
    return jsonify(armar_respuesta_estado(
        mensaje_accion="Asignación rolada al azar • Presiona 'Optimizar (Hill Climbing)' para resolverla"
    ))

@app.route('/api/asignar_turno', methods=['POST'])
def api_asignar_turno():
    global asignacion_actual_global
    datos = request.get_json() or {}
    emp_objetivo = datos.get('empleado')
    nuevo_turno = datos.get('nuevo_turno')

    if emp_objetivo in asignacion_actual_global and nuevo_turno in turnos_disponibles:
        turno_anterior = asignacion_actual_global[emp_objetivo]
        # Buscar quién tenía ese nuevo_turno para intercambiarlo (swap) y no repetir turno
        emp_con_ese_turno = None
        for emp, t in asignacion_actual_global.items():
            if t == nuevo_turno and emp != emp_objetivo:
                emp_con_ese_turno = emp
                break

        asignacion_actual_global[emp_objetivo] = nuevo_turno
        if emp_con_ese_turno:
            asignacion_actual_global[emp_con_ese_turno] = turno_anterior
            msg = f"Cambio manual: {emp_objetivo} → {nuevo_turno} (intercambió turno con {emp_con_ese_turno})"
        else:
            msg = f"Cambio manual: {emp_objetivo} → {nuevo_turno}"

        return jsonify(armar_respuesta_estado(mensaje_accion=msg))

    return jsonify(armar_respuesta_estado(mensaje_accion="Sin cambios"))

@app.route('/api/cambiar_preferencia', methods=['POST'])
def api_cambiar_preferencia():
    global preferencias_actuales
    datos = request.get_json() or {}
    emp = datos.get('empleado')
    nueva_pref = datos.get('nueva_preferencia')

    if emp in preferencias_actuales and nueva_pref in preferencias_disponibles:
        preferencias_actuales[emp] = nueva_pref
        return jsonify(armar_respuesta_estado(
            mensaje_accion=f"Preferencia actualizada: {emp} ahora prefiere turno {nueva_pref}"
        ))

    return jsonify(armar_respuesta_estado(mensaje_accion="Sin cambios"))

@app.route('/api/optimizar', methods=['POST'])
def api_optimizar():
    global asignacion_actual_global
    estado_optimo, _, _, historial_hc = hill_climbing_turnos(asignacion_actual_global, preferencias_actuales)
    asignacion_actual_global = estado_optimo.copy()
    return jsonify(armar_respuesta_estado(
        historial_custom=historial_hc,
        mensaje_accion=f"¡Optimizado con Hill Climbing en {len(historial_hc)} paso(s) hasta máxima satisfacción!"
    ))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
