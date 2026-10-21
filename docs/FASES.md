# 🗺️ FASES DEL PROYECTO

> Estado: ⬜ pendiente · 🟨 en progreso · ✅ hecho · ⛔ bloqueado
> Actualizar al final de cada sesión de trabajo.

## Resumen
| Fase | Nombre | Estado | Depende de | Entregable principal |
|---|---|---|---|---|
| 0 | Setup y documentación | ✅ | — | Repo con estructura y `/docs` |
| 1 | Fichas y recolección PRE | ✅ | 0 | 3 fichas + datos PRE de los 70 alumnos. Vigente: PRE 2026 v5 (2026-10-09, 3.° A control 35, 4.° B experimental 34, 1 excluido por traslado) |
| 2 | Dataset de entrenamiento (etiquetado) | ✅ | 1 | `data/processed/2024_pre_v5.csv`: 70 alumnos (2024), 13 desertores; se completa con aumento SMOTE solo en entrenamiento (D8). 2025 descartado |
| 3 | Entrenamiento y evaluación del modelo | ✅ | 2 | En producción `rf_v5` (D12): entrenamiento equilibrado a 40 % de desertores (13 reales + 25 sintéticos SMOTE vs 57 reales), CV 5x5 sobre reales AUC 0.99, F1 0.93. Umbrales: 0.222 / 0.50. `rf_v3`/`rf_v4` (SMOTE x2) quedan como comparación |
| 4 | Backend (API) | ✅ | 3 | FastAPI con predicción, CRUD y autenticación propia, conectado a Neon. Falta crear usuarios |
| 5 | Frontend (dashboard) | ✅ | 4 | Next.js 16: listado de riesgo por alumno, registro, CSV, detalle y modelo |
| 6 | Despliegue e intervención | 🟨 | 5 | Web en producción, usada con grupo experimental. Despliegue pendiente (lo hace el autor después); falta registrar fechas y forma de uso de la intervención |
| 7 | Recolección POST | ✅ | 6 | POST III bimestre (10/08–09/10, D13): 69 incluidos, 1 excluido. Desenlace real hasta el 09/10 (D14) |
| 8 | Análisis estadístico | ✅ | 7 | `stats/output/` 1–7: descriptivos, niveles, normalidad, contraste, Wilcoxon complementario (D15), métricas de `rf_v5` y validación con el desenlace |
| 9 | Redacción de Resultados y Discusión | 🟨 | 8 | Capítulos III a VI. La redacta el autor en otro chat con `docs/avances/2026-10-21_contexto_redaccion_tesis.md` |

---

## Detalle por fase

### Fase 0 — Setup y documentación ✅
- [x] Definir documentos del repo
- [x] Crear repo y estructura de carpetas (`ARQUITECTURA.md`)
- [x] Configurar `.gitignore` (datos reales fuera)
- [x] Cerrar decisiones pendientes de `VARIABLES.md` y `MODELO.md` (D2 opción b, umbral 50 %, cita [42]) — 2026-10-03. Las del `PLAN_ESTADISTICO.md` (variable contrastada y Wilcoxon) se cerraron con D15 el 2026-10-21, sin asesor disponible

### Preparación de Fase 3 (adelantada)
- [x] `ml/generate_synthetic.py` + `data/synthetic/historico.csv` y `carga_prueba.csv`, para no bloquear el desarrollo mientras llega el histórico real (ver `LOG_AVANCES.md`)

**Qué decir al presentar:** "Definí la arquitectura (frontend, backend, base de datos y modelo), el diccionario de datos que traduce mis 3 fichas a variables del sistema, y el plan de fases hasta Resultados."

### Fase 1 — Fichas y recolección PRE
- [x] Diseñar las 3 fichas como plantillas (Excel/Sheets) con las columnas de `VARIABLES.md` → `fichas/` (verificadas en Excel)
- [x] Definir el periodo de corte (D3: I bimestre; la IE trabaja por bimestres)
- [x] Confirmar con la IE la escala de calificación → vigesimal 0–20 (D1)
- [x] Fichas pre-llenadas listas para rellenar: `generar_fichas.py --prellenar 2026_pre` → `data/raw/2026_pre/`
- [x] Rellenar las fichas con los datos PRE de los 70 alumnos (I bimestre) → `data/raw/2026_pre/`
- [x] Herramienta de consolidación y exclusión lista: `ml/preprocess.py` (16 pruebas en `ml/tests/`)
- [x] Aplicar criterios de inclusión/exclusión a los datos reales → `data/processed/2026_pre.csv`: 69 incluidos, 1 excluido (traslado definitivo)

**Qué decir:** "Las fichas aplican exactamente las fórmulas de mi metodología; aquí está la estructura y el estado de recolección."

