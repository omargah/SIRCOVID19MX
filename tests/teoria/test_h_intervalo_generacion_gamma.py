"""(h) Intervalo de generación gamma: R = (1 + r T/k)^k.

Afirmación
----------
Ecuación de Euler–Lotka (Wallinga y Lipsitch 2007): en crecimiento
exponencial a tasa r, 1/R = ∫_0^inf g(tau) e^{-r tau} dtau = M_g(-r).
Con g ~ Gamma(forma k, media T) (escala T/k):
       M_g(-r) = (1 + r T/k)^{-k}   =>   R = (1 + r T/k)^k.
Casos límite:
  k = 1  (exponencial, media T):  R = 1 + r T   — es el SIR con T = 1/gamma,
                                                  coincide con la derivación g.
  k -> inf (delta en T):          R = exp(r T)  — el "exp(rD)" de (g).
Para r > 0, R(k) crece con k: con la misma r, el SIR da el R más chico.

Nota sobre el test numérico
---------------------------
src/sir.py es un SIR, cuyo intervalo de generación es exponencial (k = 1).
Solo el caso k = 1 se puede comprobar contra sir.py. Para k > 1 se usa una
comprobación numérica independiente (no es sir.py): la cadena lineal con
k-1 compartimentos latentes y uno infeccioso, todos con tasa k/T, cuyo
intervalo de generación es exactamente Gamma(k, media T).
"""

import numpy as np
import pytest
import sympy as sp

from src import sir

pytestmark = pytest.mark.teoria

tau, r, T, k = sp.symbols("tau r T k", positive=True)
g = (k / T) ** k * tau ** (k - 1) * sp.exp(-k * tau / T) / sp.gamma(k)


def test_g_es_densidad_con_media_T():
    assert sp.simplify(sp.integrate(g, (tau, 0, sp.oo))) == 1
    assert sp.simplify(sp.integrate(tau * g, (tau, 0, sp.oo))) == T


def test_euler_lotka_da_1_mas_rT_sobre_k_a_la_k():
    M = sp.integrate(g * sp.exp(-r * tau), (tau, 0, sp.oo))
    assert sp.simplify(1 / M - (1 + r * T / k) ** k) == 0


def test_limites_k_1_y_k_infinito():
    R = (1 + r * T / k) ** k
    assert sp.simplify(R.subs(k, 1) - (1 + r * T)) == 0
    assert sp.limit(R, k, sp.oo) == sp.exp(r * T)


def test_R_crece_con_k_para_r_positivo():
    """d ln R / dk = ln(1+x) - x/(1+x) con x = rT/k > 0, que es > 0."""
    xx = sp.symbols("x", positive=True)
    dlnR_dk = sp.diff(k * sp.log(1 + r * T / k), k)
    assert sp.simplify(dlnR_dk - (sp.log(1 + xx) - xx / (1 + xx)).subs(xx, r * T / k)) == 0
    h = sp.log(1 + xx) - xx / (1 + xx)
    assert h.subs(xx, 0) == 0 and sp.simplify(sp.diff(h, xx) - xx / (1 + xx) ** 2) == 0


# --------------------------------------------------------------------------
# Numérico
# --------------------------------------------------------------------------
def test_k_igual_1_contra_sir_py():
    R0_, s0, T_ = 2.5, 0.6, 7.0
    tt = np.linspace(0.0, 20.0, 201)
    _, i = sir.integrar_sir(R0_, 1 / T_, s0, 1e-10, tt)
    r_ = np.polyfit(tt, np.log(i), 1)[0]
    assert abs((1 + r_ * T_ / 1) ** 1 - R0_ * s0) < 1e-6


def tasa_cadena_lineal(R, T_, k_):
    """Autovalor dominante de la cadena E_1 -> ... -> E_{k-1} -> I con tasa
    k/T en cada etapa y nuevas infecciones R*(k/T)*I hacia E_1 (s ≈ 1)."""
    lam = k_ / T_
    A = np.zeros((k_, k_))
    for j in range(k_):
        A[j, j] = -lam
        if j > 0:
            A[j, j - 1] = lam
    A[0, k_ - 1] += R * lam  # el infeccioso (último) genera en E_1 (o en sí mismo si k=1)
    return max(np.linalg.eigvals(A).real)


@pytest.mark.parametrize("k_", [1, 2, 3, 5, 10])
def test_cadena_lineal_cumple_la_formula(k_):
    R, T_ = 1.5, 7.0
    r_ = tasa_cadena_lineal(R, T_, k_)
    assert (1 + r_ * T_ / k_) ** k_ == pytest.approx(R, rel=1e-10)


def test_cadena_lineal_k1_es_el_sir_py():
    R, T_ = 1.5, 7.0
    tt = np.linspace(0.0, 20.0, 201)
    _, i = sir.integrar_sir(R, 1 / T_, 1.0, 1e-10, tt)
    r_sir = np.polyfit(tt, np.log(i), 1)[0]
    assert abs(r_sir - tasa_cadena_lineal(R, T_, 1)) < 1e-7


def test_misma_r_distinto_R_segun_k():
    r_, T_ = 0.5 / 7, 7.0
    Rs = [(1 + r_ * T_ / k_) ** k_ for k_ in (1, 2, 5, 50)]
    assert all(a < b for a, b in zip(Rs, Rs[1:]))
    assert Rs[0] == pytest.approx(1.5) and Rs[-1] < np.exp(0.5)
