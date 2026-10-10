"""API del sistema de riesgo de deserción escolar (docs/API.md).

Desarrollo (desde backend/):  .venv/Scripts/uvicorn app.main:crear_app --factory --reload
Swagger:                      http://localhost:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import SECRETO_MINIMO, LimitadorIntentos
from .config import Config, leer_config
from .db import crear_sesiones
from .routers import auth, estudiantes, general, registros
from .services.modelo import cargar_modelo

log = logging.getLogger("uvicorn.error")


def crear_app(config: Config | None = None) -> FastAPI:
    config = config or leer_config()
    if config.auth_desactivada and not config.database_url.startswith("sqlite"):
        raise RuntimeError(
            "AUTH_DESACTIVADA=1 solo se permite con SQLite (desarrollo local)"
        )
    if not config.auth_desactivada and len(config.jwt_secret) < SECRETO_MINIMO:
        raise RuntimeError(
            f"JWT_SECRET debe tener al menos {SECRETO_MINIMO} caracteres "
            '(generar con: python -c "import secrets; print(secrets.token_urlsafe(48))")'
        )

    app = FastAPI(
        title="Riesgo de deserción escolar",
        description="Random Forest sobre promedio, % asistencia y % reuniones "
        "(tesis UCV 2026).",
        version="1.0.0",
    )
    app.state.config = config
    app.state.limitador = LimitadorIntentos()
    app.state.sesiones = crear_sesiones(config.database_url)
    try:
        app.state.modelo = cargar_modelo(config.model_path)
        log.info("Modelo cargado: %s", app.state.modelo.version)
    except (FileNotFoundError, ValueError) as error:
        # /health lo informa y los endpoints que predicen responden 503
        app.state.modelo = None
        log.warning("Sin modelo: %s", error)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(auth.router)
    app.include_router(general.router)
    app.include_router(estudiantes.router)
    app.include_router(registros.router)
    return app
