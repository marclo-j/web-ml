# Plan — Cierre de Fase 0 + plantillas de fichas (Fase 1, punto 1)

> Aprobado el 2026-09-24. Pendiente de ejecución.

## Contexto
El Hito 1 (sábado 26/09/2026) exige como mínimo la Fase 0 completa y las plantillas de las 3 fichas.

Decisiones tomadas:
- Cerrar la Fase 0 antes de las fichas.
- Ficha de rendimiento con **nota por curso**: la plantilla calcula `suma_notas`, `n_notas` y `promedio`, y soporta escala vigesimal o literal.
- **Periodo de corte = I bimestre / trimestre**, igual para el PRE 2026 y para el histórico 2024–2025. Evita fuga de información: un desertor tiene menos días asistidos *porque* se fue, y si se usa el año completo el modelo aprende la consecuencia y no la causa.

## 1. Cerrar Fase 0
- Crear la estructura de `docs/ARQUITECTURA.md` con `.gitkeep`: `data/{raw,processed,synthetic}/`, `ml/models/`, `stats/`, `backend/app/{routers,services}/`, `frontend/{app,components,lib}/` y la nueva carpeta `fichas/`.
- Verificar que `git status` no lista nada bajo `data/raw` ni `data/processed`.

## 2. Plantillas de fichas (Excel) — `fichas/`
Generadas por un script reproducible `fichas/generar_fichas.py` (openpyxl) → 3 archivos versionados (plantillas vacías, sin datos reales):

| Archivo | Columnas de captura | Columnas calculadas |
|---|---|---|
| `ficha_1_rendimiento.xlsx` | codigo, grado, seccion, grupo, momento, una columna por área curricular MINEDU de secundaria (Matemática, Comunicación, Inglés, Arte y Cultura, CC.SS., DPCC, Ed. Física, Ed. Religiosa, CyT, EPT) | `n_notas`, `suma_notas` (convertida si es literal), `promedio` = suma/n redondeado a 2 |
| `ficha_2_asistencia.xlsx` | codigo, grado, seccion, grupo, momento, `dias_programados` (DP), `dias_asistidos` (DA) | `pct_asistencia` = DA/DP×100 |
| `ficha_3_reuniones.xlsx` | codigo, grado, seccion, grupo, momento, `reuniones_programadas` (RT), `reuniones_asistidas` (RA) | `pct_reuniones` = RA/RT×100 |

Común a las 3:
- Hoja **Instrucciones**: fórmula de la tesis con su cita ([1] Albonny y Duru / [39] Ttito y Choque), periodo de corte y reglas de anonimización (solo `EST-###`, sin nombres ni DNI, Ley N.° 29733).
- Encabezado: año, periodo (I bimestre/trimestre), fecha_inicio, fecha_fin, responsable.
- Columnas opcionales para el histórico: `anio`, `deserto` (0/1).
- Columnas de exclusión: `excluido` (sí/no), `motivo_exclusion` (traslado, dato faltante, inconsistente).
- Validaciones de `VARIABLES.md`: grado ∈ {3, 4}, grupo/momento en lista, DA ≤ DP, RA ≤ RT, divisores > 0, codigo con patrón `EST-###`; celdas calculadas bloqueadas y resaltadas.
- Ficha 1: celda "escala" (vigesimal / literal) + hoja **Conversión** (AD=4, A=3, B=2, C=1, provisional hasta cerrar D1).
- Nombres de columna 1:1 con el CSV de carga masiva de `VARIABLES.md`.

## 3. Documentación
- `VARIABLES.md`: sección "Fichas → columnas"; nueva decisión D3 (periodo de corte) ✅.
- `MODELO.md`: nota de fuga de información y por qué el histórico usa el mismo corte.
- `ARQUITECTURA.md`: añadir `fichas/`; aclarar que la raíz real es `web-ml/`.
- `LOG_AVANCES.md`: pregunta al docente sobre el periodo de corte y observación #5 (definir periodo PRE/POST en la metodología).
- `FASES.md`: Fase 0 ✅, Fase 1 🟨 con el primer punto ✅.

## Verificación
- `python fichas/generar_fichas.py` regenera los 3 `.xlsx` sin error; `ruff` limpio.
- Fila de prueba: promedio correcto, DP=95/DA=85 → 89.47, RT=4/RA=1 → 25.00; escala literal (A, B, AD) → promedio correcto. No se guarda.
- La validación rechaza DA > DP.
