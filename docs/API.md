# 🔌 API — Backend FastAPI

Base URL local: `http://localhost:8000` · Documentación automática: `/docs` (Swagger)
Autenticación propia (D10): `POST /auth/login` devuelve un token; enviarlo como `Authorization: Bearer <token>` en todo excepto `/health` y `/auth/login`. En `/docs`, el botón *Authorize* inicia sesión con correo y contraseña.

Código: `backend/app/` (routers en `routers/`, fórmulas en `services/indicadores.py`, modelo en `services/modelo.py`). Pruebas: `backend/tests/` (42). Esquema de la base (Neon): `backend/sql/001_esquema.sql`.

## Resumen
| Método | Ruta | Descripción | Estado |
|---|---|---|---|
| GET | `/health` | Verifica que el servicio y el modelo cargaron | ✅ |
| POST | `/auth/login` | Inicia sesión (correo + contraseña) → token | ✅ |
| GET | `/auth/yo` | Usuario de la sesión (correo y rol) | ✅ |
| POST | `/auth/cambiar-password` | Cambia la contraseña propia | ✅ |
| POST | `/predecir` | Predicción directa sin guardar (demo/pruebas) | ✅ |
| GET | `/estudiantes` | Lista estudiantes con su última predicción | ✅ |
| POST | `/estudiantes` | Crea un estudiante | ✅ |
| GET | `/estudiantes/{id}` | Detalle con registros PRE/POST y predicciones | ✅ |
| POST | `/registros` | Guarda datos crudos → calcula indicadores → predice | ✅ |
| POST | `/registros/importar` | Carga masiva por CSV (formato en `VARIABLES.md`) | ✅ |
| GET | `/resumen` | Conteo por nivel de riesgo, por grupo y momento | ✅ |
| GET | `/modelo` | Versión, métricas y umbrales del modelo activo | ✅ |

---

## GET `/health`
```json
{ "status": "ok", "modelo": "rf_v3" }
```

## POST `/auth/login`
`application/x-www-form-urlencoded` (formulario OAuth2): `username` = correo, `password`.
```json
{
  "access_token": "eyJ...", "token_type": "bearer", "expira_en": 28800,
  "usuario": { "email": "tutor@ie.edu.pe", "rol": "tutor" }
}
```
401 con el mismo mensaje si el correo no existe o la contraseña es incorrecta; 429 tras 5 intentos fallidos seguidos (bloqueo de 15 min).

## POST `/auth/cambiar-password`
```json
{ "password_actual": "...", "password_nueva": "..." }
```
204 si se cambió; 400 si la actual no es correcta; 422 si la nueva tiene menos de 10 caracteres.

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
  "version_modelo": "rf_v3"
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
Response: el registro con indicadores calculados + la predicción creada. Un registro por alumno y momento: si ya existe, se reemplazan sus datos y su predicción.

## POST `/registros/importar`
`multipart/form-data` con campo `archivo` (.csv, máx. 1 MB, separador coma o punto y coma, coma decimal admitida). Crea los alumnos que no existan; `grupo` puede ir vacío (se deduce del grado). `fila` es la línea del archivo (la 1 es el encabezado).
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
Lee el `.json` de metadatos que `ml/train.py` guarda junto al `.joblib` (y, si existe, `comparacion_aumento_<fuente>.json` para la métrica principal).
```json
{
  "version": "rf_v3", "entrenado": "2026-10-10", "fuente_datos": "historico_real",
  "features": ["promedio", "pct_asistencia", "pct_reuniones"], "n_entrenamiento": 70,
  "metricas": {
    "validacion_cruzada_k5_sobre_train": { "f1": { "media": 0.0, "desviacion": 0.0 } },
    "holdout_20pct": { "f1": 0.0 },
    "cv_5x5_sobre_reales": { "roc_auc": { "media": 0.0, "desviacion": 0.0 } }
  },
  "umbrales": { "medio": 0.15, "alto": 0.50 },
  "aumento": { "metodo": "smote", "factor": 2.0 },
  "aviso": null
}
```
_(valores de ejemplo, no resultados)_

## Errores
| Código | Cuándo |
|---|---|
| 401 | Token ausente, inválido o vencido; usuario desactivado; login incorrecto |
| 403 | El rol no permite la acción (reservado para `requiere_rol`) |
| 404 | Estudiante/registro inexistente |
| 409 | Código de estudiante ya registrado |
| 413 | CSV mayor a 1 MB |
| 429 | Demasiados intentos de login fallidos |
| 422 | Falla una regla de validación de `VARIABLES.md` (el mensaje indica cuál) |
| 503 | Modelo no cargado |
