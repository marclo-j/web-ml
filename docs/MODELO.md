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
| ✅ **A (en uso)** | Alumnos de años anteriores con desenlace conocido, entregados por la IE | ✅ Histórico 2024 v5 (70 alumnos, 13 desertores) + aumento SMOTE solo en entrenamiento (D8). Ver "Histórico final". Las versiones anteriores (2024–2025, `rf_v1`/`rf_v2`) se descartaron (ver `LOG_AVANCES.md`) |
| ⚠️ B (respaldo, ya no se usa) | Etiquetar por reglas de umbral tomadas de la literatura, sobre los datos PRE 2026 reales (69 alumnos) | Solo prueba de pipeline — `ml/etiquetar_umbral.py` → `rf_v0b` |

> ⚠️ Con la opción B el modelo solo aprende a reproducir las reglas con que se etiquetó. Las métricas saldrían altas pero no demostrarían capacidad predictiva real. Si se usa, debe declararse como limitación en la tesis.
>
> **Esto se confirmó empíricamente**, no solo en teoría: `rf_v0b` (abajo) dio accuracy = 1.0 en el holdout. Es la prueba de que el modelo aprendió la regla de umbral, no un patrón de deserción real — el motivo exacto por el que la Opción A sigue siendo necesaria.

### Histórico final (2024 v5, 2026-10-09)
Archivo: `data/processed/historico.csv` (copia de `2024_pre_v5.csv`; la versión anterior de 140 alumnos quedó en `historico_v1_2024_2025.csv`). CSV para SPSS: `spss_historico_v5.csv`.

| Aspecto | Valor |
|---|---|
| Fuente | Fichas 2024 de la IE (I bimestre, mismo corte que PRE 2026, D3) |
| Registros / incluidos / excluidos | 70 / 70 / 0 (sin traslados, dimensiones incompletas ni registros inconsistentes) |
| Desertores | 13 (18.6 %): 3.° A 6 de 35, 4.° B 7 de 35 |
| Balance | 57 : 13 (≈ 4.4 : 1) → `class_weight="balanced"` + SMOTE x2 en entrenamiento (D8) |
| Datos crudos | 10 notas por alumno, 45 días programados, 2 reuniones programadas (iguales para todos) |

Desertores frente a no desertores (mediana y RIC; U de Mann-Whitney, porque al menos un grupo no es normal en cada indicador; r = correlación biserial de rangos):

| Indicador | Desertó (n = 13) | No desertó (n = 57) | U | p | r |
|---|---|---|---|---|---|
| Promedio | 10.60 (8.80–12.60) | 14.80 (11.90–16.20) | 170.5 | 0.003 | 0.54 |
| % asistencia | 28.89 (17.78–33.33) | 64.44 (57.78–86.67) | 32.5 | < 0.001 | 0.91 |
| % reuniones | 0.00 (0.00–0.00) | 50.00 (0.00–100.00) | 110.5 | < 0.001 | 0.70 |

Limitaciones a declarar: un solo año lectivo y 13 casos positivos; la tasa de la muestra (18.6 %) es menor que la institucional de la realidad problemática (29 % y 35 %); las clases están casi separadas por asistencia y reuniones, por lo que las métricas son cercanas al techo y la validación externa real es el desenlace 2026 (D2).

### Umbrales de la Opción B
Un alumno se etiqueta `deserto = 1` (en riesgo, solo para entrenar) si cumple **cualquiera** de estas 3 reglas — no son inventadas, cada una tiene una fuente:

| Regla | Umbral | Fuente |
|---|---|---|
| Rendimiento | `promedio` < 11 | Nota mínima aprobatoria en la escala vigesimal peruana (RVM N.° 094-2020-MINEDU, misma norma de la decisión D1) |
| Asistencia | `pct_asistencia` < 85 % | Absentismo crónico de alto riesgo: Balfanz y Byrnes [42], difundido por Attendance Works / U.S. Dept. of Education — investigación en EE. UU., se declara como adaptación al no encontrarse una cifra específica para secundaria peruana |
| Apoyo familiar | `pct_reuniones` < 50 % | **Umbral operacional del autor** (participación por debajo de la mitad de las reuniones); no proviene de una cifra publicada. Decisión 2026-10-03: se mantiene en 50 % y se declara como supuesto del autor |

El propio MINEDU usa un enfoque análogo (rendimiento + asistencia con ML) en su sistema **Alerta Escuela** [41] — la misma cita que ya usa la Introducción de la tesis para ese sistema — lo que respalda el enfoque general aunque no publica el umbral numérico exacto.

> ✅ **[42] confirmado por el autor el 2026-10-03** (en el documento se usan del [1] al [41], con el [9] libre — se revisó `CALDERON SALAZAR.docx` el 2026-09-25). [41] ya es Alerta Escuela en la Introducción [línea ~72]. Al escribir Resultados, agregar a Referencias:
> - [42] R. Balfanz y J. Byrnes, "Chronic Absenteeism: A Significant, Overlooked Challenge to Student Success", Everyone Graduates Center / Attendance Works.
>
> La sección Referencias del documento todavía está vacía (solo el título) — revisar también que el [9] no esté reservado para algo antes de reutilizarlo.

Script: `ml/etiquetar_umbral.py --entrada data/processed/2026_pre.csv --salida data/processed/2026_pre_opcion_b.csv`.

**Periodo de corte y fuga de información (decisión D3):** los indicadores del histórico se calculan con datos acumulados solo hasta el cierre del I bimestre, igual que el PRE 2026. Si se usara el año completo, un alumno que desertó a mitad de año tendría menos días asistidos y menos notas *porque ya se había ido*: el modelo aprendería la consecuencia de la deserción y no sus señales tempranas, y las métricas saldrían infladas.

