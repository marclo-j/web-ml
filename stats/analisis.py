"""
analisis.py

Análisis estadístico de la tesis (docs/PLAN_ESTADISTICO.md), Fase 8. Exporta
cada tabla a stats/output/ como CSV con ";" y coma decimal (se abre directo en
Excel en español y se pega en Word).

Funciona por partes: con solo --pre calcula lo que ya se puede reportar
(descriptivos, niveles, normalidad y equivalencia de grupos en la preprueba).
Cuando exista la posprueba, --post agrega las filas POST y el contraste final.
La comparación PRE vs POST dentro de cada grupo (Wilcoxon) solo se calcula
con --intragrupo, porque está pendiente de validar con el asesor.

Tablas:
  1_descriptivos.csv      media, DE, mín, máx, mediana y RIC por grupo, momento e indicador
  2_niveles.csv           conteo y % de bajo / medio / alto por grupo y momento
  3_normalidad.csv        K-S (Lilliefors) y Shapiro-Wilk; decide con Shapiro-Wilk (n < 50)
  4_contraste.csv         control vs experimental por momento: t de Student o U de Mann-Whitney
  5_intragrupo.csv        PRE vs POST en cada grupo (solo con --intragrupo)
  6_metricas_modelo.csv   CV 5x5 sobre reales, holdout, matriz e importancia

Uso:
    python stats/analisis.py --pre data/processed/2026_pre_v5.csv
    python stats/analisis.py --pre data/processed/2026_pre_v5.csv --post data/processed/2026_post.csv
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import lilliefors

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "stats" / "output"
MODELO = RAIZ / "ml" / "models" / "rf_v5.joblib"
ALFA = 0.05
INDICADORES = {
    "promedio": "Promedio de calificaciones",
    "pct_asistencia": "% de asistencia",
    "pct_reuniones": "% asistencia a reuniones",
}
GRUPOS = ("control", "experimental")
MOMENTOS = ("pre", "post")
NIVELES = ("bajo", "medio", "alto")
ORDEN_NIVEL = {n: i for i, n in enumerate(NIVELES)}


def cargar(ruta: Path, momento: str) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    faltan = {"codigo", "grupo", *INDICADORES} - set(df.columns)
    if faltan:
        raise SystemExit(f"[ERROR] Faltan columnas en {ruta}: {sorted(faltan)}")
    return df.assign(momento=momento)


def clasificar(df: pd.DataFrame, ruta_modelo: Path) -> pd.DataFrame:
    """Probabilidad y nivel con el modelo y los umbrales D9 de su .json."""
    modelo = joblib.load(ruta_modelo)
    umbrales = json.loads(ruta_modelo.with_suffix(".json").read_text(encoding="utf-8"))[
        "umbrales_nivel_riesgo"
    ]
    p = modelo.predict_proba(df[list(INDICADORES)])[:, 1]
    nivel = np.where(
        p >= umbrales["alto"], "alto", np.where(p >= umbrales["medio"], "medio", "bajo")
    )
    return df.assign(probabilidad=p.round(4), nivel=nivel)


def descriptivos(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for momento, grupo, (col, nombre) in _combinaciones(df):
        x = _valores(df, momento, grupo, col)
        filas.append(
            {
                "indicador": nombre,
                "momento": momento,
                "grupo": grupo,
                "n": len(x),
                "media": x.mean(),
                "de": x.std(ddof=1),
                "minimo": x.min(),
                "maximo": x.max(),
                "mediana": x.median(),
                "q1": x.quantile(0.25),
                "q3": x.quantile(0.75),
            }
        )
    return pd.DataFrame(filas).round(2)


def niveles(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for momento in _momentos(df):
        for grupo in GRUPOS:
            sub = df[(df.momento == momento) & (df.grupo == grupo)]
            fila = {"momento": momento, "grupo": grupo, "n": len(sub)}
            for nivel in NIVELES:
                k = int((sub.nivel == nivel).sum())
                fila[nivel] = k
                fila[f"{nivel}_pct"] = round(100 * k / len(sub), 1) if len(sub) else 0
            filas.append(fila)
    return pd.DataFrame(filas)


def normalidad(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for momento, grupo, (col, nombre) in _combinaciones(df):
        x = _valores(df, momento, grupo, col)
        ks, p_ks = lilliefors(x, dist="norm")
        sw, p_sw = stats.shapiro(x)
        filas.append(
            {
                "indicador": nombre,
                "grupo_momento": f"{momento.capitalize()} – {grupo.capitalize()}",
                "ks_estadistico": round(float(ks), 3),
                "ks_gl": len(x),
                "ks_sig": round(float(p_ks), 3),
                "sw_estadistico": round(float(sw), 3),
                "sw_gl": len(x),
                "sw_sig": round(float(p_sw), 3),
                "normal": "sí" if p_sw >= ALFA else "no",
            }
        )
    return pd.DataFrame(filas)


def comparar(a: pd.Series, b: pd.Series, ordinal: bool = False) -> dict:
    """Control (a) vs experimental (b), regla de PLAN_ESTADISTICO.md."""
    normales = not ordinal and all(stats.shapiro(x).pvalue >= ALFA for x in (a, b))
    if normales:
        p_levene = stats.levene(a, b).pvalue
        t = stats.ttest_ind(a, b, equal_var=p_levene >= ALFA)
        sd = np.sqrt(
            ((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2)
        )
        return {
            "prueba": "t de Student" if p_levene >= ALFA else "t de Welch",
            "estadistico": float(t.statistic),
            "p": float(t.pvalue),
            "efecto": "d de Cohen",
            "valor_efecto": float((b.mean() - a.mean()) / sd) if sd else 0.0,
        }
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    # r = Z / √N, con Z de la aproximación normal de U
    n1, n2 = len(a), len(b)
    z = (u.statistic - n1 * n2 / 2) / np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    return {
        "prueba": "U de Mann-Whitney",
        "estadistico": float(u.statistic),
        "p": float(u.pvalue),
        "efecto": "r",
        "valor_efecto": float(abs(z) / np.sqrt(n1 + n2)),
    }


def contraste(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for momento in _momentos(df):
        variables = [(col, nombre, False) for col, nombre in INDICADORES.items()]
        variables.append(("nivel_ordinal", "Nivel de riesgo (ordinal)", True))
        for col, nombre, ordinal in variables:
            a = _valores(
                df.assign(nivel_ordinal=df.nivel.map(ORDEN_NIVEL)),
                momento,
                "control",
                col,
            )
            b = _valores(
                df.assign(nivel_ordinal=df.nivel.map(ORDEN_NIVEL)),
                momento,
                "experimental",
                col,
            )
            r = comparar(a, b, ordinal)
            filas.append(
                {
                    "momento": momento,
                    "variable": nombre,
                    "n_control": len(a),
                    "n_experimental": len(b),
                    **r,
                    "decision": "se rechaza H0"
                    if r["p"] < ALFA
                    else "no se rechaza H0",
                }
            )
    return pd.DataFrame(filas).round({"estadistico": 3, "p": 3, "valor_efecto": 2})


def intragrupo(df: pd.DataFrame) -> pd.DataFrame:
    """PRE vs POST del mismo alumno (Wilcoxon de rangos con signo)."""
    filas = []
    for grupo in GRUPOS:
        pre = df[(df.momento == "pre") & (df.grupo == grupo)].set_index("codigo")
        post = df[(df.momento == "post") & (df.grupo == grupo)].set_index("codigo")
        comunes = pre.index.intersection(post.index)
        for col, nombre in INDICADORES.items():
            w = stats.wilcoxon(pre.loc[comunes, col], post.loc[comunes, col])
            filas.append(
                {
                    "grupo": grupo,
                    "variable": nombre,
                    "n_pares": len(comunes),
                    "mediana_pre": pre.loc[comunes, col].median(),
                    "mediana_post": post.loc[comunes, col].median(),
                    "prueba": "Wilcoxon",
                    "estadistico": float(w.statistic),
                    "p": float(w.pvalue),
                    "decision": "se rechaza H0"
                    if w.pvalue < ALFA
                    else "no se rechaza H0",
                }
            )
    return pd.DataFrame(filas).round({"estadistico": 3, "p": 3})


def metricas_modelo(ruta_modelo: Path) -> pd.DataFrame:
    m = json.loads(ruta_modelo.with_suffix(".json").read_text(encoding="utf-8"))
    filas = []
    aumento = m.get("aumento") or {}
    proporcion = aumento.get("proporcion_objetivo")
    # Igual que el backend (/modelo): equilibrado a una proporción (D12) o aumento por factor (D8)
    cv = None
    if proporcion is not None:
        ruta_cv = ruta_modelo.parent / f"comparacion_proporcion_{m['fuente_datos']}.json"
        if ruta_cv.is_file():
            cv = (
                json.loads(ruta_cv.read_text(encoding="utf-8"))
                .get("configuraciones", {})
                .get(f"proporcion_{proporcion:.2f}", {})
                .get("metricas")
            )
    else:
        ruta_cv = ruta_modelo.parent / f"comparacion_aumento_{m['fuente_datos']}.json"
        if ruta_cv.is_file():
            metodo = aumento.get("metodo", "sin_aumento")
            cv = json.loads(ruta_cv.read_text(encoding="utf-8"))["utilidad"].get(metodo)
    for nombre, v in (cv or {}).items():
        filas.append(
            {
                "seccion": "CV 5x5 sobre reales",
                "medida": nombre,
                "valor": v["media"],
                "de": v["desviacion"],
            }
        )
    for nombre, v in m["holdout_20pct"].items():
        if nombre != "matriz_confusion":
            filas.append(
                {"seccion": "Holdout 20 %", "medida": nombre, "valor": v, "de": None}
            )
    (vn, fp), (fn, vp) = m["holdout_20pct"]["matriz_confusion"]["valores"]
    for nombre, v in (("VN", vn), ("FP", fp), ("FN", fn), ("VP", vp)):
        filas.append(
            {
                "seccion": "Matriz de confusión (holdout)",
                "medida": nombre,
                "valor": v,
                "de": None,
            }
        )
    for tipo, valores in m["importancia_variables"].items():
        for col, v in valores.items():
            filas.append(
                {
                    "seccion": f"Importancia ({tipo})",
                    "medida": INDICADORES[col],
                    "valor": v,
                    "de": None,
                }
            )
    return pd.DataFrame(filas)


def _momentos(df):
    return [m for m in MOMENTOS if (df.momento == m).any()]


def _combinaciones(df):
    for col_nombre in INDICADORES.items():
        for momento in _momentos(df):
            for grupo in GRUPOS:
                yield momento, grupo, col_nombre


def _valores(df, momento, grupo, col) -> pd.Series:
    return (
        df.loc[(df.momento == momento) & (df.grupo == grupo), col]
        .astype(float)
        .reset_index(drop=True)
    )


def guardar(tabla: pd.DataFrame, nombre: str, salida: Path) -> None:
    tabla.to_csv(
        salida / nombre, sep=";", decimal=",", index=False, encoding="utf-8-sig"
    )
    print(f"[OK] {salida / nombre}")


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pre", type=Path, required=True, help="CSV de la preprueba con indicadores"
    )
    parser.add_argument("--post", type=Path, help="CSV de la posprueba (cuando exista)")
    parser.add_argument("--modelo", type=Path, default=MODELO)
    parser.add_argument(
        "--intragrupo",
        action="store_true",
        help="Agrega Wilcoxon PRE vs POST (pendiente del asesor)",
    )
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()

    partes = [cargar(args.pre, "pre")]
    if args.post:
        partes.append(cargar(args.post, "post"))
    df = clasificar(pd.concat(partes, ignore_index=True), args.modelo)

    args.salida.mkdir(parents=True, exist_ok=True)
    guardar(descriptivos(df), "1_descriptivos.csv", args.salida)
    guardar(niveles(df), "2_niveles.csv", args.salida)
    guardar(normalidad(df), "3_normalidad.csv", args.salida)
    tabla_contraste = contraste(df)
    guardar(tabla_contraste, "4_contraste.csv", args.salida)
    if args.intragrupo:
        if not args.post:
            raise SystemExit("[ERROR] --intragrupo necesita --post")
        guardar(intragrupo(df), "5_intragrupo.csv", args.salida)
    guardar(metricas_modelo(args.modelo), "6_metricas_modelo.csv", args.salida)

    print()
    print(
        tabla_contraste[["momento", "variable", "prueba", "p", "decision"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
