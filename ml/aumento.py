"""
aumento.py

Aumento de datos del histórico, decisión D8 de docs/MODELO.md. Dos métodos:

- smote: interpolación intra-clase (Chawla et al., 2002). Cada registro
  sintético se crea entre un alumno real y uno de sus k vecinos más cercanos
  de la misma clase (`deserto`).
- ctgan: red generativa adversarial para datos tabulares (Xu et al., 2019).
  Un generador crea registros y un discriminador intenta distinguirlos de los
  reales; se muestrea condicionando por `deserto`.

Ambos conservan la proporción de desertores y el rango de cada indicador.

Regla metodológica: el aumento solo se aplica a los datos con los que el
modelo se entrena (cada partición de entrenamiento de la validación cruzada y
el 80 % del holdout). Las métricas se calculan siempre sobre alumnos reales;
si se evaluara sobre sintéticos, el modelo se calificaría con datos que salen
de su propio conjunto de entrenamiento y las métricas saldrían infladas.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors

# Rango válido de cada indicador (docs/VARIABLES.md)
RANGOS = {"promedio": (0, 20), "pct_asistencia": (0, 100), "pct_reuniones": (0, 100)}
K_VECINOS = 5
METODOS = ("smote", "ctgan")

# CTGAN: con ~100 registros el batch por defecto (500) daría 1 paso por época.
# El batch debe ser múltiplo de PAC (registros que el discriminador ve juntos).
CTGAN_EPOCAS = 300
CTGAN_BATCH = 50
CTGAN_PAC = 10


def generar_sinteticos(
    x: pd.DataFrame,
    y: pd.Series,
    factor: float,
    k: int = K_VECINOS,
    semilla: int = 42,
    metodo: str = "smote",
) -> tuple[pd.DataFrame, pd.Series]:
    """Devuelve solo los registros sintéticos: round(factor × n) por clase."""
    if metodo not in METODOS:
        raise ValueError(f"método de aumento {metodo!r} no es uno de {METODOS}")
    x = pd.DataFrame(x).reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True)
    por_clase = {
        clase: round(factor * int((y == clase).sum())) for clase in sorted(y.unique())
    }
    por_clase = {c: n for c, n in por_clase.items() if n > 0 and (y == c).sum() >= 2}
    if not por_clase:
        return x.iloc[:0].copy(), y.iloc[:0].copy()

    if metodo == "smote":
        bloques_x = _smote(x, y, por_clase, k, semilla)
    else:
        bloques_x = _ctgan(x, y, por_clase, semilla)

    sinteticos = pd.DataFrame(np.vstack(bloques_x), columns=x.columns)
    for columna, (minimo, maximo) in RANGOS.items():
        if columna in sinteticos:
            sinteticos[columna] = sinteticos[columna].clip(minimo, maximo).round(2)
    etiquetas = np.concatenate([np.full(n, c) for c, n in por_clase.items()])
    return sinteticos, pd.Series(etiquetas, name=y.name).astype(int)


def _smote(x, y, por_clase, k, semilla) -> list[np.ndarray]:
    rng = np.random.default_rng(semilla)
    bloques = []
    for clase, n_nuevos in por_clase.items():
        reales = x[y == clase].to_numpy(dtype=float)
        vecinos = min(k, len(reales) - 1)
        nn = NearestNeighbors(n_neighbors=vecinos + 1).fit(reales)
        _, indices = nn.kneighbors(reales)  # la columna 0 es el propio alumno
        base = rng.integers(0, len(reales), n_nuevos)
        elegido = indices[base, rng.integers(1, vecinos + 1, n_nuevos)]
        u = rng.random((n_nuevos, 1))
        bloques.append(reales[base] + u * (reales[elegido] - reales[base]))
    return bloques


def _ctgan(x, y, por_clase, semilla) -> list[np.ndarray]:
    from ctgan import CTGAN  # importa torch: solo se carga si se usa

    objetivo = y.name or "deserto"
    tabla = x.assign(**{objetivo: y.astype(int).astype(str).to_numpy()})
    modelo = CTGAN(
        epochs=CTGAN_EPOCAS,
        batch_size=CTGAN_BATCH,
        pac=CTGAN_PAC,
        enable_gpu=False,
    )
    modelo.set_random_state(semilla)
    modelo.fit(tabla, discrete_columns=[objetivo])

    bloques = []
    for clase, n_nuevos in por_clase.items():
        filas = []
        # El muestreo condicional no garantiza la clase en cada fila: se filtra
        while sum(len(f) for f in filas) < n_nuevos:
            muestra = modelo.sample(
                max(n_nuevos, 50),
                condition_column=objetivo,
                condition_value=str(int(clase)),
            )
            filas.append(muestra[muestra[objetivo] == str(int(clase))])
        bloques.append(
            pd.concat(filas)[list(x.columns)].to_numpy(dtype=float)[:n_nuevos]
        )
    return bloques


class RFAumentado(ClassifierMixin, BaseEstimator):
    """Random Forest que aumenta sus datos de entrenamiento al hacer fit.

    Como el aumento ocurre dentro de fit, cross_validate lo aplica solo a la
    partición de entrenamiento de cada fold y evalúa sobre reales.
    """

    def __init__(
        self,
        factor=1.0,
        k_vecinos=K_VECINOS,
        semilla=42,
        hiperparametros=None,
        metodo="smote",
    ):
        self.factor = factor
        self.k_vecinos = k_vecinos
        self.semilla = semilla
        self.hiperparametros = hiperparametros
        self.metodo = metodo

    def fit(self, x, y):
        x = pd.DataFrame(x).reset_index(drop=True)
        y = pd.Series(y).reset_index(drop=True)
        x_sint, y_sint = generar_sinteticos(
            x, y, self.factor, self.k_vecinos, self.semilla, self.metodo
        )
        self.n_reales_ = len(x)
        self.n_sinteticos_ = len(x_sint)
        self.sinteticos_ = x_sint.assign(**{y.name or "deserto": y_sint.to_numpy()})
        self.modelo_ = RandomForestClassifier(**(self.hiperparametros or {}))
        self.modelo_.fit(
            pd.concat([x, x_sint], ignore_index=True),
            pd.concat([y, y_sint], ignore_index=True),
        )
        self.classes_ = self.modelo_.classes_
        self.feature_importances_ = self.modelo_.feature_importances_
        return self

    def predict(self, x):
        return self.modelo_.predict(x)

    def predict_proba(self, x):
        return self.modelo_.predict_proba(x)
