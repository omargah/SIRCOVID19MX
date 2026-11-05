"""(e) R_eff, pico en S = N/R0 e I_max.

Afirmación
----------
1. R_eff(t) = R0 S(t)/N, y dI/dt = gamma (R_eff - 1) I: I crece si y solo si
   R_eff > 1.
2. Si R0 S0/N > 1, I tiene un único máximo, en S = N/R0 (R_eff = 1).
3. Usando H (derivación c) entre t = 0 y el pico:
       I_max = I0 + S0 - (N/R0) [1 + ln(R0 S0 / N)].
   Si R0 S0/N <= 1, I_max = I0 (no hay pico interior).
"""

import numpy as np
import pytest
import sympy as sp
from scipy.optimize import minimize_scalar

from src import sir
from firma_sir import integrar_sir_frac

pytestmark = pytest.mark.teoria

beta, gamma, N, R0 = sp.symbols("beta gamma N R_0", positive=True)
S, I, S0, I0, Imax = sp.symbols("S I S_0 I_0 I_max", positive=True)


def test_dI_dt_en_terminos_de_R_eff():
    R_eff = R0 * S / N
    dI = (R0 * gamma) * S * I / N - gamma * I
    assert sp.simplify(dI - gamma * (R_eff - 1) * I) == 0


def test_pico_en_S_igual_N_sobre_R0():
    dI = (R0 * gamma) * S * I / N - gamma * I
    assert sp.solve(sp.Eq(dI / I, 0), S) == [N / R0]
    # Es máximo: d2I/dt2 = (dI/dS)(dS/dt)... en el pico se reduce a
    # gamma*R0*I*dS/dt/N < 0 porque dS/dt < 0.
    dS = -(R0 * gamma) * S * I / N
    d2I_en_pico = (gamma * R0 / N * dS * I).subs(S, N / R0)
    assert d2I_en_pico.is_negative


def test_I_max_desde_la_integral_primera():
    H = lambda S_, I_: S_ + I_ - N / R0 * sp.log(S_)
    sol = sp.solve(sp.Eq(H(S0, I0), H(N / R0, Imax)), Imax)
    formula = I0 + S0 - N / R0 * (1 + sp.log(R0 * S0 / N))
    assert len(sol) == 1
    assert sp.simplify(sp.expand_log(sol[0] - formula, force=True)) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
@pytest.mark.parametrize("R0_,s0,i0", [(2.5, 0.6, 1e-5), (3.0, 1.0 - 1e-6, 1e-6), (1.5, 0.9, 1e-3)])
def test_pico_e_I_max_en_sir_py(R0_, s0, i0):
    g = 1 / 7

    def menos_i(t):
        _, i = integrar_sir_frac(R0_, g, s0, i0, [0.0, t])
        return -i[-1]

    # Rejilla gruesa para acotar el pico; luego se refina.
    tt = np.linspace(0.0, 600.0, 601)
    _, ig = integrar_sir_frac(R0_, g, s0, i0, tt)
    k = int(np.argmax(ig))
    res = minimize_scalar(menos_i, bounds=(tt[k - 1], tt[k + 1]), method="bounded",
                          options={"xatol": 1e-6})
    s_pico, i_pico = (x[-1] for x in integrar_sir_frac(R0_, g, s0, i0, [0.0, res.x]))
    i_max_formula = i0 + s0 - (1 + np.log(R0_ * s0)) / R0_
    assert abs(i_pico - i_max_formula) < 1e-8
    assert abs(s_pico - 1 / R0_) < 1e-4  # s se mueve rápido cerca del pico: tol. por xatol


def test_signo_de_di_dt_sigue_a_R_eff_en_sir_py():
    tt = np.linspace(0.0, 300.0, 3001)
    s, i = integrar_sir_frac(2.5, 1 / 7, 0.6, 1e-5, tt)
    R_eff = 2.5 * s
    di = np.gradient(i, tt)
    lejos_del_pico = np.abs(R_eff - 1) > 1e-2
    assert np.all(np.sign(di[lejos_del_pico]) == np.sign(R_eff[lejos_del_pico] - 1))


def test_sin_pico_interior_si_R0_s0_menor_que_uno():
    tt = np.linspace(0.0, 300.0, 301)
    _, i = integrar_sir_frac(2.5, 1 / 7, 0.35, 1e-3, tt)
    assert np.argmax(i) == 0 and i[0] == pytest.approx(1e-3)
