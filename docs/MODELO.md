# 🤖 MODELO — Random Forest

## Planteamiento
| Aspecto | Definición |
|---|---|
| Tipo de aprendizaje | Supervisado (según la tesis [27]) |
| Tarea | Clasificación binaria: `deserto` (0/1) |
| Salida al usuario | `probabilidad` → `nivel_riesgo` (bajo / medio / alto) |
| Features | `promedio`, `pct_asistencia`, `pct_reuniones` |
| Algoritmo | `RandomForestClassifier` (scikit-learn) [28] |

**Por qué binaria y no directo en 3 clases:** el desenlace que la IE sí registra es "desertó o no". Entrenar sobre ese hecho observable y luego escalar la probabilidad en 3 niveles evita inventar etiquetas de "riesgo medio" que nadie registró.

## Datos de entrenamiento
| Opción | Descripción | Estado |
|---|---|---|
| ✅ **A (preferida)** | Alumnos de 2024–2025 con desenlace conocido. La IE reporta 29 % y 35 % de deserción esos años, por lo que el registro existe | ⬜ Solicitar a la IE |
| ⚠️ B (respaldo) | Etiquetar por reglas de umbral tomadas de la literatura | Solo si A no es posible |

> ⚠️ Con la opción B el modelo solo aprende a reproducir las reglas con que se etiquetó. Las métricas saldrían altas pero no demostrarían capacidad predictiva real. Si se usa, debe declararse como limitación en la tesis.

**Periodo de corte y fuga de información (decisión D3):** los indicadores del histórico se calculan con datos acumulados solo hasta el cierre del I bimestre / I trimestre, igual que el PRE 2026. Si se usara el año completo, un alumno que desertó a mitad de año tendría menos días asistidos y menos notas *porque ya se había ido*: el modelo aprendería la consecuencia de la deserción y no sus señales tempranas, y las métricas saldrían infladas.

**Datos sintéticos:** `ml/generate_synthetic.py` genera datos con la misma estructura solo para validar que el pipeline funciona. Nunca se reportan como resultados.

## Configuración inicial
```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=None,          # ajustar con GridSearchCV
    min_samples_leaf=2,
    class_weight="balanced", # clases desbalanceadas (~30 % desertores)
    random_state=42,
)
```
Búsqueda de hiperparámetros (opcional, grilla pequeña por el tamaño de datos): `n_estimators` ∈ {100, 200, 400}, `max_depth` ∈ {None, 3, 5, 8}, `min_samples_leaf` ∈ {1, 2, 4}.

## Validación
- **Holdout estratificado 80/20** para las métricas finales reportadas.
- **Validación cruzada estratificada k = 5** sobre el 80 % para elegir hiperparámetros y reportar media ± desviación estándar.
- `random_state=42` en todo para que sea reproducible.

## Métricas (declaradas en la metodología)
| Métrica | Función | Qué responde |
|---|---|---|
| Accuracy | `accuracy_score` | % de aciertos totales |
| Precision | `precision_score` | De los que marcó en riesgo, cuántos lo estaban |
| Recall | `recall_score` | De los que estaban en riesgo, cuántos detectó (**la más importante**: no dejar escapar casos) |
| F1 | `f1_score` | Balance precision/recall |
| Matriz de confusión | `confusion_matrix` | Tabla base de las 4 anteriores |

Opcional: ROC-AUC (aparece en los antecedentes [3], [14] y sirve para la Discusión).

## Umbrales de nivel de riesgo (provisionales)
| Probabilidad | Nivel | Color UI |
|---|---|---|
| < 0.33 | Bajo | 🟢 |
| 0.33 – < 0.66 | Medio | 🟡 |
| ≥ 0.66 | Alto | 🔴 |

Ajustar después de ver la distribución real de probabilidades y justificar el criterio en la tesis.

## Importancia de variables → sustento de OE1, OE2 y OE3
- `feature_importances_` (MDI, reducción de impureza de Gini)
- `permutation_importance` sobre el conjunto de prueba (más robusta; es la que se reporta)

Cada objetivo específico se sustenta con el peso de su dimensión en la predicción, además del contraste estadístico de `PLAN_ESTADISTICO.md`.

## Registro de versiones
| Versión | Fecha | Datos | n | Accuracy | Precision | Recall | F1 | Nota |
|---|---|---|---|---|---|---|---|---|
| rf_v0 | — | sintéticos | — | — | — | — | — | Solo prueba de pipeline |

Cada versión se guarda como `ml/models/rf_vN.joblib` + `rf_vN.json` (features, hiperparámetros, métricas, fecha, umbrales).

## Notas técnicas
- scikit-learn ≥ 1.4 admite valores nulos en Random Forest, pero los registros incompletos se **excluyen** igual por el criterio de exclusión de la tesis.
- Random Forest no requiere escalar las features.
