"""Pruebas de ml/aumento.py y de --aumentar en ml/train.py."""

import numpy as np
import pandas as pd
from aumento import RFAumentado, generar_sinteticos
from sklearn.model_selection import StratifiedKFold, cross_validate
from train import FEATURES, TARGET, entrenar


def _datos(n=60, semilla=0):
    rng = np.random.default_rng(semilla)
    y = pd.Series((rng.random(n) < 0.3).astype(int), name=TARGET)
    x = pd.DataFrame(
        {
            "promedio": np.where(
                y == 1, rng.normal(11, 1.5, n), rng.normal(15, 1.5, n)
            ),
            "pct_asistencia": np.where(
                y == 1, rng.normal(70, 8, n), rng.normal(92, 4, n)
            ),
            "pct_reuniones": rng.uniform(0, 100, n),
        }
    )
    return x, y


def test_sinteticos_conservan_proporcion_y_rangos():
    x, y = _datos()
    x_s, y_s = generar_sinteticos(x, y, factor=2)
    assert len(x_s) == 2 * len(x)
    assert (y_s == 1).sum() == 2 * (y == 1).sum()
    assert x_s["promedio"].between(0, 20).all()
    assert x_s[["pct_asistencia", "pct_reuniones"]].stack().between(0, 100).all()


def test_sinteticos_quedan_dentro_de_su_clase():
    """Interpolar entre vecinos de la misma clase no sale de la caja de esa clase."""
    x, y = _datos()
    x_s, y_s = generar_sinteticos(x, y, factor=3)
    for clase in (0, 1):
        reales, sint = x[y == clase], x_s[y_s.to_numpy() == clase]
        assert (sint.min() >= reales.min() - 1e-9).all()
        assert (sint.max() <= reales.max() + 1e-9).all()


def test_sinteticos_reproducibles():
    x, y = _datos()
    a, _ = generar_sinteticos(x, y, factor=1, semilla=7)
    b, _ = generar_sinteticos(x, y, factor=1, semilla=7)
    pd.testing.assert_frame_equal(a, b)


def test_cv_evalua_solo_sobre_reales():
    """En cada fold, el test tiene el tamaño de la partición real (sin sintéticos)."""
    x, y = _datos()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    modelo = RFAumentado(
        factor=2, hiperparametros={"n_estimators": 20, "random_state": 0}
    )
    resultado = cross_validate(
        modelo, x, y, cv=cv, return_estimator=True, return_indices=True
    )
    for estimador, test in zip(resultado["estimator"], resultado["indices"]["test"]):
        assert estimador.n_reales_ == len(x) - len(test)
        assert estimador.n_sinteticos_ == 2 * estimador.n_reales_


def test_entrenar_con_aumento_registra_metadatos(tmp_path):
    x, y = _datos(n=80)
    ruta = tmp_path / "hist.csv"
    x.assign(**{TARGET: y}).to_csv(ruta, index=False)
    r = entrenar(ruta, "sintetico", aumentar=2)
    m = r["metadatos"]
    assert m["n_test"] == 16 and m["aumento"]["factor"] == 2
    assert m["aumento"]["n_sinteticos_en_train"] == 2 * m["n_train"]
    assert list(r["sinteticos"].columns) == [*FEATURES, TARGET]
    assert entrenar(ruta, "sintetico")["metadatos"]["aumento"] is None


def test_ctgan_conserva_proporcion_y_rangos(monkeypatch):
    """Pocas épocas: solo se prueba la forma de la salida, no su calidad."""
    import aumento

    monkeypatch.setattr(aumento, "CTGAN_EPOCAS", 2)
    x, y = _datos()
    x_s, y_s = generar_sinteticos(x, y, factor=1, metodo="ctgan")
    assert len(x_s) == len(x) and (y_s == 1).sum() == (y == 1).sum()
    assert x_s["promedio"].between(0, 20).all()
    assert x_s[["pct_asistencia", "pct_reuniones"]].stack().between(0, 100).all()


def test_metodo_desconocido():
    import pytest

    x, y = _datos()
    with pytest.raises(ValueError, match="método de aumento"):
        generar_sinteticos(x, y, factor=1, metodo="gan")


def test_rf_aumentado_es_clasificador_para_auc():
    """Sin esto, el scorer roc_auc recibe las 2 columnas de predict_proba."""
    from sklearn.base import is_classifier

    assert is_classifier(RFAumentado())
