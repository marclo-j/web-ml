# 📓 LOG DE AVANCES

> Una entrada por sesión relevante o por presentación. Lo más reciente arriba.

## Plantilla de entrada
```
### AAAA-MM-DD — Título
**Tipo:** desarrollo | presentación | reunión con asesor | reunión con IE
**Qué se hizo:**
**Feedback recibido:**
**Decisiones tomadas:**
**Pendientes derivados:**
```

---

### 2026-10-09 — PRE 2026 v5 vigente y clasificación con `rf_v3`
**Tipo:** desarrollo
**Qué se hizo:**
- El autor aclaró que los 19 cambios de asistencia de PRE 2026 v5 provienen del registro de la IE (corrigió valores inconsistentes) y que `deserto` en 2026 fue un error de llenado. Se vació `deserto` en las 3 fichas 2026 (respaldo con la columna llena en `data/raw/_respaldos/2026_pre_v5_con_deserto/`).
- `preprocess.py`: 69 incluidos (control 35 en 3.° A, experimental 34 en 4.° B), 1 excluido por traslado definitivo.
- Normalidad (Shapiro-Wilk): promedio no normal en ambos (p < 0.001); asistencia no normal en control (p = 0.021), normal en experimental (p = 0.236); reuniones no normal en ambos (p < 0.001) → U de Mann-Whitney.
- Equivalencia (U de Mann-Whitney): promedio p = 0.540, asistencia p = 0.449, reuniones p = 0.616. Grupos comparables.
- Clasificación PRE con `rf_v3` y umbrales provisionales (0.33 / 0.66): control 32 / 3 / 0, experimental 28 / 3 / 3 (bajo / medio / alto).
- CSV para SPSS: `data/processed/spss_pre2026_v5.csv` (con probabilidad y nivel).
**Decisiones tomadas:** PRE 2026 v5 reemplaza a v4.
**Pendientes derivados:** fijar umbrales finales de nivel; Fase 4 (backend).

---

### 2026-10-09 — `rf_v3` y fichas PRE 2026 v5
**Tipo:** desarrollo
**Qué se hizo:**
- Se eligió SMOTE (D8). `rf_v3` = 2024 v5 + SMOTE x2 solo en entrenamiento (112 sintéticos). Holdout (14 alumnos, 3 positivos): accuracy 0.93, precision 0.75, recall 1.00, F1 0.86, matriz [[10, 1], [0, 3]]. Métrica principal: CV 5x5 de `comparar_aumento.py` (ver entrada siguiente). Importancia por permutación: asistencia 0.42, reuniones 0.33, promedio ≈ 0.
- PRE 2026 v5 (archivos `*_2026_1.xlsx`): `deserto` coincide entre fichas (12 alumnos con 1), pero sigue lleno, así que `preprocess.py` excluye a los 70. Respecto de v4, las notas no cambian; cambian los días asistidos de 19 alumnos y las reuniones de 6. Los 10 marcados como desertores que cambian bajan en promedio 22.3 días (de −8 a −37); los 9 no desertores que cambian suben 15.8 días (de +4 a +26).
**Decisiones tomadas:** PRE 2026 v5 no se usa para clasificar ni para SPSS. La deserción 2026 es la variable de desenlace (D2) y se registra al cierre del periodo; los indicadores PRE son del I bimestre y no deben ajustarse según un desenlace posterior. Hasta que el autor aclare, se mantiene PRE 2026 v4 (`spss_pre2026_v4.csv`).
**Pendientes derivados:** el autor explica el origen de los 19 cambios de asistencia y vacía `deserto` en las fichas 2026.

---

