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


def test_proporcion_aumenta_solo_la_minoritaria():
    x, y = _datos()
    x_s, y_s = generar_sinteticos(x, y, factor=0, proporcion=0.4)
    assert (y_s == 1).all()  # la clase 0 es la mayoritaria: no se toca
    desertores = (y == 1).sum() + len(x_s)
    assert abs(desertores / (len(y) + len(x_s)) - 0.4) < 0.02
    assert x_s["promedio"].between(0, 20).all()


def test_proporcion_no_genera_si_ya_se_cumple():
    x, y = _datos()
    x_s, _ = generar_sinteticos(x, y, factor=0, proporcion=0.05)
    assert len(x_s) == 0


def test_proporcion_invalida():
    import pytest

    x, y = _datos()
    with pytest.raises(ValueError, match="proporción objetivo"):
        generar_sinteticos(x, y, factor=0, proporcion=1.0)


def test_cv_con_proporcion_evalua_solo_sobre_reales():
    x, y = _datos()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    modelo = RFAumentado(
        factor=0, proporcion=0.4, hiperparametros={"n_estimators": 20, "random_state": 0}
    )
    r = cross_validate(modelo, x, y, cv=cv, return_estimator=True, return_indices=True)
    for est, test in zip(r["estimator"], r["indices"]["test"]):
        assert est.n_reales_ == len(x) - len(test)
        assert est.n_sinteticos_ > 0


def test_proporcion_mas_factor_refuerza_y_conserva_el_equilibrio():
    x, y = _datos()
    x_s, y_s = generar_sinteticos(x, y, factor=1, proporcion=0.4)
    d = (y == 1).sum() + (y_s == 1).sum()
    n = (y == 0).sum() + (y_s == 0).sum()
    assert abs(d / (d + n) - 0.4) < 0.02  # sigue en 40 %
    assert (y_s == 0).sum() == (y == 0).sum()  # x1 de la mayoritaria
    assert (y_s == 1).sum() > (y == 1).sum()


def test_entrenar_proporcion_registra_metadatos(tmp_path):
    x, y = _datos(n=80)
    ruta = tmp_path / "hist.csv"
    x.assign(**{TARGET: y}).to_csv(ruta, index=False)
    m = entrenar(ruta, "sintetico", proporcion=0.4)["metadatos"]["aumento"]
    assert m["proporcion_objetivo"] == 0.4 and m["n_sinteticos_en_train"] > 0


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


def test_submuestreo_acerca_clases_sin_tocar_la_minoritaria():
    from aumento import submuestrear_mayoritaria

    x, y = _datos()
    x2, y2 = submuestrear_mayoritaria(x, y, 0.4, semilla=1)
    assert (y2 == 1).sum() == (y == 1).sum()
    assert abs((y2 == 1).mean() - 0.4) < 0.03
    assert len(x2) == len(y2) < len(y)


def test_opcion_b_reduce_y_luego_genera():
    x, y = _datos()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    modelo = RFAumentado(
        proporcion_previa=0.3,
        proporcion=0.4,
        hiperparametros={"n_estimators": 20, "random_state": 0},
    )
    r = cross_validate(modelo, x, y, cv=cv, return_estimator=True, return_indices=True)
    for est, test in zip(r["estimator"], r["indices"]["test"]):
        assert est.n_reales_ < est.n_reales_disponibles_ == len(x) - len(test)
        assert est.n_sinteticos_ > 0


def test_proporcion_exacta_sin_error_de_coma_flotante():
    """0.4/0.6 × 57 = 38.00000000000001 no debe redondearse a 39."""
    y = pd.Series([1] * 13 + [0] * 57, name=TARGET)
    x = pd.DataFrame(np.random.default_rng(0).random((70, 3)) * 10, columns=FEATURES)
    x_s, _ = generar_sinteticos(x, y, factor=0, proporcion=0.4)
    assert len(x_s) == 25
