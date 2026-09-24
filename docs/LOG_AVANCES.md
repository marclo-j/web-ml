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

**Feedback recibido:** _(completar tras la presentación)_
**Decisiones tomadas:** _(completar)_
**Pendientes derivados:** _(completar)_

---

### 2026-09-24 — Repositorio en GitHub y plan de Fase 0 + fichas
**Tipo:** desarrollo
**Qué se hizo:** Se inicializó el repositorio git, se añadió `.gitignore` (datos reales fuera) y se subió a GitHub (`marclo-j/web-ml`). Se guardó el plan de trabajo en `docs/planes/2026-09-24_fase0-y-fichas.md`.
**Decisiones tomadas:**
- Ficha de rendimiento con nota por curso; la plantilla calcula `suma_notas`, `n_notas` y `promedio` (soporta escala vigesimal o literal).
- Periodo de corte: I bimestre / trimestre, igual para PRE 2026 e histórico 2024–2025, para evitar fuga de información (un desertor tiene menos asistencia porque ya se fue).
**Pendientes derivados:** ejecutar el plan (estructura de carpetas + fichas) y registrar D3 en `VARIABLES.md`.

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
