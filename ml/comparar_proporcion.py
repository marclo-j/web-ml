"""
comparar_proporcion.py

Compara el aumento actual (SMOTE x2, `rf_v3`/`rf_v4`) con el equilibrado de la
decisión D12 (SMOTE solo sobre desertores hasta una proporción objetivo), y
recalcula los umbrales de nivel de riesgo de cada configuración (D9).

Todo con validación cruzada estratificada 5 × R sobre alumnos reales: el
aumento se aplica solo a la partición de entrenamiento de cada fold. Las
probabilidades fuera de muestra (cada alumno predicho por modelos que no lo
vieron) se promedian por alumno entre repeticiones.

Uso:
    python ml/comparar_proporcion.py --data data/processed/historico.csv --fuente historico_real
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from train import AVISO_NO_RESULTADO, FUENTES, K_FOLDS, SEMILLA, cargar_datos, crear_modelo


def probabilidades_oof(modelo_fn, x, y, repeticiones: int):
    """Devuelve (metricas por fold, probabilidad media por alumno)."""
    cv = RepeatedStratifiedKFold(
        n_splits=K_FOLDS, n_repeats=repeticiones, random_state=SEMILLA
    )
    suma, cuenta = np.zeros(len(y)), np.zeros(len(y))
    folds = []
    for entrena, prueba in cv.split(x, y):
        m = modelo_fn()
        m.fit(x.iloc[entrena], y.iloc[entrena])
        p = m.predict_proba(x.iloc[prueba])[:, 1]
        pred = (p >= 0.5).astype(int)
        yt = y.iloc[prueba]
        folds.append(
            {
                "roc_auc": roc_auc_score(yt, p),
                "f1": f1_score(yt, pred, zero_division=0),
                "recall": recall_score(yt, pred, zero_division=0),
                "precision": precision_score(yt, pred, zero_division=0),
                "accuracy": accuracy_score(yt, pred),
            }
        )
        suma[prueba] += p
        cuenta[prueba] += 1
    return folds, suma / cuenta


def resumen(folds: list[dict]) -> dict:
    return {
        m: {
            "media": round(float(np.mean([f[m] for f in folds])), 4),
            "desviacion": round(float(np.std([f[m] for f in folds])), 4),
        }
        for m in folds[0]
    }


def umbrales(y, p) -> dict:
    """Criterio de D9 sobre las probabilidades fuera de muestra."""
    y = np.asarray(y)
    fpr, tpr, cortes = roc_curve(y, p)
    youden = float(cortes[np.argmax(tpr - fpr)])
    alto = 0.5
    pred = p >= alto
    return {
        "medio_p90_no_desertores": round(float(np.percentile(p[y == 0], 90)), 3),
        "alto_corte_clasificador": alto,
        "alto_youden": round(youden, 3),
        "desertores_detectados_en_0.50": f"{int((pred & (y == 1)).sum())}/{int(y.sum())}",
        "falsos_positivos_en_0.50": int((pred & (y == 0)).sum()),
        "p_minima_desertores": round(float(p[y == 1].min()), 3),
        "p_maxima_no_desertores": round(float(p[y == 0].max()), 3),
    }


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--fuente", required=True, choices=FUENTES)
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--proporciones", type=float, nargs="*", default=[])
    parser.add_argument("--refuerzos", type=float, nargs="+", default=[1, 2])
    parser.add_argument(
        "--out", type=Path, default=Path(__file__).resolve().parent / "models"
    )
    args = parser.parse_args()

    x, y = cargar_datos(args.data)
    print(f"Datos: {args.data} ({args.fuente}) | n={len(x)} | positivos={int(y.sum())}")
    if args.fuente != "historico_real":
        print("[AVISO]", AVISO_NO_RESULTADO)

    configuraciones = {
        "sin_aumento": lambda: crear_modelo(0),
        "smote_x2 (rf_v3)": lambda: crear_modelo(2),
    }
    # Equilibrar primero (D12) y reforzar después con sintéticos de ambas clases
    for f in args.refuerzos:
        configuraciones[f"A: equilibrar 0.40 + x{f:g}"] = lambda f=f: crear_modelo(
            f, proporcion=0.40
        )
        configuraciones[f"B: reducir 0.28, equilibrar 0.40 + x{f:g}"] = (
            lambda f=f: crear_modelo(f, proporcion=0.40, proporcion_previa=0.28)
        )
    for p in args.proporciones:
        configuraciones[f"proporcion_{p:.2f}"] = lambda p=p: crear_modelo(
            0, proporcion=p
        )

    salida = {
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "fuente_datos": args.fuente,
        "archivo_datos": str(args.data),
        "n": len(x),
        "positivos": int(y.sum()),
        "validacion": f"estratificada {K_FOLDS}x{args.repeticiones}, prueba solo con reales",
        "configuraciones": {},
    }
    for nombre, fn in configuraciones.items():
        print(f"  CV {K_FOLDS}x{args.repeticiones}: {nombre}...", flush=True)
        folds, p = probabilidades_oof(fn, x, y, args.repeticiones)
        salida["configuraciones"][nombre] = {
            "metricas": resumen(folds),
            "umbrales": umbrales(y, p),
            "auc_probabilidad_media_por_alumno": round(float(roc_auc_score(y, p)), 4),
        }
    if args.fuente != "historico_real":
        salida["aviso"] = AVISO_NO_RESULTADO

    metricas = ("roc_auc", "f1", "recall", "precision", "accuracy")
    print(f"\n{'Configuración':<20}" + "".join(f"{m:>18}" for m in metricas))
    for nombre, r in salida["configuraciones"].items():
        celdas = "".join(
            f"{r['metricas'][m]['media']:>11.3f} ± {r['metricas'][m]['desviacion']:.2f}"
            for m in metricas
        )
        print(f"{nombre:<20}{celdas}")
    print("\nUmbrales (probabilidades fuera de muestra):")
    for nombre, r in salida["configuraciones"].items():
        print(f"  {nombre:<20}", json.dumps(r["umbrales"], ensure_ascii=False))

    args.out.mkdir(parents=True, exist_ok=True)
    ruta = args.out / f"comparacion_proporcion_{args.fuente}.json"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {ruta}")


if __name__ == "__main__":
    main()