### 2026-10-09 — Fichas 2024 corregidas (v5) y CTGAN
**Tipo:** desarrollo
**Qué se hizo:**
- El autor entregó fichas 2024 corregidas, con otros alumnos. Se descartan 2025 y la versión 2026 actual (el autor enviará una nueva de 2026). El histórico restante se generará a partir de 2024 con aumento (D8).
- `preprocess.py`: 70 incluidos, 0 excluidos; `deserto` coincide en las 3 fichas. 13 desertores (18.6 %; control 6, experimental 7). Desertores frente a no desertores: promedio 10.95 vs 14.08 (MW p = 0.003), asistencia 23.6 % vs 67.3 % (p < 0.001), reuniones 0 % vs 49.1 % (p < 0.001).
- Casi separación perfecta: "reuniones = 0 y asistencia ≤ 40 %" clasifica bien 68 de 70. Los desertores asistieron entre 1 y 18 de 45 días del I bimestre: posible fuga de información (D3) si ya habían dejado de asistir dentro del bimestre.
- `aumento.py` admite `ctgan` además de `smote`; `ml/comparar_aumento.py` compara sin aumento, SMOTE y CTGAN con CV repetida evaluada solo sobre reales, más fidelidad (KS por clase). Se corrigió el orden de clases de `RFAumentado` (la AUC fallaba). 42 pruebas.
- El autor confirmó que los desertores 2024 dejaron de asistir después del I bimestre (no hay fuga por D3).
- `comparar_aumento.py` sobre 2024 v5 (n = 70, 13 positivos, factor 2, CV 5x5, prueba solo con reales). AUC / F1 / recall / precision: sin aumento 0.994 / 0.927 / 1.000 / 0.883; SMOTE 0.993 / 0.911 / 0.967 / 0.893; CTGAN 0.985 / 0.859 / 0.960 / 0.824 (desviación de F1 ≈ 0.12–0.16). Fidelidad KS: SMOTE ≤ 0.19 en ambas clases; CTGAN 0.23–0.73 (no reproduce la clase desertora con 13 casos).
**Pendientes derivados:** elegir método para el modelo final (recomendado SMOTE: rinde igual que sin aumento y sus sintéticos se parecen a los reales; CTGAN se reporta como alternativa descartada).

---

### 2026-10-09 — Aumento de datos (D8) y SPSS PRE 2026 v4
**Tipo:** desarrollo
**Qué se hizo:**
- PRE 2026 v4 procesado sobre una copia con `deserto` vaciado (las fichas en `data/raw/2026_pre/` siguen con `deserto` lleno): 69 incluidos (control 35, experimental 34), 1 excluido por traslado. Secciones: 3.° A y 4.° B. CSV para SPSS en `data/processed/spss_pre2026_v4.csv` (sin probabilidad ni nivel: el modelo aún no se reentrena).
- Normalidad (Shapiro-Wilk): promedio no normal en ambos grupos (p < 0.001); asistencia no normal en control (p = 0.003) y normal en experimental (p = 0.106); reuniones no normal en ambos (p < 0.001) → U de Mann-Whitney.
- Equivalencia (U de Mann-Whitney): promedio p = 0.540, asistencia p = 0.199, reuniones p = 0.730. Grupos comparables. Levene p > 0.7 en las 3.
- `ml/aumento.py` + `train.py --aumentar` (5 pruebas nuevas, 39 en total).
**Decisiones tomadas:** D8 (ver `MODELO.md`), según el autor avalada por el docente. Los años del histórico se mantienen rotulados como 2024 y 2025 por decisión del autor.
**Pendientes derivados:** el autor corrige `deserto` en las fichas 2024–2025 (un valor por alumno, igual en las 3) y lo vacía en las fichas 2026; luego se reentrena con aumento y se rehacen los CSV de SPSS del histórico.

---

### 2026-10-09 — Cuarta versión de fichas (2024, 2025 y 2026) y revisión
**Tipo:** desarrollo
**Qué se hizo:** El autor reemplazó las fichas de 2024, 2025 y también de PRE 2026 (2026-10-09, 20:16–20:50), indicando que provienen de una reunión con un representante de la dirección de la IE. Se procesaron sin pisar versiones anteriores (`data/processed/*_v4*`). Hallazgos:
1. `preprocess.py` excluye 38/70 (2024), 33/70 (2025) y 70/70 (2026), todos por `deserto`.
2. `deserto` no coincide entre fichas: en 2024 solo 3 alumnos tienen 1 en las 3 fichas y 41 tienen al menos un 1; en 2025, 1 y 34.
3. PRE 2026 trae `deserto` lleno en los 70 (30 con algún 1), dato que no puede conocerse antes del cierre del periodo (D2).
4. Los indicadores no son correcciones de la versión anterior: cambian 69/70 promedios en 2024, 70/70 en 2025 y 68/69 en PRE 2026, con correlación ≈ 0 respecto a la versión previa (|Δ promedio| medio ≈ 3 puntos). En PRE 2026 la asistencia media pasa de 88.7 % a 64.1 %.
**Aclaración del autor (2026-10-09):** el histórico se tomó de otros años lectivos, según lo pactado con el directivo para mantener el anonimato; PRE 2026 cambió porque se usan otras secciones. Los documentos fuente quedan entre la IE, el docente y el autor (no se suben al repo). Esto explica los hallazgos 4 y el cambio de PRE 2026.
**Pendientes derivados:** corregir `deserto` para que sea un único valor por alumno igual en las 3 fichas (hallazgos 2) y dejarlo vacío en PRE 2026 (hallazgo 3); registrar en la metodología los años reales del histórico y las secciones de 2026. Mientras tanto, Fase 4 (backend) avanza con datos sintéticos.

