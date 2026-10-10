# Web con Machine Learning — Riesgo de deserción escolar

Sistema web que clasifica el nivel de riesgo de deserción escolar (bajo / medio / alto) a partir del promedio de calificaciones, el porcentaje de asistencia y la asistencia a reuniones de padres, usando Random Forest.

Proyecto de tesis — Ingeniería de Sistemas, Universidad César Vallejo, 2026.

## Requisitos
- Python 3.11+
- Node.js 20+
- Cuenta de Supabase (proyecto creado)

## Inicio rápido

### 1. Variables de entorno
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```
| Variable | Dónde | Descripción |
|---|---|---|
| `DATABASE_URL` | backend | Cadena del connection pooler de Supabase |
| `SUPABASE_URL` | backend / frontend | URL del proyecto |
| `SUPABASE_ANON_KEY` | frontend | Clave pública |
| `SUPABASE_JWT_SECRET` | backend | Para validar tokens |
| `MODEL_PATH` | backend | ej. `ml/models/rf_v3.joblib` (relativo a la raíz del repo) |
| `AUTH_DESACTIVADA` | backend | `1` solo en desarrollo local con SQLite (sin login) |
| `NEXT_PUBLIC_API_URL` | frontend | ej. `http://localhost:8000` |

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
uvicorn app.main:app --reload    # http://localhost:8000/docs
pytest                           # pruebas
```
Sin `DATABASE_URL` usa SQLite (`backend/local.db`). Para Supabase: ejecutar `backend/sql/001_esquema.sql` en el SQL Editor y poner en `DATABASE_URL` la cadena del *Transaction pooler*.
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev                      # http://localhost:3000
```

## Documentación
Todo en [`/docs`](docs/). Empezar por [`FASES.md`](docs/FASES.md) y [`CONTEXTO.md`](docs/CONTEXTO.md).

## Privacidad
Los datos reales de estudiantes no se versionan. El sistema solo almacena códigos anonimizados (Ley N.° 29733).
