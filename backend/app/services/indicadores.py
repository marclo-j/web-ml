"""Cálculo de los 3 indicadores con las fórmulas de la tesis (docs/VARIABLES.md).

Es la misma función que ml/preprocess.py (calcular_indicadores); el backend
lleva su copia para desplegarse sin la carpeta ml/. tests/test_indicadores.py
comprueba que ambas den exactamente lo mismo.
"""

NOTA_MIN, NOTA_MAX = 0, 20  # escala vigesimal (decisión D1)
GRUPO_POR_GRADO = {3: "control", 4: "experimental"}


class ErrorValidacion(ValueError):
    """Falla una regla de docs/VARIABLES.md; el mensaje dice cuál."""


def calcular_indicadores(
    suma_notas: float,
    n_notas: int,
    dias_asistidos: int,
    dias_programados: int,
    reuniones_asistidas: int,
    reuniones_programadas: int,
) -> dict[str, float]:
    """Promedio = Σ Notas / n; Asistencia = (DA / DP) × 100; CA = (RA / RT) × 100."""
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
