"""
etiquetar_umbral.py

Etiqueta `deserto` (0/1) por reglas de umbral tomadas de la literatura
— Opción B de docs/MODELO.md, usada solo mientras no se consigue el
histórico real (Opción A) con desenlace efectivo.

⚠️ Con esta opción el modelo aprende a reproducir las reglas de etiquetado,
no a predecir la deserción real. Las métricas que salgan de aquí NUNCA se
reportan en el capítulo de Resultados; solo sirven como prueba de concepto
del pipeline. Ver la advertencia completa en docs/MODELO.md.

Umbrales (declarados en docs/MODELO.md, con su fuente):
  - promedio < 11              → nota desaprobatoria (escala vigesimal, MINEDU)
  - pct_asistencia < 85        → absentismo crónico de alto riesgo
                                  (Balfanz & Byrnes, difundido por Attendance
                                  Works / U.S. Dept. of Education)
  - pct_reuniones < 50         → baja participación familiar (umbral
                                  operacional del autor; no viene de una
                                  cifra específica en la literatura — se
                                  declara así y se valida con el asesor)

Se marca deserto = 1 (en riesgo, para efectos de entrenamiento) si se
cumple CUALQUIERA de las 3 reglas.

Uso:
    python ml/etiquetar_umbral.py --entrada data/processed/2026_pre.csv \\
        --salida data/processed/2026_pre_opcion_b.csv
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess import comprobar_salida

# Umbrales por defecto (docs/MODELO.md → Opción B)
UMBRAL_PROMEDIO = 11.0
UMBRAL_ASISTENCIA = 85.0
UMBRAL_REUNIONES = 50.0

METODO = "opcion_b_umbral"

AVISO = (
    "OPCIÓN B (docs/MODELO.md): deserto etiquetado por reglas de umbral, no "
    "es el desenlace real de la IE. El modelo entrenado con esto solo "
    "reproduce las reglas de etiquetado; sus métricas NO se reportan como "
    "resultados de la tesis, solo como validación técnica del pipeline."
)


def etiquetar(
    df: pd.DataFrame,
    umbral_promedio: float = UMBRAL_PROMEDIO,
    umbral_asistencia: float = UMBRAL_ASISTENCIA,
    umbral_reuniones: float = UMBRAL_REUNIONES,
) -> pd.DataFrame:
    """Agrega deserto (0/1) y deserto_metodo a partir de los 3 indicadores."""
    faltan = {"promedio", "pct_asistencia", "pct_reuniones"} - set(df.columns)
    if faltan:
        raise ValueError(f"Faltan columnas para etiquetar: {sorted(faltan)}")

    en_riesgo = (
        (df["promedio"] < umbral_promedio)
        | (df["pct_asistencia"] < umbral_asistencia)
        | (df["pct_reuniones"] < umbral_reuniones)
    )
    salida = df.copy()
    salida["deserto"] = en_riesgo.astype(int)
    salida["deserto_metodo"] = METODO
    return salida


def resumen(df: pd.DataFrame) -> dict:
    total = len(df)
    positivos = int(df["deserto"].sum())
    return {
        "metodo": METODO,
        "umbrales": {
            "promedio_menor_que": UMBRAL_PROMEDIO,
            "pct_asistencia_menor_que": UMBRAL_ASISTENCIA,
            "pct_reuniones_menor_que": UMBRAL_REUNIONES,
        },
        "n": total,
        "en_riesgo": positivos,
        "en_riesgo_pct": round(positivos / total * 100, 1) if total else 0.0,
        "por_regla": {
            "promedio": int((df["promedio"] < UMBRAL_PROMEDIO).sum()),
            "pct_asistencia": int((df["pct_asistencia"] < UMBRAL_ASISTENCIA).sum()),
            "pct_reuniones": int((df["pct_reuniones"] < UMBRAL_REUNIONES).sum()),
        },
        "aviso": AVISO,
    }


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entrada", type=Path, required=True, help="CSV de indicadores"
    )
    parser.add_argument("--salida", type=Path, required=True, help="CSV etiquetado")
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Sobrescribir deserto aunque el archivo ya traiga valores reales",
    )
    args = parser.parse_args()

    comprobar_salida(args.salida)
    df = pd.read_csv(args.entrada)
    if "deserto" in df.columns and df["deserto"].notna().any() and not args.forzar:
        raise SystemExit(
            "[ERROR] La entrada ya tiene valores reales en deserto; use --forzar "
            "solo si de verdad quiere reemplazarlos por el etiquetado de la Opción B."
        )

    etiquetado = etiquetar(df)
    info = resumen(etiquetado)

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    etiquetado.to_csv(args.salida, index=False)
    Path(args.salida.with_suffix("")).with_name(
        args.salida.stem + "_umbral.json"
    ).write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 70)
    print("[AVISO]", AVISO)
    print("=" * 70)
    print(
        f"n = {info['n']} | en riesgo: {info['en_riesgo']} ({info['en_riesgo_pct']}%)"
    )
    print("por regla:", info["por_regla"])
    print(f"[OK] {args.salida}")


if __name__ == "__main__":
    main()
