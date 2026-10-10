"""Fixtures: app con SQLite en memoria, un modelo pequeño entrenado aquí con
datos inventados (no se usa el modelo real ni datos de alumnos) y tokens HS256
firmados con un secreto de prueba."""

import json
import sys
import time
from pathlib import Path

import joblib
import jwt
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Config
from app.main import crear_app

SECRETO = "secreto-de-prueba-que-no-es-real-0123456789"
FEATURES = ["promedio", "pct_asistencia", "pct_reuniones"]


@pytest.fixture(scope="session")
def ruta_modelo(tmp_path_factory) -> Path:
    rng = np.random.default_rng(0)
    n = 200
    y = (rng.random(n) < 0.3).astype(int)
    x = pd.DataFrame(
        {
            "promedio": np.where(
                y == 1, rng.normal(10, 1.5, n), rng.normal(15, 1.5, n)
            ),
            "pct_asistencia": np.where(
                y == 1, rng.normal(30, 10, n), rng.normal(85, 8, n)
            ),
            "pct_reuniones": np.where(y == 1, 0, rng.choice([50, 100], n)),
        }
    )
    modelo = RandomForestClassifier(n_estimators=50, random_state=0).fit(x, y)
    carpeta = tmp_path_factory.mktemp("modelos")
    joblib.dump(modelo, carpeta / "rf_test.joblib")
    (carpeta / "rf_test.json").write_text(
        json.dumps(
            {
                "fecha": "2026-10-10",
                "fuente_datos": "sintetico",
                "features": FEATURES,
                "n_total": n,
                "umbrales_nivel_riesgo": {"medio": 0.15, "alto": 0.5},
                "holdout_20pct": {"f1": 0.9},
                "aviso": "solo pruebas",
            }
        ),
        encoding="utf-8",
    )
    return carpeta / "rf_test.joblib"


def _config(ruta_modelo: Path, **cambios) -> Config:
    valores = {
        "database_url": "sqlite://",
        "model_path": ruta_modelo,
        "supabase_url": "",
        "supabase_jwt_secret": SECRETO,
        "auth_desactivada": False,
        "cors_origins": ["http://localhost:3000"],
    }
    return Config(**{**valores, **cambios})


@pytest.fixture
def crear_cliente(ruta_modelo):
    def fabrica(**cambios) -> TestClient:
        return TestClient(crear_app(_config(ruta_modelo, **cambios)))

    return fabrica


def token(**cambios) -> str:
    datos = {
        "sub": "usuario-1",
        "email": "tutor@ejemplo.test",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
        "app_metadata": {"rol": "tutor"},
        **cambios,
    }
    return jwt.encode(datos, SECRETO, algorithm="HS256")


@pytest.fixture
def cliente(crear_cliente) -> TestClient:
    """Cliente autenticado como tutor."""
    c = crear_cliente()
    c.headers["Authorization"] = f"Bearer {token()}"
    return c


CRUDOS_BAJO = {
    "suma_notas": 160,
    "n_notas": 10,
    "dias_asistidos": 44,
    "dias_programados": 45,
    "reuniones_asistidas": 2,
    "reuniones_programadas": 2,
}
CRUDOS_ALTO = {
    "suma_notas": 95,
    "n_notas": 10,
    "dias_asistidos": 9,
    "dias_programados": 45,
    "reuniones_asistidas": 0,
    "reuniones_programadas": 2,
}
