"""(g) R0 S0/N = 1 + r D  frente a  exp(r D).

Afirmación
----------
Al inicio de la ola S ≈ S0, y dI/dt ≈ (beta S0/N - gamma) I, así que I (y la
incidencia) crecen como e^{r t} con
       r = gamma (R0 S0/N - 1)   =>   R_eff(0) = R0 S0/N = 1 + r D,  D = 1/gamma.
La fórmula R = exp(r D) NO sale del SIR: corresponde a un intervalo de
generación fijo (delta) de duración D (límite k -> inf de la derivación h).
Como exp(x) > 1 + x para todo x != 0, usar exp(rD) con un modelo SIR
sobrestima R_eff(0) tanto en crecimiento (r > 0) como en descenso (r < 0);
la diferencia es (rD)^2/2 + O((rD)^3).

Resultado de la comparación (DISCREPANCIA entre las dos fórmulas, no un
error del código): para R_eff(0) = 1.5 y D = 7 d, exp(rD) = 1.649, +9.9 %.
src/sir.py y el código anterior (v0-anterior/analisis_montecarlo.py,
"R0 = (1 + growth*D)/S0") usan 1 + rD, que es la consistente con el SIR.
"""

import numpy as np
import pytest
import sympy as sp

from src import sir

pytestmark = pytest.mark.teoria

beta, gamma, N, S0, R0, r, D, x = sp.symbols("beta gamma N S_0 R_0 r D x", positive=True)


def test_tasa_de_crecimiento_linealizada():
    """Linealización en I ≈ 0, S = S0: dI/dt = (beta S0/N - gamma) I."""
    S, I = sp.symbols("S I")
    dI = beta * S * I / N - gamma * I
    r_lin = sp.diff(dI, I).subs({I: 0, S: S0})
    r_esperada = gamma * (R0 * S0 / N - 1)
    assert sp.simplify(r_lin.subs(beta, R0 * gamma) - r_esperada) == 0


def test_R_eff0_igual_1_mas_rD():
    r_sir = gamma * (R0 * S0 / N - 1)
    assert sp.simplify((1 + r_sir * (1 / gamma)) - R0 * S0 / N) == 0


def test_exp_rD_difiere_a_segundo_orden():
    diferencia = sp.series(sp.exp(x) - (1 + x), x, 0, 4).removeO()
    assert sp.simplify(diferencia - (x**2 / 2 + x**3 / 6)) == 0
    # f = exp(x) - 1 - x: f(0) = f'(0) = 0 y f'' = exp(x) > 0 (convexa),
    # así que f > 0 para todo x real distinto de 0.
    xr = sp.symbols("x_r", real=True)
    f = sp.exp(xr) - 1 - xr
    assert f.subs(xr, 0) == 0 and sp.diff(f, xr).subs(xr, 0) == 0
    assert sp.diff(f, xr, 2).is_positive


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
def tasa_crecimiento(R0_, gamma_, s0, i0, T=20.0):
    """Pendiente de log i en [0, T] por mínimos cuadrados."""
    tt = np.linspace(0.0, T, 201)
    _, i = sir.integrar_sir(R0_, gamma_, s0, i0, tt)
    return np.polyfit(tt, np.log(i), 1)[0]


@pytest.mark.parametrize("R0_,s0,D_", [(2.5, 0.6, 7.0), (3.0, 1.0, 5.0), (1.2, 1.0, 10.0)])
def test_1_mas_rD_recupera_R_eff0_en_sir_py(R0_, s0, D_):
    r_ = tasa_crecimiento(R0_, 1 / D_, s0, 1e-10)
    assert abs((1 + r_ * D_) - R0_ * s0) < 1e-6


def test_exp_rD_sobrestima_en_sir_py():
    """Magnitud de la discrepancia con los valores sintéticos del proyecto."""
    R0_, s0, D_ = 2.5, 0.6, 7.0  # R_eff(0) = 1.5
    r_ = tasa_crecimiento(R0_, 1 / D_, s0, 1e-10)
    R_lin, R_exp = 1 + r_ * D_, np.exp(r_ * D_)
    assert R_lin == pytest.approx(1.5, abs=1e-6)
    assert R_exp == pytest.approx(np.exp(0.5), rel=1e-6)
    assert R_exp / R_lin - 1 == pytest.approx(0.0991, abs=1e-3)


def test_incidencia_crece_a_la_misma_tasa():
    """La tasa medida en la incidencia semanal de sir.py también es r.

    i0 = 1e-6 y no 1e-10: con i0 diminuto incidencia_semanal pierde
    precisión por cancelación en s_k - s_{k+1} (DISCREPANCIA documentada en
    test_i_casos_incidencia.py). Con 1e-6 el error residual (~4e-5 relativo
    por semana, más el agotamiento de s ~ R0*gamma*Δs ~ 4e-6) cabe en 1e-5.
    """
    R0_, g, s0 = 2.5, 1 / 7, 0.6
    mu = sir.incidencia_semanal(R0_, g, s0, 1e-6, 1.0, 1.0, 3)
    r_sem = np.polyfit(7.0 * np.arange(3), np.log(mu), 1)[0]
    assert abs(r_sem - g * (R0_ * s0 - 1)) < 1e-5
