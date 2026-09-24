# 🗺️ FASES DEL PROYECTO

> Estado: ⬜ pendiente · 🟨 en progreso · ✅ hecho · ⛔ bloqueado
> Actualizar al final de cada sesión de trabajo.

## Resumen
| Fase | Nombre | Estado | Depende de | Entregable principal |
|---|---|---|---|---|
| 0 | Setup y documentación | ✅ | — | Repo con estructura y `/docs` |
| 1 | Fichas y recolección PRE | ⬜ | 0 | 3 fichas + datos PRE de los 70 alumnos |
| 2 | Dataset de entrenamiento (etiquetado) | ⬜ | 1 | CSV histórico con variable objetivo |
| 3 | Entrenamiento y evaluación del modelo | ⬜ | 2 | `rf_v1.joblib` + métricas |
| 4 | Backend (API) | ⬜ | 3 | FastAPI con predicción y CRUD |
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
- [ ] Cerrar decisiones pendientes marcadas con ❓ en `VARIABLES.md` y `MODELO.md` — sigue abierto, depende de la IE y del asesor

### Preparación de Fase 3 (adelantada)
- [x] `ml/generate_synthetic.py` + `data/synthetic/historico.csv` y `carga_prueba.csv`, para no bloquear el desarrollo mientras llega el histórico real (ver `LOG_AVANCES.md`)

**Qué decir al presentar:** "Definí la arquitectura (frontend, backend, base de datos y modelo), el diccionario de datos que traduce mis 3 fichas a variables del sistema, y el plan de fases hasta Resultados."

### Fase 1 — Fichas y recolección PRE
- [ ] Diseñar las 3 fichas como plantillas (Excel/Sheets) con las columnas de `VARIABLES.md`
- [ ] Confirmar con la IE la escala de calificación (vigesimal o literal)
- [ ] Solicitar datos de los 70 alumnos (momento PRE)
- [ ] Aplicar criterios de inclusión/exclusión y registrar cuántos se excluyeron y por qué

**Qué decir:** "Las fichas aplican exactamente las fórmulas de mi metodología; aquí está la estructura y el estado de recolección."

### Fase 2 — Dataset de entrenamiento
- [ ] Solicitar a la IE registros de 2024–2025 con desenlace conocido (desertó sí/no)
- [ ] Limpiar, anonimizar y consolidar en `data/processed/historico.csv`
- [ ] Documentar tamaño, balance de clases y exclusiones en `MODELO.md`

**Qué decir:** "El modelo es supervisado: aprende de alumnos de años anteriores cuyo desenlace ya se conoce."

### Fase 3 — Modelo
- [ ] Script `ml/train.py` con validación cruzada estratificada
- [ ] Métricas: accuracy, precision, recall, F1 + matriz de confusión
- [ ] Importancia de variables (sustenta OE1–OE3)
- [ ] Guardar modelo versionado y registrar en `MODELO.md`

**Qué decir:** "Estas son las métricas del modelo y el peso de cada dimensión en la predicción."

### Fase 4 — Backend
- [ ] Endpoints de `API.md` implementados
- [ ] Conexión a Supabase
- [ ] Cálculo de indicadores en el servidor (no en el cliente)

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
