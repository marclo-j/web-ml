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

## ❓ Decisiones pendientes
| # | Decisión | Opciones | Estado |
|---|---|---|---|
| D1 | Escala de calificación de la IE | a) Vigesimal 0–20 (usar tal cual) · b) Literal AD/A/B/C (normativa MINEDU para EBR, RVM N.° 094-2020-MINEDU) → convertir a numérico (ej. AD=4, A=3, B=2, C=1) y justificarlo en la tesis | ⬜ Confirmar con la IE |
| D2 | Qué es `nivel_riesgo_real` en 2026 | a) Clasificación del tutor/TOE · b) Deserción efectiva al cierre del periodo · c) Otra fuente institucional | ⬜ Consultar con asesor |