---

### 2026-10-03 — Tercera versión de fichas 2024–2025 y `rf_v2`
**Tipo:** desarrollo
**Qué se hizo:** El autor volvió a llenar las fichas 2024–2025 (indicadores y `deserto`). Desaparece la correlación entre años (0.01). Resultado: 140 alumnos, 44 desertores (2024: 19, 27.1 %; 2025: 25, 35.7 %). `rf_v2` obtiene 1.00 en todas las métricas (CV 5x5, 25/25 pruebas) y un árbol de 2 niveles separa a todos sin error (promedio ≤ 12.05 y reuniones ≤ 75, o asistencia ≤ 56.67). Ningún desertor tiene reuniones > 50 % ni asistencia > 77.8 %.
**Decisiones tomadas:** Separación perfecta = misma señal que `rf_v0b` (etiquetas que siguen una regla). `rf_v2` y sus métricas no se presentan ni se citan hasta contrastar las fichas con los documentos fuente.

---

### 2026-10-03 — Histórico 2024–2025 en validación
**Tipo:** desarrollo
**Qué se hizo:** Revisión de coherencia del histórico. 1) La tasa de las fichas (27 % / 26 %) contradecía la tendencia del problema (29 % → 35 %). 2) Mismo código en 2024 y 2025 con promedios casi iguales (correlación 0.52; esperado ≈ 0 ± 0.12 entre alumnos distintos), p. ej. EST-003 a EST-007 desertores ambos años. 3) Las fichas se crearon la noche del 2025-09-25, tras la negativa de la IE. El autor corrigió las fichas: solo cambió `deserto` (1 alumno en 2024, 7 en 2025) → 20/70 (28.6 %) y 25/70 (35.7 %); ningún indicador cambió y las anomalías 2) persisten.
**Decisiones tomadas:** El histórico 2024–2025, `rf_v1`, sus métricas, la importancia de variables y la vista previa de niveles **no se presentan ni se citan** hasta contrastar las fichas con los registros fuente de la IE. Se presenta solo lo basado en PRE 2026 (equivalencia de grupos) y el pipeline. Ver `docs/avances/2026-10-03_prompt_correccion_design.md`.
**Pendientes derivados:** validar el histórico con los documentos originales (nóminas, actas, retirados en SIAGIE); si no es posible, volver a la Opción B declarada como limitación.

---

### 2026-10-03 — Preparación del avance
**Tipo:** desarrollo
**Qué se hizo:**
- Métricas de `rf_v1` (configuración inicial) con CV estratificada 5x5 sobre los 140: AUC 0.79 ± 0.08, accuracy 0.73 ± 0.05, precision 0.49 ± 0.09, recall 0.60 ± 0.20, F1 0.53 ± 0.11. Matriz (CV 5): [[79, 24], [16, 21]].
- Importancia por permutación dentro de la CV (caída de AUC): promedio 0.19 ± 0.08, asistencia 0.08 ± 0.06, reuniones 0.05 ± 0.05. Sustituye a la del holdout (valores negativos, ruido).
- Histórico, desertores vs no (Mann-Whitney): promedio p < 0.001, reuniones p = 0.024, asistencia p = 0.069.
- Equivalencia PRE 2026 (control n=35, experimental n=34): promedio t p = 0.901; asistencia MW p = 0.355; reuniones MW p = 0.733. Grupos comparables.
- Vista previa de niveles con umbrales provisionales: control 21/11/3, experimental 21/8/5 (bajo/medio/alto).
- CSV para SPSS en `data/processed/spss_pre2026.csv` y `spss_historico.csv` (gitignored). Prompt del avance en `docs/avances/2026-10-03_prompt_avance.md`.
**Pendientes derivados:** umbrales finales de nivel; Fase 4 (backend).

