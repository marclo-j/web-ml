"""
validar_desenlace.py

Valida el modelo de producción contra la deserción real (D2, opción b): compara
la predicción hecha con los indicadores PRE 2026 con el `deserto` que entregó la
IE. Es una validación descriptiva: con pocos desertores no hay potencia para una
prueba de hipótesis.

Entrada: carpeta con las 3 fichas que traen `deserto` (data/raw/2026_desenlace/).
Solo se lee `codigo` y `deserto`; no pasa por preprocess.py porque ahí `deserto`
debe estar vacío en 2026. Las 3 fichas deben coincidir alumno por alumno.

Salida: stats/output/7_validacion_desenlace.csv (CSV con ";" y coma decimal).

Uso:
    python ml/validar_desenlace.py --desenlace data/raw/2026_desenlace \
        --pre data/processed/2026_pre_v5.csv
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "stats"))

from analisis import MODELO, cargar, clasificar
from preprocess import FILA_ENCABEZADO, HOJA_DATOS

SALIDA = RAIZ / "stats" / "output"


def leer_deserto(carpeta: Path) -> pd.DataFrame:
    """Une `deserto` de las 3 fichas por código; error si no coinciden."""
    columnas = []
    for n in (1, 2, 3):
        archivos = sorted(carpeta.glob(f"ficha_{n}_*.xlsx"))
        if len(archivos) != 1:
            raise SystemExit(f"[ERROR] Se esperaba una ficha_{n}_*.xlsx en {carpeta}")
        tabla = pd.read_excel(
            archivos[0], sheet_name=HOJA_DATOS, header=FILA_ENCABEZADO - 1
        )
        tabla = tabla[tabla["codigo"].notna()]
        columnas.append(tabla.set_index("codigo")["deserto"].rename(f"f{n}"))
    return unir_fichas(columnas)


def unir_fichas(columnas: list[pd.Series]) -> pd.DataFrame:
    df = pd.concat(columnas, axis=1)
    if df.index.has_duplicates:
        raise SystemExit("[ERROR] Código repetido en las fichas")
    distinto = df.nunique(axis=1, dropna=False) > 1
    if distinto.any():
        raise SystemExit(
            f"[ERROR] `deserto` distinto entre fichas: {df.index[distinto].tolist()}"
        )
    df = df.dropna()
    if not df.stack().isin([0, 1]).all():
        raise SystemExit("[ERROR] `deserto` debe ser 0 o 1")
    return df[["f1"]].rename(columns={"f1": "deserto"}).astype(int)


def _tasa(a: int, b: int) -> float | None:
    return round(a / b, 4) if b else None


def metricas(y: pd.Series, p: pd.Series, corte: float) -> dict:
    pred = (p >= corte).astype(int)
    vn, fp, fn, vp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    recall = _tasa(vp, vp + fn)
    precision = _tasa(vp, vp + fp)
    f1 = (
        round(2 * precision * recall / (precision + recall), 4)
        if precision and recall
        else None
    )
    return {
        "VN": int(vn),
        "FP": int(fp),
        "FN": int(fn),
        "VP": int(vp),
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": _tasa(vn + vp, len(y)),
    }


def validar(df: pd.DataFrame, umbrales: dict) -> pd.DataFrame:
    """df: deserto, probabilidad, nivel, grupo. Devuelve una tabla en formato largo."""
    filas = []
    ambitos = [("Todos", df)] + [(g.capitalize(), s) for g, s in df.groupby("grupo")]
    for ambito, sub in ambitos:
        y = sub["deserto"]
        base = {"ambito": ambito, "n": len(sub), "desertores": int(y.sum())}
        auc = (
            round(float(roc_auc_score(y, sub["probabilidad"])), 4)
            if y.nunique() == 2
            else None
        )
        filas.append({**base, "criterio": "AUC", "auc": auc})
        for nombre in ("alto", "medio"):
            corte = umbrales[nombre]
            filas.append(
                {
                    **base,
                    "criterio": f"corte {nombre} {corte}",
                    **metricas(y, sub["probabilidad"], corte),
                }
            )
        for nivel in ("bajo", "medio", "alto"):
            s = sub[sub["nivel"] == nivel]
            filas.append(
                {
                    **base,
                    "criterio": f"nivel {nivel}",
                    "alumnos_en_nivel": len(s),
                    "desertores_en_nivel": int(s["deserto"].sum()),
                }
            )
    return pd.DataFrame(filas)


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desenlace", type=Path, required=True)
    parser.add_argument("--pre", type=Path, required=True)
    parser.add_argument("--modelo", type=Path, default=MODELO)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()

    deserto = leer_deserto(args.desenlace)
    pre = clasificar(cargar(args.pre, "pre"), args.modelo).set_index("codigo")
    faltan = sorted(set(pre.index) - set(deserto.index))
    if faltan:
        raise SystemExit(f"[ERROR] Alumnos del PRE sin `deserto`: {faltan}")
    df = pre.join(deserto, how="inner")
    meta = json.loads(args.modelo.with_suffix(".json").read_text(encoding="utf-8"))
    tabla = validar(df, meta["umbrales_nivel_riesgo"])

    args.salida.mkdir(parents=True, exist_ok=True)
    destino = args.salida / "7_validacion_desenlace.csv"
    tabla.to_csv(destino, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    print(f"[OK] {destino}  ({len(df)} alumnos, {int(df['deserto'].sum())} desertores)")
    print(tabla.to_string(index=False))


if __name__ == "__main__":
    main()
