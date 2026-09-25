"""
train.py

Entrena y evalúa el Random Forest de la tesis (docs/MODELO.md): clasificación
binaria `deserto` (0/1) sobre los 3 indicadores (promedio, pct_asistencia,
pct_reuniones), con holdout estratificado 80/20 y validación cruzada
estratificada k=5 sobre el 80%.

--fuente es obligatorio y queda registrado en ml/models/rf_<version>.json:
  - historico_real   datos con desenlace efectivo de la IE (Opción A)
  - opcion_b         etiquetado por umbrales de la literatura (Opción B),
                      ver ml/etiquetar_umbral.py
  - sintetico        datos simulados (ml/generate_synthetic.py)

Solo "historico_real" puede citarse como resultado de la tesis. Con
"opcion_b" o "sintetico" el script imprime y guarda una advertencia: son
prueba de concepto del pipeline, no resultados (docs/MODELO.md).

Uso:
    python ml/train.py --data data/synthetic/historico.csv --version v0 --fuente sintetico
    python ml/train.py --data data/processed/2026_pre_opcion_b.csv --version v0b --fuente opcion_b
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

FEATURES = ["promedio", "pct_asistencia", "pct_reuniones"]
TARGET = "deserto"

# Configuración e hiperparámetros por defecto (docs/MODELO.md)
HIPERPARAMETROS = {
    "n_estimators": 200,
    "max_depth": None,
    "min_samples_leaf": 2,
    "class_weight": "balanced",
    "random_state": 42,
}
SEMILLA = 42
PROPORCION_TEST = 0.20
K_FOLDS = 5

# Umbrales de nivel de riesgo (docs/MODELO.md)
UMBRAL_MEDIO = 0.33
UMBRAL_ALTO = 0.66

FUENTES = ("historico_real", "opcion_b", "sintetico")
AVISO_NO_RESULTADO = (
    "Esta corrida usa datos que NO son el desenlace histórico real de la IE. "
    "Es una validación técnica del pipeline (docs/MODELO.md); NO se reporta "
    "en el capítulo de Resultados ni en slides como hallazgo."
)


def nivel_desde_probabilidad(p: float) -> str:
    """Probabilidad de deserción → nivel de riesgo (umbrales de MODELO.md)."""
    if p >= UMBRAL_ALTO:
        return "alto"
    if p >= UMBRAL_MEDIO:
        return "medio"
    return "bajo"


def cargar_datos(ruta: Path) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(ruta)
    faltan = {*FEATURES, TARGET} - set(df.columns)
    if faltan:
        raise SystemExit(f"[ERROR] Faltan columnas en {ruta}: {sorted(faltan)}")
    df = df.dropna(subset=[*FEATURES, TARGET])
    if df.empty:
        raise SystemExit(f"[ERROR] {ruta} no tiene filas completas para entrenar")
    return df[FEATURES], df[TARGET].astype(int)


def validar_cruzada(modelo, x_train, y_train) -> dict:
    cv = StratifiedKFold(n_splits=K_FOLDS, shuffle=True, random_state=SEMILLA)
    metricas = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
    }
    resultado = cross_validate(modelo, x_train, y_train, cv=cv, scoring=metricas)
    return {
        nombre: {
            "media": round(float(np.mean(resultado[f"test_{nombre}"])), 4),
            "desviacion": round(float(np.std(resultado[f"test_{nombre}"])), 4),
        }
        for nombre in metricas
    }


def evaluar_holdout(modelo, x_test, y_test) -> dict:
    y_pred = modelo.predict(x_test)
    matriz = confusion_matrix(y_test, y_pred, labels=[0, 1])
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "matriz_confusion": {
            "etiquetas": ["no_deserto (0)", "deserto (1)"],
            "valores": matriz.tolist(),
        },
    }


def importancia_variables(modelo, x_test, y_test) -> dict:
    mdi = dict(zip(FEATURES, (round(float(v), 4) for v in modelo.feature_importances_)))
    perm = permutation_importance(
        modelo, x_test, y_test, n_repeats=30, random_state=SEMILLA, scoring="f1"
    )
    permutacion = dict(
        zip(FEATURES, (round(float(v), 4) for v in perm.importances_mean))
    )
    return {"mdi_gini": mdi, "permutacion_f1": permutacion}


def distribucion_niveles(modelo, x_test) -> dict:
    probabilidades = modelo.predict_proba(x_test)[:, 1]
    niveles = [nivel_desde_probabilidad(p) for p in probabilidades]
    return {n: niveles.count(n) for n in ("bajo", "medio", "alto")}


def entrenar(ruta_datos: Path, fuente: str) -> dict:
    x, y = cargar_datos(ruta_datos)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=PROPORCION_TEST, stratify=y, random_state=SEMILLA
    )

    modelo = RandomForestClassifier(**HIPERPARAMETROS)
    cv = validar_cruzada(modelo, x_train, y_train)
    modelo.fit(x_train, y_train)
    holdout = evaluar_holdout(modelo, x_test, y_test)
    importancias = importancia_variables(modelo, x_test, y_test)
    niveles = distribucion_niveles(modelo, x_test)

    metadatos = {
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "fuente_datos": fuente,
        "archivo_datos": str(ruta_datos),
        "n_total": len(x),
        "n_train": len(x_train),
        "n_test": len(x_test),
        "tasa_positivos": round(float(y.mean()), 4),
        "features": FEATURES,
        "hiperparametros": HIPERPARAMETROS,
        "validacion_cruzada_k5_sobre_train": cv,
        "holdout_20pct": holdout,
        "importancia_variables": importancias,
        "umbrales_nivel_riesgo": {"medio": UMBRAL_MEDIO, "alto": UMBRAL_ALTO},
        "distribucion_niveles_en_holdout": niveles,
    }
    if fuente != "historico_real":
        metadatos["aviso"] = AVISO_NO_RESULTADO
    return {"modelo": modelo, "metadatos": metadatos}


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, required=True, help="CSV con features + deserto"
    )
    parser.add_argument(
        "--version", required=True, help="Nombre de versión, ej. v0, v0b, v1"
    )
    parser.add_argument("--fuente", required=True, choices=FUENTES)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "models",
        help="Carpeta de modelos (default: ml/models/)",
    )
    args = parser.parse_args()

    resultado = entrenar(args.data, args.fuente)
    args.out.mkdir(parents=True, exist_ok=True)
    ruta_modelo = args.out / f"rf_{args.version}.joblib"
    ruta_json = args.out / f"rf_{args.version}.json"
    joblib.dump(resultado["modelo"], ruta_modelo)
    ruta_json.write_text(
        json.dumps(resultado["metadatos"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    m = resultado["metadatos"]
    if args.fuente != "historico_real":
        print("=" * 70)
        print("[AVISO]", AVISO_NO_RESULTADO)
        print("=" * 70)
    print(
        f"Datos: {args.data} ({args.fuente}) | n={m['n_total']} | tasa positivos={m['tasa_positivos']}"
    )
    print(f"CV (k={K_FOLDS}, sobre train):", m["validacion_cruzada_k5_sobre_train"])
    print(
        "Holdout 20%:",
        {k: v for k, v in m["holdout_20pct"].items() if k != "matriz_confusion"},
    )
    print("Matriz de confusión:", m["holdout_20pct"]["matriz_confusion"]["valores"])
    print(
        "Importancia (permutación, f1):", m["importancia_variables"]["permutacion_f1"]
    )
    print(f"[OK] {ruta_modelo}")
    print(f"[OK] {ruta_json}")


if __name__ == "__main__":
    main()
