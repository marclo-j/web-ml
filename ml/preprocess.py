"""
preprocess.py

Consolida las 3 fichas llenas de un lote (rendimiento, asistencia y
reuniones), aplica las reglas de validación y los criterios de exclusión de
la tesis (docs/VARIABLES.md) y calcula los 3 indicadores.

Entrada: carpeta con ficha_1*.xlsx, ficha_2*.xlsx y ficha_3*.xlsx llenas.
         Son datos reales: siempre en data/raw/.
Salida (en data/processed/, gitignored):
  - <salida>.csv                incluidos: datos crudos + indicadores
  - <salida>_excluidos.csv      un registro por estudiante excluido y su motivo
  - <salida>_resumen.json       conteos para el capítulo de Resultados

Uso:
    python ml/preprocess.py --entrada data/raw/2026_pre --salida data/processed/2026_pre.csv
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parent.parent

# Distribución de la hoja "Datos" (fichas/generar_fichas.py)
HOJA_DATOS = "Datos"
FILA_ENCABEZADO = 9
FILA_INICIO = 10
CELDA_ANIO = "B2"

# Mismo orden que fichas/generar_fichas.py (lo comprueba ml/tests)
AREAS = [
    "matematica",
    "comunicacion",
    "ingles",
    "arte_cultura",
    "ciencias_sociales",
    "dpcc",
    "educacion_fisica",
    "educacion_religiosa",
    "ciencia_tecnologia",
    "ept",
]

# Escala vigesimal confirmada por la IE (decisión D1)
NOTA_MIN, NOTA_MAX = 0, 20

# Marca de las filas de ejemplo (datos inventados para aprender a llenar)
MARCA_EJEMPLO = "EJEMPLO"

# Columnas que --prellenar ya escribe; una fila con solo esto es un código sin usar
IDENTIFICACION = {"codigo", "grado", "momento", "anio"}

GRUPO_POR_GRADO = {3: "control", 4: "experimental"}
MOMENTOS = {"pre", "post"}
ANIO_ACTUAL = 2026
ANIOS = {2024, 2025, ANIO_ACTUAL}
PATRON_CODIGO = re.compile(r"EST-\d{3}")

# Criterios de exclusión de la tesis (mismos textos que la lista de las fichas)
TRASLADO = "traslado definitivo"
INCOMPLETA = "dimensión incompleta"
INCONSISTENTE = "registro inconsistente"
MOTIVOS = [TRASLADO, INCOMPLETA, INCONSISTENTE]

FICHAS = {
    1: ("ficha_1*.xlsx", "rendimiento académico"),
    2: ("ficha_2*.xlsx", "asistencia escolar"),
    3: ("ficha_3*.xlsx", "apoyo familiar"),
}
MEDIDAS = {
    2: ("dias_programados", "dias_asistidos"),
    3: ("reuniones_programadas", "reuniones_asistidas"),
}

COLUMNAS_SALIDA = [
    "codigo",
    "grado",
    "seccion",
    "grupo",
    "momento",
    "suma_notas",
    "n_notas",
    "dias_asistidos",
    "dias_programados",
    "reuniones_asistidas",
    "reuniones_programadas",
    "anio",
    "deserto",
    "promedio",
    "pct_asistencia",
    "pct_reuniones",
]


class ErrorValidacion(ValueError):
    """Falla una regla de docs/VARIABLES.md; el mensaje dice cuál."""


# --- Indicadores (misma función para ml/ y para el backend) ------------------


def calcular_indicadores(
    suma_notas: float,
    n_notas: int,
    dias_asistidos: int,
    dias_programados: int,
    reuniones_asistidas: int,
    reuniones_programadas: int,
) -> dict[str, float]:
    """Aplica las fórmulas de la tesis a los datos crudos de las fichas.

    Promedio = Σ Notas / n; Asistencia = (DA / DP) × 100; CA = (RA / RT) × 100.
    Lanza ErrorValidacion si falla alguna regla de docs/VARIABLES.md.
    """
    if n_notas <= 0:
        raise ErrorValidacion("n_notas debe ser mayor que 0")
    if dias_programados <= 0:
        raise ErrorValidacion("dias_programados debe ser mayor que 0")
    if reuniones_programadas <= 0:
        raise ErrorValidacion("reuniones_programadas debe ser mayor que 0")
    if not 0 <= dias_asistidos <= dias_programados:
        raise ErrorValidacion("dias_asistidos > dias_programados")
    if not 0 <= reuniones_asistidas <= reuniones_programadas:
        raise ErrorValidacion("reuniones_asistidas > reuniones_programadas")
    promedio = round(suma_notas / n_notas, 2)
    if not NOTA_MIN <= promedio <= NOTA_MAX:
        raise ErrorValidacion(
            f"promedio {promedio} fuera de la escala ({NOTA_MIN}-{NOTA_MAX})"
        )
    return {
        "promedio": promedio,
        "pct_asistencia": round(dias_asistidos / dias_programados * 100, 2),
        "pct_reuniones": round(reuniones_asistidas / reuniones_programadas * 100, 2),
    }


# --- Lectura de fichas -------------------------------------------------------


@dataclass
class Fila:
    """Una fila de una ficha, ya interpretada."""

    ficha: int
    archivo: str
    fila_excel: int
    codigo: str
    anio: int | None
    momento: str
    grado: int | None
    seccion: str
    deserto: int | None
    excluido_motivo: str | None = None
    solo_identificacion: bool = False
    ejemplo: bool = False  # observaciones con la marca MARCA_EJEMPLO
    datos: dict = field(default_factory=dict)
    faltantes: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)

    @property
    def clave(self) -> tuple:
        # Sin código no se puede unir con las otras fichas: queda aislada
        codigo = self.codigo or f"(sin código, {self.referencia})"
        return (codigo, self.anio, self.momento)

    @property
    def referencia(self) -> str:
        return f"{self.archivo}:fila {self.fila_excel}"


def vacio(valor) -> bool:
    return (
        valor is None
        or (isinstance(valor, float) and pd.isna(valor))
        or (isinstance(valor, str) and not valor.strip())
    )


def entero(valor) -> int | None:
    """Convierte a entero; None si está vacío. Lanza ValueError si no es entero."""
    if vacio(valor):
        return None
    numero = float(valor)
    if not numero.is_integer():
        raise ValueError(valor)
    return int(numero)


def leer_ficha(ruta: Path, ficha: int) -> tuple[list[Fila], dict]:
    libro = load_workbook(ruta, data_only=True, read_only=True)
    hoja = libro[HOJA_DATOS]
    meta = {"anio": hoja[CELDA_ANIO].value}
    libro.close()

    tabla = pd.read_excel(
        ruta, sheet_name=HOJA_DATOS, header=FILA_ENCABEZADO - 1, dtype=object
    )
    captura = [c for c in tabla.columns if c not in _CALCULADAS]
    filas = []
    for i, registro in tabla.iterrows():
        if all(vacio(registro[c]) for c in captura):
            continue
        fila = interpretar_fila(registro, ficha, ruta.name, FILA_INICIO + i, meta)
        fila.solo_identificacion = all(
            vacio(registro[c]) for c in captura if c not in IDENTIFICACION
        )
        fila.ejemplo = MARCA_EJEMPLO in str(registro.get("observaciones") or "").upper()
        filas.append(fila)
    return filas, meta


# Columnas que la ficha calcula en Excel: aquí se recalculan, no se leen
_CALCULADAS = {
    "grupo",
    "n_notas",
    "suma_notas",
    "promedio",
    "pct_asistencia",
    "pct_reuniones",
}


def interpretar_fila(registro, ficha: int, archivo: str, fila_excel: int, meta):
    errores, faltantes = [], []

    def texto(nombre: str) -> str:
        valor = registro.get(nombre)
        return "" if vacio(valor) else str(valor).strip()

    def leer_entero(nombre: str) -> int | None:
        try:
            return entero(registro.get(nombre))
        except (TypeError, ValueError):
            errores.append(f"{nombre} no es un número entero")
            return None

    codigo = texto("codigo")
    if not codigo:
        errores.append("fila sin código")
    elif not PATRON_CODIGO.fullmatch(codigo):
        errores.append(f"código {codigo!r} no tiene el formato EST-###")

    grado = leer_entero("grado")
    if grado is None:
        faltantes.append("grado")
    elif grado not in GRUPO_POR_GRADO:
        errores.append(f"grado {grado} fuera de 3.° o 4.°")

    seccion = texto("seccion")
    if not seccion:
        faltantes.append("seccion")

    momento = texto("momento").lower()
    if not momento:
        faltantes.append("momento")
    elif momento not in MOMENTOS:
        errores.append(f"momento {momento!r} no es pre ni post")

    anio = leer_entero("anio")
    if anio is None:
        try:
            anio = entero(meta["anio"])
        except (TypeError, ValueError):
            anio = None
    if anio is None:
        faltantes.append("anio")
    elif anio not in ANIOS:
        errores.append(f"año {anio} fuera de 2024-2026")

    deserto = leer_entero("deserto")
    if deserto is not None and deserto not in (0, 1):
        errores.append("deserto debe ser 0 o 1")
    if anio == ANIO_ACTUAL and deserto is not None:
        errores.append("deserto debe estar vacío en 2026")

    excluido = texto("excluido").lower()
    motivo = texto("motivo_exclusion").lower()
    excluido_motivo = None
    if excluido in ("sí", "si"):
        if motivo not in MOTIVOS:
            errores.append("excluido = sí sin un motivo válido")
        else:
            excluido_motivo = motivo

    datos = {}
    if ficha == 1:
        datos.update(leer_notas(registro, errores, faltantes))
    else:
        programado, realizado = MEDIDAS[ficha]
        for nombre in (programado, realizado):
            valor = leer_entero(nombre)
            if valor is None and not any(nombre in e for e in errores):
                faltantes.append(nombre)
            datos[nombre] = valor

    return Fila(
        ficha=ficha,
        archivo=archivo,
        fila_excel=fila_excel,
        codigo=codigo,
        anio=anio,
        momento=momento,
        grado=grado,
        seccion=seccion,
        deserto=deserto,
        excluido_motivo=excluido_motivo,
        datos=datos,
        faltantes=faltantes,
        errores=errores,
    )


def leer_notas(registro, errores, faltantes) -> dict:
    """Convierte las notas por área (0 a 20) a suma_notas y n_notas."""
    valores = []
    for area in AREAS:
        nota = registro.get(area)
        if vacio(nota):
            continue  # área que no aplica (ej. exonerado)
        try:
            numero = float(nota)
        except (TypeError, ValueError):
            errores.append(f"nota {nota!r} en {area} no es numérica")
            continue
        if not NOTA_MIN <= numero <= NOTA_MAX:
            errores.append(f"nota {nota} en {area} fuera de {NOTA_MIN}-{NOTA_MAX}")
            continue
        valores.append(numero)
    if not valores and not errores:
        faltantes.append("notas")
    return {"suma_notas": round(sum(valores), 2), "n_notas": len(valores)}


# --- Consolidación -----------------------------------------------------------


def consolidar(
    carpeta: Path, permitir_ejemplo: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Une las 3 fichas por codigo + anio + momento y aplica las exclusiones.

    Si alguna fila está marcada como EJEMPLO se detiene, para que un dato
    inventado nunca llegue a Resultados (salvo permitir_ejemplo, para demos).
    """
    filas: dict[int, list[Fila]] = {}
    archivos = {}
    for ficha, (patron, _) in FICHAS.items():
        rutas = sorted(carpeta.glob(patron))
        if not rutas:
            raise FileNotFoundError(f"No hay {patron} en {carpeta}")
        archivos[ficha] = [r.name for r in rutas]
        filas[ficha] = []
        for ruta in rutas:
            leidas, _ = leer_ficha(ruta, ficha)
            filas[ficha].extend(leidas)

    ejemplos = [f.referencia for lista in filas.values() for f in lista if f.ejemplo]
    if ejemplos and not permitir_ejemplo:
        raise ErrorValidacion(
            f"{len(ejemplos)} filas siguen marcadas como {MARCA_EJEMPLO} en "
            f"observaciones (ej. {ejemplos[0]}). Reemplace los datos inventados "
            "y borre la marca antes de procesar."
        )

    # Agrupar por estudiante; las filas sin clave válida se excluyen aparte
    por_clave: dict[tuple, dict[int, list[Fila]]] = {}
    for ficha, lista in filas.items():
        for fila in lista:
            por_clave.setdefault(fila.clave, {}).setdefault(ficha, []).append(fila)

    # Códigos pre-llenados que no se usaron (ej. sección con menos de 35
    # alumnos): no son excluidos, se informan aparte para revisarlos
    sin_usar = sorted(
        clave[0]
        for clave, fichas in por_clave.items()
        if all(f.solo_identificacion for lista in fichas.values() for f in lista)
    )
    incluidos, excluidos = [], []
    for clave, fichas in por_clave.items():
        if clave[0] in sin_usar:
            continue
        registro, exclusion = evaluar(clave, fichas)
        if exclusion:
            excluidos.append(exclusion)
        else:
            incluidos.append(registro)

    df_incluidos = pd.DataFrame(incluidos, columns=COLUMNAS_SALIDA)
    if not df_incluidos.empty and (df_incluidos["anio"] == ANIO_ACTUAL).all():
        df_incluidos = df_incluidos.drop(columns="deserto")
    df_incluidos = df_incluidos.sort_values(["anio", "momento", "codigo"])
    df_excluidos = pd.DataFrame(
        excluidos,
        columns=[
            "codigo",
            "anio",
            "momento",
            "grado",
            "grupo",
            "motivo",
            "detalle",
            "filas",
        ],
    ).sort_values(["motivo", "codigo"])

    resumen = {
        "datos_de_ejemplo": bool(ejemplos),
        "archivos": archivos,
        "registros": len(por_clave) - len(sin_usar),
        "codigos_sin_usar": sin_usar,
        "incluidos": len(df_incluidos),
        "excluidos": len(df_excluidos),
        "excluidos_por_motivo": {
            m: int((df_excluidos["motivo"] == m).sum()) for m in MOTIVOS
        },
        "incluidos_por_grupo": _conteo(df_incluidos, "grupo"),
        "excluidos_por_grupo": _conteo(df_excluidos, "grupo"),
    }
    return df_incluidos, df_excluidos, resumen


