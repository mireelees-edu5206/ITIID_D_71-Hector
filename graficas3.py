"""
==============================================================
            Teoría del Color y Paletas Profesionales
==============================================================

Objetivo:
Conocer y comparar las principales paletas de colores
utilizadas en Ciencia de Datos y Machine Learning.

Puede existir la posibilidad de elección de diferentes paletas
de colores a las presentadas, todo dependera de lo que se pretende 
presentar al usuario.

==============================================================
"""

# ==========================================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================================

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

plt.style.use("default")

# ==========================================================
# DATOS
# ==========================================================

x = np.arange(1, 11)
y = np.random.randint(10, 100, 10)

# ==========================================================
# LISTA DE PALETAS 
# Aplicaciones:
# ==========================================================

paletas = [
        # Se utilizan cuando los datos representan categorías diferentes, sin un orden natural, Departamentos de una empresa, 
        # Tipos de productos, Carreras universitarias, Categorías de clientes,
    "deep",
    "muted",
    "bright",
    "pastel",
    "dark",
    "colorblind",
        
        # Representan una progresión de menor a mayor intensidad, Aplicaciones: Ventas, Temperaturas, Ingresos, Producción, Población.
    "Blues",
    "Greens",
    "Reds",
    "Purples",

        # Diseñadas para que los cambios de color sean interpretados de forma uniforme por el ojo humano, Mapas de calor, Machine Learning,
        # PCA, K-Means, Matrices de correlación, Visualización científica.
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis"

]

# ==========================================================
# CREAR FIGURA
# ==========================================================

fig, axs = plt.subplots(
    len(paletas),
    1,
    figsize=(14, 28)
)

fig.suptitle(
    "Comparación Profesional de Paletas de Colores",
    fontsize=24,
    fontweight="bold"
)

# ==========================================================
# DIBUJAR CADA PALETA
# ==========================================================

for ax, paleta in zip(axs, paletas):

    colores = sns.color_palette(paleta, len(x))

    ax.bar(
        x,
        y,
        color=colores
    )

    ax.set_title(
        f"Paleta: {paleta}",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_ylabel("Valor")

    ax.grid(
        linestyle="--",
        alpha=0.3
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ==========================================================
# PIE DE FIGURA
# ==========================================================

plt.figtext(

    0.01,

    0.01,

    "Fuente: Datos simulados | Manual Profesional de Visualización | UTVT",

    fontsize=10,

    color="gray"

)

plt.tight_layout()

plt.savefig(
    "Capitulo03_Paletas_Profesionales.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("="*60)
print("Galería de paletas creada correctamente.")
print("="*60)