"""Autenticación con tokens de Supabase Auth (header Authorization: Bearer).

Supabase firma los tokens con el secreto JWT del proyecto (HS256, proyectos
antiguos) o con claves asimétricas publicadas en su JWKS (ES256/RS256). Se
aceptan ambos. El rol (tutor / directivo) se lee de app_metadata.rol, que solo
puede asignar un administrador del proyecto.
"""

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Config

AUDIENCIA = "authenticated"
_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Usuario:
    id: str
    email: str | None
    rol: str | None


USUARIO_DESARROLLO = Usuario(id="desarrollo", email=None, rol="directivo")


@lru_cache(maxsize=4)
def _cliente_jwks(supabase_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")


def verificar_token(token: str, config: Config) -> Usuario:
    try:
        algoritmo = jwt.get_unverified_header(token).get("alg")
        if algoritmo == "HS256":
            if not config.supabase_jwt_secret:
                raise jwt.InvalidTokenError("SUPABASE_JWT_SECRET no configurado")
            clave = config.supabase_jwt_secret
        else:
            if not config.supabase_url:
                raise jwt.InvalidTokenError("SUPABASE_URL no configurado")
            clave = (
                _cliente_jwks(config.supabase_url).get_signing_key_from_jwt(token).key
            )
        datos = jwt.decode(
            token,
            clave,
            algorithms=["HS256", "ES256", "RS256"],
            audience=AUDIENCIA,
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            f"Token inválido: {error}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return Usuario(
        id=datos["sub"],
        email=datos.get("email"),
        rol=(datos.get("app_metadata") or {}).get("rol"),
    )


def usuario_actual(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Usuario:
    config: Config = request.app.state.config
    if config.auth_desactivada:
        return USUARIO_DESARROLLO
    if credenciales is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Falta el token (Authorization: Bearer <token de Supabase>)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verificar_token(credenciales.credentials, config)
