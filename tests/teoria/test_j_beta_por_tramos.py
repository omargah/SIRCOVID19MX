"""(j) beta(t) por tramos y R_t = beta(t) S / (gamma N).

Afirmación
----------
1. Para cualquier beta(t), con R_t = beta(t) S(t) / (gamma N):
       dI/dt = gamma (R_t - 1) I,
   así que I crece si y solo si R_t > 1 (generaliza la derivación e).
2. Con beta constante por tramos, beta = beta_j en [tau_j, tau_{j+1}):
   - S e I son continuas en los cortes; R_t salta por beta_{j+1}/beta_j.
   - Dentro del tramo j se conserva H_j = s + i - ln(s)/R0_j (derivación c).
   - En el corte tau, H salta: H_{j+1} - H_j = -ln s(tau) (1/R0_{j+1} - 1/R0_j).
   - Por eso el tamaño final y el pico con beta(t) NO se obtienen con las
     fórmulas de beta constante (derivaciones e, f) usando un R0 "promedio".

DISCREPANCIA / limitación de src/sir.py
---------------------------------------
sir.py solo admite R0 constante. H2 y H5 (plan de análisis) necesitan beta
por tramos, y no existe en src/. Aquí se construye encadenando
sir.integrar_sir tramo por tramo (el estado final de un tramo es el inicial
del siguiente). Esa función debería moverse a src/sir.py cuando se trabaje H5.
"""

import numpy as np
import pytest
import sympy as sp
from scipy.integrate import solve_ivp

from src import sir

pytestmark = pytest.mark.teoria

t = sp.symbols("t", real=True)
gamma, N = sp.symbols("gamma N", positive=True)
beta = sp.Function("beta")
S, I = sp.symbols("S I", positive=True)


def test_dI_dt_igual_gamma_Rt_menos_1_para_beta_arbitraria():
    R_t = beta(t) * S / (gamma * N)
    dI = beta(t) * S * I / N - gamma * I
    assert sp.simplify(dI - gamma * (R_t - 1) * I) == 0


def test_salto_de_H_en_un_corte():
    s, i, Ra, Rb = sp.symbols("s i R_a R_b", positive=True)
    Ha = s + i - sp.log(s) / Ra
    Hb = s + i - sp.log(s) / Rb  # mismas s, i: son continuas en el corte
    assert sp.simplify((Hb - Ha) - (-sp.log(s) * (1 / Rb - 1 / Ra))) == 0


def test_H_j_se_conserva_dentro_del_tramo():
    s, i, Rj = sp.symbols("s i R_j", positive=True)
    Hj = s + i - sp.log(s) / Rj
    ds, di = -Rj * gamma * s * i, Rj * gamma * s * i - gamma * i
    assert sp.simplify(sp.diff(Hj, s) * ds + sp.diff(Hj, i) * di) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
G = 1 / 7
CORTES = [0.0, 40.0, 90.0, 250.0]  # días
R0S = [2.5, 0.8, 1.6]               # R0 de cada tramo
S0, I0 = 0.9, 1e-5


def integrar_sir_tramos(cortes, R0s, gamma_, s0, i0, n_por_tramo=2001):
    """Encadena sir.integrar_sir. Devuelve (t, s, i, indice_de_tramo)."""
    ts, ss, ii, jj = [], [], [], []
    s_ini, i_ini = s0, i0
    for j, R0j in enumerate(R0s):
        tt = np.linspace(cortes[j], cortes[j + 1], n_por_tramo)
        s_, i_ = sir.integrar_sir(R0j, gamma_, s_ini, i_ini, tt)
        ts.append(tt); ss.append(s_); ii.append(i_); jj.append(np.full(tt.size, j))
        s_ini, i_ini = s_[-1], i_[-1]
    return ts, ss, ii, jj


def referencia_tramos(cortes, R0s, gamma_, s0, i0, ts):
    """Integrador independiente (DOP853 en variables s, i sin logaritmo)."""
    out, y = [], [s0, i0]
    for j, R0j in enumerate(R0s):
        f = lambda _t, y, b=R0j * gamma_: [-b * y[0] * y[1], b * y[0] * y[1] - gamma_ * y[1]]
        sol = solve_ivp(f, (cortes[j], cortes[j + 1]), y, t_eval=ts[j],
                        method="DOP853", rtol=1e-13, atol=1e-16)
        out.append(sol.y)
        y = sol.y[:, -1]
    return out


def test_tramos_de_sir_py_coinciden_con_referencia():
    ts, ss, ii, _ = integrar_sir_tramos(CORTES, R0S, G, S0, I0)
    ref = referencia_tramos(CORTES, R0S, G, S0, I0, ts)
    for s_, i_, (sr, ir) in zip(ss, ii, ref):
        np.testing.assert_allclose(s_, sr, atol=1e-9)
        np.testing.assert_allclose(i_, ir, rtol=1e-6, atol=1e-14)


def test_tasa_de_log_i_es_gamma_por_Rt_menos_1():
    ts, ss, ii, _ = integrar_sir_tramos(CORTES, R0S, G, S0, I0)
    for tt, s_, i_, R0j in zip(ts, ss, ii, R0S):
        dlogi = np.gradient(np.log(i_), tt, edge_order=2)
        R_t = R0j * s_
        interior = slice(5, -5)  # lejos de los cortes
        np.testing.assert_allclose(dlogi[interior], G * (R_t[interior] - 1), atol=1e-5)


def test_tramo_con_Rt_menor_que_uno_hace_bajar_I():
    ts, ss, ii, _ = integrar_sir_tramos(CORTES, R0S, G, S0, I0)
    assert np.all(R0S[1] * ss[1] < 1)
    assert np.all(np.diff(ii[1]) < 0)
    # y en el primer tramo, antes del corte, I estaba creciendo
    assert np.all(R0S[0] * ss[0] > 1) and ii[0][-1] > ii[0][0]


def test_H_por_tramo_y_su_salto():
    ts, ss, ii, _ = integrar_sir_tramos(CORTES, R0S, G, S0, I0)
    Hs = [s_ + i_ - np.log(s_) / R0j for s_, i_, R0j in zip(ss, ii, R0S)]
    for Hj in Hs:
        assert np.max(np.abs(Hj - Hj[0])) < 1e-8
    for j in range(len(R0S) - 1):
        s_corte = ss[j][-1]
        salto = -np.log(s_corte) * (1 / R0S[j + 1] - 1 / R0S[j])
        assert Hs[j + 1][0] - Hs[j][-1] == pytest.approx(salto, abs=1e-10)
        # R_t salta por beta_{j+1}/beta_j en el corte (s es continua)
        assert (R0S[j + 1] * ss[j + 1][0]) / (R0S[j] * ss[j][-1]) == pytest.approx(R0S[j + 1] / R0S[j])
