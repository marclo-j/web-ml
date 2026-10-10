"""/registros y /registros/importar."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import usuario_actual
from ..db import Estudiante
from ..dependencias import modelo as dep_modelo
from ..dependencias import sesion as dep_sesion
from ..services.indicadores import ErrorValidacion
from ..services.modelo import ModeloRiesgo
from ..services.registros import CRUDOS, guardar_registro, leer_csv

router = APIRouter(dependencies=[Depends(usuario_actual)], tags=["registros"])

TAMANO_MAXIMO_CSV = 1_000_000  # 1 MB: ~10 000 filas, sobra para una IE


@router.post(
    "/registros", response_model=schemas.Registro, status_code=status.HTTP_201_CREATED
)
def crear_registro(
    datos: schemas.RegistroNuevo,
    sesion: Session = Depends(dep_sesion),
    modelo: ModeloRiesgo = Depends(dep_modelo),
):
    """Guarda los datos crudos, calcula los indicadores y predice. Si el alumno
    ya tiene registro en ese momento, se reemplaza."""
    estudiante = sesion.get(Estudiante, datos.estudiante_id)
    if estudiante is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Estudiante inexistente")
    crudos = datos.model_dump(include=set(CRUDOS))
    try:
        registro = guardar_registro(sesion, estudiante, datos.momento, crudos, modelo)
    except ErrorValidacion as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)
        ) from error
    sesion.commit()
    return registro


@router.post("/registros/importar", response_model=schemas.ResultadoImportacion)
def importar(
    archivo: UploadFile = File(...),
    sesion: Session = Depends(dep_sesion),
    modelo: ModeloRiesgo = Depends(dep_modelo),
):
    """Carga masiva por CSV (formato en docs/VARIABLES.md). Crea los alumnos que
    no existan; las filas que fallan una regla se excluyen y se informan."""
    contenido = archivo.file.read(TAMANO_MAXIMO_CSV + 1)
    if len(contenido) > TAMANO_MAXIMO_CSV:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "El CSV supera 1 MB")
    try:
        validas, excluidos = leer_csv(contenido)
    except (ErrorValidacion, UnicodeDecodeError) as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)
        ) from error

    procesados = 0
    for numero, fila in validas:
        estudiante = sesion.scalar(
            select(Estudiante).where(Estudiante.codigo == fila["codigo"])
        )
        if estudiante is None:
            estudiante = Estudiante(
                codigo=fila["codigo"],
                grado=fila["grado"],
                seccion=fila["seccion"],
                grupo=fila["grupo"],
            )
            sesion.add(estudiante)
        elif (estudiante.grado, estudiante.seccion) != (fila["grado"], fila["seccion"]):
            excluidos.append(
                {
                    "fila": numero,
                    "codigo": fila["codigo"],
                    "motivo": "grado o sección distintos a los ya registrados",
                }
            )
            continue
        guardar_registro(sesion, estudiante, fila["momento"], fila["crudos"], modelo)
        procesados += 1
    sesion.commit()
    excluidos.sort(key=lambda e: e["fila"])
    return {
        "procesados": procesados,
        "excluidos": len(excluidos),
        "detalle_excluidos": excluidos,
    }
