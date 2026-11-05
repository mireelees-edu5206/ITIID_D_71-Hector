from pathlib import Path

import pandas as pd

# Cada clave es una columna y cada lista contiene los valores de esa columna por fila.
datos = {
    "estudiante":              ["Ana",    "Luis",  "Maria", "Carlos", "Sofia", "Pedro", "Elena", "Jorge", "Diego", "Valeria", "Hugo", "Lucia", "Andres", "Camila", "Ivan", "Paola", "Ricardo", "Daniela", "Mateo", "Fernanda"],
    "horas_estudio":           [8,        3,       10,      5,        6,       2,       7,       4,       9,       1,         6,      8,       4,        7,       3,      5,      9,         2,         6,       10],
    "asistencia":              [95,       60,      98,      75,       85,      55,      90,      70,      92,      48,        80,     96,      65,       88,      58,     72,     94,        50,        83,      100],
    "actividades_entregadas":  [100,      50,      100,     80,       90,      40,      95,      65,      95,      35,        85,     100,     60,       90,      45,     75,     98,        30,        88,      100],
    "calificacion":            [92,       58,      96,      72,       81,      50,      88,      64,      90,      45,        76,     94,      55,       84,      52,     70,     93,        41,        79,      98],
}

ARCHIVO = Path(__file__).with_name("datos_estudiantes.csv")


def titulo(texto):
    print(f"\n=== {texto} ===")


def main():
    pd.DataFrame(datos).to_csv(ARCHIVO, index=False)
    df = pd.read_csv(ARCHIVO)
    print(f"Archivo leído: {ARCHIVO.name}")

    titulo("1. Encabezado (primeros registros)")
    print(df.head().to_string(index=False))

    titulo("2. Últimos registros")
    print(df.tail().to_string(index=False))

    titulo("3. Tipos de datos")
    print(df.dtypes.to_string())

    titulo("4. Información general")
    print(f"Shape: {df.shape} -> {df.shape[0]} filas, {df.shape[1]} columnas")
    df.info()

    titulo("5. Estadísticas descriptivas")
    print(df.describe().round(2).to_string())

    titulo("6. Consulta de la columna calificacion")
    print(df["calificacion"].to_string())

    titulo("7. Promedio de calificaciones")
    print(round(df["calificacion"].mean(), 2))

    titulo("8. Horas de estudio con nombre")
    print(df[["estudiante", "horas_estudio"]].to_string(index=False))
    mayor = df.loc[df["horas_estudio"].idxmax()]
    menor = df.loc[df["horas_estudio"].idxmin()]
    print(f"\nMás horas: {mayor['estudiante']} ({mayor['horas_estudio']} hrs)")
    print(f"Menos horas: {menor['estudiante']} ({menor['horas_estudio']} hrs)")


if __name__ == "__main__":
    main()
