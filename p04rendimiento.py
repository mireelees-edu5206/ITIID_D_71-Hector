from flask import Flask, render_template_string

app = Flask(__name__)

estudiantes = {
    "Ana": 8,
    "Luis": 3,
    "Maria": 10,
    "Carlos": 5,
}


def clasificar(horas):
    if horas >= 6:
        return "Alto"
    if horas >= 5:
        return "Medio"
    return "Bajo"


def evaluar(horas):
    nivel = clasificar(horas)
    aprobado = nivel != "Bajo"
    return {
        "horas": horas,
        "nivel": nivel,
        "aprobado": aprobado,
        "resultado": "Aprueba" if aprobado else "Reprueba",
        "ayuda": not aprobado,
    }


HTML = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rendimiento académico</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    :root {
        --negro: #111;
        --crema: #fff3d1;
        --amarillo: #ffd23f;
        --rosa: #ff8fc7;
        --menta: #7ef0b8;
        --azul: #7ccfff;
        --rojo: #ff7a6b;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        min-height: 100vh;
        padding: 40px 20px 60px;
        background-color: var(--crema);
        background-image: radial-gradient(var(--negro) 1.2px, transparent 1.4px);
        background-size: 22px 22px;
        color: var(--negro);
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
    main { position: relative; max-width: 1100px; margin: 0 auto; }

    .titulo { margin-bottom: 34px; }
    .sello {
        display: inline-block;
        padding: 6px 14px;
        border: 3px solid var(--negro);
        background: var(--amarillo);
        box-shadow: 5px 5px 0 var(--negro);
        font-weight: 700;
        text-transform: uppercase;
        transform: rotate(-2deg);
    }
    h1 {
        margin: 22px 0 12px;
        font-family: 'Archivo Black', sans-serif;
        font-size: clamp(3rem, 9vw, 6.5rem);
        line-height: .92;
        text-transform: uppercase;
        text-shadow: 6px 6px 0 var(--rosa);
    }
    .titulo p { max-width: 560px; font-size: 1.05rem; font-weight: 700; }

    .regla, .resumen {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 22px;
        margin-bottom: 34px;
    }
    .caja, .stat {
        padding: 18px 20px;
        border: 4px solid var(--negro);
        box-shadow: 8px 8px 0 var(--negro);
        background: #fff;
    }
    .caja b, .stat strong { display: block; font-family: 'Archivo Black', sans-serif; font-size: 1.6rem; }
    .caja span, .stat small { font-weight: 700; text-transform: uppercase; font-size: .85rem; }
    .amarillo { background: var(--amarillo); }
    .azul { background: var(--azul); }
    .rosa { background: var(--rosa); }
    .menta { background: var(--menta); }
    .rojo { background: var(--rojo); }

    .tarjetas {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 30px;
    }
    .tarjeta {
        position: relative;
        padding: 22px;
        border: 4px solid var(--negro);
        box-shadow: 10px 10px 0 var(--negro);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .tarjeta:hover { transform: translate(-3px, -3px); box-shadow: 13px 13px 0 var(--negro); }
    .r0 { transform: rotate(-1.2deg); }
    .r1 { transform: rotate(1deg); }
    .r2 { transform: rotate(-.6deg); }
    .aprueba { background: var(--menta); }
    .reprueba { background: var(--rojo); }

    .cabeza { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    h2 { margin: 0; font-family: 'Archivo Black', sans-serif; font-size: 2rem; text-transform: uppercase; }
    .nivel {
        padding: 4px 10px;
        border: 3px solid var(--negro);
        background: #fff;
        font-weight: 700;
        font-size: .8rem;
        text-transform: uppercase;
        box-shadow: 3px 3px 0 var(--negro);
    }
    .horas { margin: 14px 0 10px; font-weight: 700; }
    .barra {
        height: 26px;
        border: 3px solid var(--negro);
        background: #fff;
        position: relative;
    }
    .barra div { height: 100%; background: var(--negro); }
    .barra::after {
        content: "";
        position: absolute;
        top: -10px;
        bottom: -10px;
        left: 50%;
        width: 3px;
        background: var(--negro);
    }
    .veredicto {
        margin-top: 18px;
        font-family: 'Archivo Black', sans-serif;
        font-size: 1.5rem;
        text-transform: uppercase;
    }
    .ayuda {
        display: inline-block;
        margin-top: 12px;
        padding: 6px 12px;
        border: 3px solid var(--negro);
        background: var(--amarillo);
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 4px 4px 0 var(--negro);
        transform: rotate(2deg);
    }

    .seccion-titulo {
        margin: 46px 0 18px;
        font-family: 'Archivo Black', sans-serif;
        font-size: 1.8rem;
        text-transform: uppercase;
    }
    .nota {
        margin-top: 44px;
        padding: 16px 20px;
        border: 3px dashed var(--negro);
        font-weight: 700;
    }
    @media (max-width: 600px) {
        h1 { text-shadow: 4px 4px 0 var(--rosa); }
        .tarjeta { box-shadow: 6px 6px 0 var(--negro); }
    }
</style>
</head>
<body>
<main>
    <header class="titulo">
        <span class="sello">Práctica 04 · Inteligencia artificial</span>
        <h1>Rendimiento<br>académico</h1>
        <p>Clasificación con una regla fija según las horas de estudio: define quién aprueba, quién reprueba y quién necesita ayuda.</p>
    </header>

    <section class="regla">
        <div class="caja amarillo"><b>Alto</b><span>6 hrs o más · aprueba</span></div>
        <div class="caja azul"><b>Medio</b><span>5 a 5.9 hrs · aprueba</span></div>
        <div class="caja rosa"><b>Bajo</b><span>menos de 5 hrs · reprueba y necesita ayuda</span></div>
    </section>

    <section class="resumen">
        <div class="stat menta"><small>Aprueban</small><strong>{{ aprueban|length }}</strong>{{ aprueban|join(', ') or 'Nadie' }}</div>
        <div class="stat rojo"><small>Reprueban</small><strong>{{ reprueban|length }}</strong>{{ reprueban|join(', ') or 'Nadie' }}</div>
        <div class="stat amarillo"><small>Necesitan ayuda</small><strong>{{ ayuda|length }}</strong>{{ ayuda|join(', ') or 'Nadie' }}</div>
    </section>

    <h2 class="seccion-titulo">Estudiantes</h2>
    <section class="tarjetas">
        {% for f in filas %}
        <article class="tarjeta {{ 'aprueba' if f.aprobado else 'reprueba' }} r{{ loop.index0 % 3 }}">
            <div class="cabeza">
                <h2>{{ f.nombre }}</h2>
                <span class="nivel">{{ f.nivel }}</span>
            </div>
            <p class="horas">{{ f.horas }} hrs de estudio</p>
            <div class="barra"><div style="width: {{ ([f.horas, 10] | min) * 10 }}%"></div></div>
            <div class="veredicto">{{ f.resultado }}</div>
            {% if f.ayuda %}<span class="ayuda">Necesita ayuda</span>{% endif %}
        </article>
        {% endfor %}
    </section>

    <p class="nota">La barra va de 0 a 10 horas. La línea marca 5 horas, el mínimo para aprobar.</p>
</main>
</body>
</html>
"""


@app.route("/")
def inicio():
    filas = [{"nombre": nombre, **evaluar(horas)} for nombre, horas in estudiantes.items()]
    return render_template_string(
        HTML,
        filas=filas,
        aprueban=[f["nombre"] for f in filas if f["aprobado"]],
        reprueban=[f["nombre"] for f in filas if not f["aprobado"]],
        ayuda=[f["nombre"] for f in filas if f["ayuda"]],
    )


if __name__ == "__main__":
    app.run(debug=True, port=5004)
