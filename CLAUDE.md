# CLAUDE.md — Web con Machine Learning para riesgo de deserción escolar

Proyecto de tesis (Ingeniería de Sistemas, UCV). Web que clasifica el **nivel de riesgo de deserción escolar** (bajo / medio / alto) de estudiantes de 3.° y 4.° de secundaria de una IE de Comas, Lima, 2026, usando **Random Forest** sobre 3 indicadores.

## Orden de lectura al iniciar sesión
1. `docs/FASES.md` → en qué fase estamos y qué sigue
2. `docs/CONTEXTO.md` → qué es el proyecto (tesis, objetivos, variables)
3. Solo si la tarea lo requiere:
   | Tarea | Leer |
   |---|---|
   | Datos, fórmulas, CSV, validaciones | `docs/VARIABLES.md` |
   | Entrenamiento, métricas, umbrales | `docs/MODELO.md` |
   | Backend / endpoints | `docs/API.md` |
   | Estructura, stack, despliegue | `docs/ARQUITECTURA.md` |
   | Pruebas estadísticas, capítulo Resultados | `docs/PLAN_ESTADISTICO.md` |
   | Feedback del docente, historial | `docs/LOG_AVANCES.md` |

## Reglas no negociables
- **Datos reales nunca se commitean.** `data/raw/` y `data/processed/` están en `.gitignore`. Son datos de menores (Ley N.° 29733). Solo se usan códigos anonimizados (`EST-001`).
- **Datos sintéticos (`data/synthetic/`) solo sirven para probar el pipeline.** Jamás se reportan en Resultados ni en slides como hallazgos.
- **Las fórmulas son las de la tesis** (ver `docs/VARIABLES.md`). No inventar indicadores nuevos sin registrarlo como decisión.
- Toda decisión técnica o metodológica nueva → se anota en el doc correspondiente y en `docs/LOG_AVANCES.md`.
- Al cerrar una sesión de trabajo → actualizar estado en `docs/FASES.md`.

## Convenciones
- Idioma: español en docs, UI y comentarios; nombres de variables en código en español sin tildes (`pct_asistencia`).
- Python 3.11, formateo con `ruff`. TypeScript en frontend.
- Commits: `tipo(área): descripción` → ej. `feat(ml): entrenamiento RF con validación cruzada`.
- Redacción de capítulos de tesis: prosa, tercera persona, tiempo pasado (Resultados) o presente (Discusión), sin viñetas ni negritas, citas en formato **IEEE** `[n]`.
