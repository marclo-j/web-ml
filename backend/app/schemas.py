"""Modelos Pydantic de la API (docs/API.md)."""

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .services.indicadores import GRUPO_POR_GRADO

Grupo = Literal["control", "experimental"]
Momento = Literal["pre", "post"]
Nivel = Literal["bajo", "medio", "alto"]
PATRON_CODIGO = r"^EST-\d{3}$"


class DatosCrudos(BaseModel):
    """Lo que se copia de las 3 fichas. Las reglas cruzadas (DA ≤ DP, etc.)
    las aplica calcular_indicadores y responden 422 con la regla que falla."""

    suma_notas: float = Field(ge=0)
    n_notas: int = Field(gt=0)
    dias_asistidos: int = Field(ge=0)
    dias_programados: int = Field(gt=0)
    reuniones_asistidas: int = Field(ge=0)
    reuniones_programadas: int = Field(gt=0)


class Indicadores(BaseModel):
    promedio: float
    pct_asistencia: float
    pct_reuniones: float


class Prediccion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    probabilidad: float
    nivel_riesgo: Nivel
    version_modelo: str


class RespuestaPrediccion(Prediccion):
    indicadores: Indicadores


class EstudianteNuevo(BaseModel):
    codigo: str = Field(pattern=PATRON_CODIGO, examples=["EST-001"])
    grado: Literal[3, 4]
    seccion: str = Field(min_length=1, max_length=8)
    grupo: Grupo | None = Field(
        default=None,
        description="Opcional: se deduce del grado (3.° control, 4.° experimental)",
    )

    @model_validator(mode="after")
    def grupo_coherente(self):
        esperado = GRUPO_POR_GRADO[self.grado]
        if self.grupo is None:
            self.grupo = esperado
        elif self.grupo != esperado:
            raise ValueError(f"{self.grado}.° corresponde al grupo {esperado}")
        return self


class Estudiante(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    codigo: str
    grado: int
    seccion: str
    grupo: Grupo


class UltimaPrediccion(BaseModel):
    momento: Momento
    nivel_riesgo: Nivel
    probabilidad: float


class EstudianteConPrediccion(Estudiante):
    ultima_prediccion: UltimaPrediccion | None


class RegistroNuevo(DatosCrudos):
    estudiante_id: uuid.UUID
    momento: Momento


class Registro(Indicadores, DatosCrudos):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    estudiante_id: uuid.UUID
    momento: Momento
    nivel_riesgo_real: str | None
    prediccion: Prediccion | None


class EstudianteDetalle(Estudiante):
    registros: list[Registro]


class Excluido(BaseModel):
    fila: int
    codigo: str | None
    motivo: str


class ResultadoImportacion(BaseModel):
    procesados: int
    excluidos: int
    detalle_excluidos: list[Excluido]


class Salud(BaseModel):
    status: Literal["ok", "sin_modelo"]
    modelo: str | None


class InfoModelo(BaseModel):
    version: str
    entrenado: str
    fuente_datos: str
    features: list[str]
    n_entrenamiento: int
    metricas: dict
    umbrales: dict[str, float]
    aumento: dict | None
    aviso: str | None