**Datos sintéticos:** `ml/generate_synthetic.py` genera datos con la misma estructura solo para validar que el pipeline funciona. Nunca se reportan como resultados.

**Aumento de datos del histórico (decisión D8, 2026-10-09, avalada por el docente según el autor):** `ml/train.py --aumentar F` agrega F × n registros sintéticos a partir de las fichas históricas reales (`ml/aumento.py`), con `--metodo-aumento smote` (interpolación intra-clase [Chawla et al., 2002]) o `ctgan` (red generativa adversarial tabular [Xu et al., 2019], lo que sugirió el docente). `ml/comparar_aumento.py` compara sin aumento, SMOTE y CTGAN con la misma CV repetida evaluada sobre reales, más la fidelidad de los sintéticos (KS por clase); se reporta el método elegido con esa evidencia. Reglas:
- El aumento se aplica solo al entrenamiento (cada partición de la CV y el 80 % del holdout). CV, holdout, matriz de confusión e importancia de variables se calculan solo sobre alumnos reales; evaluar sobre sintéticos inflaría las métricas.
- Se conserva la proporción de desertores y el rango de cada indicador.
- En la tesis se declara en Metodología (técnica, factor y n reales / n sintéticos) y en Limitaciones. Los sintéticos de cada corrida quedan en `data/processed/sinteticos_rf_<versión>.csv` para el anexo; nunca se presentan como registros de la IE.
- El aumento no corrige etiquetas: `deserto` del histórico real tiene que estar resuelto antes (un valor por alumno, igual en las 3 fichas).
- Falta agregar las referencias de SMOTE (Chawla et al., 2002) y CTGAN (Xu et al., 2019) a la lista IEEE de la tesis al redactar Metodología.
- Base real (2026-10-09): solo 2024 v5 (70 alumnos, 13 desertores); 2025 se descarta. El histórico se completa con aumento, no con un año ficticio.

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

**Resultado (2026-10-10, `ml/tune.py --aumentar 2`, CV anidada 5x2 externa / 5 interna, SMOTE dentro de cada partición de entrenamiento):** la búsqueda no mejora la configuración inicial (ambas: AUC 0.993 ± 0.015, F1 0.899 ± 0.134, recall 0.95 ± 0.15, precision 0.892 ± 0.175, accuracy 0.964 ± 0.048) y la combinación elegida cambia entre folds (6 distintas en 10). Se mantiene la configuración inicial: es la más simple y la grilla no aporta evidencia para cambiarla.

## Validación
- **Métrica principal: validación cruzada estratificada repetida 5x5 sobre los 70 alumnos reales** (`comparar_aumento.py`), media ± desviación. Con 13 positivos, un holdout de 14 alumnos (3 positivos) es demasiado inestable para ser la métrica principal (decisión 2026-10-10).
- **Holdout estratificado 80/20** (`train.py`): se reporta como complemento, con su matriz de confusión.
- **Validación cruzada estratificada k = 5** sobre el 80 % para elegir hiperparámetros.
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

## Umbrales de nivel de riesgo (decisión D9, 2026-10-10)
| Probabilidad | Nivel | Color UI |
|---|---|---|
| < 0.15 | Bajo | 🟢 |
| 0.15 – < 0.50 | Medio | 🟡 |
| ≥ 0.50 | Alto | 🔴 |

Criterio, a partir de las probabilidades fuera de muestra del histórico (cada alumno 2024 predicho por modelos que no lo vieron; CV 5x5 con SMOTE, configuración de `rf_v3`):
- **Alto (≥ 0.50):** es el corte con que el clasificador predice `deserto = 1`, así que el nivel alto coincide con las métricas reportadas. El índice de Youden de la curva ROC da 0.556, cercano. Con este corte se identificaron los 13 desertores con 2 falsos positivos (precision 0.87). Ningún desertor tuvo probabilidad menor a 0.556.
- **Medio (0.15 – < 0.50):** 0.15 ≈ percentil 90 de la probabilidad de los no desertores (0.152): solo 1 de cada 10 alumnos que no desertaron supera ese valor. Es una franja de seguimiento preventivo, no una predicción de deserción.
- **Bajo (< 0.15):** el 90 % de los no desertores del histórico.

Distribución en PRE 2026 con `rf_v3`: control 27 / 7 / 1, experimental 27 / 4 / 3 (bajo / medio / alto).

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
| rf_v3 | 2026-10-09 | Histórico 2024 v5 (70 alumnos, 13 desertores) + SMOTE x2 solo en entrenamiento (D8) | 70 | 0.93 | 0.75 | 1.00 | 0.86 | Holdout de 14 alumnos (3 positivos), inestable. Métrica principal: CV 5x5 sobre reales de `comparar_aumento.py` con SMOTE: AUC 0.993 ± 0.02, F1 0.911 ± 0.13, recall 0.967 ± 0.12, precision 0.893 ± 0.18, accuracy 0.966 ± 0.05. Importancia (permutación, holdout): asistencia 0.42, reuniones 0.33, promedio ≈ 0 |

Cada versión se guarda como `ml/models/rf_vN.joblib` + `rf_vN.json` (features, hiperparámetros, CV, holdout, matriz de confusión, importancia de variables, fecha, umbrales; con aviso si `fuente_datos` ≠ `historico_real`). No versionados (`ml/models/` solo tiene el `.gitkeep`).

## Notas técnicas
- scikit-learn ≥ 1.4 admite valores nulos en Random Forest, pero los registros incompletos se **excluyen** igual por el criterio de exclusión de la tesis.
- Random Forest no requiere escalar las features.
