"""Pruebas de los endpoints de docs/API.md."""

import pytest

from .conftest import CRUDOS_ALTO, CRUDOS_BAJO, token

# --- Autenticación -----------------------------------------------------------


def test_health_sin_token(crear_cliente):
    r = crear_cliente().get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "modelo": "rf_test"}


@pytest.mark.parametrize(
    "encabezado",
    [
        None,
        "Bearer no-es-un-jwt",
        f"Bearer {token(exp=1)}",  # vencido
        f"Bearer {token(aud='otra')}",
    ],
)
def test_401_sin_token_valido(crear_cliente, encabezado):
    c = crear_cliente()
    if encabezado:
        c.headers["Authorization"] = encabezado
    assert c.get("/estudiantes").status_code == 401


def test_token_firmado_con_otro_secreto(crear_cliente):
    import jwt

    malo = jwt.encode(
        {"sub": "x", "aud": "authenticated", "exp": 9999999999}, "otro" * 10, "HS256"
    )
    c = crear_cliente()
    c.headers["Authorization"] = f"Bearer {malo}"
    assert c.get("/estudiantes").status_code == 401


def test_auth_desactivada_solo_con_sqlite(crear_cliente):
    assert crear_cliente(auth_desactivada=True).get("/estudiantes").status_code == 200
    with pytest.raises(RuntimeError, match="SQLite"):
        crear_cliente(auth_desactivada=True, database_url="postgresql://x@localhost/db")


# --- Modelo y predicción -----------------------------------------------------


def test_modelo(cliente):
    r = cliente.get("/modelo").json()
    assert r["version"] == "rf_test"
    assert r["umbrales"] == {"medio": 0.15, "alto": 0.5}
    assert r["aviso"] == "solo pruebas"


def test_predecir_calcula_indicadores_y_nivel(cliente):
    r = cliente.post("/predecir", json=CRUDOS_ALTO)
    assert r.status_code == 200
    datos = r.json()
    assert datos["indicadores"] == {
        "promedio": 9.5,
        "pct_asistencia": 20.0,
        "pct_reuniones": 0.0,
    }
    assert datos["nivel_riesgo"] == "alto" and datos["probabilidad"] >= 0.5
    assert cliente.post("/predecir", json=CRUDOS_BAJO).json()["nivel_riesgo"] == "bajo"


def test_predecir_422_con_la_regla_que_falla(cliente):
    r = cliente.post("/predecir", json={**CRUDOS_BAJO, "dias_asistidos": 50})
    assert r.status_code == 422
    assert "dias_asistidos > dias_programados" in r.json()["detail"]


def test_503_sin_modelo(crear_cliente, tmp_path):
    c = crear_cliente(model_path=tmp_path / "rf_no_existe.joblib")
    c.headers["Authorization"] = f"Bearer {token()}"
    assert c.get("/health").json() == {"status": "sin_modelo", "modelo": None}
    assert c.post("/predecir", json=CRUDOS_BAJO).status_code == 503


# --- Estudiantes y registros -------------------------------------------------