def _conteo(df: pd.DataFrame, columna: str) -> dict:
    if df.empty:
        return {}
    return {
        str(k): int(v)
        for k, v in df[columna].fillna("sin grado").value_counts().items()
    }


def evaluar(clave, fichas: dict[int, list[Fila]]):
    """Devuelve (registro incluido, None) o (None, exclusión con su motivo)."""
    todas = [f for lista in fichas.values() for f in lista]
    codigo, anio, momento = clave
    grado = next((f.grado for f in todas if f.grado in GRUPO_POR_GRADO), None)
    base = {
        "codigo": codigo or "(sin código)",
        "anio": anio,
        "momento": momento,
        "grado": grado,
        "grupo": GRUPO_POR_GRADO.get(grado),
        "filas": "; ".join(f.referencia for f in todas),
    }

    def excluir(motivo: str, detalle: str):
        return None, {**base, "motivo": motivo, "detalle": detalle}

    # 1. Exclusión marcada en la ficha (ej. traslado definitivo)
    marcados = [f for f in todas if f.excluido_motivo]
    if marcados:
        return excluir(
            marcados[0].excluido_motivo, f"marcado en {marcados[0].referencia}"
        )

    # 2. Filas duplicadas o sin identificación
    duplicadas = [n for n, lista in fichas.items() if len(lista) > 1]
    if duplicadas:
        nombres = ", ".join(f"ficha {n}" for n in duplicadas)
        return excluir(INCONSISTENTE, f"estudiante repetido en {nombres}")

    # 3. Falta una dimensión completa o un dato obligatorio
    faltan = [n for n in FICHAS if n not in fichas]
    if faltan:
        detalle = ", ".join(f"falta ficha {n} ({FICHAS[n][1]})" for n in faltan)
        return excluir(INCOMPLETA, detalle)
    faltantes = [f"{c} (ficha {f.ficha})" for f in todas for c in f.faltantes]
    errores = [f"{e} (ficha {f.ficha})" for f in todas for e in f.errores]
    if errores:
        return excluir(INCONSISTENTE, "; ".join(errores))
    if faltantes:
        return excluir(INCOMPLETA, "falta " + ", ".join(faltantes))

    # 4. Coherencia entre fichas
    f1, f2, f3 = (fichas[n][0] for n in (1, 2, 3))
    for campo in ("grado", "seccion"):
        valores = {getattr(f, campo) for f in (f1, f2, f3)}
        if len(valores) > 1:
            return excluir(
                INCONSISTENTE,
                f"{campo} distinto entre fichas: {sorted(map(str, valores))}",
            )
    # deserto basta en una ficha; si está en varias, debe coincidir
    desercion = {f.deserto for f in (f1, f2, f3) if f.deserto is not None}
    if len(desercion) > 1:
        return excluir(INCONSISTENTE, "deserto distinto entre fichas")
    deserto = desercion.pop() if desercion else None
    if anio < ANIO_ACTUAL and deserto is None:
        return excluir(INCOMPLETA, "falta deserto (obligatorio en el histórico)")

    # 5. Reglas de las fórmulas
    crudos = {**f1.datos, **f2.datos, **f3.datos}
    try:
        indicadores = calcular_indicadores(**crudos)
    except ErrorValidacion as error:
        return excluir(INCONSISTENTE, str(error))

    return {
        **{k: base[k] for k in ("codigo", "anio", "momento", "grado", "grupo")},
        "seccion": f1.seccion,
        "deserto": deserto,
        **crudos,
        **indicadores,
    }, None


