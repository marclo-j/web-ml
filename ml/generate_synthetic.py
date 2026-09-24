"""
generate_synthetic.py

Genera datos SINTETICOS (simulados) para probar el pipeline mientras se
consigue el histórico real de la IE. NO representan estudiantes reales.

Genera dos archivos en data/synthetic/:
  - historico.csv     -> con 'deserto' (0/1), para entrenar el modelo (ml/train.py)
  - carga_prueba.csv  -> sin 'deserto', formato de carga masiva, para probar
                         POST /registros/importar y el dashboard

Uso:
    python generate_synthetic.py
    python generate_synthetic.py --historico 300 --prueba 20 --seed 42
"""

import argparse
import os

import numpy as np
import pandas as pd

COLUMNAS_BASE = [
    "codigo",
    "grado",
    "seccion",
    "grupo",
    "momento",
    "suma_notas",
    "n_notas",
    "dias_asistidos",
    "dias_programados",
    "reuniones_asistidas",
    "reuniones_programadas",
]


# Diseño de la tesis: 3.° = control, 4.° = experimental
GRUPO_POR_GRADO = {3: "control", 4: "experimental"}


def generar_lote(n, anio, rng, momento, incluir_deserto):
    filas = []
    for i in range(n):
        # Mismo formato anonimizado que las fichas (EST-###); el código es único
        # dentro de cada año, por eso el histórico se identifica con codigo + anio.
        codigo = f"EST-{i + 1:03d}"
        grado = int(rng.choice([3, 4]))
        seccion = str(rng.choice(["A", "B"]))
        grupo = GRUPO_POR_GRADO[grado]

        # Rendimiento: escala vigesimal (0-20), 10 áreas curriculares de las
        # que 1 puede faltar (ej. exoneración de Educación Religiosa)
        n_notas = int(rng.integers(9, 11))
        promedio_base = float(np.clip(rng.normal(13.5, 3.0), 5, 20))
        suma_notas = round(promedio_base * n_notas, 1)

        # Asistencia: días lectivos del periodo de corte (I bimestre ~45 días,
        # I trimestre ~60 días; decisión D3), no el año completo
        dias_programados = int(rng.integers(45, 66))
        pct_asist_base = float(np.clip(rng.normal(0.85, 0.15), 0.4, 1.0))
        dias_asistidos = round(pct_asist_base * dias_programados)

        # Apoyo familiar: entre 2 y 4 reuniones de padres en el periodo de corte
        reuniones_programadas = int(rng.integers(2, 5))
        pct_reun_base = float(np.clip(rng.normal(0.5, 0.3), 0.0, 1.0))
        reuniones_asistidas = round(pct_reun_base * reuniones_programadas)

        fila = {
            "codigo": codigo,
            "grado": grado,
            "seccion": seccion,
            "grupo": grupo,
            "momento": momento,
            "suma_notas": suma_notas,
            "n_notas": n_notas,
            "dias_asistidos": dias_asistidos,
            "dias_programados": dias_programados,
            "reuniones_asistidas": reuniones_asistidas,
            "reuniones_programadas": reuniones_programadas,
        }

        if incluir_deserto:
            fila["anio"] = anio

            promedio = suma_notas / n_notas
            pct_asistencia = 100 * dias_asistidos / dias_programados
            pct_reuniones = (
                100 * reuniones_asistidas / reuniones_programadas
                if reuniones_programadas > 0
                else 0.0
            )

            # Riesgo latente: combinación ponderada de las 3 dimensiones + ruido.
            # Pesos aproximados a lo hallado en los antecedentes de la tesis
            # (económico/familiar > rendimiento > apoyo familiar), solo para
            # que el dataset simulado tenga una señal aprendible, no para
            # sustentar hallazgos.
            riesgo = (
                0.40 * (1 - promedio / 20)
                + 0.40 * (1 - pct_asistencia / 100)
                + 0.20 * (1 - pct_reuniones / 100)
            )
            ruido = rng.normal(0, 0.08)
            prob = float(np.clip(riesgo + ruido, 0, 1))
            fila["deserto"] = int(rng.random() < prob)

        filas.append(fila)

    columnas = COLUMNAS_BASE + (["anio", "deserto"] if incluir_deserto else [])
    return pd.DataFrame(filas, columns=columnas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--historico",
        type=int,
        default=300,
        help="Filas del histórico de entrenamiento (2024+2025)",
    )
    parser.add_argument(
        "--prueba",
        type=int,
        default=20,
        help="Filas del lote de prueba para la web (2026, sin deserto)",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Semilla (reproducibilidad)"
    )
    parser.add_argument(
        "--out", type=str, default="../data/synthetic", help="Carpeta de salida"
    )
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    mitad = args.historico // 2
    hist_2024 = generar_lote(mitad, 2024, rng, momento="pre", incluir_deserto=True)
    hist_2025 = generar_lote(
        args.historico - mitad, 2025, rng, momento="pre", incluir_deserto=True
    )
    historico = pd.concat([hist_2024, hist_2025], ignore_index=True)

    prueba = generar_lote(args.prueba, 2026, rng, momento="pre", incluir_deserto=False)

    os.makedirs(args.out, exist_ok=True)
    ruta_hist = os.path.join(args.out, "historico.csv")
    ruta_prueba = os.path.join(args.out, "carga_prueba.csv")
    historico.to_csv(ruta_hist, index=False)
    prueba.to_csv(ruta_prueba, index=False)

    tasa = historico["deserto"].mean() * 100
    print(
        f"[OK] {ruta_hist} -> {len(historico)} filas | tasa de deserción sintética: {tasa:.1f}%"
    )
    print(
        f"[OK] {ruta_prueba} -> {len(prueba)} filas (sin 'deserto', formato de carga masiva)"
    )
    print(
        "\nRecuerda: estos datos son SIMULADOS. No se reportan como hallazgos ni se citan en Resultados."
    )


if __name__ == "__main__":
    main()
