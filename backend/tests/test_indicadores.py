"""La copia del backend da exactamente lo mismo que ml/preprocess.py."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from app.services import indicadores as backend

RUTA_ML = Path(__file__).resolve().parents[2] / "ml" / "preprocess.py"


@pytest.fixture(scope="module")
def ml():
    pytest.importorskip("openpyxl")
    spec = importlib.util.spec_from_file_location("preprocess_ml", RUTA_ML)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_mismos_resultados_que_ml(ml):
    rng = np.random.default_rng(0)
    for _ in range(2000):
        n = int(rng.integers(1, 11))
        dp, rt = int(rng.integers(1, 60)), int(rng.integers(1, 6))
        args = {
            "suma_notas": round(float(rng.uniform(0, 20 * n)), 1),
            "n_notas": n,
            "dias_asistidos": int(rng.integers(0, dp + 1)),
            "dias_programados": dp,
            "reuniones_asistidas": int(rng.integers(0, rt + 1)),
            "reuniones_programadas": rt,
        }
        assert backend.calcular_indicadores(**args) == ml.calcular_indicadores(**args)


@pytest.mark.parametrize(
    "cambio, mensaje",
    [
        ({"n_notas": 0}, "n_notas"),
        ({"dias_asistidos": 50}, "dias_asistidos > dias_programados"),
        ({"reuniones_asistidas": 3}, "reuniones_asistidas > reuniones_programadas"),
        ({"suma_notas": 250}, "fuera de la escala"),
    ],
)
def test_mismos_errores_que_ml(ml, cambio, mensaje):
    args = {
        "suma_notas": 140,
        "n_notas": 10,
        "dias_asistidos": 40,
        "dias_programados": 45,
        "reuniones_asistidas": 1,
        "reuniones_programadas": 2,
        **cambio,
    }
    with pytest.raises(backend.ErrorValidacion, match=mensaje):
        backend.calcular_indicadores(**args)
    with pytest.raises(ml.ErrorValidacion, match=mensaje):
        ml.calcular_indicadores(**args)
