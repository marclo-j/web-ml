# 🔌 API — Backend FastAPI

Base URL local: `http://localhost:8000` · Documentación automática: `/docs` (Swagger)
Autenticación: header `Authorization: Bearer <token de Supabase>` en todo excepto `/health`.

## Resumen
| Método | Ruta | Descripción | Estado |
|---|---|---|---|
| GET | `/health` | Verifica que el servicio y el modelo cargaron | ⬜ |
| POST | `/predecir` | Predicción directa sin guardar (demo/pruebas) | ⬜ |
| GET | `/estudiantes` | Lista estudiantes con su última predicción | ⬜ |
| POST | `/estudiantes` | Crea un estudiante | ⬜ |
| GET | `/estudiantes/{id}` | Detalle con registros PRE/POST y predicciones | ⬜ |
| POST | `/registros` | Guarda datos crudos → calcula indicadores → predice | ⬜ |
| POST | `/registros/importar` | Carga masiva por CSV (formato en `VARIABLES.md`) | ⬜ |
| GET | `/resumen` | Conteo por nivel de riesgo, por grupo y momento | ⬜ |
| GET | `/modelo` | Versión, métricas y umbrales del modelo activo | ⬜ |

---

## GET `/health`
```json
{ "status": "ok", "modelo": "rf_v1" }
```

## POST `/predecir`
Request (datos crudos, igual que las fichas):
```json
{
  "suma_notas": 142, "n_notas": 10,
  "dias_asistidos": 85, "dias_programados": 95,
  "reuniones_asistidas": 1, "reuniones_programadas": 4
}
```
Response:
```json
{
  "indicadores": { "promedio": 14.2, "pct_asistencia": 89.47, "pct_reuniones": 25.0 },
  "probabilidad": 0.41,
  "nivel_riesgo": "medio",
  "version_modelo": "rf_v1"
}
```

## GET `/estudiantes?grupo=experimental&momento=pre&nivel=alto`
Filtros opcionales: `grupo`, `momento`, `nivel`.
```json
[
  {
    "id": "uuid", "codigo": "EST-001", "grado": 4, "seccion": "A",
    "grupo": "experimental",
    "ultima_prediccion": { "momento": "pre", "nivel_riesgo": "alto", "probabilidad": 0.78 }
  }
]
```

## POST `/estudiantes`
```json
{ "codigo": "EST-001", "grado": 4, "seccion": "A", "grupo": "experimental" }
```

## POST `/registros`
```json
{
  "estudiante_id": "uuid", "momento": "pre",
  "suma_notas": 142, "n_notas": 10,
  "dias_asistidos": 85, "dias_programados": 95,
  "reuniones_asistidas": 1, "reuniones_programadas": 4
}
```
Response: el registro con indicadores calculados + la predicción creada.

## POST `/registros/importar`
`multipart/form-data` con campo `archivo` (.csv).
```json
{ "procesados": 35, "excluidos": 2, "detalle_excluidos": [
  { "fila": 12, "codigo": "EST-012", "motivo": "dias_asistidos > dias_programados" }
] }
```

## GET `/resumen?momento=pre`
```json
{
  "control":      { "bajo": 18, "medio": 10, "alto": 7 },
  "experimental": { "bajo": 16, "medio": 11, "alto": 8 }
}
```

## GET `/modelo`
```json
{
  "version": "rf_v1", "entrenado": "2026-10-05",
  "features": ["promedio", "pct_asistencia", "pct_reuniones"],
  "metricas": { "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0 },
  "umbrales": { "medio": 0.33, "alto": 0.66 }
}
```
_(valores de ejemplo, no resultados)_

## Errores
| Código | Cuándo |
|---|---|
| 401 | Token ausente o inválido |
| 404 | Estudiante/registro inexistente |
| 422 | Falla una regla de validación de `VARIABLES.md` (el mensaje indica cuál) |
| 503 | Modelo no cargado |