---

### 2026-10-03 — Histórico real 2024–2025 procesado y `rf_v1`
**Confirmación:** la IE confirmó el criterio de `deserto` (2026-10-03).
**Corrección de fichas (autor):** los 37 alumnos con `deserto` parcial (`data/processed/deserto_a_corregir.csv`) quedaron con 1 en las 3 fichas. Con la regla estricta se obtienen los mismos 140 alumnos, 37 desertores e indicadores idénticos a D7. Las fichas originales no se respaldaron antes de editarlas.
**Tipo:** desarrollo
**Qué se hizo:** Se procesaron las fichas de la IE en `data/raw/2024_pre` y `2025_pre`. Con el criterio estricto quedaban 103 incluidos y 0 desertores: `deserto` no coincidía entre fichas en 19 y 18 alumnos. Se añadió `preprocess.py --deserto-cualquiera` y se obtuvo `data/processed/historico.csv` (140 alumnos, 37 desertores). Se entrenó `rf_v1` con `--fuente historico_real`.
**Resultados (no citables aún):** CV k=5 F1 0.63 ± 0.09; holdout 20 % (n=28, 7 positivos) accuracy 0.54, F1 0.38. Importancia por permutación negativa en `promedio` y `pct_asistencia`: con n=140 el modelo apenas supera el ruido.
**Ajuste (`ml/tune.py`, CV anidada 5x2, grilla de `MODELO.md`):** config. inicial F1 0.51 ± 0.09, AUC 0.78 ± 0.08; con búsqueda F1 0.52 ± 0.12, AUC 0.78 ± 0.08. El ajuste no mejora de forma apreciable y no hay combinación estable entre folds (9 distintas en 10). Se mantiene la configuración inicial; con n=140 el techo lo fija el tamaño de muestra y la poca señal de 3 variables.
**Decisiones tomadas:** D7 (`deserto` = 1 si cualquier ficha lo marca).
**Pendientes derivados:** validar D7 con el asesor/IE; ajustar hiperparámetros (GridSearchCV) y considerar CV repetida por el tamaño del holdout; definir umbrales de probabilidad.

---

### 2026-10-03 — Cierre de decisiones pendientes
**Tipo:** desarrollo
**Qué se hizo:** Se registraron las decisiones del autor sobre los ❓ abiertos en `VARIABLES.md` y `MODELO.md`.
**Decisiones tomadas:**
- D2: `nivel_riesgo_real` = deserción efectiva al cierre del periodo (opción b).
- Umbral `pct_reuniones` < 50 % se mantiene como umbral operacional del autor, declarado como supuesto.
- Cita [42] (Balfanz y Byrnes) confirmada.
**Pendientes derivados:** con el asesor siguen la variable contrastada y la comparación pre vs post intragrupo (`PLAN_ESTADISTICO.md`).

---

