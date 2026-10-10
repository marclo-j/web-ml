"""Configuración por variables de entorno (ver backend/.env.example)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[2]


def _cargar_env(ruta: Path) -> None:
    """Lee backend/.env si existe (sin dependencias extra). No pisa el entorno."""
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


@dataclass(frozen=True)
class Config:
    database_url: str
    model_path: Path
    supabase_url: str
    supabase_jwt_secret: str
    auth_desactivada: bool
    cors_origins: list[str] = field(default_factory=list)


def leer_config() -> Config:
    _cargar_env(Path(__file__).resolve().parents[1] / ".env")
    ruta_modelo = Path(os.getenv("MODEL_PATH", "ml/models/rf_v3.joblib"))
    if not ruta_modelo.is_absolute():
        ruta_modelo = RAIZ_REPO / ruta_modelo
    return Config(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./local.db"),
        model_path=ruta_modelo,
        supabase_url=os.getenv("SUPABASE_URL", "").rstrip("/"),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        # Solo para desarrollo local; main.py se niega a arrancar así con Postgres
        auth_desactivada=os.getenv("AUTH_DESACTIVADA", "") == "1",
        cors_origins=_lista(os.getenv("CORS_ORIGINS", "http://localhost:3000")),
    )
