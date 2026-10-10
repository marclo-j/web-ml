"""/auth/login, /auth/yo y /auth/cambiar-password."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import (
    BLOQUEO_MIN,
    ErrorPassword,
    autenticar,
    crear_token,
    hashear_password,
    normalizar_email,
    usuario_actual,
)
from ..db import Usuario
from ..dependencias import sesion as dep_sesion

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    sesion: Session = Depends(dep_sesion),
):
    """Formulario `username` (correo) + `password`. Devuelve el token Bearer."""
    limitador = request.app.state.limitador
    clave = normalizar_email(form.username)
    if limitador.bloqueado(clave):
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Demasiados intentos fallidos. Espera {BLOQUEO_MIN} minutos.",
        )
    usuario = autenticar(sesion, form.username, form.password)
    if usuario is None:
        limitador.fallo(clave)
        # Mismo mensaje para correo inexistente y contraseña incorrecta
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    limitador.exito(clave)
    token, expira_seg = crear_token(usuario, request.app.state.config)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expira_en": expira_seg,
        "usuario": usuario,
    }


@router.get("/yo", response_model=schemas.UsuarioPublico)
def yo(usuario: Usuario = Depends(usuario_actual)):
    return usuario


@router.post("/cambiar-password", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    datos: schemas.CambioPassword,
    usuario: Usuario = Depends(usuario_actual),
    sesion: Session = Depends(dep_sesion),
):
    if autenticar(sesion, usuario.email, datos.password_actual) is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "La contraseña actual no es correcta"
        )
    try:
        usuario.password_hash = hashear_password(datos.password_nueva)
    except ErrorPassword as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)
        ) from error
    sesion.commit()
