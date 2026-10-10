"""Autenticación propia (decisión D10): login, tokens, bloqueo y usuarios."""

import pytest

from app.auth import FALLOS_MAXIMOS
from app.crear_usuario import guardar_usuario

from .conftest import (
    EMAIL,
    PASSWORD,
    SECRETO,
    crear_usuario,
    iniciar_sesion,
    token_firmado,
)


def test_health_sin_token(crear_cliente):
    r = crear_cliente().get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "modelo": "rf_test"}


def test_login_devuelve_token_y_usuario(crear_cliente):
    c = crear_cliente()
    crear_usuario(c, rol="directivo")
    r = iniciar_sesion(c, email="  TUTOR@ie.test ")  # sin distinguir mayúsculas
    assert r.status_code == 200
    datos = r.json()
    assert datos["token_type"] == "bearer" and datos["expira_en"] == 480 * 60
    assert datos["usuario"] == {"email": EMAIL, "rol": "directivo"}
    assert "password" not in r.text

    c.headers["Authorization"] = f"Bearer {datos['access_token']}"
    assert c.get("/auth/yo").json() == {"email": EMAIL, "rol": "directivo"}
    assert c.get("/estudiantes").status_code == 200


def test_mismo_error_para_correo_inexistente_y_clave_incorrecta(crear_cliente):
    c = crear_cliente()
    crear_usuario(c)
    malo = iniciar_sesion(c, password="otra-clave-123")
    nadie = iniciar_sesion(c, email="nadie@ie.test")
    assert malo.status_code == nadie.status_code == 401
    assert malo.json() == nadie.json()


def test_bloqueo_tras_intentos_fallidos(crear_cliente):
    c = crear_cliente()
    crear_usuario(c)
    for _ in range(FALLOS_MAXIMOS):
        assert iniciar_sesion(c, password="incorrecta-123").status_code == 401
    # Bloqueado incluso con la contraseña correcta
    assert iniciar_sesion(c).status_code == 429


def test_login_correcto_reinicia_el_contador(crear_cliente):
    c = crear_cliente()
    crear_usuario(c)
    for _ in range(FALLOS_MAXIMOS - 1):
        iniciar_sesion(c, password="incorrecta-123")
    assert iniciar_sesion(c).status_code == 200
    assert iniciar_sesion(c, password="incorrecta-123").status_code == 401  # no 429


@pytest.mark.parametrize(
    "encabezado",
    [
        None,
        "Bearer no-es-un-jwt",
        f"Bearer {token_firmado(exp=1)}",  # vencido
        f"Bearer {token_firmado(iss='otro-sistema')}",
        f"Bearer {token_firmado(secreto='x' * 40)}",  # otro secreto
        f"Bearer {token_firmado(sub='no-es-uuid')}",
        f"Bearer {token_firmado()}",  # firma válida pero el usuario no existe
    ],
)
def test_401_sin_token_valido(crear_cliente, encabezado):
    c = crear_cliente()
    if encabezado:
        c.headers["Authorization"] = encabezado
    assert c.get("/estudiantes").status_code == 401


def test_desactivar_corta_el_acceso_con_token_vigente(cliente):
    assert cliente.get("/estudiantes").status_code == 200
    with cliente.app.state.sesiones() as sesion:
        guardar_usuario(sesion, EMAIL, None, None, activo=False)
    assert cliente.get("/estudiantes").status_code == 401
    assert iniciar_sesion(cliente).status_code == 401


def test_cambiar_password(cliente):
    nueva = "clave-nueva-456"
    r = cliente.post(
        "/auth/cambiar-password",
        json={"password_actual": "equivocada-000", "password_nueva": nueva},
    )
    assert r.status_code == 400
    r = cliente.post(
        "/auth/cambiar-password",
        json={"password_actual": PASSWORD, "password_nueva": "corta"},
    )
    assert r.status_code == 422
    r = cliente.post(
        "/auth/cambiar-password",
        json={"password_actual": PASSWORD, "password_nueva": nueva},
    )
    assert r.status_code == 204
    assert iniciar_sesion(cliente).status_code == 401
    assert iniciar_sesion(cliente, password=nueva).status_code == 200


def test_la_base_guarda_hash_argon2_no_la_clave(cliente):
    from sqlalchemy import select

    from app.db import Usuario

    with cliente.app.state.sesiones() as sesion:
        usuario = sesion.scalar(select(Usuario))
    assert usuario.password_hash.startswith("$argon2id$")
    assert PASSWORD not in usuario.password_hash


@pytest.mark.parametrize(
    "email, password, rol, mensaje",
    [
        ("no-es-correo", PASSWORD, "tutor", "Correo inválido"),
        (EMAIL, PASSWORD, "admin", "Rol inválido"),
        (EMAIL, "corta", "tutor", "al menos 10"),
        (EMAIL, None, "tutor", "hacen falta"),
    ],
)
def test_guardar_usuario_valida(crear_cliente, email, password, rol, mensaje):
    c = crear_cliente()
    with c.app.state.sesiones() as sesion, pytest.raises(ValueError, match=mensaje):
        guardar_usuario(sesion, email, password, rol)


def test_auth_desactivada_solo_con_sqlite(crear_cliente):
    assert crear_cliente(auth_desactivada=True).get("/estudiantes").status_code == 200
    with pytest.raises(RuntimeError, match="SQLite"):
        crear_cliente(auth_desactivada=True, database_url="postgresql://x@localhost/db")


def test_no_arranca_sin_secreto_suficiente(crear_cliente):
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        crear_cliente(jwt_secret="corto")
    assert len(SECRETO) >= 32
