"""Fixtures: app con SQLite en memoria, un modelo pequeño entrenado aquí con
datos inventados (no se usa el modelo real ni datos de alumnos) y un usuario de
prueba que inicia sesión por /auth/login."""

import json
import sys
import time
from pathlib import Path

import joblib
import jwt
import numpy as np
import pandas as pd
import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import auth
from app.auth import EMISOR
from app.config import Config
from app.crear_usuario import guardar_usuario
from app.main import crear_app

SECRETO = "secreto-de-prueba-que-no-es-real-0123456789"
EMAIL = "tutor@ie.test"
PASSWORD = "clave-de-prueba-123"  # solo existe en la base en memoria de las pruebas
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
        "jwt_secret": SECRETO,
        "auth_desactivada": False,
        "cors_origins": ["http://localhost:3000"],
    }
    return Config(**{**valores, **cambios})


@pytest.fixture(autouse=True)
def hasher_rapido(monkeypatch):
    """Argon2id con parámetros mínimos: las pruebas no miden su costo."""
    monkeypatch.setattr(
        auth, "_hasher", PasswordHasher(time_cost=1, memory_cost=64, parallelism=1)
    )


@pytest.fixture
def crear_cliente(ruta_modelo):
    def fabrica(**cambios) -> TestClient:
        return TestClient(crear_app(_config(ruta_modelo, **cambios)))

    return fabrica


def crear_usuario(cliente: TestClient, email=EMAIL, password=PASSWORD, rol="tutor"):
    with cliente.app.state.sesiones() as sesion:
        guardar_usuario(sesion, email, password, rol)


def iniciar_sesion(cliente: TestClient, email=EMAIL, password=PASSWORD):
    return cliente.post("/auth/login", data={"username": email, "password": password})


def token_firmado(secreto=SECRETO, **cambios) -> str:
    datos = {
        "sub": "00000000-0000-0000-0000-000000000001",
        "iss": EMISOR,
        "exp": int(time.time()) + 3600,
        **cambios,
    }
    return jwt.encode(datos, secreto, algorithm="HS256")


@pytest.fixture
def cliente(crear_cliente) -> TestClient:
    """Cliente con sesión iniciada como tutor."""
    c = crear_cliente()
    crear_usuario(c)
    r = iniciar_sesion(c)
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
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
