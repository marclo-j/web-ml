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
| 3 | Falta precisar la escala de calificación de la IE y su conversión si es literal | Metodología, ficha de rendimiento | ⬜ |
| 4 | Falta indicar el origen de los datos etiquetados para entrenar el modelo | Metodología | ⬜ |
| 5 | Falta definir el periodo que abarcan el PRE y el POST (periodo de corte, decisión D3) | Metodología, instrumentos | ⬜ |