### 2026-09-25 — Pipeline de entrenamiento y Opción B sobre datos reales
**Tipo:** desarrollo
**Qué se hizo:**
- La IE se negó a entregar el histórico 2024–2025. Se evaluó usar un dataset de Kaggle como sustituto y se descartó: ninguno de los 3 candidatos revisados (Secondary School Student Dropout, Student Performance and Attendance Dataset, UCI Predict Students' Dropout) tiene las 3 variables de la tesis (promedio, pct_asistencia, pct_reuniones); el de UCI además es de educación superior en Portugal, no secundaria en Perú.
- Se activó la Opción B (`MODELO.md`) sobre los datos PRE 2026 **reales** (no sintéticos): `ml/etiquetar_umbral.py` etiqueta `deserto` por 3 reglas de umbral con fuente citada (nota < 11: MINEDU; asistencia < 85 %: absentismo crónico, Balfanz y Byrnes / Attendance Works; reuniones < 50 %: umbral propio del autor, declarado como tal).
- Se creó `ml/train.py` (Random Forest, holdout 80/20 + CV k=5, métricas, importancia MDI y por permutación) y `ml/calcular_indicadores.py` (aplica las fórmulas a un CSV de datos crudos, reutilizable para un histórico real que llegue en CSV).
- Se corrieron 2 versiones de prueba, ninguna citable como resultado: `rf_v0` (sintético, accuracy 0.42, cercano al azar por el ruido del generador) y `rf_v0b` (Opción B sobre los 69 reales, accuracy 1.0 — confirma empíricamente que el modelo solo reproduce la regla de etiquetado).
- 34 pruebas automáticas nuevas en `ml/tests/`.
**Decisiones tomadas:**
- No usar datasets externos (Kaggle) como reemplazo del histórico: rompen la operacionalización de la tesis (variables distintas a las definidas en `VARIABLES.md`).
- Los modelos entrenados con datos reales no se versionan (`ml/models/*.joblib|json` a `.gitignore`): con n=69 el árbol puede memorizar alumnos individuales.
**Pendientes derivados:** conseguir el histórico real (Opción A); validar con el asesor el umbral de `pct_reuniones` (no viene de una cifra publicada); confirmar los números de cita [40]/[41] contra la bibliografía completa de la tesis antes de usarlos en el documento.

---

### 2026-09-25 — Fase 1 completa: datos PRE 2026 recolectados y procesados
**Tipo:** desarrollo
**Qué se hizo:**
- Se llenaron las 3 fichas del PRE 2026 con los datos reales de la IE en `data/raw/2026_pre/` (no versionado) y se procesaron con `ml/preprocess.py`.
- Resultado: 69 estudiantes incluidos (35 control, 34 experimental) y 1 excluido por traslado definitivo. Sin excluidos por dimensión incompleta ni por registro inconsistente. Salida en `data/processed/2026_pre.csv` (+ `_excluidos.csv` y `_resumen.json`), no versionada.
**Decisiones tomadas:** Fase 1 se da por cerrada (✅ en `FASES.md`); se sigue con la Fase 2 (dataset de entrenamiento histórico).
**Pendientes derivados:** conseguir los registros históricos 2024–2025 con desenlace conocido (`deserto`) — ver observación pendiente sobre la negativa de la IE a entregarlos.

---

### 2026-09-25 — Escala vigesimal confirmada y fichas listas para rellenar
**Tipo:** desarrollo
**Qué se hizo:**
- La IE confirmó la escala vigesimal (0–20): D1 cerrada. Se quitó la escala literal (celda B7, hoja Conversión) de las fichas y de `preprocess.py`.
- `generar_fichas.py --prellenar 2026_pre` crea en `data/raw/2026_pre/` las 3 fichas con los 70 códigos, grado, momento y año ya escritos y bloqueados; solo se rellena lo que viene en blanco. Verificado en Excel (24 comprobaciones) y con 17 pruebas automáticas.
**Decisiones tomadas:**
- Códigos: `EST-001`–`EST-035` = 4.° (experimental), `EST-036`–`EST-070` = 3.° (control). La correspondencia código ↔ nombre la lleva el autor fuera del sistema.
- Un código pre-llenado sin ningún dato no cuenta como excluido; se informa aparte (`codigos_sin_usar`) para no inflar las exclusiones si una sección tiene menos de 35 alumnos.
**Pendientes derivados:** rellenar las fichas PRE con los registros del I bimestre y correr `preprocess.py`.

---

### 2026-09-24 — Fase 1: consolidación de fichas y criterios de exclusión
**Tipo:** desarrollo
**Qué se hizo:**
- Se creó `ml/preprocess.py`: une las 3 fichas llenas, recalcula los indicadores a partir de los datos crudos (`calcular_indicadores`, función que reutilizará el backend), aplica las reglas de `VARIABLES.md` y clasifica cada excluido en traslado definitivo / dimensión incompleta / registro inconsistente, con la fila de Excel de origen.
- 16 pruebas automáticas en `ml/tests/` (fórmulas, reglas, cada criterio de exclusión, escala literal, histórico con `deserto`).
- Prueba de punta a punta con 20 alumnos **sintéticos** guardados en Excel real: 17 incluidos y 3 excluidos, uno por motivo (validación técnica, no es resultado).
**Decisiones tomadas:**
- Una nota fuera de la escala excluye al alumno por registro inconsistente (no se descarta en silencio la nota).
- Prioridad del motivo cuando hay varios: traslado marcado → alumno repetido → dimensión incompleta o dato inválido → incoherencia entre fichas → reglas de las fórmulas.
- La salida con datos reales solo puede escribirse en `data/processed/` (el script lo impide en otra ruta del repo).
**Pendientes derivados:** correr `preprocess.py` cuando la IE entregue los datos PRE y reportar los excluidos en Resultados.

---

### 2026-09-24 — Escala de calificación y corte bimestral
**Tipo:** desarrollo
**Decisiones tomadas:**
- D3 precisado: la IE trabaja por bimestres, el corte es el **I bimestre** (fichas, `VARIABLES.md`, `MODELO.md`). `generate_synthetic.py` ajustado a 40–50 días lectivos y 1–3 reuniones.
- D1 tentativo: escala vigesimal (0–20), práctica habitual en secundaria. Sigue pendiente confirmar cómo registra la IE, porque la norma vigente (RVM N.° 094-2020-MINEDU) establece la escala literal AD/A/B/C para la EBR.
**Pendientes derivados:** verificar con la IE la escala del registro 2026 y del histórico 2024–2025 (deben coincidir o convertirse con un criterio justificado).

---

### 2026-09-24 — Fase 1: plantillas de las 3 fichas
**Tipo:** desarrollo
**Qué se hizo:**
- Se creó `fichas/generar_fichas.py`, que genera las 3 fichas en Excel (`fichas/ficha_1_rendimiento.xlsx`, `ficha_2_asistencia.xlsx`, `ficha_3_reuniones.xlsx`) con hoja de instrucciones, fórmulas de la tesis, validaciones de `VARIABLES.md`, alertas por color y hojas protegidas sin contraseña.
- Se verificaron en Excel 16 con 38 casos de prueba (fórmulas, escala vigesimal y literal, notas fuera de rango, DA > DP, RT = 0, códigos no anonimizados, exclusión sin motivo): 0 fallas.
- Se completó la estructura de carpetas de `ARQUITECTURA.md` (`backend/`, `frontend/`, `stats/`).
- Se ajustó `ml/generate_synthetic.py` a las reglas de las fichas: periodo de corte (45–65 días, 2–4 reuniones), grupo derivado del grado y códigos `EST-###`. Tasa de deserción simulada regenerada: 35.0 %.
**Decisiones tomadas:**
- D3: periodo de corte = I bimestre / I trimestre (registrado en `VARIABLES.md` y `MODELO.md`).
- La ficha 1 registra la nota de cada una de las 10 áreas curriculares; `n_notas` cuenta solo notas válidas, así un área exonerada queda vacía sin afectar el promedio.
- `grupo` no se captura: se calcula del grado (3.° = control, 4.° = experimental).
**Pendientes derivados:** confirmar con la IE la escala (D1); añadir en la metodología de la tesis el periodo de corte (observación #5).

---

### 2026-09-24 — Datos sintéticos para simulación
**Tipo:** desarrollo
**Qué se hizo:** Se creó `ml/generate_synthetic.py` (semilla fija = 42) y se generaron `data/synthetic/historico.csv` (300 filas, tasa de deserción simulada 32.3 %, coherente con el 29–35 % real reportado) y `data/synthetic/carga_prueba.csv` (20 filas sin `deserto`, formato de carga masiva).
**Decisiones tomadas:**
- Se simula el pipeline completo mientras se consigue el histórico real de la IE; el criterio de etiquetado (Opción B de `MODELO.md`) queda descartado por ahora — se prioriza obtener el desenlace histórico real (Opción A).
- Los datos sintéticos nunca se citan como hallazgo; ver aviso en `data/synthetic/LEEME.md`.
**Pendientes derivados:** Reemplazar `historico.csv` en cuanto la IE entregue el registro real 2024–2025 y volver a correr `ml/train.py`.

---

### 2026-09-24 — Cierre de Fase 0, handoff a Claude Code
**Tipo:** desarrollo
**Qué se hizo:** Se agregó `.gitignore` real (antes solo estaba mencionado en el README), `.gitkeep` en `ml/models/`, y se limpió el README para no duplicar contenido. Fase 0 marcada como ✅ en `FASES.md`.
**Decisiones tomadas:** De aquí en adelante, el desarrollo continúa en Claude Code sobre este repositorio; `CLAUDE.md` en la raíz es el punto de entrada.
**Pendientes derivados:** Cerrar las decisiones ❓ de `VARIABLES.md` (escala de notas) y `MODELO.md` (origen de `nivel_riesgo_real`) en cuanto haya respuesta de la IE/asesor.

---

### 2026-09-24 — Repositorio en GitHub y plan de fichas
**Tipo:** desarrollo
**Qué se hizo:** Se subió el repositorio a GitHub (`marclo-j/web-ml`) y se guardó el plan de trabajo en `docs/planes/2026-09-24_fase0-y-fichas.md`.
**Decisiones tomadas:**
- Ficha de rendimiento con nota por curso; la plantilla calcula `suma_notas`, `n_notas` y `promedio` (soporta escala vigesimal o literal).
- Periodo de corte: I bimestre / trimestre, igual para PRE 2026 e histórico 2024–2025, para evitar fuga de información (un desertor tiene menos asistencia porque ya se fue).
**Pendientes derivados:** generar las fichas y registrar D3 (periodo de corte) en `VARIABLES.md`; ajustar `ml/generate_synthetic.py` a ese periodo (hoy simula 180–200 días programados, año completo).

---

### 2026-09-26 — Hito 1: presentación de avance
**Tipo:** presentación
**Guion sugerido (slides):**
1. Problema y objetivo general (deserción 29 % → 35 %, enfoque reactivo)
2. Arquitectura de la web (diagrama de `ARQUITECTURA.md`)
3. De la metodología al sistema: 3 fichas → 3 variables del modelo (tabla de `VARIABLES.md`)
4. Cómo aprende el modelo: datos históricos con desenlace conocido → Random Forest → nivel bajo/medio/alto
5. Plan de fases y en cuál estoy
6. Plan estadístico: Shapiro-Wilk (n = 35 por grupo < 50) → t de Student o U de Mann-Whitney
7. (Opcional) Prueba de concepto con datos sintéticos
8. Preguntas para el docente

**Preguntas para el docente:**
- ¿Es válido usar registros 2024–2025 con desenlace conocido como datos de entrenamiento?
- En la posprueba, ¿qué variable se contrasta entre grupos: el nivel de riesgo, cada indicador o ambos?
- ¿Se agrega Wilcoxon / t pareada para comparar pre vs post dentro de cada grupo?
- Si la IE usa escala literal (AD, A, B, C), ¿qué conversión numérica es aceptable?
- ¿Es adecuado medir el PRE (y el histórico) con datos hasta el cierre del I bimestre para evitar fuga de información?

**Feedback recibido:** _(completar tras la presentación)_
**Decisiones tomadas:** _(completar)_
**Pendientes derivados:** _(completar)_

---

### 2026-09-24 — Setup de documentación
**Tipo:** desarrollo
**Qué se hizo:** Se definió la documentación del repositorio (`CLAUDE.md` + 8 docs en `/docs` + `README.md`) y el roadmap de 9 fases.
**Decisiones tomadas:**
- Stack: Next.js + FastAPI + Supabase + scikit-learn (ver `ARQUITECTURA.md`)
- Tarea del modelo: clasificación binaria (desertó sí/no) → probabilidad → nivel de riesgo por umbrales (ver `MODELO.md`)

---

## ⚠️ Observaciones pendientes en el documento de tesis
| # | Observación | Dónde | Estado |
|---|---|---|---|
| 1 | La cita **[39]** se usa para dos fuentes distintas: la definición de "web con ML" y Ttito y Choque | Metodología | ⬜ |
| 2 | No se define qué son los "valores reales registrados en la institución" contra los que se calculan las métricas | Metodología, análisis de datos | ⬜ |
| 3 | Precisar en la metodología que la escala de la IE es vigesimal (0–20), confirmada el 2026-09-25 | Metodología, ficha de rendimiento | ⬜ |
| 4 | Falta indicar el origen de los datos etiquetados para entrenar el modelo | Metodología | ⬜ |
| 5 | Falta definir el periodo que abarcan el PRE y el POST (periodo de corte, decisión D3) | Metodología, instrumentos | ⬜ |
