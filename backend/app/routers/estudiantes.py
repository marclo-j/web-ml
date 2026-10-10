"""/estudiantes y /resumen."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .. import schemas
from ..auth import usuario_actual
from ..db import Estudiante, Registro
from ..dependencias import sesion as dep_sesion

router = APIRouter(dependencies=[Depends(usuario_actual)], tags=["estudiantes"])

NIVELES = ("bajo", "medio", "alto")


def _con_registros():
    return select(Estudiante).options(
        selectinload(Estudiante.registros).selectinload(Registro.prediccion)
    )


def _registro_de(estudiante: Estudiante, momento: str | None) -> Registro | None:
    """El registro del momento pedido o, sin filtro, el más reciente (post > pre)."""
    con_prediccion = {r.momento: r for r in estudiante.registros if r.prediccion}
    if momento:
        return con_prediccion.get(momento)
    return con_prediccion.get("post") or con_prediccion.get("pre")


@router.get("/estudiantes", response_model=list[schemas.EstudianteConPrediccion])
def listar(
    grupo: schemas.Grupo | None = None,
    momento: schemas.Momento | None = None,
    nivel: schemas.Nivel | None = None,
    sesion: Session = Depends(dep_sesion),
):
    consulta = _con_registros().order_by(Estudiante.codigo)
    if grupo:
        consulta = consulta.where(Estudiante.grupo == grupo)
    salida = []
    for estudiante in sesion.scalars(consulta):
        registro = _registro_de(estudiante, momento)
        if (momento or nivel) and registro is None:
            continue
        if nivel and registro.prediccion.nivel_riesgo != nivel:
            continue
        ultima = None
        if registro:
            ultima = {
                "momento": registro.momento,
                "nivel_riesgo": registro.prediccion.nivel_riesgo,
                "probabilidad": registro.prediccion.probabilidad,
            }
        datos = schemas.Estudiante.model_validate(estudiante).model_dump()
        salida.append({**datos, "ultima_prediccion": ultima})
    return salida


@router.post(
    "/estudiantes",
    response_model=schemas.Estudiante,
    status_code=status.HTTP_201_CREATED,
)
def crear(datos: schemas.EstudianteNuevo, sesion: Session = Depends(dep_sesion)):
    estudiante = Estudiante(**datos.model_dump())
    sesion.add(estudiante)
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe {datos.codigo}"
        ) from error
    return estudiante


@router.get("/estudiantes/{estudiante_id}", response_model=schemas.EstudianteDetalle)
def detalle(estudiante_id: uuid.UUID, sesion: Session = Depends(dep_sesion)):
    estudiante = sesion.scalar(_con_registros().where(Estudiante.id == estudiante_id))
    if estudiante is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Estudiante inexistente")
    estudiante.registros.sort(key=lambda r: r.momento != "pre")  # pre antes que post
    return estudiante


@router.get("/resumen", response_model=dict[str, dict[str, int]])
def resumen(momento: schemas.Momento = "pre", sesion: Session = Depends(dep_sesion)):
    """Conteo por nivel de riesgo y grupo en un momento."""
    conteo = {g: dict.fromkeys(NIVELES, 0) for g in ("control", "experimental")}
    for estudiante in sesion.scalars(_con_registros()):
        registro = _registro_de(estudiante, momento)
        if registro:
            conteo[estudiante.grupo][registro.prediccion.nivel_riesgo] += 1
    return conteo