# --- CLI ---------------------------------------------------------------------


def comprobar_salida(salida: Path) -> None:
    """Los datos reales solo se escriben en data/processed/ (gitignored)."""
    salida = salida.resolve()
    permitida = (RAIZ / "data" / "processed").resolve()
    if salida.is_relative_to(RAIZ) and not salida.is_relative_to(permitida):
        raise SystemExit(
            f"La salida debe ir en data/processed/ (datos de menores, Ley N.° 29733): "
            f"{salida}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entrada", type=Path, required=True, help="Carpeta con las 3 fichas"
    )
    parser.add_argument("--salida", type=Path, required=True, help="CSV de incluidos")
    parser.add_argument(
        "--permitir-ejemplo",
        action="store_true",
        help="Solo para demostraciones: procesa aunque haya filas EJEMPLO",
    )
    args = parser.parse_args()

    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")
    comprobar_salida(args.salida)
    try:
        incluidos, excluidos, resumen = consolidar(args.entrada, args.permitir_ejemplo)
    except (FileNotFoundError, ErrorValidacion) as error:
        raise SystemExit(f"[ERROR] {error}") from error

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    base = args.salida.with_suffix("")
    incluidos.to_csv(args.salida, index=False)
    # utf-8-sig: Excel abre bien las tildes de los motivos
    excluidos.to_csv(f"{base}_excluidos.csv", index=False, encoding="utf-8-sig")
    Path(f"{base}_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if resumen["datos_de_ejemplo"]:
        print("[AVISO] Lote con datos de EJEMPLO: no usar en Resultados.")
    print(f"Registros con datos: {resumen['registros']}")
    if resumen["codigos_sin_usar"]:
        sin_usar = resumen["codigos_sin_usar"]
        print(
            f"[AVISO] {len(sin_usar)} códigos sin ningún dato (no cuentan como "
            f"excluidos): {', '.join(sin_usar)}"
        )
    print(f"[OK] incluidos: {resumen['incluidos']} -> {args.salida}")
    print(f"[OK] excluidos: {resumen['excluidos']} -> {base}_excluidos.csv")
    for motivo, n in resumen["excluidos_por_motivo"].items():
        print(f"     - {motivo}: {n}")


if __name__ == "__main__":
    sys.exit(main())
