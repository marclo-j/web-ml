# ⚠️ Datos simulados — no son estudiantes reales

Generados por `ml/generate_synthetic.py` (semilla fija = 42, reproducible).

| Archivo | Uso | Contiene `deserto` |
|---|---|---|
| `historico.csv` | Entrenar el modelo mientras no llega el histórico real 2024–2025 | Sí |
| `carga_prueba.csv` | Probar `POST /registros/importar` y el dashboard con datos "2026" | No |

**No usar en:**
- El capítulo de Resultados
- Las métricas finales del modelo (`MODELO.md` → tabla de versiones)
- Las slides de sustentación, salvo etiquetado explícito como "prueba de concepto / datos simulados"

En cuanto llegue el histórico real de la IE, este archivo se reemplaza y `ml/train.py` se corre de nuevo apuntando a `data/processed/historico.csv`.

## `fichas_ejemplo/`
Las 3 fichas del PRE 2026 llenas por completo con datos **inventados** (`*_EJEMPLO.xlsx`), solo para aprender a llenarlas. Cada fila lleva `EJEMPLO` en `observaciones`: `ml/preprocess.py` se niega a procesarlas salvo con `--permitir-ejemplo`. Las fichas reales se llenan en `data/raw/2026_pre/`, nunca copiando valores de aquí.
