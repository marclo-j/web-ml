# 📊 DICCIONARIO DE DATOS

Puente entre las **fichas de registro** de la metodología y las **columnas** del sistema.

## Indicadores (features del modelo)
| Símbolo en tesis | Nombre en código | Fórmula | Datos crudos | Tipo | Rango | Ficha |
|---|---|---|---|---|---|---|
| Promedio | `promedio` | Σ Notas / n | `suma_notas`, `n_notas` | float | ❓ depende de la escala | Rendimiento académico |
| Asistencia | `pct_asistencia` | (DA / DP) × 100 | `dias_asistidos` (DA), `dias_programados` (DP) | float | 0–100 | Asistencia escolar |
| CA | `pct_reuniones` | (RA / RT) × 100 | `reuniones_asistidas` (RA), `reuniones_programadas` (RT) | float | 0–100 | Apoyo familiar |

Redondeo: 2 decimales. Se calculan **siempre en el backend** (`backend/app/services/indicadores.py`) o en `ml/preprocess.py`, con la misma función.

## Variable objetivo
| Nombre | Descripción | Tipo | Valores | Dónde |
|---|---|---|---|---|
| `deserto` | Si el alumno abandonó en ese año (dato histórico) | int | 0 / 1 | Solo en dataset de entrenamiento |
| `probabilidad` | Salida del modelo, P(deserto = 1) | float | 0–1 | Predicciones |
| `nivel_riesgo` | Nivel derivado de la probabilidad | categórica ordinal | bajo / medio / alto | Predicciones |
| `nivel_riesgo_real` | Valor de referencia de la IE para evaluar el modelo en 2026 | categórica | ❓ por definir | Registros |

Umbrales de probabilidad → nivel: ver `MODELO.md`.

## Identificación y diseño
| Campo | Tipo | Valores | Nota |
|---|---|---|---|
| `codigo` | text | `EST-001`… | Anonimizado; sin nombres ni DNI |
| `grado` | int | 3, 4 | |
| `seccion` | text | ej. `A` | |
| `grupo` | text | `control`, `experimental` | 3.° = control, 4.° = experimental |
| `momento` | text | `pre`, `post` | |
| `anio` | int | 2024, 2025, 2026 | 2024–2025 = histórico |

## Reglas de validación
| Regla | Acción si falla |
|---|---|
| `n_notas > 0`, `dias_programados > 0`, `reuniones_programadas > 0` | Rechazar (división por cero) |
| `dias_asistidos ≤ dias_programados` | Rechazar |
| `reuniones_asistidas ≤ reuniones_programadas` | Rechazar |
| Promedio dentro del rango de la escala | Rechazar |
| Falta cualquiera de las 3 dimensiones | **Excluir** (criterio de exclusión de la tesis) y contarlo |
| Traslado definitivo antes del cierre | **Excluir** y contarlo |

Los excluidos se reportan en Resultados (cuántos y por qué).

## Formato CSV de carga masiva
```csv
codigo,grado,seccion,grupo,momento,suma_notas,n_notas,dias_asistidos,dias_programados,reuniones_asistidas,reuniones_programadas
EST-001,4,A,experimental,pre,142,10,85,95,2,4
```
Dataset histórico: mismas columnas + `anio,deserto`.

## Fichas → columnas
Las 3 fichas están en `fichas/` (plantillas Excel generadas por `fichas/generar_fichas.py`). Se unen por `codigo` + `momento` + `anio`.

| Ficha | Se captura | Se calcula en la ficha |
|---|---|---|
| 1 · Rendimiento académico | Nota de cada una de las 10 áreas curriculares de secundaria (`matematica`, `comunicacion`, `ingles`, `arte_cultura`, `ciencias_sociales`, `dpcc`, `educacion_fisica`, `educacion_religiosa`, `ciencia_tecnologia`, `ept`); vacío si no aplica (ej. exonerado) | `n_notas` (solo notas válidas), `suma_notas`, `promedio` |
| 2 · Asistencia escolar | `dias_programados`, `dias_asistidos` | `pct_asistencia` |
| 3 · Apoyo familiar | `reuniones_programadas`, `reuniones_asistidas` | `pct_reuniones` |

Columnas comunes: `codigo`, `grado`, `seccion`, `grupo` (calculado: 3.° = control, 4.° = experimental), `momento`, `anio`, `deserto` (solo histórico), `excluido`, `motivo_exclusion`, `observaciones`.

El cálculo en la ficha sirve para revisar al llenar; el valor oficial lo recalcula el backend / `ml/preprocess.py` a partir de los datos crudos.

## Consolidación y exclusiones (`ml/preprocess.py`)
Une las 3 fichas de un lote por `codigo` + `anio` + `momento`, aplica las reglas de validación y clasifica cada exclusión en uno de los 3 criterios de la tesis:

| Motivo | Cuándo |
|---|---|
| `traslado definitivo` | Marcado en cualquiera de las fichas (`excluido = sí`) |
| `dimensión incompleta` | Falta el alumno en alguna ficha, falta un dato obligatorio, no tiene ninguna nota o, en el histórico, falta `deserto` |
| `registro inconsistente` | Nota fuera de la escala, DA > DP, RA > RT, código que no es `EST-###`, grado o sección distintos entre fichas, alumno repetido, `deserto` lleno en 2026 |

```bash
ml/.venv/Scripts/python ml/preprocess.py --entrada data/raw/2026_pre --salida data/processed/2026_pre.csv
```
Genera `2026_pre.csv` (incluidos con indicadores), `2026_pre_excluidos.csv` (motivo, detalle y fila de Excel de cada excluido) y `2026_pre_resumen.json` (conteos por motivo y grupo, para Resultados). Se niega a escribir fuera de `data/processed/`. Un lote debe usar una sola escala de calificación.

## ❓ Decisiones pendientes
| # | Decisión | Opciones | Estado |
|---|---|---|---|
| D1 | Escala de calificación de la IE | a) Vigesimal 0–20 (usar tal cual) · b) Literal AD/A/B/C (normativa MINEDU para EBR, RVM N.° 094-2020-MINEDU) → convertir a numérico (ej. AD=4, A=3, B=2, C=1) y justificarlo en la tesis | 🟨 Tentativo: vigesimal (práctica habitual en secundaria según el autor). Confirmar cómo están los registros de la IE, incluido el histórico 2024–2025 (la ficha 1 soporta ambas) |
| D2 | Qué es `nivel_riesgo_real` en 2026 | a) Clasificación del tutor/TOE · b) Deserción efectiva al cierre del periodo · c) Otra fuente institucional | ⬜ Consultar con asesor |
| D3 | Periodo de corte de los indicadores | Datos acumulados hasta el cierre del **I bimestre** (la IE trabaja por bimestres), igual para el PRE 2026 y el histórico 2024–2025 | ✅ Decidido 2026-09-24 (ver `MODELO.md` → fuga de información) |
