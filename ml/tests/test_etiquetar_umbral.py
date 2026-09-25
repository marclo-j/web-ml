"""Pruebas de ml/etiquetar_umbral.py."""

import pandas as pd
import pytest
from etiquetar_umbral import (
    UMBRAL_ASISTENCIA,
    UMBRAL_PROMEDIO,
    UMBRAL_REUNIONES,
    etiquetar,
)


def fila(promedio=15, pct_asistencia=95, pct_reuniones=100):
    return {
        "promedio": promedio,
        "pct_asistencia": pct_asistencia,
        "pct_reuniones": pct_reuniones,
    }


def test_sin_ninguna_regla_no_esta_en_riesgo():
    df = pd.DataFrame([fila()])
    salida = etiquetar(df)
    assert salida.iloc[0]["deserto"] == 0
    assert salida.iloc[0]["deserto_metodo"] == "opcion_b_umbral"


@pytest.mark.parametrize(
    "cambio",
    [
        {"promedio": UMBRAL_PROMEDIO - 1},
        {"pct_asistencia": UMBRAL_ASISTENCIA - 1},
        {"pct_reuniones": UMBRAL_REUNIONES - 1},
    ],
)
def test_cualquier_regla_marca_riesgo(cambio):
    df = pd.DataFrame([fila(**cambio)])
    assert etiquetar(df).iloc[0]["deserto"] == 1


def test_en_el_limite_no_esta_en_riesgo():
    """Los umbrales son estrictos (<), el valor exacto no cuenta como riesgo."""
    df = pd.DataFrame(
        [
            fila(
                promedio=UMBRAL_PROMEDIO,
                pct_asistencia=UMBRAL_ASISTENCIA,
                pct_reuniones=UMBRAL_REUNIONES,
            )
        ]
    )
    assert etiquetar(df).iloc[0]["deserto"] == 0


def test_columnas_faltantes():
    with pytest.raises(ValueError, match="Faltan columnas"):
        etiquetar(pd.DataFrame([{"promedio": 15}]))


def test_no_pisa_deserto_real_sin_forzar(tmp_path, capsys):
    import subprocess
    import sys

    entrada = tmp_path / "entrada.csv"
    pd.DataFrame([{**fila(), "deserto": 1}]).to_csv(entrada, index=False)
    salida = tmp_path / "salida.csv"
    r = subprocess.run(
        check=False,
        args=[
            sys.executable,
            "etiquetar_umbral.py",
            "--entrada",
            str(entrada),
            "--salida",
            str(salida),
        ],
        cwd=__file__.rsplit("tests", 1)[0],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "ya tiene valores reales" in r.stderr
    assert not salida.exists()
