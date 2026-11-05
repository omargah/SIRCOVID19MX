"""(a) Adimensionalización del SIR.

Afirmación
----------
Con s = S/N, i = I/N, r = R/N y tau = gamma*t, el SIR dimensional

    dS/dt = -beta S I / N,  dI/dt = beta S I / N - gamma I,  dR/dt = gamma I

se vuelve

    ds/dtau = -R0 s i,  di/dtau = (R0 s - 1) i,  dr/dtau = i,   R0 = beta/gamma,

así que la forma de la ola depende solo de (R0, s0, i0); N solo escala los
conteos y gamma solo estira el eje del tiempo.
"""

import numpy as np
import pytest
import sympy as sp
from sympy.physics import units as u

from src import sir
from firma_sir import integrar_sir_frac, incidencia_semanal_frac

pytestmark = pytest.mark.teoria


# --------------------------------------------------------------------------
# Simbólico
# --------------------------------------------------------------------------
beta, gamma, N, R0 = sp.symbols("beta gamma N R_0", positive=True)
S, I, s, i = sp.symbols("S I s i", positive=True)


def campo_dimensional(S, I):
    return sp.Matrix([-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I])


def campo_adimensional(s, i):
    return sp.Matrix([-R0 * s * i, (R0 * s - 1) * i, i])


def test_campo_dimensional_es_N_gamma_por_el_adimensional():
    """Si S = N s(gamma t), entonces dS/dt = N*gamma*ds/dtau. Basta probar
    que el campo dimensional evaluado en (N s, N i) es N*gamma veces el
    adimensional, con beta = R0*gamma."""
    lhs = campo_dimensional(N * s, N * i).subs(beta, R0 * gamma)
    rhs = N * gamma * campo_adimensional(s, i)
    assert sp.simplify(lhs - rhs) == sp.zeros(3, 1)


def test_regla_de_la_cadena_tau_igual_gamma_t():
    """d/dt f(gamma t) = gamma f'(gamma t): el factor gamma de arriba."""
    t = sp.symbols("t", positive=True)
    f = sp.Function("f")
    tau = sp.symbols("tau")
    lhs = sp.diff(f(gamma * t), t)
    rhs = gamma * sp.diff(f(tau), tau).subs(tau, gamma * t)
    assert sp.simplify(lhs - rhs.doit()) == 0


def test_R0_es_adimensional():
    """beta y gamma tienen unidades de 1/tiempo; su cociente no tiene unidades."""
    b = sp.Rational(5, 14) / u.day
    g = sp.Rational(1, 7) / u.day
    cociente = u.convert_to(b / g, [])
    assert cociente.free_symbols == set()
    assert cociente == sp.Rational(5, 2)


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
def test_sir_py_solo_depende_de_gamma_t():
    """Mismo R0, s0, i0 y dos gammas distintas: las trayectorias coinciden
    al compararlas en el mismo tau = gamma*t."""
    R0_, s0, i0 = 2.5, 0.8, 1e-5
    tau = np.linspace(0.0, 40.0, 81)
    g1, g2 = 1 / 7, 1 / 3
    s1, i1 = integrar_sir_frac(R0_, g1, s0, i0, tau / g1)
    s2, i2 = integrar_sir_frac(R0_, g2, s0, i0, tau / g2)
    np.testing.assert_allclose(s1, s2, rtol=1e-8)
    np.testing.assert_allclose(i1, i2, rtol=1e-6, atol=1e-14)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DISCREPANCIA (surgió al adaptar a la firma actual de sir.py): ahora sir.py "
    "integra en PERSONAS con atol = ATOL_RELATIVA_A_N*N y rtol=1e-10, así que el "
    "error numérico de LSODA depende de N. La escala exacta en N y rho (rtol=1e-12) "
    "ya no se cumple: la diferencia medida es ~9e-9 relativo. Matemáticamente la "
    "linealidad sigue valiendo; la implementación la cumple solo al nivel del "
    "error del integrador. La tolerancia 1e-12 NO se aflojó: ver la prueba "
    "compañera ..._al_nivel_del_integrador. strict=True: si sir.py vuelve a "
    "ser exacto en N, pytest avisa para quitar el xfail."))
def test_sir_py_N_y_rho_solo_escalan():
    """incidencia_semanal es lineal en N y en rho (la dinámica no ve N)."""
    args = (2.5, 1 / 7, 0.6, 1e-5)
    base = incidencia_semanal_frac(*args, rho=1.0, N=1.0, n_semanas=20)
    otra = incidencia_semanal_frac(*args, rho=0.13, N=3.7e6, n_semanas=20)
    np.testing.assert_allclose(otra, 0.13 * 3.7e6 * base, rtol=1e-12)


def test_sir_py_N_y_rho_solo_escalan_al_nivel_del_integrador():
    """Prueba NUEVA (no sustituye a la anterior): la misma escala, pero con la
    cota que sí garantiza el integrador. Con rtol=1e-10 por paso, el error
    global en incidencia (diferencia de S) se mide ~9e-9; 1e-7 deja un factor
    ~10 de margen. Si esto falla, el cambio es mayor que ruido de LSODA."""
    args = (2.5, 1 / 7, 0.6, 1e-5)
    base = incidencia_semanal_frac(*args, rho=1.0, N=1.0, n_semanas=20)
    otra = incidencia_semanal_frac(*args, rho=0.13, N=3.7e6, n_semanas=20)
    np.testing.assert_allclose(otra, 0.13 * 3.7e6 * base, rtol=1e-7)
