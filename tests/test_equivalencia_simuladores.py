"""Equivalencia entre el simulador de F4 (sirmx, RK4 + numba) y src/sir.py (LSODA).

Decisión D-C (docs/decisiones_integracion.md): sirmx/ se queda con su RK4
compilado porque LSODA es ~170 veces más lento (~44 s por ajuste), inviable
para la búsqueda de puntos de cambio. src/sir.py es la REFERENCIA OFICIAL, y
la equivalencia se garantiza con ESTE test, no con una llamada.

Qué se compara, en fracciones de N y en 200 días con D = 7:
  s(t), i(t) y r(t) = 1 - s - i en t = 0, 1, ..., 200,
  y la incidencia diaria: media_casos() de sirmx (infecciones por día, con
  rho = 1 y sin efecto de día de la semana) contra -diff(S) de src/sir.py.

Escenarios: R0 ∈ {1.5, 2.5, 8} × i0 ∈ {1e-5, 2.5e-5}, con s0 = 0.999.
(s0 = 0.999 y no 1.0: ver docs/pendientes_integracion.md, "s0 = 1".)

Convención del estado inicial. sirmx usa s0 = fracción susceptible e
i0 = fracción infecciosa, sin más condición. src/sir.py (estado_inicial)
usa s0 = (S0 + I0)/N. Aquí se llama a integrar_sir con S0 = N*s0 e I0 = N*i0
para que los dos simuladores partan del MISMO estado; con s0 = 0.999 y
i0 <= 2.5e-5 se cumple S0 + I0 <= N.

TOLERANCIA (declarada antes de medir): TOL = 1e-6, absoluta, en fracciones de N.
De dónde sale: el inventario de integración (docs/inventario_integracion.md,
§2.2 c) midió que el error de sirmx contra una referencia de alta precisión
es < 1e-6; src/sir.py aporta, por su parte, <= 1e-8 incluso en una ola
explosiva (docs/teoria_verificacion.md, discrepancia 1), es decir, 100 veces
menos. Por eso 1e-6 es la cota que se puede defender: es el error que se
declaró para sirmx. NO se aflojó cuando R0 = 8 no la cumplió (ver abajo).

RESULTADO CONOCIDO (medido contra DOP853, rtol = 1e-13): el RK4 de sirmx con
4 subpasos por día NO cumple 1e-6 con R0 = 8: error ~5e-5 en s y ~4e-5 en i.
Con R0 = 1.5 el error es ~8e-10 y con R0 = 2.5, ~1e-7. El error baja con el
orden 4 esperado (con 16 subpasos, R0 = 8 daría ~2.5e-7). Esos dos
escenarios quedan como xfail(strict=True, raises=AssertionError): no se
esconde el hallazgo, y si alguien sube NSUB, pytest avisa para quitar el
xfail. Decidir qué hacer (subir NSUB, o declarar que sirmx solo vale para
R_eff <= ~3) es pendiente de Omar (docs/pendientes_integracion.md).
"""
import numpy as np
import pytest

from sirmx.modelo import ParamsOla, media_casos, sir_incidencia
from src import sir

D = 7.0
GAMMA = 1.0 / D
T = 200                 # días
N = 1e7                 # el valor por omisión de ParamsOla; el resultado no depende de N
S0 = 0.999
TOL = 1e-6              # absoluta, en fracciones de N (ver docstring)

_MOTIVO_R0_8 = (
    "HALLAZGO: el RK4 de sirmx con NSUB = 4 subpasos/día tiene error ~5e-5 en s y "
    "~4e-5 en i para R0 = 8 (medido contra DOP853 rtol=1e-13), por encima de TOL = 1e-6. "
    "src/sir.py (LSODA) está a ~1e-10 de esa referencia, así que el desvío es de sirmx. "
    "Con 16 subpasos daría ~2.5e-7. No se aflojó la tolerancia; ver "
    "docs/pendientes_integracion.md. strict=True: si se corrige, pytest avisa."
)


def _caso(R0, i0):
    if R0 == 8.0:
        return pytest.param(R0, i0, id=f"R0={R0}-i0={i0}",
                            marks=pytest.mark.xfail(strict=True, raises=AssertionError,
                                                    reason=_MOTIVO_R0_8))
    return pytest.param(R0, i0, id=f"R0={R0}-i0={i0}")


ESCENARIOS = [_caso(R0, i0) for R0 in (1.5, 2.5, 8.0) for i0 in (1e-5, 2.5e-5)]


def _sirmx(R0, i0):
    p = ParamsOla(R0=R0, s0=S0, rho=1.0, i0=i0, k=10.0, D=D, N=N)
    _, infecciones, _ = media_casos(p, T)            # infecciones/día (personas)
    beta = np.full(T, R0 * GAMMA)
    _, s, i = sir_incidencia(beta, GAMMA, S0, i0)    # (T+1,), fracciones
    return s, i, infecciones


def _sir_oficial(R0, i0):
    t = np.arange(T + 1, dtype=float)
    S, I, R = sir.integrar_sir(R0, D, N * S0, N * i0, N, t)
    return S / N, I / N, R / N, -np.diff(S)          # nuevas infecciones/día (personas)


@pytest.mark.parametrize("R0,i0", ESCENARIOS)
def test_sirmx_equivale_a_sir_py(R0, i0):
    s_m, i_m, inc_m = _sirmx(R0, i0)
    s_o, i_o, r_o, inc_o = _sir_oficial(R0, i0)
    r_m = 1.0 - s_m - i_m

    err = {
        "s": np.max(np.abs(s_m - s_o)),
        "i": np.max(np.abs(i_m - i_o)),
        "r": np.max(np.abs(r_m - r_o)),
        # incidencia en fracciones de N (por día); los dos recortan a >= 0
        "incidencia": np.max(np.abs(inc_m - np.maximum(inc_o, 0.0)) / N),
    }
    malos = {k: f"{v:.2e}" for k, v in err.items() if not v <= TOL}
    assert not malos, f"R0={R0}, i0={i0}: errores sobre TOL={TOL:g}: {malos}; todos: " + \
        ", ".join(f"{k}={v:.2e}" for k, v in err.items())


def test_ambos_simuladores_conservan_la_poblacion():
    """Control: la comparación parte de un estado válido y ninguno pierde gente."""
    s_o, i_o, r_o, _ = _sir_oficial(2.5, 1e-5)
    np.testing.assert_allclose(s_o + i_o + r_o, 1.0, atol=1e-9)
    s_m, i_m, _ = _sirmx(2.5, 1e-5)
    assert np.all(s_m > 0) and np.all(i_m > 0) and s_m[0] + i_m[0] <= 1.0
