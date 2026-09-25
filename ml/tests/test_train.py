"""Pruebas de ml/train.py."""

import pandas as pd
import pytest
from train import (
    FEATURES,
    TARGET,
    UMBRAL_ALTO,
    UMBRAL_MEDIO,
    cargar_datos,
    entrenar,
    nivel_desde_probabilidad,
)


@pytest.mark.parametrize(
    "p, esperado",
    [
        (0.0, "bajo"),
        (UMBRAL_MEDIO - 0.01, "bajo"),
        (UMBRAL_MEDIO, "medio"),
        (UMBRAL_ALTO - 0.01, "medio"),
        (UMBRAL_ALTO, "alto"),
        (1.0, "alto"),
    ],
)
def test_nivel_desde_probabilidad(p, esperado):
    assert nivel_desde_probabilidad(p) == esperado


def test_cargar_datos_descarta_filas_incompletas(tmp_path):
    ruta = tmp_path / "datos.csv"
    pd.DataFrame(
        [
            {"promedio": 15, "pct_asistencia": 90, "pct_reuniones": 100, "deserto": 0},
            {
                "promedio": None,
                "pct_asistencia": 90,
                "pct_reuniones": 100,
                "deserto": 1,
            },
        ]
    ).to_csv(ruta, index=False)
    x, y = cargar_datos(ruta)
    assert len(x) == 1 and list(x.columns) == FEATURES and y.name == TARGET


def test_cargar_datos_columnas_faltantes(tmp_path):
    ruta = tmp_path / "datos.csv"
    pd.DataFrame([{"promedio": 15}]).to_csv(ruta, index=False)
    with pytest.raises(SystemExit, match="Faltan columnas"):
        cargar_datos(ruta)


def test_entrenar_extremo_a_extremo(tmp_path):
    """Dataset sintético pequeño pero con señal real: el pipeline corre y
    guarda el aviso de 'no es resultado' para fuentes que no son el histórico."""
    import numpy as np

    rng = np.random.default_rng(0)
    filas = []
    for _ in range(120):
        riesgo = rng.random()
        promedio = max(0, min(20, rng.normal(16 - 8 * riesgo, 2)))
        asistencia = max(0, min(100, rng.normal(95 - 40 * riesgo, 8)))
        reuniones = max(0, min(100, rng.normal(90 - 50 * riesgo, 15)))
        deserto = int(rng.random() < riesgo * 0.7)
        filas.append(
            {
                "promedio": promedio,
                "pct_asistencia": asistencia,
                "pct_reuniones": reuniones,
                "deserto": deserto,
            }
        )
    ruta = tmp_path / "sintetico.csv"
    pd.DataFrame(filas).to_csv(ruta, index=False)

    resultado = entrenar(ruta, fuente="sintetico")
    m = resultado["metadatos"]
    assert m["fuente_datos"] == "sintetico"
    assert "aviso" in m
    assert 0 <= m["holdout_20pct"]["accuracy"] <= 1
    assert set(m["importancia_variables"]["mdi_gini"]) == set(FEATURES)
    assert sum(m["distribucion_niveles_en_holdout"].values()) == m["n_test"]

    resultado_real = entrenar(ruta, fuente="historico_real")
    assert "aviso" not in resultado_real["metadatos"]
