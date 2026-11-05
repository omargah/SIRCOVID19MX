"""(b) Conservación de N y positividad.

Afirmación
----------
1. d(S + I + R)/dt = 0, así que S + I + R = N para todo t.
2. Si S0 > 0 e I0 > 0, entonces para todo t >= 0
       S(t) = S0 exp(-(beta/N) ∫_0^t I)          > 0,
       I(t) = I0 exp(∫_0^t (beta S/N - gamma))   > 0,
       dR/dt = gamma I >= 0,  dS/dt <= 0.
   (Las fórmulas exponenciales satisfacen las EDO; la positividad se lee de ellas.)

Nota honesta sobre el test numérico
-----------------------------------
src/sir.py NO integra r: lo define como r = 1 - s - i. Comprobar
"s + i + r = 1" con su salida sería una tautología. Por eso la prueba
numérica compara r(t) - r(0) = 1 - s - i - (1 - s0 - i0) con gamma*∫ i dt
calculada por cuadratura independiente sobre la trayectoria.
"""

import numpy as np
import pytest
import sympy as sp
from scipy.integrate import cumulative_simpson

from src import sir
from firma_sir import integrar_sir_frac

pytestmark = pytest.mark.teoria

t, x = sp.symbols("t x", nonnegative=True)
beta, gamma, N, S0, I0 = sp.symbols("beta gamma N S_0 I_0", positive=True)
S, I = sp.Function("S"), sp.Function("I")


def test_suma_del_campo_es_cero():
    Sv, Iv = sp.symbols("S I")
    dS = -beta * Sv * Iv / N
    dI = beta * Sv * Iv / N - gamma * Iv
    dR = gamma * Iv
    assert sp.simplify(dS + dI + dR) == 0


def test_formula_exponencial_de_S_satisface_la_EDO():
    S_formula = S0 * sp.exp(-beta / N * sp.Integral(I(x), (x, 0, t)))
    residuo = sp.diff(S_formula, t) - (-beta * S_formula * I(t) / N)
    assert sp.simplify(residuo) == 0
    assert S_formula.subs(t, 0).doit() == S0


def test_formula_exponencial_de_I_satisface_la_EDO():
    I_formula = I0 * sp.exp(sp.Integral(beta * S(x) / N - gamma, (x, 0, t)))
    residuo = sp.diff(I_formula, t) - (beta * S(t) * I_formula / N - gamma * I_formula)
    assert sp.simplify(residuo) == 0
    assert I_formula.subs(t, 0).doit() == I0


def test_signos_de_las_derivadas():
    Sv, Iv = sp.symbols("S I", positive=True)
    assert (-beta * Sv * Iv / N).is_negative
    assert (gamma * Iv).is_positive


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
CASOS = [
    # (R0, gamma, s0, i0, tolerancia absoluta de la conservación)
    # La tolerancia del caso explosivo es mayor A PROPÓSITO: ahí LSODA
    # acumula un error global ~1e-8 en s (ver DISCREPANCIA abajo).
    (0.7, 1 / 7, 1.0 - 1e-3, 1e-3, 1e-9),   # subcrítico
    (2.5, 1 / 7, 0.6, 1e-5, 1e-9),   # típico (valores sintéticos del proyecto)
    (15.0, 1 / 5, 0.99, 1e-9, 5e-8),  # explosivo
    (3.0, 1 / 7, 0.5, 0.2, 1e-9),    # i0 grande
]


@pytest.mark.parametrize("R0,gamma_,s0,i0,tol", CASOS)
def test_sir_py_positivo_monotono_y_conserva(R0, gamma_, s0, i0, tol):
    tt = np.linspace(0.0, 400.0, 40001)  # paso 0.01 d para la cuadratura
    s, i = integrar_sir_frac(R0, gamma_, s0, i0, tt)
    r = 1.0 - s - i
    assert np.all(s > 0) and np.all(i > 0)
    assert np.all(np.diff(s) <= 1e-15)  # S no crece
    assert np.all(np.diff(r) >= -1e-12)  # R no decrece
    # Conservación no tautológica: R(t)-R(0) = gamma ∫ I.
    r_cuadratura = gamma_ * cumulative_simpson(i, x=tt, initial=0.0)
    np.testing.assert_allclose(r - r[0], r_cuadratura, atol=tol)


def test_sir_py_rechaza_estados_no_positivos():
    for s0, i0 in [(0.0, 1e-5), (0.5, 0.0), (-0.1, 1e-5)]:
        with pytest.raises(ValueError):
            integrar_sir_frac(2.0, 1 / 7, s0, i0, [0.0, 1.0])


# --------------------------------------------------------------------------
# DISCREPANCIA encontrada: error global de sir.py vs su tolerancia documentada
# --------------------------------------------------------------------------
# src/sir.py dice que con RTOL=1e-10 el error numérico es "~1e-10 relativo".
# Eso es cierto para el error LOCAL por paso. El error GLOBAL de LSODA en la
# fase de crecimiento rápido de una ola explosiva llega a ~1e-8 en s (no es
# la interpolación de t_eval: integrando hasta ese t como punto final el
# error es el mismo). DOP853 o Radau con la misma rtol quedan en ~1e-10.
# tests/test_sir.py no lo detecta porque solo mira s(t -> inf), que es un
# atractor: el error se contrae al final de la ola.
# Impacto: despreciable frente al ruido binomial negativo para R0 ~ 2-3
# (error ~4e-10), pero la cifra documentada es optimista.

def _referencia(R0, gamma_, s0, i0, tt):
    from scipy.integrate import solve_ivp

    f = lambda _t, y: [-R0 * gamma_ * y[0] * np.exp(y[1]), R0 * gamma_ * y[0] - gamma_]
    ref = solve_ivp(f, (tt[0], tt[-1]), [s0, np.log(i0)], t_eval=tt,
                    method="DOP853", rtol=1e-13, atol=1e-15)
    return ref.y[0]


def test_sir_py_error_global_en_caso_tipico():
    """Con los valores sintéticos del proyecto el error global sí es ~1e-10."""
    tt = np.linspace(0.0, 400.0, 4001)
    s, _ = integrar_sir_frac(2.5, 1 / 7, 0.6, 1e-5, tt)
    assert np.max(np.abs(s - _referencia(2.5, 1 / 7, 0.6, 1e-5, tt))) < 1e-9


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DISCREPANCIA: LSODA (rtol=1e-10) acumula error global ~1e-8 en s durante "
    "una ola explosiva (R0=15); sir.py documenta ~1e-10. strict=True: si se "
    "corrige (p. ej. method='DOP853'), este test pasa y pytest avisa para quitar el xfail."))
def test_sir_py_cumple_su_tolerancia_documentada_en_ola_explosiva():
    tt = np.linspace(0.0, 400.0, 4001)
    s, _ = integrar_sir_frac(15.0, 1 / 5, 0.99, 1e-9, tt)
    assert np.max(np.abs(s - _referencia(15.0, 1 / 5, 0.99, 1e-9, tt))) < 1e-9
