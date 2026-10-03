"""Ajuste de hiperparámetros del Random Forest con CV anidada repetida.

Grilla de docs/MODELO.md. Con n pequeño (140) un solo holdout 20 % es muy
inestable, así que se reporta la media ± desviación de una CV externa
estratificada 5x2 repetida; la búsqueda de la grilla (CV interna k=5) ocurre
solo dentro de cada fold de entrenamiento, para no inflar la métrica.

Uso: python ml/tune.py --data data/processed/historico.csv
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    GridSearchCV,
    RepeatedStratifiedKFold,
    StratifiedKFold,
    cross_validate,
)

sys.path.insert(0, str(Path(__file__).parent))
from train import FEATURES, SEMILLA, cargar_datos

GRILLA = {
    "n_estimators": [100, 200, 400],
    "max_depth": [None, 3, 5, 8],
    "min_samples_leaf": [1, 2, 4],
}
METRICAS = ["accuracy", "precision", "recall", "f1", "roc_auc"]


def resumen(res: dict) -> dict:
    return {
        m: {
            "media": round(float(np.mean(res[f"test_{m}"])), 4),
            "desviacion": round(float(np.std(res[f"test_{m}"])), 4),
        }
        for m in METRICAS
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    x, y = cargar_datos(args.data)
    base = RandomForestClassifier(
        class_weight="balanced", random_state=SEMILLA, n_jobs=1
    )

    externa = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEMILLA)
    interna = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    kw = {"cv": externa, "scoring": METRICAS, "return_estimator": True}

    print(f"n={len(y)} positivos={int(y.sum())}")
    ref = cross_validate(base.set_params(min_samples_leaf=2), x, y, **kw)
    print("Configuración inicial (min_samples_leaf=2):", json.dumps(resumen(ref)))

    busqueda = GridSearchCV(base, GRILLA, cv=interna, scoring="f1", n_jobs=-1)
    anidada = cross_validate(busqueda, x, y, **kw)
    print("CV anidada con búsqueda:", json.dumps(resumen(anidada)))

    # Hiperparámetros finales: búsqueda sobre todos los datos
    busqueda.fit(x, y)
    print(
        "Mejor combinación (todos los datos):",
        busqueda.best_params_,
        "F1 interno:",
        round(busqueda.best_score_, 4),
    )
    elegidos = [e.best_params_ for e in anidada["estimator"]]
    print("Combinaciones elegidas por fold externo:")
    for p in sorted({json.dumps(c, sort_keys=True) for c in elegidos}):
        print("  ", p, "x", sum(json.dumps(c, sort_keys=True) == p for c in elegidos))
    print("Features:", FEATURES)


if __name__ == "__main__":
    main()
