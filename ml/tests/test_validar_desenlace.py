"""Pruebas de ml/validar_desenlace.py con datos simulados (nunca datos reales)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validar_desenlace import metricas, unir_fichas, validar

UMBRALES = {"medio": 0.2, "alto": 0.5}


def ficha(valores: dict, nombre: str) -> pd.Series:
    return pd.Series(valores, name=nombre, dtype=float)


def test_unir_fichas_coincidentes_descarta_vacios():
    v = {"EST-001": 0, "EST-002": 1, "EST-003": None}
    df = unir_fichas([ficha(v, "f1"), ficha(v, "f2"), ficha(v, "f3")])
    assert df["deserto"].to_dict() == {"EST-001": 0, "EST-002": 1}


def test_unir_fichas_discordantes_falla():
    a = ficha({"EST-001": 0}, "f1")
    b = ficha({"EST-001": 1}, "f2")
    with pytest.raises(SystemExit):
        unir_fichas([a, b, a.rename("f3")])


def test_unir_fichas_valor_invalido_falla():
    a = ficha({"EST-001": 2}, "f1")
    with pytest.raises(SystemExit):
        unir_fichas([a, a.rename("f2"), a.rename("f3")])


def test_metricas_matriz_y_tasas():
    y = pd.Series([1, 1, 0, 0, 0, 0])
    p = pd.Series([0.9, 0.3, 0.6, 0.1, 0.1, 0.2])
    m = metricas(y, p, 0.5)
    assert (m["VP"], m["FN"], m["FP"], m["VN"]) == (1, 1, 1, 3)
    assert m["recall"] == 0.5 and m["precision"] == 0.5


def test_validar_cuenta_desertores_por_nivel_y_grupo():
    df = pd.DataFrame(
        {
            "deserto": [1, 1, 0, 0],
            "probabilidad": [0.9, 0.3, 0.1, 0.05],
            "nivel": ["alto", "medio", "bajo", "bajo"],
            "grupo": ["control", "control", "experimental", "experimental"],
        }
    )
    t = validar(df, UMBRALES)
    todos = t[(t.ambito == "Todos") & (t.criterio == "nivel alto")].iloc[0]
    assert todos.alumnos_en_nivel == 1 and todos.desertores_en_nivel == 1
    assert set(t.ambito) == {"Todos", "Control", "Experimental"}
    auc_exp = t[(t.ambito == "Experimental") & (t.criterio == "AUC")].iloc[0]["auc"]
    assert pd.isna(auc_exp)  # una sola clase: sin AUC
