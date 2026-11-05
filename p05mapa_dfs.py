from flask import Flask, render_template_string

app = Flask(__name__)

mapa = [
    ("Laboratorio", "Cafeteria"),
    ("Laboratorio", "Aulas"),
    ("Cafeteria", "Biblioteca"),
    ("Aulas", "Auditorio"),
    ("Aulas", "Biblioteca"),
    ("Auditorio", "Biblioteca"),
]

posiciones = {
    "Laboratorio": (130, 220),
    "Cafeteria": (340, 100),
    "Aulas": (340, 340),
    "Biblioteca": (550, 220),
    "Auditorio": (550, 400),
}


def construir_grafo(mapa):
    grafo = {}
    for a, b in mapa:
        grafo.setdefault(a, []).append(b)
        grafo.setdefault(b, []).append(a)
    return grafo


def busqueda_profunda(grafo, actual, meta, visitados=None, camino=None):
    visitados = set() if visitados is None else visitados
    camino = [actual] if camino is None else camino
    if actual == meta:
        return camino
    visitados.add(actual)
    for vecino in grafo.get(actual, []):
        if vecino not in visitados:
            ruta = busqueda_profunda(grafo, vecino, meta, visitados, camino + [vecino])
            if ruta:
                return ruta
    return None


HTML = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa del campus · Búsqueda en profundidad</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    :root {
        --tinta: #3b1024;
        --crema: #ffe3f0;
        --papel: #fff6fb;
        --cafe: #e8559a;
        --caramelo: #ffb3d9;
        --arena: #ffc2e2;
        --naranja: #ff2e88;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        min-height: 100vh;
        padding: 40px 18px 60px;
        background-color: var(--crema);
        background-image: radial-gradient(var(--tinta) 1.1px, transparent 1.3px);
        background-size: 22px 22px;
        color: var(--tinta);
        font-family: 'Space Mono', monospace;
    }
    body::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: .14;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
    }
    main { position: relative; max-width: 920px; margin: 0 auto; }

    header {
        padding: 22px 26px;
        background: var(--cafe);
        color: var(--papel);
        border: 4px solid var(--tinta);
        box-shadow: 9px 9px 0 var(--tinta);
        transform: rotate(-.6deg);
    }
    h1 {
        margin: 0 0 8px;
        font-family: 'Archivo Black', sans-serif;
        font-size: clamp(2.2rem, 6vw, 3.6rem);
        line-height: .95;
        text-transform: uppercase;
        text-shadow: 5px 5px 0 var(--caramelo);
    }
    header p { margin: 0; font-weight: 700; color: var(--arena); }

    .panel {
        margin-top: 30px;
        padding: 24px;
        background: var(--papel);
        border: 4px solid var(--tinta);
        box-shadow: 10px 10px 0 var(--tinta);
    }
    .ruta {
        display: inline-block;
        margin: 0 0 10px;
        padding: 8px 14px;
        background: var(--arena);
        border: 3px solid var(--tinta);
        box-shadow: 4px 4px 0 var(--tinta);
        font-family: 'Archivo Black', sans-serif;
        font-size: 1.05rem;
        text-transform: uppercase;
        transform: rotate(-1deg);
    }
    .saltos { margin: 14px 0 0; font-weight: 700; }

    svg {
        width: 100%;
        max-width: 560px;
        height: auto;
        display: block;
        margin: 18px auto 0;
        background: var(--crema);
        border: 3px solid var(--tinta);
    }
    .arista { stroke: var(--tinta); stroke-width: 3; stroke-dasharray: 8 6; }
    .arista.ruta { stroke: var(--naranja); stroke-width: 9; stroke-dasharray: none; }
    .nodo { fill: var(--papel); stroke: var(--tinta); stroke-width: 4; }
    .nodo.activo { fill: var(--caramelo); }
    .etiqueta {
        fill: var(--tinta);
        font-family: 'Archivo Black', sans-serif;
        font-size: 16px;
        text-anchor: middle;
        text-transform: uppercase;
    }

    .leyenda { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 22px; }
    .leyenda span {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border: 3px solid var(--tinta);
        background: #fff;
        font-weight: 700;
        font-size: .85rem;
        text-transform: uppercase;
        box-shadow: 4px 4px 0 var(--tinta);
    }
    .muestra { display: inline-block; width: 28px; height: 10px; border: 2px solid var(--tinta); }
    @media (max-width: 600px) {
        header, .panel { box-shadow: 6px 6px 0 var(--tinta); }
    }
</style>
</head>
<body>
<main>
    <header>
        <h1>Mapa del campus</h1>
        <p>Búsqueda en profundidad (DFS) desde Laboratorio hasta Biblioteca</p>
    </header>

    <section class="panel">
        {% if ruta %}
        <div class="ruta">Ruta: {{ ruta|join(' → ') }}</div>
        <p class="saltos">Saltos: {{ saltos }}</p>
        {% else %}
        <div class="ruta">No existe ruta de Laboratorio a Biblioteca</div>
        {% endif %}

        <svg viewBox="0 0 700 480" role="img" aria-label="Mapa del campus">
            {% for a in aristas %}
            <line x1="{{ a.x1 }}" y1="{{ a.y1 }}" x2="{{ a.x2 }}" y2="{{ a.y2 }}" class="{{ 'arista ruta' if a.ruta else 'arista' }}"/>
            {% endfor %}
            {% for n in nodos %}
            <g transform="rotate({{ (loop.index0 % 3) - 1 }} {{ n.x }} {{ n.y }})">
                <rect x="{{ n.x - 75 }}" y="{{ n.y - 22 }}" width="150" height="44" rx="6" class="{{ 'nodo activo' if n.en_ruta else 'nodo' }}"/>
                <text x="{{ n.x }}" y="{{ n.y + 6 }}" class="etiqueta">{{ n.nombre }}</text>
            </g>
            {% endfor %}
        </svg>

        <div class="leyenda">
            <span><i class="muestra" style="background:#ff2e88"></i>Recorrido DFS</span>
            <span><i class="muestra" style="background:#3b1024; background-image:repeating-linear-gradient(90deg,#3b1024 0 6px,transparent 6px 10px)"></i>Conexión</span>
            <span><i class="muestra" style="background:#ffb3d9"></i>Lugar en la ruta</span>
        </div>
    </section>
</main>
</body>
</html>
"""


@app.route("/")
def inicio():
    grafo = construir_grafo(mapa)
    ruta = busqueda_profunda(grafo, "Laboratorio", "Biblioteca") or []
    tramos = set(zip(ruta, ruta[1:]))
    aristas = [
        {
            "x1": posiciones[a][0], "y1": posiciones[a][1],
            "x2": posiciones[b][0], "y2": posiciones[b][1],
            "ruta": (a, b) in tramos or (b, a) in tramos,
        }
        for a, b in mapa
    ]
    nodos = [
        {"nombre": nombre, "x": x, "y": y, "en_ruta": nombre in ruta}
        for nombre, (x, y) in posiciones.items()
    ]
    return render_template_string(
        HTML,
        aristas=aristas,
        nodos=nodos,
        ruta=ruta,
        saltos=max(len(ruta) - 1, 0),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5005)
