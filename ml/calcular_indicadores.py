"""
calcular_indicadores.py

Calcula promedio, pct_asistencia y pct_reuniones a partir de un CSV de datos
crudos en el formato de carga masiva de docs/VARIABLES.md (suma_notas,
n_notas, dias_asistidos, dias_programados, reuniones_asistidas,
reuniones_programadas [+ deserto en el histórico]).

Usa calcular_indicadores de preprocess.py: la misma fórmula que aplican las
fichas y que aplicará el backend. Las filas que no cumplan las reglas de
validación de VARIABLES.md (ej. dias_asistidos > dias_programados) se
excluyen y se listan aparte, igual que en preprocess.py.

Pensado para el histórico 2024-2025 si la IE lo entrega como CSV (en vez de
las fichas Excel, que ya procesa ml/preprocess.py) y para los datos
sintéticos de ml/generate_synthetic.py.

Uso:
    python ml/calcular_indicadores.py --entrada data/synthetic/historico.csv \\
        --salida data/synthetic/historico_indicadores.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess import ErrorValidacion, calcular_indicadores

CRUDOS = [
    "suma_notas",
    "n_notas",
    "dias_asistidos",
    "dias_programados",
    "reuniones_asistidas",
    "reuniones_programadas",
]


def procesar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    faltan = set(CRUDOS) - set(df.columns)
    if faltan:
        raise SystemExit(f"[ERROR] Faltan columnas: {sorted(faltan)}")

    filas_ok, filas_excluidas = [], []
    for i, fila in df.iterrows():
        try:
            indicadores = calcular_indicadores(**{c: fila[c] for c in CRUDOS})
            filas_ok.append({**fila.to_dict(), **indicadores})
        except ErrorValidacion as error:
            filas_excluidas.append(
                {**fila.to_dict(), "motivo": str(error), "fila_csv": i + 2}
            )
    return pd.DataFrame(filas_ok), pd.DataFrame(filas_excluidas)


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.entrada)
    ok, excluidas = procesar(df)

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    ok.to_csv(args.salida, index=False)
    print(f"[OK] {len(ok)} filas con indicadores -> {args.salida}")
    if not excluidas.empty:
        ruta_excluidas = args.salida.with_name(args.salida.stem + "_excluidas.csv")
        excluidas.to_csv(ruta_excluidas, index=False, encoding="utf-8-sig")
        print(
            f"[AVISO] {len(excluidas)} filas excluidas por regla de validación -> {ruta_excluidas}"
        )


if __name__ == "__main__":
    main()