def _crear(cliente, codigo="EST-001", grado=4, seccion="B"):
    r = cliente.post(
        "/estudiantes", json={"codigo": codigo, "grado": grado, "seccion": seccion}
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_crear_estudiante_deduce_grupo(cliente):
    assert _crear(cliente, grado=3)["grupo"] == "control"
    assert _crear(cliente, codigo="EST-002", grado=4)["grupo"] == "experimental"


@pytest.mark.parametrize(
    "datos",
    [
        {"codigo": "Juan Pérez", "grado": 3, "seccion": "A"},  # sin nombres
        {"codigo": "EST-001", "grado": 5, "seccion": "A"},
        {"codigo": "EST-001", "grado": 3, "seccion": "A", "grupo": "experimental"},
    ],
)
def test_crear_estudiante_invalido(cliente, datos):
    assert cliente.post("/estudiantes", json=datos).status_code == 422


def test_codigo_duplicado(cliente):
    _crear(cliente)
    assert (
        cliente.post(
            "/estudiantes", json={"codigo": "EST-001", "grado": 4, "seccion": "B"}
        ).status_code
        == 409
    )


def test_registro_predice_y_se_reemplaza(cliente):
    est = _crear(cliente)
    cuerpo = {"estudiante_id": est["id"], "momento": "pre", **CRUDOS_ALTO}
    r = cliente.post("/registros", json=cuerpo)
    assert r.status_code == 201
    assert r.json()["pct_asistencia"] == 20.0
    assert r.json()["prediccion"]["nivel_riesgo"] == "alto"

    # Mismo alumno y momento: reemplaza datos y predicción, no duplica
    r = cliente.post("/registros", json={**cuerpo, **CRUDOS_BAJO})
    assert r.json()["prediccion"]["nivel_riesgo"] == "bajo"
    detalle = cliente.get(f"/estudiantes/{est['id']}").json()
    assert len(detalle["registros"]) == 1
    assert detalle["registros"][0]["promedio"] == 16.0


def test_registro_estudiante_inexistente(cliente):
    cuerpo = {
        "estudiante_id": "00000000-0000-0000-0000-000000000000",
        "momento": "pre",
        **CRUDOS_BAJO,
    }
    assert cliente.post("/registros", json=cuerpo).status_code == 404
    assert cliente.get(f"/estudiantes/{cuerpo['estudiante_id']}").status_code == 404


def test_listar_filtrar_y_resumen(cliente):
    a, b = _crear(cliente, "EST-001", 3, "A"), _crear(cliente, "EST-002", 4, "B")
    _crear(cliente, "EST-003", 4, "B")  # sin registro
    cliente.post(
        "/registros", json={"estudiante_id": a["id"], "momento": "pre", **CRUDOS_BAJO}
    )
    cliente.post(
        "/registros", json={"estudiante_id": b["id"], "momento": "pre", **CRUDOS_ALTO}
    )
    cliente.post(
        "/registros", json={"estudiante_id": b["id"], "momento": "post", **CRUDOS_BAJO}
    )

    todos = cliente.get("/estudiantes").json()
    assert [e["codigo"] for e in todos] == ["EST-001", "EST-002", "EST-003"]
    assert todos[1]["ultima_prediccion"]["momento"] == "post"  # post > pre
    assert todos[2]["ultima_prediccion"] is None

    altos_pre = cliente.get(
        "/estudiantes", params={"momento": "pre", "nivel": "alto"}
    ).json()
    assert [e["codigo"] for e in altos_pre] == ["EST-002"]
    control = cliente.get("/estudiantes", params={"grupo": "control"}).json()
    assert [e["codigo"] for e in control] == ["EST-001"]

    assert cliente.get("/resumen").json() == {
        "control": {"bajo": 1, "medio": 0, "alto": 0},
        "experimental": {"bajo": 0, "medio": 0, "alto": 1},
    }
    assert cliente.get("/resumen", params={"momento": "post"}).json()[
        "experimental"
    ] == {
        "bajo": 1,
        "medio": 0,
        "alto": 0,
    }


# --- Carga masiva -------------------------------------------------------------

ENCABEZADO = (
    "codigo,grado,seccion,grupo,momento,suma_notas,n_notas,dias_asistidos,"
    "dias_programados,reuniones_asistidas,reuniones_programadas"
)


def _importar(cliente, texto: str):
    return cliente.post(
        "/registros/importar",
        files={"archivo": ("carga.csv", texto.encode("utf-8"), "text/csv")},
    )


def test_importar_csv_con_exclusiones(cliente):
    # Fila 3: grupo vacío, se deduce del grado. Filas 4 a 7 se excluyen:
    # DA > DP, grupo incoherente, sin código y alumno repetido.
    texto = f"""{ENCABEZADO}
EST-001,4,B,experimental,pre,142,10,40,45,1,2
EST-002,3,A,,pre,95,10,9,45,0,2
EST-003,4,B,experimental,pre,142,10,50,45,1,2
EST-004,3,A,experimental,pre,142,10,40,45,1,2
Juan,3,A,control,pre,142,10,40,45,1,2
EST-001,4,B,experimental,pre,150,10,40,45,1,2"""
    r = _importar(cliente, texto)
    assert r.status_code == 200, r.text
    datos = r.json()
    assert datos["procesados"] == 2 and datos["excluidos"] == 4
    assert [e["fila"] for e in datos["detalle_excluidos"]] == [4, 5, 6, 7]
    assert (
        "dias_asistidos > dias_programados" in datos["detalle_excluidos"][0]["motivo"]
    )
    grupos = {e["codigo"]: e["grupo"] for e in cliente.get("/estudiantes").json()}
    assert grupos == {"EST-001": "experimental", "EST-002": "control"}


def test_importar_csv_punto_y_coma_y_coma_decimal(cliente):
    texto = (
        ENCABEZADO.replace(",", ";")
        + "\nEST-001;4;B;experimental;pre;142,5;10;40;45;1;2\n"
    )
    datos = _importar(cliente, texto).json()
    assert datos["procesados"] == 1
    est = cliente.get("/estudiantes").json()[0]
    assert (
        cliente.get(f"/estudiantes/{est['id']}").json()["registros"][0]["promedio"]
        == 14.25
    )


def test_importar_seccion_distinta_a_la_registrada(cliente):
    _crear(cliente, "EST-001", 4, "B")
    datos = _importar(
        cliente, ENCABEZADO + "\nEST-001,4,C,experimental,pre,142,10,40,45,1,2"
    ).json()
    assert datos["procesados"] == 0
    assert "sección" in datos["detalle_excluidos"][0]["motivo"]


def test_importar_csv_sin_columnas(cliente):
    r = _importar(cliente, "codigo,grado\nEST-001,4\n")
    assert r.status_code == 422 and "Faltan columnas" in r.json()["detail"]
