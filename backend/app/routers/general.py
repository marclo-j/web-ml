"""/health, /modelo y /predecir."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .. import schemas
from ..auth import usuario_actual
from ..dependencias import modelo as dep_modelo
from ..services.indicadores import ErrorValidacion, calcular_indicadores
from ..services.modelo import ModeloRiesgo

router = APIRouter(tags=["general"])


@router.get("/health", response_model=schemas.Salud)
def health(request: Request):
    cargado = request.app.state.modelo
    return {
        "status": "ok" if cargado else "sin_modelo",
        "modelo": cargado.version if cargado else None,
    }


@router.get(
    "/modelo",
    response_model=schemas.InfoModelo,
    dependencies=[Depends(usuario_actual)],
)
def info_modelo(request: Request, modelo: ModeloRiesgo = Depends(dep_modelo)):
    m = modelo.metadatos
    metricas = {
        "validacion_cruzada_k5_sobre_train": m.get("validacion_cruzada_k5_sobre_train"),
        "holdout_20pct": m.get("holdout_20pct"),
    }
    # Métrica principal (docs/MODELO.md): CV 5x5 sobre reales de comparar_aumento.py
    ruta = request.app.state.config.model_path.parent / (
        f"comparacion_aumento_{m.get('fuente_datos')}.json"
    )
    metodo = (m.get("aumento") or {}).get("metodo", "sin_aumento")
    if ruta.is_file():
        comparacion = json.loads(ruta.read_text(encoding="utf-8"))
        if metodo in comparacion.get("utilidad", {}):
            metricas["cv_5x5_sobre_reales"] = comparacion["utilidad"][metodo]
    return {
        "version": modelo.version,
        "entrenado": m.get("fecha", ""),
        "fuente_datos": m.get("fuente_datos", ""),
        "features": m["features"],
        "n_entrenamiento": m.get("n_total", 0),
        "metricas": metricas,
        "umbrales": modelo.umbrales,
        "aumento": m.get("aumento"),
        "aviso": m.get("aviso"),
    }


@router.post(
    "/predecir",
    response_model=schemas.RespuestaPrediccion,
    dependencies=[Depends(usuario_actual)],
)
def predecir(datos: schemas.DatosCrudos, modelo: ModeloRiesgo = Depends(dep_modelo)):
    """Predicción directa sin guardar (demo y pruebas)."""
    try:
        indicadores = calcular_indicadores(**datos.model_dump())
    except ErrorValidacion as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)
        ) from error
    probabilidad, nivel = modelo.predecir(indicadores)
    return {
        "indicadores": indicadores,
        "probabilidad": probabilidad,
        "nivel_riesgo": nivel,
        "version_modelo": modelo.version,
    }
