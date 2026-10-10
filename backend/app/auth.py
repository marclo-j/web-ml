"""Autenticación propia del backend (decisión D10: sin servicios externos).

- Contraseñas: hash Argon2id (argon2-cffi); nunca se guarda la contraseña.
- Sesión: token JWT HS256 firmado con JWT_SECRET, válido JWT_EXPIRA_MIN
  minutos, enviado en el header Authorization: Bearer <token>.
- En cada petición se vuelve a leer el usuario: desactivarlo corta su acceso
  aunque su token siga vigente.
- Tras FALLOS_MAXIMOS intentos fallidos seguidos, el correo queda bloqueado
  BLOQUEO_MIN minutos (frena la prueba de contraseñas por fuerza bruta).

No hay registro público: los usuarios los crea el administrador con
`python -m app.crear_usuario` (ver README).
"""

import threading
import time
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Config
from .db import Usuario
from .dependencias import sesion as dep_sesion

ALGORITMO = "HS256"
EMISOR = "web-ml-desercion"
ROLES = ("tutor", "directivo")
PASSWORD_MINIMO = 10
SECRETO_MINIMO = 32  # caracteres de JWT_SECRET
FALLOS_MAXIMOS = 5
BLOQUEO_MIN = 15

_hasher = PasswordHasher()  # Argon2id con los parámetros recomendados (RFC 9106)
# tokenUrl: el botón Authorize de /docs inicia sesión con correo y contraseña
_bearer = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
_hash_ficticio: str | None = None


class ErrorPassword(ValueError):
    """La contraseña no cumple el mínimo."""


def hashear_password(password: str) -> str:
    if len(password) < PASSWORD_MINIMO:
        raise ErrorPassword(
            f"La contraseña debe tener al menos {PASSWORD_MINIMO} caracteres"
        )
    return _hasher.hash(password)


def _verificar_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def normalizar_email(email: str) -> str:
    return email.strip().lower()


class LimitadorIntentos:
    """Cuenta fallos por correo, en memoria del proceso (un solo servidor)."""

    def __init__(
        self, maximo: int = FALLOS_MAXIMOS, bloqueo_seg: int = BLOQUEO_MIN * 60
    ):
        self.maximo, self.bloqueo_seg = maximo, bloqueo_seg
        self._fallos: dict[str, tuple[int, float]] = {}
        self._candado = threading.Lock()

    def bloqueado(self, clave: str) -> bool:
        with self._candado:
            fallos, hasta = self._fallos.get(clave, (0, 0.0))
            if hasta and time.monotonic() >= hasta:
                del self._fallos[clave]
                return False
            return fallos >= self.maximo

    def fallo(self, clave: str) -> None:
        with self._candado:
            fallos, _ = self._fallos.get(clave, (0, 0.0))
            fallos += 1
            hasta = (
                time.monotonic() + self.bloqueo_seg if fallos >= self.maximo else 0.0
            )
            self._fallos[clave] = (fallos, hasta)

    def exito(self, clave: str) -> None:
        with self._candado:
            self._fallos.pop(clave, None)


def autenticar(sesion: Session, email: str, password: str) -> Usuario | None:
    """Devuelve el usuario si correo y contraseña son correctos y está activo."""
    global _hash_ficticio
    usuario = sesion.scalar(
        select(Usuario).where(Usuario.email == normalizar_email(email))
    )
    if usuario is None:
        # Mismo tiempo de respuesta que con un correo existente: no revela
        # qué correos están registrados
        _hash_ficticio = _hash_ficticio or _hasher.hash("contraseña-ficticia")
        _verificar_password(_hash_ficticio, password)
        return None
    if not _verificar_password(usuario.password_hash, password) or not usuario.activo:
        return None
    if _hasher.check_needs_rehash(usuario.password_hash):
        usuario.password_hash = _hasher.hash(password)
        sesion.commit()
    return usuario


def crear_token(usuario: Usuario, config: Config) -> tuple[str, int]:
    ahora = datetime.now(UTC)
    expira_seg = config.jwt_expira_min * 60
    datos = {
        "sub": str(usuario.id),
        "rol": usuario.rol,
        "iss": EMISOR,
        "iat": ahora,
        "exp": ahora + timedelta(seconds=expira_seg),
    }
    return jwt.encode(datos, config.jwt_secret, algorithm=ALGORITMO), expira_seg


def _no_autorizado(mensaje: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, mensaje, headers={"WWW-Authenticate": "Bearer"}
    )


def usuario_actual(
    request: Request,
    token: str | None = Depends(_bearer),
    sesion: Session = Depends(dep_sesion),
) -> Usuario:
    config: Config = request.app.state.config
    if config.auth_desactivada:
        return Usuario(id=uuid.UUID(int=0), email="desarrollo@local", rol="directivo")
    if token is None:
        raise _no_autorizado("Falta el token (Authorization: Bearer <token>)")
    try:
        datos = jwt.decode(
            token,
            config.jwt_secret,
            algorithms=[ALGORITMO],
            issuer=EMISOR,
            options={"require": ["exp", "sub", "iss"]},
        )
        usuario_id = uuid.UUID(datos["sub"])
    except (jwt.PyJWTError, ValueError) as error:
        raise _no_autorizado("Token inválido o vencido") from error
    usuario = sesion.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise _no_autorizado("Usuario inexistente o desactivado")
    return usuario


def requiere_rol(*roles: str):
    """Dependencia para restringir un endpoint, ej. Depends(requiere_rol("directivo"))."""

    def verificar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Tu rol no permite esta acción"
            )
        return usuario

    return verificar
