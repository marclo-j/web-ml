"""Carga del Random Forest entrenado (ml/train.py) y predicción.

Junto al .joblib está el .json de metadatos que escribe train.py: de ahí salen
la versión, las métricas y los umbrales de nivel (decisión D9), para que el
backend use siempre los del modelo con que se predice.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

FEATURES = ["promedio", "pct_asistencia", "pct_reuniones"]


@dataclass
class ModeloRiesgo:
    estimador: object
    metadatos: dict
    version: str

    @property
    def umbrales(self) -> dict[str, float]:
        return self.metadatos["umbrales_nivel_riesgo"]

    def nivel(self, probabilidad: float) -> str:
        if probabilidad >= self.umbrales["alto"]:
            return "alto"
        if probabilidad >= self.umbrales["medio"]:
            return "medio"
        return "bajo"

    def predecir(self, indicadores: dict[str, float]) -> tuple[float, str]:
        fila = pd.DataFrame([[indicadores[f] for f in FEATURES]], columns=FEATURES)
        probabilidad = round(float(self.estimador.predict_proba(fila)[0, 1]), 4)
        return probabilidad, self.nivel(probabilidad)


def cargar_modelo(ruta: Path) -> ModeloRiesgo:
    ruta_json = ruta.with_suffix(".json")
    if not ruta.is_file() or not ruta_json.is_file():
        raise FileNotFoundError(
            f"Falta {ruta.name} o {ruta_json.name} en {ruta.parent}"
        )
    metadatos = json.loads(ruta_json.read_text(encoding="utf-8"))
    if metadatos.get("features") != FEATURES:
        raise ValueError(
            f"El modelo usa {metadatos.get('features')}, se esperaba {FEATURES}"
        )
    version = ruta.stem.removeprefix("rf_")
    return ModeloRiesgo(joblib.load(ruta), metadatos, f"rf_{version}")
