"""Guardar datos crudos → calcular indicadores → predecir (docs/ARQUITECTURA.md, flujo principal)."""

import csv
import io
import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import Estudiante, Prediccion, Registro
from .indicadores import GRUPO_POR_GRADO, ErrorValidacion, calcular_indicadores
from .modelo import ModeloRiesgo

CRUDOS = [
    "suma_notas",
    "n_notas",
    "dias_asistidos",
    "dias_programados",
    "reuniones_asistidas",
    "reuniones_programadas",
]
COLUMNAS_CSV = ["codigo", "grado", "seccion", "grupo", "momento", *CRUDOS]
PATRON_CODIGO = re.compile(r"EST-\d{3}")


def guardar_registro(
    sesion: Session,
    estudiante: Estudiante,
    momento: str,
    crudos: dict,
    modelo: ModeloRiesgo,
) -> Registro:
    """Un registro por alumno y momento: si ya existe, se reemplazan sus datos
    y su predicción. No hace commit."""
    indicadores = calcular_indicadores(**{c: crudos[c] for c in CRUDOS})
    probabilidad, nivel = modelo.predecir(indicadores)

    registro = sesion.scalar(
        select(Registro).where(
            Registro.estudiante_id == estudiante.id, Registro.momento == momento
        )
    )
    if registro is None:
        registro = Registro(estudiante=estudiante, momento=momento)
        sesion.add(registro)
    for campo, valor in {**{c: crudos[c] for c in CRUDOS}, **indicadores}.items():
        setattr(registro, campo, valor)
    # Se actualiza la fila existente: reemplazarla insertaría la nueva antes de
    # borrar la anterior y violaría la unicidad de registro_id
    if registro.prediccion is None:
        registro.prediccion = Prediccion()
    registro.prediccion.probabilidad = probabilidad
    registro.prediccion.nivel_riesgo = nivel
    registro.prediccion.version_modelo = modelo.version
    registro.prediccion.created_at = datetime.now(UTC)
    sesion.flush()
    return registro


def _entero(texto: str, nombre: str) -> int:
    try:
        valor = float(texto)
    except ValueError:
        raise ErrorValidacion(f"{nombre} no es numérico") from None
    if not valor.is_integer():
        raise ErrorValidacion(f"{nombre} debe ser entero")
    return int(valor)


def _numero(texto: str, nombre: str) -> float:
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ErrorValidacion(f"{nombre} no es numérico") from None


def leer_csv(contenido: bytes) -> tuple[list[tuple[int, dict]], list[dict]]:
    """Valida el CSV de carga masiva (docs/VARIABLES.md).

    Devuelve (filas válidas con su número de línea, excluidos). Separador
    coma o punto y coma (Excel en español guarda con punto y coma).
    """
    texto = contenido.decode("utf-8-sig")
    primera = texto.splitlines()[0] if texto.strip() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    lector = csv.DictReader(io.StringIO(texto), delimiter=separador)
    faltan = [c for c in COLUMNAS_CSV if c not in (lector.fieldnames or [])]
    if faltan:
        raise ErrorValidacion(f"Faltan columnas en el CSV: {', '.join(faltan)}")

    validas, excluidos, vistos = [], [], set()
    for numero, fila in enumerate(lector, start=2):  # línea 1 = encabezado
        fila = {k: (v or "").strip() for k, v in fila.items() if k}
        codigo = fila.get("codigo") or None
        try:
            if not codigo or not PATRON_CODIGO.fullmatch(codigo):
                raise ErrorValidacion(f"código {codigo!r} no tiene el formato EST-###")
            grado = _entero(fila["grado"], "grado")
            if grado not in GRUPO_POR_GRADO:
                raise ErrorValidacion(f"grado {grado} fuera de 3.° o 4.°")
            grupo = fila["grupo"].lower() or GRUPO_POR_GRADO[grado]
            if grupo != GRUPO_POR_GRADO[grado]:
                raise ErrorValidacion(
                    f"{grado}.° corresponde al grupo {GRUPO_POR_GRADO[grado]}"
                )
            momento = fila["momento"].lower()
            if momento not in ("pre", "post"):
                raise ErrorValidacion(f"momento {momento!r} no es pre ni post")
            if not fila["seccion"]:
                raise ErrorValidacion("falta seccion")
            if (codigo, momento) in vistos:
                raise ErrorValidacion("alumno repetido en el archivo")
            crudos = {"suma_notas": _numero(fila["suma_notas"], "suma_notas")}
            for c in CRUDOS[1:]:
                crudos[c] = _entero(fila[c], c)
            calcular_indicadores(**crudos)  # aplica las reglas de validación
        except ErrorValidacion as error:
            excluidos.append({"fila": numero, "codigo": codigo, "motivo": str(error)})
            continue
        vistos.add((codigo, momento))
        validas.append(
            (
                numero,
                {
                    "codigo": codigo,
                    "grado": grado,
                    "seccion": fila["seccion"].upper(),
                    "grupo": grupo,
                    "momento": momento,
                    "crudos": crudos,
                },
            )
        )
    return validas, excluidos
