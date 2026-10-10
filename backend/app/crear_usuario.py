"""Crea un usuario (tutor o directivo) o restablece su contraseña.

La contraseña se escribe en la terminal sin mostrarse (getpass); nunca va como
argumento, para que no quede en el historial. Usa la DATABASE_URL de
backend/.env: con Neon, primero ejecutar sql/001_esquema.sql.

Uso (desde backend/):
    .venv/Scripts/python -m app.crear_usuario --email tutor@ie.edu.pe --rol tutor
    .venv/Scripts/python -m app.crear_usuario --email tutor@ie.edu.pe --restablecer
    .venv/Scripts/python -m app.crear_usuario --email tutor@ie.edu.pe --desactivar
"""

import argparse
import getpass
import re
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import ROLES, ErrorPassword, hashear_password, normalizar_email
from .config import leer_config
from .db import Usuario, crear_sesiones

PATRON_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def guardar_usuario(
    sesion: Session,
    email: str,
    password: str | None,
    rol: str | None,
    activo: bool = True,
) -> tuple[Usuario, bool]:
    """Crea o actualiza; devuelve (usuario, creado). Valida antes de escribir."""
    email = normalizar_email(email)
    if not PATRON_EMAIL.fullmatch(email):
        raise ValueError(f"Correo inválido: {email!r}")
    if rol is not None and rol not in ROLES:
        raise ValueError(f"Rol inválido: {rol!r} (tutor o directivo)")
    usuario = sesion.scalar(select(Usuario).where(Usuario.email == email))
    creado = usuario is None
    if creado:
        if rol is None or password is None:
            raise ValueError("Para crear un usuario hacen falta --rol y contraseña")
        usuario = Usuario(email=email, rol=rol)
        sesion.add(usuario)
    elif rol is not None:
        usuario.rol = rol
    if password is not None:
        usuario.password_hash = hashear_password(password)
    usuario.activo = activo
    sesion.commit()
    return usuario, creado


def _pedir_password() -> str:
    primera = getpass.getpass("Contraseña (mín. 10 caracteres): ")
    if primera != getpass.getpass("Repite la contraseña: "):
        sys.exit("[ERROR] Las contraseñas no coinciden")
    return primera


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--rol", choices=ROLES)
    accion = parser.add_mutually_exclusive_group()
    accion.add_argument("--restablecer", action="store_true", help="Nueva contraseña")
    accion.add_argument("--desactivar", action="store_true", help="Corta el acceso")
    args = parser.parse_args()

    fabrica = crear_sesiones(leer_config().database_url)
    with fabrica() as sesion:
        existe = sesion.scalar(
            select(Usuario).where(Usuario.email == normalizar_email(args.email))
        )
        if args.desactivar and existe is None:
            sys.exit("[ERROR] No existe ese usuario")
        pedir = not args.desactivar and (existe is None or args.restablecer)
        password = _pedir_password() if pedir else None
        try:
            usuario, creado = guardar_usuario(
                sesion, args.email, password, args.rol, activo=not args.desactivar
            )
        except (ValueError, ErrorPassword) as error:
            sys.exit(f"[ERROR] {error}")
    estado = (
        "creado" if creado else ("desactivado" if args.desactivar else "actualizado")
    )
    print(f"[OK] {usuario.email} ({usuario.rol}) {estado}")


if __name__ == "__main__":
    main()
