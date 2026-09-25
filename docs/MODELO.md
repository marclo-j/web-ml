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
| ✅ **A (preferida)** | Alumnos de 2024–2025 con desenlace conocido. La IE reporta 29 % y 35 % de deserción esos años, por lo que el registro existe | ⬜ Solicitada a la IE (2026-09-25); no la entregó |
| ⚠️ B (respaldo, en uso para el avance) | Etiquetar por reglas de umbral tomadas de la literatura, sobre los datos PRE 2026 reales (69 alumnos) | 🟨 En uso — `ml/etiquetar_umbral.py` → `rf_v0b` |

> ⚠️ Con la opción B el modelo solo aprende a reproducir las reglas con que se etiquetó. Las métricas saldrían altas pero no demostrarían capacidad predictiva real. Si se usa, debe declararse como limitación en la tesis.
>
> **Esto se confirmó empíricamente**, no solo en teoría: `rf_v0b` (abajo) dio accuracy = 1.0 en el holdout. Es la prueba de que el modelo aprendió la regla de umbral, no un patrón de deserción real — el motivo exacto por el que la Opción A sigue siendo necesaria.

### Umbrales de la Opción B
Un alumno se etiqueta `deserto = 1` (en riesgo, solo para entrenar) si cumple **cualquiera** de estas 3 reglas — no son inventadas, cada una tiene una fuente:

| Regla | Umbral | Fuente |
|---|---|---|
| Rendimiento | `promedio` < 11 | Nota mínima aprobatoria en la escala vigesimal peruana (RVM N.° 094-2020-MINEDU, misma norma de la decisión D1) |
| Asistencia | `pct_asistencia` < 85 % | Absentismo crónico de alto riesgo: Balfanz y Byrnes [40], difundido por Attendance Works / U.S. Dept. of Education — investigación en EE. UU., se declara como adaptación al no encontrarse una cifra específica para secundaria peruana |
| Apoyo familiar | `pct_reuniones` < 50 % | **Umbral operacional del autor** (participación por debajo de la mitad de las reuniones); no proviene de una cifra publicada — pendiente de validar con el asesor |

El propio MINEDU usa un enfoque análogo (rendimiento + asistencia con ML) en su sistema **Alerta Escuela**, sobre SIAGIE [41], lo que respalda el enfoque general aunque no publica el umbral numérico exacto.

> ❓ **[40] y [41] son números provisionales** (siguientes disponibles a falta de ver la bibliografía completa de la tesis): al incorporar esto al documento, verificar que no choquen con una cita ya asignada y agregar las referencias:
> - [40] R. Balfanz y J. Byrnes, "Chronic Absenteeism: A Significant, Overlooked Challenge to Student Success", Everyone Graduates Center / Attendance Works.
> - [41] Ministerio de Educación del Perú, "Alerta Escuela — sistema de alerta temprana", SIAGIE. Disponible: https://alertaescuela.minedu.gob.pe/

Script: `ml/etiquetar_umbral.py --entrada data/processed/2026_pre.csv --salida data/processed/2026_pre_opcion_b.csv`.

**Periodo de corte y fuga de información (decisión D3):** los indicadores del histórico se calculan con datos acumulados solo hasta el cierre del I bimestre, igual que el PRE 2026. Si se usara el año completo, un alumno que desertó a mitad de año tendría menos días asistidos y menos notas *porque ya se había ido*: el modelo aprendería la consecuencia de la deserción y no sus señales tempranas, y las métricas saldrían infladas.

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

## Entrenamiento (`ml/train.py`)
```bash
ml/.venv/Scripts/python ml/train.py --data <csv_con_indicadores_y_deserto> --version <vN> --fuente {historico_real,opcion_b,sintetico}
```
`--fuente` es obligatorio: solo `historico_real` se puede citar en Resultados; con `opcion_b` o `sintetico` el script imprime la advertencia y la deja escrita en el `.json`. Holdout 80/20 + CV k=5 sobre el train, con los hiperparámetros de este documento. Si los datos vienen en crudo (`suma_notas`, `dias_asistidos`…) en vez de indicadores ya calculados, primero: `ml/calcular_indicadores.py`.

## Registro de versiones
| Versión | Fecha | Datos | n | Accuracy | Precision | Recall | F1 | Nota |
|---|---|---|---|---|---|---|---|---|
| rf_v0 | 2026-09-25 | sintéticos (300, histórico simulado con ruido) | 300 | 0.42 | 0.24 | 0.35 | 0.29 | Solo prueba de pipeline; el generador agrega ruido a propósito, no se espera buen desempeño |
| rf_v0b | 2026-09-25 | PRE 2026 real (69 alumnos) + Opción B (umbral) | 69 | 1.00 | 1.00 | 1.00 | 1.00 | **No es resultado.** Confirma la advertencia de la Opción B: el modelo reproduce la regla de etiquetado, no aprende deserción real |

Cada versión se guarda como `ml/models/rf_vN.joblib` + `rf_vN.json` (features, hiperparámetros, CV, holdout, matriz de confusión, importancia de variables, fecha, umbrales; con aviso si `fuente_datos` ≠ `historico_real`). No versionados (`ml/models/` solo tiene el `.gitkeep`).

## Notas técnicas
- scikit-learn ≥ 1.4 admite valores nulos en Random Forest, pero los registros incompletos se **excluyen** igual por el criterio de exclusión de la tesis.
- Random Forest no requiere escalar las features.