### Fase 2 — Dataset de entrenamiento
- [x] Solicitar a la IE registros de 2024–2025 con desenlace conocido → **se negó** (2026-09-25); se sigue insistiendo en paralelo
- [x] Limpiar, anonimizar y consolidar en `data/processed/historico.csv` → 2024 v5, 70 alumnos, 13 desertores, 0 excluidos (2026-10-10)
- [x] Documentar tamaño, balance de clases y exclusiones en `MODELO.md` ("Histórico final") + `spss_historico_v5.csv`
- [x] Aumento de datos D8 (SMOTE elegido frente a CTGAN con `comparar_aumento.py`)
- [x] Mientras tanto: `ml/etiquetar_umbral.py` etiqueta por Opción B (umbral) sobre los datos PRE 2026 reales, declarado como limitación

**Qué decir:** "El modelo es supervisado: aprende de 70 alumnos de 2024 cuyo desenlace ya se conoce (13 desertaron). Como la muestra es pequeña, se completó el entrenamiento con datos sintéticos generados por SMOTE, y el modelo se evalúa solo con alumnos reales."

### Fase 3 — Modelo
- [x] Script `ml/train.py` con validación cruzada estratificada k=5 + holdout 80/20
- [x] Métricas: accuracy, precision, recall, F1 + matriz de confusión
- [x] Importancia de variables (MDI y permutación; sustenta OE1–OE3)
- [x] ~~`rf_v1` (2026-10-03)~~ descartado junto con el histórico 2024–2025
- [x] Comparación de aumento SMOTE vs CTGAN vs sin aumento (`comparar_aumento.py`) → SMOTE
- [x] `rf_v3` = 2024 + SMOTE x2: CV 5x5 sobre reales AUC 0.993, F1 0.911, recall 0.967 (registrado en `MODELO.md`)
- [x] Ajuste de hiperparámetros con CV anidada + SMOTE (`tune.py --aumentar 2`): sin mejora, se mantiene la configuración inicial
- [x] Umbrales finales de nivel (D9): bajo < 0.15 ≤ medio < 0.50 ≤ alto
- [x] Modelo de producción `rf_v4` (D11, 2026-10-10): reentrenado con los 70 reales + SMOTE; el backend lo carga por defecto
- [x] Reimportar `carga_pre2026.csv` en la web para que las predicciones de Neon pasen a `rf_v4` (autor, 2026-10-10)
- [x] Observación del docente (2026-10-17): clases muy desbalanceadas sesgan al modelo → D12, entrenamiento equilibrado a 40 % (`--proporcion 0.40`), comparado con refuerzo y submuestreo en `comparar_proporcion.py`
- [x] Modelo de producción `rf_v5` (D12): 70 reales + 25 sintéticos desertores; umbral medio 0.222 (alto 0.50); backend y `analisis.py` apuntan a `rf_v5`
- [x] Predicciones de Neon pasadas a `rf_v5` (PRE 2026: 55 / 11 / 3)
- [x] Interpretación de "equilibrar a 40 / 60" confirmada por el autor; `spss_pre2026_v5.csv` regenerado con `rf_v5` (2026-10-20)
- [x] Borrados de Neon los alumnos de prueba EST-071 a EST-074 (2026-10-20): quedan 69 estudiantes, registros y predicciones
- [x] Corridas de prueba: `rf_v0` (sintético) y `rf_v0b` (Opción B, real PRE 2026) — ver `MODELO.md`, ninguna es resultado de tesis

**Qué decir:** "El modelo detecta a los desertores del histórico con AUC 0.99 evaluado solo sobre alumnos reales; la asistencia y la participación familiar son las dimensiones que más pesan. Los niveles bajo, medio y alto salen de las probabilidades del propio histórico."

### Fase 4 — Backend
- [x] Endpoints de `API.md` implementados (`backend/app/`, 28 pruebas) — 2026-10-10
- [x] Cálculo de indicadores en el servidor (`services/indicadores.py`, idéntico a `ml/preprocess.py`, lo comprueba una prueba)
- [x] Autenticación propia (D10): Argon2id + JWT, bloqueo por intentos, usuarios por CLI (`app.crear_usuario`)
- [x] Prueba de punta a punta con `rf_v3`: importar PRE 2026 por CSV da el mismo resumen (27/7/1 y 27/4/3)
- [x] Conexión a Neon verificada (2026-10-10): PostgreSQL 18.6, pooler + SSL, 4 tablas con todas sus columnas; escritura de prueba deshecha
- [ ] Crear los usuarios (autor, `python -m app.crear_usuario`)

