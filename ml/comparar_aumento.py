"""
comparar_aumento.py

Compara el Random Forest sin aumento, con SMOTE y con CTGAN (decisión D8,
docs/MODELO.md) para elegir qué método se reporta en la tesis.

Dos criterios, ambos medidos con alumnos reales:
1. Utilidad: validación cruzada estratificada repetida (5 partes × R
   repeticiones). El aumento se aplica solo a la partición de entrenamiento de
   cada fold; AUC, F1, recall, precision y accuracy salen de la partición de
   prueba, que siempre son alumnos reales. Las mismas particiones para los
   tres modelos.
2. Fidelidad: los sintéticos generados con todo el histórico se comparan con
   los reales por clase (media de cada indicador y estadístico KS de dos
   muestras: 0 = misma distribución, 1 = totalmente distinta).

Se elige el método con mejor AUC y F1; si ninguno mejora al modelo sin
aumento, se declara así en la tesis.

Uso:
    python ml/comparar_aumento.py --data data/processed/historico.csv --fuente historico_real
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from aumento import METODOS, generar_sinteticos
from scipy.stats import ks_2samp
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
from train import (
    AVISO_NO_RESULTADO,
    FEATURES,
    FUENTES,
    K_FOLDS,
    SEMILLA,
    cargar_datos,
    crear_modelo,
)

METRICAS = ("roc_auc", "f1", "recall", "precision", "accuracy")


def utilidad(x, y, factor: float, repeticiones: int) -> dict:
    cv = RepeatedStratifiedKFold(
        n_splits=K_FOLDS, n_repeats=repeticiones, random_state=SEMILLA
    )
    configuraciones = {"sin_aumento": crear_modelo(0)}
    for metodo in METODOS:
        configuraciones[metodo] = crear_modelo(factor, metodo)

    resultados = {}
    for nombre, modelo in configuraciones.items():
        print(f"  CV {K_FOLDS}x{repeticiones}: {nombre}...", flush=True)
        r = cross_validate(modelo, x, y, cv=cv, scoring=list(METRICAS))
        resultados[nombre] = {
            m: {
                "media": round(float(np.mean(r[f"test_{m}"])), 4),
                "desviacion": round(float(np.std(r[f"test_{m}"])), 4),
            }
            for m in METRICAS
        }
    return resultados


def fidelidad(x, y, factor: float) -> dict:
    resultado = {}
    for metodo in METODOS:
        print(f"  Fidelidad: {metodo}...", flush=True)
        x_s, y_s = generar_sinteticos(x, y, factor, semilla=SEMILLA, metodo=metodo)
        por_clase = {}
        for clase in (0, 1):
            reales, sint = x[y.to_numpy() == clase], x_s[y_s.to_numpy() == clase]
            por_clase[str(clase)] = {
                f: {
                    "media_real": round(float(reales[f].mean()), 2),
                    "media_sintetico": round(float(sint[f].mean()), 2),
                    "ks": round(float(ks_2samp(reales[f], sint[f]).statistic), 3),
                }
                for f in FEATURES
            }
        resultado[metodo] = por_clase
    return resultado


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--fuente", required=True, choices=FUENTES)
    parser.add_argument("--factor", type=float, default=2, help="Sintéticos por real")
    parser.add_argument("--repeticiones", type=int, default=3)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "models",
        help="Carpeta del JSON de resultados (default: ml/models/)",
    )
    args = parser.parse_args()

    x, y = cargar_datos(args.data)
    print(f"Datos: {args.data} ({args.fuente}) | n={len(x)} | positivos={int(y.sum())}")
    if args.fuente != "historico_real":
        print("[AVISO]", AVISO_NO_RESULTADO)

    salida = {
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "fuente_datos": args.fuente,
        "archivo_datos": str(args.data),
        "n": len(x),
        "positivos": int(y.sum()),
        "factor": args.factor,
        "validacion": f"estratificada {K_FOLDS}x{args.repeticiones}, prueba solo con reales",
        "utilidad": utilidad(x, y, args.factor, args.repeticiones),
        "fidelidad": fidelidad(x, y, args.factor),
    }
    if args.fuente != "historico_real":
        salida["aviso"] = AVISO_NO_RESULTADO

    print(f"\n{'Modelo':<12}" + "".join(f"{m:>18}" for m in METRICAS))
    for nombre, r in salida["utilidad"].items():
        celdas = "".join(
            f"{r[m]['media']:>11.3f} ± {r[m]['desviacion']:.2f}" for m in METRICAS
        )
        print(f"{nombre:<12}{celdas}")
    print("\nFidelidad (KS por clase; 0 = igual a los reales):")
    for metodo, clases in salida["fidelidad"].items():
        for clase, fs in clases.items():
            ks = ", ".join(f"{f} {v['ks']:.2f}" for f, v in fs.items())
            print(f"  {metodo:<6} deserto={clase}: {ks}")

    args.out.mkdir(parents=True, exist_ok=True)
    ruta = args.out / f"comparacion_aumento_{args.fuente}.json"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {ruta}")


if __name__ == "__main__":
    main()
