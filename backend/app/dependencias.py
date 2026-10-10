"""Dependencias comunes de los routers."""

from collections.abc import Iterator

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from .db import sesion_desde
from .services.modelo import ModeloRiesgo


def sesion(request: Request) -> Iterator[Session]:
    yield from sesion_desde(request.app.state.sesiones)


def modelo(request: Request) -> ModeloRiesgo:
    cargado = request.app.state.modelo
    if cargado is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Modelo no cargado")
    return cargado
