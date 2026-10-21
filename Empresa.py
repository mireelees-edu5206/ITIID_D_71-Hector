from flask import Flask, render_template_string

app = Flask(__name__)

# 1. Definición de los datos
productos = {
    'A': {'costo': 200, 'beneficio': 30},
    'B': {'costo': 300, 'beneficio': 50},
    'C': {'costo': 400, 'beneficio': 70},
    'D': {'costo': 250, 'beneficio': 40},
    'E': {'costo': 350, 'beneficio': 60}
}
PRESUPUESTO = 1000

# 2. Función de evaluación (Fitness)
def evaluar(estado):
    costo_total = sum(productos[p]['costo'] for p in estado if estado[p] == 1)
    beneficio_total = sum(productos[p]['beneficio'] for p in estado if estado[p] == 1)
    
    # Si supera el presupuesto, retornamos beneficio 0 para descartar este estado
    if costo_total > PRESUPUESTO:
        return 0, costo_total 
    
    return beneficio_total, costo_total

# 3. Generación de vecinos
def obtener_vecinos(estado):
    vecinos = []
    # Generamos vecinos cambiando el estado de un solo producto (agregarlo o quitarlo)
    for p in estado:
        vecino = estado.copy()
        vecino[p] = 1 - vecino[p]  # Cambia 0 a 1 o de 1 a 0
        vecinos.append(vecino)
    return vecinos

# 4. Algoritmo Hill Climbing
def hill_climbing():
    # Estado inicial: ningún producto seleccionado (todo en 0)
    estado_actual = {p: 0 for p in productos}
    beneficio_actual, costo_actual = evaluar(estado_actual)
    
    historial = []

    while True:
        historial.append({
            'estado': [p for p, v in estado_actual.items() if v == 1],
            'beneficio': beneficio_actual,
            'costo': costo_actual
        })

        vecinos = obtener_vecinos(estado_actual)
        mejor_vecino = None
        mejor_beneficio_vecino = -1
        mejor_costo_vecino = 0

        # Evaluamos todos los vecinos y nos quedamos con el que dé mayor beneficio
        for vecino in vecinos:
            beneficio_vecino, costo_vecino = evaluar(vecino)
            if beneficio_vecino > mejor_beneficio_vecino and costo_vecino <= PRESUPUESTO:
                mejor_beneficio_vecino = beneficio_vecino
                mejor_vecino = vecino
                mejor_costo_vecino = costo_vecino

        # Si el mejor vecino mejora el estado actual, nos movemos a él
        if mejor_beneficio_vecino > beneficio_actual:
            estado_actual = mejor_vecino
            beneficio_actual = mejor_beneficio_vecino
            costo_actual = mejor_costo_vecino
        else:
            # Si no hay mejora, hemos llegado al máximo local/global
            break
            
    return estado_actual, beneficio_actual, costo_actual, historial

