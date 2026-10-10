# 🗺️ FASES DEL PROYECTO

> Estado: ⬜ pendiente · 🟨 en progreso · ✅ hecho · ⛔ bloqueado
> Actualizar al final de cada sesión de trabajo.

## Resumen
| Fase | Nombre | Estado | Depende de | Entregable principal |
|---|---|---|---|---|
| 0 | Setup y documentación | ✅ | — | Repo con estructura y `/docs` |
| 1 | Fichas y recolección PRE | ✅ | 0 | 3 fichas + datos PRE de los 70 alumnos. Vigente: PRE 2026 v5 (2026-10-09, 3.° A control 35, 4.° B experimental 34, 1 excluido por traslado) |
| 2 | Dataset de entrenamiento (etiquetado) | ✅ | 1 | `data/processed/2024_pre_v5.csv`: 70 alumnos (2024), 13 desertores; se completa con aumento SMOTE solo en entrenamiento (D8). 2025 descartado |
| 3 | Entrenamiento y evaluación del modelo | ✅ | 2 | `rf_v3` (2024 + SMOTE): CV 5x5 sobre reales AUC 0.99, F1 0.91. Hiperparámetros iniciales (la búsqueda no mejora). Umbrales D9: 0.15 / 0.50 |
| 4 | Backend (API) | 🟨 | 3 | FastAPI con predicción y CRUD — implementado y probado; falta conectar el proyecto de Supabase |
| 5 | Frontend (dashboard) | ⬜ | 4 | Web con listado de riesgo por alumno |
| 6 | Despliegue e intervención | ⬜ | 5 | Web en producción, usada con grupo experimental |
| 7 | Recolección POST | ⬜ | 6 | Datos POST de los 70 alumnos |
| 8 | Análisis estadístico | ⬜ | 7 | Tablas de normalidad, contraste y métricas |
| 9 | Redacción de Resultados y Discusión | ⬜ | 8 | Capítulos III y IV |

---

## Detalle por fase

### Fase 0 — Setup y documentación ✅
- [x] Definir documentos del repo
- [x] Crear repo y estructura de carpetas (`ARQUITECTURA.md`)
- [x] Configurar `.gitignore` (datos reales fuera)
- [x] Cerrar decisiones pendientes de `VARIABLES.md` y `MODELO.md` (D2 opción b, umbral 50 %, cita [42]) — 2026-10-03. Siguen abiertas con el asesor las del `PLAN_ESTADISTICO.md` (variable contrastada y Wilcoxon / t pareada)

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
- [x] Corridas de prueba: `rf_v0` (sintético) y `rf_v0b` (Opción B, real PRE 2026) — ver `MODELO.md`, ninguna es resultado de tesis

**Qué decir:** "El modelo detecta a los desertores del histórico con AUC 0.99 evaluado solo sobre alumnos reales; la asistencia y la participación familiar son las dimensiones que más pesan. Los niveles bajo, medio y alto salen de las probabilidades del propio histórico."

### Fase 4 — Backend
- [x] Endpoints de `API.md` implementados (`backend/app/`, 28 pruebas) — 2026-10-10
- [x] Cálculo de indicadores en el servidor (`services/indicadores.py`, idéntico a `ml/preprocess.py`, lo comprueba una prueba)
- [x] Autenticación con tokens de Supabase (HS256 o JWKS)
- [x] Prueba de punta a punta con `rf_v3`: importar PRE 2026 por CSV da el mismo resumen (27/7/1 y 27/4/3)
- [ ] Conexión a Supabase: código y esquema listos (`sql/001_esquema.sql`); falta que el autor cree el proyecto y complete `backend/.env`

### Fase 5 — Frontend
- [ ] Login simple para tutor/directivo
- [ ] Tabla de alumnos con nivel de riesgo y color
- [ ] Formulario de registro + carga masiva por CSV
- [ ] Vista de detalle por alumno (sus 3 indicadores)

**Qué decir (4 + 5):** Demo en vivo del flujo: se cargan los datos de un alumno → la web calcula los indicadores → el modelo devuelve el nivel de riesgo.

### Fase 6 — Despliegue e intervención
- [ ] Backend en Render, frontend en Vercel
- [ ] Capacitación breve a tutores del grupo experimental
- [ ] Registrar fecha de inicio y fin de la intervención

### Fase 7 — Recolección POST
- [ ] Mismas fichas, mismo procedimiento que Fase 1, para ambos grupos

### Fase 8 — Análisis estadístico
- [ ] Seguir `PLAN_ESTADISTICO.md` paso a paso
- [ ] Exportar tablas listas para Word

### Fase 9 — Redacción
- [ ] Capítulo III Resultados (orden: general → OE1 → OE2 → OE3)
- [ ] Capítulo IV Discusión (contraste con antecedentes)

---

## 🎯 Hito 1 — Sábado 26/09/2026
**Mínimo:** Fase 0 completa + plantillas de fichas (Fase 1, primer punto).
**Extra si da el tiempo:** prueba de concepto del pipeline con datos **sintéticos** (entrenar → predecir), presentada explícitamente como validación técnica, no como resultado.
Guion y preguntas para el docente → `LOG_AVANCES.md`.
