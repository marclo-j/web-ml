"""Pruebas de stats/analisis.py con datos simulados (nunca datos reales)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analisis import comparar, contraste, descriptivos, intragrupo, niveles, normalidad


def simulado(momento="pre", desplazamiento=0.0, semilla=0) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    filas = []
    for grupo, n in (("control", 35), ("experimental", 34)):
        extra = desplazamiento if grupo == "experimental" else 0
        for i in range(n):
            filas.append(
                {
                    "codigo": f"EST-{grupo[0]}{i:03d}",
                    "grupo": grupo,
                    "momento": momento,
                    "promedio": float(np.clip(rng.normal(14 + extra, 2), 0, 20)),
                    "pct_asistencia": float(
                        np.clip(rng.normal(70 + 10 * extra, 15), 0, 100)
                    ),
                    "pct_reuniones": float(rng.choice([0, 50, 100])),
                    "nivel": rng.choice(["bajo", "medio", "alto"], p=[0.8, 0.15, 0.05]),
                }
            )
    return pd.DataFrame(filas)


def test_tablas_pre_tienen_las_filas_del_plan():
    df = simulado()
    assert len(descriptivos(df)) == 3 * 2  # indicador x grupo
    assert len(normalidad(df)) == 3 * 2
    tabla = niveles(df)
    assert list(tabla.n) == [35, 34]
    assert (tabla[["bajo", "medio", "alto"]].sum(axis=1) == tabla.n).all()
    assert len(contraste(df)) == 4  # 3 indicadores + nivel ordinal


def test_comparar_elige_prueba_segun_normalidad():
    rng = np.random.default_rng(1)
    normal_a, normal_b = (pd.Series(rng.normal(10, 1, 40)) for _ in range(2))
    assert comparar(normal_a, normal_b)["prueba"].startswith("t de")
    sesgada = pd.Series(rng.exponential(1, 40))
    assert comparar(normal_a, sesgada)["prueba"] == "U de Mann-Whitney"
    assert comparar(normal_a, normal_b, ordinal=True)["prueba"] == "U de Mann-Whitney"


def test_contraste_detecta_diferencia_en_post():
    df = pd.concat([simulado("pre", 0, 2), simulado("post", 3, 3)], ignore_index=True)
    tabla = contraste(df).set_index(["momento", "variable"])
    assert tabla.loc[("post", "Promedio de calificaciones"), "p"] < 0.05
    assert len(tabla) == 8


def test_intragrupo_empareja_por_codigo():
    df = pd.concat([simulado("pre", 0, 4), simulado("post", 0, 5)], ignore_index=True)
    tabla = intragrupo(df)
    assert set(tabla.n_pares) == {35, 34}


@pytest.mark.parametrize("desplazamiento", [0, 3])
def test_tamano_del_efecto_r_entre_0_y_1(desplazamiento):
    df = simulado("pre", desplazamiento, 6)
    r = contraste(df).query("prueba == 'U de Mann-Whitney'").valor_efecto
    assert ((r >= 0) & (r <= 1)).all()
