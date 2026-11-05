"""(c) Integral primera H.

Afirmación
----------
En fracciones, H(s, i) = s + i - (1/R0) ln s es constante sobre las
soluciones. Equivalente dimensional: H = S + I - (N/R0) ln S.
Se obtiene integrando di/ds = (R0 s - 1) i / (-R0 s i) = -1 + 1/(R0 s).
"""

import numpy as np
import pytest
import sympy as sp

from src import sir
from firma_sir import integrar_sir_frac

pytestmark = pytest.mark.teoria

R0, N, gamma = sp.symbols("R_0 N gamma", positive=True)
s, i, S, I = sp.symbols("s i S I", positive=True)

H = s + i - sp.log(s) / R0


def test_dH_dt_es_cero_en_fracciones():
    ds = -R0 * gamma * s * i
    di = R0 * gamma * s * i - gamma * i
    dH = sp.diff(H, s) * ds + sp.diff(H, i) * di
    assert sp.simplify(dH) == 0


def test_dH_dt_es_cero_dimensional():
    beta = R0 * gamma
    Hd = S + I - N / R0 * sp.log(S)
    dS = -beta * S * I / N
    dI = beta * S * I / N - gamma * I
    assert sp.simplify(sp.diff(Hd, S) * dS + sp.diff(Hd, I) * dI) == 0


def test_H_sale_de_integrar_di_ds():
    """dsolve de di/ds = -1 + 1/(R0 s) da i(s) = C - s + ln(s)/R0, es decir H = C."""
    sv = sp.symbols("s", positive=True)
    iF = sp.Function("i")
    sol = sp.dsolve(sp.Eq(iF(sv).diff(sv), -1 + 1 / (R0 * sv)), iF(sv))
    H_en_sol = (sv + sol.rhs - sp.log(sv) / R0)
    assert sp.diff(sp.simplify(H_en_sol), sv) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
@pytest.mark.parametrize("R0_,s0,i0", [(2.5, 0.6, 1e-5), (1.3, 1.0 - 1e-4, 1e-4), (8.0, 0.9, 0.05)])
def test_H_constante_en_trayectoria_de_sir_py(R0_, s0, i0):
    tt = np.linspace(0.0, 500.0, 2001)
    s_, i_ = integrar_sir_frac(R0_, 1 / 7, s0, i0, tt)
    Hn = s_ + i_ - np.log(s_) / R0_
    assert np.max(np.abs(Hn - Hn[0])) < 1e-8