### Fase 5 — Frontend
- [x] Login simple para tutor/directivo (contra `POST /auth/login`, sesión en cookie httpOnly)
- [x] Tabla de alumnos con nivel de riesgo y color + resumen por grupo y filtros
- [x] Formulario de registro + carga masiva por CSV (con detalle de excluidos)
- [x] Vista de detalle por alumno (sus 3 indicadores con fórmula y datos crudos)
- [x] Extra: página del modelo (umbrales, CV 5x5, matriz de confusión) y cambio de contraseña
- [x] Probado en el navegador (2026-10-10) contra un backend local con SQLite temporal y datos sintéticos: login (error y éxito), importación (20 procesados, 2 excluidos), registro de un caso alto, detalle, modelo, filtros, vista móvil, salir

**Qué decir (4 + 5):** Demo en vivo del flujo: se cargan los datos de un alumno → la web calcula los indicadores → el modelo devuelve el nivel de riesgo.

### Fase 6 — Despliegue e intervención
- [ ] Backend en Render, frontend en Vercel
- [ ] Capacitación breve a tutores del grupo experimental
- [x] Corte de la POST: III bimestre, 10/08–09/10/2026 (D13)
- [ ] Registrar fecha de inicio y fin de la intervención y cómo usaron la web los tutores del experimental (lo necesita la Metodología)
- [ ] Cuentas solo para los tutores del grupo experimental

### Fase 7 — Recolección POST
- [x] Intento 2026-10-20: se llenaron las fichas con datos del **II bimestre** por error; se descartaron (quedan en `data/raw/_respaldos/2026_post_ii_bimestre_incorrecto/`). Fase 7 vuelve a empezar
- [x] Fichas POST del **III bimestre** (10/08–09/10, D13) consolidadas con `preprocess.py` → `data/processed/2026_post.csv`: 69 incluidos (35 / 34), 1 excluido (EST-020, traslado, sin notas) (2026-10-21)
- [x] `deserto` del directivo en `data/raw/2026_desenlace/` y validación del modelo con `ml/validar_desenlace.py` (D14, 2026-10-21): AUC 0.687, recall 0.09 (corte 0.50) / 0.45 (corte 0.222); corte del `deserto` 09/10/2026; declarar como limitación
- [x] Mismas fichas, mismo procedimiento que Fase 1, para ambos grupos (`momento` corregido a `post` en las 3 fichas; original en `data/raw/_respaldos/2026_post_iii_bimestre_momento_pre/`)

### Fase 8 — Análisis estadístico
- [x] `stats/analisis.py` (adelantado, 2026-10-10): tablas PRE listas (descriptivos, niveles, normalidad, contraste, métricas del modelo); la parte POST se activa con `--post`
- [x] `analisis.py --post --intragrupo` con PRE v5 y POST III bimestre, `rf_v5` (2026-10-21): POST control vs experimental significativo en los 4 contrastes (p < 0.001). Corregido en `analisis.py` que la CV de `6_metricas_modelo.csv` salía de `rf_v3`
- [x] Variable contrastada y Wilcoxon decididos (D15): nivel de riesgo (HG) e indicadores (H1–H3) control vs experimental en el POST; Wilcoxon PRE vs POST como complementario
- [x] Tablas exportadas para Word en `stats/output/` (CSV con `;` y coma decimal), incluida `7_validacion_desenlace.csv`

### Fase 9 — Redacción
- [x] Contexto y prompt para el chat de redacción: `docs/avances/2026-10-21_contexto_redaccion_tesis.md` y `2026-10-21_prompt_plan_redaccion.md`; guía UCV en `guia_de_elaboracion_tesis.md` (2026-10-21)
- [ ] Actualizar Metodología con lo ejecutado y corregir las observaciones 1–11 del contexto
- [ ] Capítulo III Resultados (orden: general → OE1 → OE2 → OE3, más complementario y validación externa)
- [ ] Capítulo IV Discusión (contraste con antecedentes y limitaciones)
- [ ] Capítulos V Conclusiones y VI Recomendaciones; Resumen y Abstract; Referencias (mín. 30) y anexos

---

## 🎯 Hito 2 — Sábado 24/10/2026: tesis completa
Estado al 2026-10-21: fases 0–5, 7 y 8 hechas; la redacción (Fase 9) la hace el autor en otro chat. Pendientes fuera del camino crítico: despliegue (Fase 6) y creación de usuarios (Fase 4).

## 🎯 Hito 1 — Sábado 26/09/2026
**Mínimo:** Fase 0 completa + plantillas de fichas (Fase 1, primer punto).
**Extra si da el tiempo:** prueba de concepto del pipeline con datos **sintéticos** (entrenar → predecir), presentada explícitamente como validación técnica, no como resultado.
Guion y preguntas para el docente → `LOG_AVANCES.md`.