# 5. Interfaz web (Plantilla HTML incrustada)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hill Climbing 3D - Optimización de Presupuesto</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {
            --neon-cyan: #00f3ff;
            --neon-pink: #ff007f;
            --neon-purple: #9d00ff;
            --neon-green: #00ff88;
            --neon-gold: #ffcc00;
            --bg-dark: #050714;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Rajdhani', sans-serif;
            background: radial-gradient(circle at 50% 0%, #131936 0%, #050714 70%);
            color: #e6f1ff;
            min-height: 100vh;
            overflow-x: hidden;
            perspective: 1400px;
        }

        #bg-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            position: relative;
            z-index: 2;
            max-width: 1320px;
            margin: 0 auto;
            padding: 35px 25px 70px;
            transform-style: preserve-3d;
        }

        .hero-header {
            text-align: center;
            margin-bottom: 40px;
            transform-style: preserve-3d;
            animation: floatHeader 5s ease-in-out infinite;
        }

        @keyframes floatHeader {
            0%, 100% { transform: translateY(0px) rotateX(4deg); }
            50% { transform: translateY(-8px) rotateX(-2deg); }
        }

        .badge-3d {
            display: inline-block;
            padding: 6px 18px;
            border-radius: 30px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.75rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
            margin-bottom: 14px;
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(2rem, 4vw, 3.4rem);
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 3px;
            background: linear-gradient(90deg, #ffffff, var(--neon-cyan), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 30px rgba(0, 243, 255, 0.35);
        }

        .subtitle {
            color: #94a3b8;
            font-size: 1.15rem;
            letter-spacing: 1px;
            margin-top: 6px;
        }

        /* KPI 3D Stat Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 28px;
            margin-bottom: 38px;
            transform-style: preserve-3d;
        }

        .card-3d {
            position: relative;
            background: linear-gradient(135deg, rgba(20, 28, 58, 0.82), rgba(10, 14, 32, 0.92));
            border: 1px solid rgba(0, 243, 255, 0.28);
            border-radius: 20px;
            padding: 28px;
            backdrop-filter: blur(16px);
            transform-style: preserve-3d;
            transition: transform 0.18s ease-out, box-shadow 0.3s ease, border-color 0.3s ease;
            box-shadow:
                0 25px 50px rgba(0, 0, 0, 0.75),
                0 0 25px rgba(0, 243, 255, 0.12),
                inset 0 1px 1px rgba(255, 255, 255, 0.2);
        }

        .card-3d::before {
            content: '';
            position: absolute;
            inset: -2px;
            border-radius: 22px;
            background: linear-gradient(135deg, var(--neon-cyan), transparent 40%, var(--neon-pink));
            z-index: -1;
            opacity: 0.45;
            filter: blur(8px);
        }

        .card-3d:hover {
            border-color: var(--neon-cyan);
            box-shadow:
                0 35px 65px rgba(0, 0, 0, 0.85),
                0 0 40px rgba(0, 243, 255, 0.35);
        }

        .kpi-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #94a3b8;
            transform: translateZ(25px);
        }

        .kpi-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.7rem;
            font-weight: 900;
            margin: 12px 0;
            transform: translateZ(45px);
            text-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
        }

        .kpi-cyan { color: var(--neon-cyan); text-shadow: 0 0 25px rgba(0, 243, 255, 0.7); }
        .kpi-green { color: var(--neon-green); text-shadow: 0 0 25px rgba(0, 255, 136, 0.7); }
        .kpi-gold { color: var(--neon-gold); text-shadow: 0 0 25px rgba(255, 204, 0, 0.7); }

        .progress-3d {
            height: 12px;
            background: rgba(255, 255, 255, 0.07);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.12);
            transform: translateZ(30px);
            margin-top: 10px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-green));
            box-shadow: 0 0 18px var(--neon-cyan);
            border-radius: 10px;
            transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
        }

        /* Layout principal 2 columnas */
        .main-grid {
            display: grid;
            grid-template-columns: 1.25fr 1fr;
            gap: 30px;
            margin-bottom: 38px;
        }

        @media (max-width: 980px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        .section-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.2rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #fff;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 12px;
            transform: translateZ(30px);
        }

        .section-title span.dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--neon-cyan);
            box-shadow: 0 0 14px var(--neon-cyan);
        }

        /* Visor 3D Interactivo de la Montaña Hill Climbing */
        #hill-3d-viewer {
            width: 100%;
            height: 390px;
            border-radius: 16px;
            background: radial-gradient(circle at center, rgba(16, 26, 66, 0.9), rgba(5, 7, 20, 0.95));
            border: 1px solid rgba(0, 243, 255, 0.35);
            box-shadow: inset 0 0 40px rgba(0, 243, 255, 0.15);
            position: relative;
            overflow: hidden;
            cursor: grab;
        }

        #hill-3d-viewer:active { cursor: grabbing; }

        .viewer-hint {
            position: absolute;
            bottom: 12px;
            right: 16px;
            font-size: 0.85rem;
            color: rgba(230, 241, 255, 0.7);
            background: rgba(5, 7, 20, 0.75);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(0, 243, 255, 0.3);
            pointer-events: none;
        }

        /* Cubos 3D de Productos */
        .products-showcase {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
            gap: 22px;
            padding: 10px 4px;
            perspective: 900px;
        }

        .product-scene {
            height: 170px;
            perspective: 700px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .cube-wrapper {
            width: 90px;
            height: 90px;
            position: relative;
            transform-style: preserve-3d;
            transform: rotateX(-22deg) rotateY(32deg);
            animation: spinCube 9s infinite linear;
        }

        .product-scene:hover .cube-wrapper {
            animation-play-state: paused;
            transform: rotateX(-15deg) rotateY(45deg) scale(1.15);
        }

        @keyframes spinCube {
            0% { transform: rotateX(-22deg) rotateY(0deg); }
            100% { transform: rotateX(-22deg) rotateY(360deg); }
        }

        .cube-face {
            position: absolute;
            width: 90px;
            height: 90px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            border: 2px solid;
            backdrop-filter: blur(6px);
        }

        .selected-cube .cube-face {
            background: rgba(0, 255, 136, 0.16);
            border-color: var(--neon-green);
            color: #fff;
            box-shadow: 0 0 25px rgba(0, 255, 136, 0.45), inset 0 0 15px rgba(0, 255, 136, 0.25);
        }

        .unselected-cube .cube-face {
            background: rgba(255, 0, 127, 0.1);
            border-color: rgba(255, 0, 127, 0.45);
            color: #94a3b8;
            box-shadow: inset 0 0 12px rgba(255, 0, 127, 0.2);
        }

        .face-front  { transform: rotateY(  0deg) translateZ(45px); }
        .face-back   { transform: rotateY(180deg) translateZ(45px); }
        .face-right  { transform: rotateY( 90deg) translateZ(45px); }
        .face-left   { transform: rotateY(-90deg) translateZ(45px); }
        .face-top    { transform: rotateX( 90deg) translateZ(45px); }
        .face-bottom { transform: rotateX(-90deg) translateZ(45px); }

        .cube-letter { font-size: 1.7rem; }
        .cube-meta { font-size: 0.72rem; font-family: 'Rajdhani', sans-serif; font-weight: 700; }

        .product-status {
            margin-top: 22px;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 3px 12px;
            border-radius: 12px;
            text-transform: uppercase;
        }

        .status-on {
            background: rgba(0, 255, 136, 0.18);
            color: var(--neon-green);
            border: 1px solid var(--neon-green);
            box-shadow: 0 0 12px rgba(0, 255, 136, 0.4);
        }

        .status-off {
            background: rgba(255, 0, 127, 0.12);
            color: #ff6b9d;
            border: 1px solid rgba(255, 0, 127, 0.4);
        }

        /* Tabla 3D con filas flotantes */
        .table-3d {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 14px;
            transform-style: preserve-3d;
        }

        .table-3d thead th {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--neon-cyan);
            padding: 12px 18px;
            text-align: center;
            border-bottom: 1px solid rgba(0, 243, 255, 0.3);
        }

        .table-3d tbody tr {
            background: linear-gradient(90deg, rgba(22, 32, 68, 0.85), rgba(14, 21, 48, 0.9));
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
        }

        .table-3d tbody tr:hover {
            transform: translateZ(28px) scale(1.015);
            box-shadow: 0 18px 35px rgba(0, 243, 255, 0.25);
        }

        .table-3d td {
            padding: 16px 18px;
            text-align: center;
            font-size: 1.1rem;
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

        .step-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            color: #050714;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        }

        .chip-item {
            display: inline-block;
            padding: 4px 12px;
            margin: 2px;
            border-radius: 8px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            background: rgba(0, 243, 255, 0.15);
            border: 1px solid var(--neon-cyan);
            color: #fff;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        }

        .final-row td:first-child {
            border-left: 4px solid var(--neon-green);
        }
        .final-row {
            background: linear-gradient(90deg, rgba(0, 255, 136, 0.16), rgba(14, 21, 48, 0.92)) !important;
        }
    </style>
</head>
<body>
    <canvas id="bg-canvas"></canvas>

    <div class="container">
        <header class="hero-header">
            <div class="badge-3d">IA • Búsqueda Local Heurística • WebGL 3D</div>
            <h1>Hill Climbing 3D Optimizer</h1>
            <p class="subtitle">Simulación tridimensional de optimización de presupuesto máximo ($1,000)</p>
        </header>

        <!-- KPIs 3D -->
        <section class="kpi-grid">
            <div class="card-3d tilt-card">
                <div class="kpi-title">Productos Óptimos Seleccionados</div>
                <div class="kpi-value kpi-cyan">
                    {{ seleccionados | join(' + ') if seleccionados else 'Ninguno' }}
                </div>
                <div style="color:#94a3b8; font-size:0.95rem;">
                    {{ seleccionados | length }} de {{ productos | length }} activos en cartera
                </div>
            </div>

            <div class="card-3d tilt-card">
                <div class="kpi-title">Beneficio Máximo Alcanzado</div>
                <div class="kpi-value kpi-green">+{{ beneficio }} PTS</div>
                <div class="progress-3d">
                    <div class="progress-bar" style="width: 100%;"></div>
                </div>
                <div style="color:#94a3b8; font-size:0.95rem; margin-top:8px;">
                    Óptimo local/global alcanzado en {{ historial | length }} pasos
                </div>
            </div>

            <div class="card-3d tilt-card">
                <div class="kpi-title">Presupuesto Utilizado</div>
                <div class="kpi-value kpi-gold">${{ costo }} <span style="font-size:1.2rem; color:#94a3b8;">/ $1000</span></div>
                <div class="progress-3d">
                    <div class="progress-bar" style="width: {{ (costo / 1000 * 100) | int }}%; background: linear-gradient(90deg, var(--neon-gold), var(--neon-pink));"></div>
                </div>
                <div style="color:#94a3b8; font-size:0.95rem; margin-top:8px;">
                    Capital restante disponible: ${{ 1000 - costo }}
                </div>
            </div>
        </section>

        <!-- Escena 3D de Ascenso + Cubos Holográficos -->
        <div class="main-grid">
            <div class="card-3d tilt-card">
                <div class="section-title">
                    <span class="dot"></span> Paisaje 3D de Ascenso (Hill Climbing)
                </div>
                <div id="hill-3d-viewer">
                    <div class="viewer-hint">Arrastra con el mouse para rotar en 3D</div>
                </div>
            </div>

            <div class="card-3d tilt-card">
                <div class="section-title">
                    <span class="dot" style="background: var(--neon-green); box-shadow: 0 0 14px var(--neon-green);"></span>
                    Inventario Holográfico 3D
                </div>
                <div class="products-showcase">
                    {% for nombre, datos in productos.items() %}
                    {% set activo = nombre in seleccionados %}
                    <div class="product-scene">
                        <div class="cube-wrapper {{ 'selected-cube' if activo else 'unselected-cube' }}">
                            <div class="cube-face face-front">
                                <span class="cube-letter">{{ nombre }}</span>
                                <span class="cube-meta">${{ datos.costo }}</span>
                            </div>
                            <div class="cube-face face-back">
                                <span class="cube-letter">{{ nombre }}</span>
                                <span class="cube-meta">+{{ datos.beneficio }} B</span>
                            </div>
                            <div class="cube-face face-right">
                                <span class="cube-meta">COSTO</span>
                                <span class="cube-letter" style="font-size:1.2rem;">${{ datos.costo }}</span>
                            </div>
                            <div class="cube-face face-left">
                                <span class="cube-meta">BENEFICIO</span>
                                <span class="cube-letter" style="font-size:1.2rem;">+{{ datos.beneficio }}</span>
                            </div>
                            <div class="cube-face face-top">
                                <span class="cube-letter">{{ nombre }}</span>
                            </div>
                            <div class="cube-face face-bottom">
                                <span class="cube-letter">{{ nombre }}</span>
                            </div>
                        </div>
                        <div class="product-status {{ 'status-on' if activo else 'status-off' }}">
                            {{ 'EN MOCHILA' if activo else 'DESCARTADO' }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Tabla 3D Paso a Paso -->
        <div class="card-3d">
            <div class="section-title">
                <span class="dot" style="background: var(--neon-pink); box-shadow: 0 0 14px var(--neon-pink);"></span>
                Trayectoria Paso a Paso del Algoritmo
            </div>
            <table class="table-3d">
                <thead>
                    <tr>
                        <th>Iteración</th>
                        <th>Productos en Mochila</th>
                        <th>Costo Acumulado</th>
                        <th>Beneficio (Fitness)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {% for paso in historial %}
                    <tr class="{{ 'final-row' if loop.last else '' }}">
                        <td><span class="step-pill">{{ loop.index }}</span></td>
                        <td>
                            {% if paso.estado %}
                                {% for item in paso.estado %}
                                    <span class="chip-item">Producto {{ item }}</span>
                                {% endfor %}
                            {% else %}
                                <span style="color:#64748b; font-style:italic;">Mochila Vacía (Estado Inicial)</span>
                            {% endif %}
                        </td>
                        <td style="color: var(--neon-gold); font-family:'Orbitron', sans-serif;">${{ paso.costo }}</td>
                        <td style="color: var(--neon-green); font-family:'Orbitron', sans-serif; font-size:1.25rem;">
                            +{{ paso.beneficio }}
                        </td>
                        <td>
                            {% if loop.last %}
                                <span class="status-on" style="padding:5px 14px; border-radius:20px; font-size:0.8rem;">CIMA ÓPTIMA</span>
                            {% else %}
                                <span style="color: var(--neon-cyan); font-size:0.9rem;">▲ Escalando...</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Datos inyectados desde Flask para graficar los pasos en 3D
        const historialPasos = {{ historial | tojson }};

        // 1. Efecto Tilt 3D interactivo en las tarjetas
        document.querySelectorAll('.tilt-card').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const rotateY = ((x / rect.width) - 0.5) * 14;
                const rotateX = ((y / rect.height) - 0.5) * -14;
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(8px)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
            });
        });

        // 2. Fondo 3D de partículas cibernéticas con Three.js
        const bgCanvas = document.getElementById('bg-canvas');
        const bgScene = new THREE.Scene();
        const bgCamera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        const bgRenderer = new THREE.WebGLRenderer({ canvas: bgCanvas, alpha: true, antialias: true });
        bgRenderer.setSize(window.innerWidth, window.innerHeight);

        const starGeo = new THREE.BufferGeometry();
        const starCount = 700;
        const starPos = new Float32Array(starCount * 3);
        for (let i = 0; i < starCount * 3; i++) {
            starPos[i] = (Math.random() - 0.5) * 120;
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        const starMat = new THREE.PointsMaterial({ color: 0x00f3ff, size: 0.35, transparent: true, opacity: 0.65 });
        const starField = new THREE.Points(starGeo, starMat);
        bgScene.add(starField);
        bgCamera.position.z = 40;

        function animateBg() {
            requestAnimationFrame(animateBg);
            starField.rotation.y += 0.0008;
            starField.rotation.x += 0.0003;
            bgRenderer.render(bgScene, bgCamera);
        }
        animateBg();

        // 3. Visor 3D de la Montaña Hill Climbing y los pasos hacia la cima
        const viewer = document.getElementById('hill-3d-viewer');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, viewer.clientWidth / viewer.clientHeight, 0.1, 500);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(viewer.clientWidth, viewer.clientHeight);
        viewer.appendChild(renderer.domElement);

        const pivot = new THREE.Group();
        scene.add(pivot);

        // Terreno wireframe 3D tipo montaña (función gaussiana)
        const planeGeo = new THREE.PlaneGeometry(18, 18, 36, 36);
        const pos = planeGeo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
            const x = pos.getX(i);
            const y = pos.getY(i);
            const dist = Math.sqrt(x * x + y * y);
            const z = 5.5 * Math.exp(-(dist * dist) / 28);
            pos.setZ(i, z);
        }
        planeGeo.computeVertexNormals();

        const wireMat = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            wireframe: true,
            transparent: true,
            opacity: 0.32
        });
        const mountain = new THREE.Mesh(planeGeo, wireMat);
        mountain.rotation.x = -Math.PI / 2;
        pivot.add(mountain);

        // Nodos 3D de cada paso del algoritmo subiendo a la cima
        const stepPoints = [];
        const totalSteps = historialPasos.length;
        historialPasos.forEach((paso, idx) => {
            const t = totalSteps > 1 ? idx / (totalSteps - 1) : 1;
            const radius = (1 - t) * 6.2;
            const angle = idx * 1.15;
            const x = Math.cos(angle) * radius;
            const z = Math.sin(angle) * radius;
            const dist = Math.sqrt(x * x + z * z);
            const y = 5.5 * Math.exp(-(dist * dist) / 28) + 0.35;

            const vec = new THREE.Vector3(x, y, z);
            stepPoints.push(vec);

            const isFinal = idx === totalSteps - 1;
            const sphereGeo = new THREE.SphereGeometry(isFinal ? 0.55 : 0.35, 24, 24);
            const sphereMat = new THREE.MeshBasicMaterial({
                color: isFinal ? 0x00ff88 : 0xff007f
            });
            const node = new THREE.Mesh(sphereGeo, sphereMat);
            node.position.copy(vec);
            pivot.add(node);
        });

        // Línea brillante conectando la ruta de escalada
        if (stepPoints.length > 1) {
            const lineGeo = new THREE.BufferGeometry().setFromPoints(stepPoints);
            const lineMat = new THREE.LineBasicMaterial({ color: 0xffcc00, linewidth: 3 });
            const pathLine = new THREE.Line(lineGeo, lineMat);
            pivot.add(pathLine);
        }

        camera.position.set(0, 9.5, 16);
        camera.lookAt(0, 2, 0);

        // Rotación con el mouse en el visor 3D
        let isDragging = false;
        let prevX = 0, prevY = 0;
        viewer.addEventListener('mousedown', e => { isDragging = true; prevX = e.clientX; prevY = e.clientY; });
        window.addEventListener('mouseup', () => { isDragging = false; });
        window.addEventListener('mousemove', e => {
            if (!isDragging) return;
            pivot.rotation.y += (e.clientX - prevX) * 0.01;
            pivot.rotation.x = Math.max(-0.5, Math.min(0.6, pivot.rotation.x + (e.clientY - prevY) * 0.008));
            prevX = e.clientX;
            prevY = e.clientY;
        });

        function animateHill() {
            requestAnimationFrame(animateHill);
            if (!isDragging) {
                pivot.rotation.y += 0.006;
            }
            renderer.render(scene, camera);
        }
        animateHill();

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
    estado_final, beneficio_maximo, costo_final, historial = hill_climbing()
    # Filtramos solo las claves que tienen valor 1 (seleccionadas)
    seleccionados = [p for p, v in estado_final.items() if v == 1]
    
    return render_template_string(HTML_TEMPLATE, 
                                  seleccionados=seleccionados, 
                                  beneficio=beneficio_maximo, 
                                  costo=costo_final, 
                                  historial=historial,
                                  productos=productos)

if __name__ == '__main__':
    app.run(debug=True)