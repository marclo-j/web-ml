# Web con Machine Learning — Riesgo de deserción escolar

Sistema web que clasifica el nivel de riesgo de deserción escolar (bajo / medio / alto) a partir del promedio de calificaciones, el porcentaje de asistencia y la asistencia a reuniones de padres, usando Random Forest.

Proyecto de tesis — Ingeniería de Sistemas, Universidad César Vallejo, 2026.

## Requisitos
- Python 3.11+
- Node.js 20+
- Proyecto de Neon (PostgreSQL) para producción; en desarrollo basta SQLite

## Inicio rápido

### 1. Variables de entorno
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```
| Variable | Dónde | Descripción |
|---|---|---|
| `DATABASE_URL` | backend | Cadena de Neon con *connection pooling* (host `-pooler`, `sslmode=require`). Vacío = SQLite local |
| `JWT_SECRET` | backend | Secreto para firmar las sesiones (≥ 32 caracteres) |
| `JWT_EXPIRA_MIN` | backend | Duración de la sesión (por defecto 480 min) |
| `MODEL_PATH` | backend | ej. `ml/models/rf_v3.joblib` (relativo a la raíz del repo) |
| `AUTH_DESACTIVADA` | backend | `1` solo en desarrollo local con SQLite (sin login) |
| `API_URL` | frontend | URL del backend, ej. `http://localhost:8000` (solo la usa el servidor de Next.js) |

### 2. Modelo
```bash
cd ml
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python generate_synthetic.py     # solo si aún no hay datos reales
python train.py --data ../data/synthetic/historico.csv --version v0
```

### 3. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:crear_app --factory --reload    # http://localhost:8000/docs
python -m app.crear_usuario --email tutor@ie.edu.pe --rol tutor   # pide la contraseña
pytest                           # pruebas
```
Sin `DATABASE_URL` usa SQLite (`backend/local.db`). Para Neon: ejecutar `backend/sql/001_esquema.sql` en el SQL Editor del proyecto y poner su cadena en `DATABASE_URL`. No hay registro público: los usuarios se crean con `app.crear_usuario` (también `--restablecer` y `--desactivar`).
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev                      # http://localhost:3000 (con el backend en marcha)
npm run lint && npm run build    # verificación
```
Páginas: login, estudiantes (resumen por grupo y nivel, filtros, tabla), detalle por alumno, registrar, importar CSV, modelo y cuenta.

## Documentación
Todo en [`/docs`](docs/). Empezar por [`FASES.md`](docs/FASES.md) y [`CONTEXTO.md`](docs/CONTEXTO.md).

## Privacidad
Los datos reales de estudiantes no se versionan. El sistema solo almacena códigos anonimizados (Ley N.° 29733).
