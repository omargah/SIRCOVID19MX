"""(i) Casos = rho × incidencia (no prevalencia).

Afirmación
----------
1. Las nuevas infecciones por unidad de tiempo (incidencia) son el flujo
   S -> I:  -dS/dt = beta S I / N. Entre t_k y t_{k+1}:
       ∫ beta S I/N dt = S(t_k) - S(t_{k+1}).
   Casos esperados: mu_k = rho N [s(t_k) - s(t_{k+1})]  (src/sir.py).
2. La prevalencia I(t) NO es la incidencia: dI/dt = incidencia - gamma I.
   Usar rho × I como casos es un error de modelo:
   a) el pico de la incidencia ocurre ANTES que el de I: en el pico de I
      (beta s = gamma) se tiene d(beta s i)/dt = -beta^2 s i^2 < 0;
   b) ∫ I dt = (tamaño final)/gamma, así que sumar prevalencias diarias
      sobrestima el total por un factor D = 1/gamma (en días).

Supuesto que NO se verifica aquí (límite del modelo, no de la derivación):
la SSA fecha los casos por inicio de síntomas; mu_k usa la fecha de
infección. El desfase (incubación) no está en sir.py.
"""

import numpy as np
import pytest
import sympy as sp
from scipy.integrate import quad

from src import sir

pytestmark = pytest.mark.teoria

beta, gamma, R0 = sp.symbols("beta gamma R_0", positive=True)
s, i = sp.symbols("s i", positive=True)
ds = -beta * s * i
di = beta * s * i - gamma * i


def test_incidencia_es_menos_ds_dt():
    incidencia = beta * s * i
    assert sp.simplify(-ds - incidencia) == 0
    # Prevalencia = incidencia acumulada - recuperados: di = incidencia - gamma i.
    assert sp.simplify(di - (incidencia - gamma * i)) == 0


def test_pico_de_incidencia_precede_al_de_prevalencia():
    incidencia = beta * s * i
    d_inc = sp.diff(incidencia, s) * ds + sp.diff(incidencia, i) * di
    assert sp.simplify(d_inc - beta * s * i * (beta * s - gamma - beta * i)) == 0
    en_pico_de_i = sp.simplify(d_inc.subs(s, gamma / beta))
    assert sp.simplify(en_pico_de_i + beta**2 * (gamma / beta) * i**2) == 0
    assert en_pico_de_i.is_negative


def test_integral_de_la_prevalencia():
    """gamma ∫ i dt = r_inf - r_0 = s0 + i0 - s_inf (por conservación)."""
    s0, i0, s_inf = sp.symbols("s_0 i_0 s_inf", positive=True)
    integral_i = (s0 + i0 - s_inf) / gamma
    tamano_final = s0 + i0 - s_inf  # infecciones totales incl. i0
    assert sp.simplify(integral_i / tamano_final - 1 / gamma) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
R0_, G, S0, I0, RHO, N = 2.5, 1 / 7, 0.6, 1e-5, 0.1, 1e7


def test_incidencia_semanal_es_la_integral_del_flujo():
    """mu_k de sir.py vs rho N ∫_{t_k}^{t_k+7} beta s i dt por cuadratura."""
    mu = sir.incidencia_semanal(R0_, G, S0, I0, RHO, N, 30)
    tt = np.linspace(0.0, 210.0, 21001)
    s_, i_ = sir.integrar_sir(R0_, G, S0, I0, tt)
    flujo = lambda t: np.interp(t, tt, R0_ * G * s_ * i_)
    for k in (0, 5, 10, 15, 25):
        integral, _ = quad(flujo, 7 * k, 7 * (k + 1), limit=200)
        assert RHO * N * integral == pytest.approx(mu[k], rel=1e-5)


def test_prevalencia_no_reproduce_los_casos():
    mu = sir.incidencia_semanal(R0_, G, S0, I0, RHO, N, 30)
    tt = np.arange(0.0, 210.0 + 1e-9, 1.0)
    s_, i_ = sir.integrar_sir(R0_, G, S0, I0, tt)
    prev_semanal = RHO * N * i_[:-1].reshape(30, 7).sum(axis=1)  # suma de prevalencias diarias
    # (a) el pico diario de incidencia ocurre antes que el de prevalencia
    inc_diaria = -np.diff(s_)
    assert np.argmax(inc_diaria) < np.argmax(i_)
    # (b) la suma de prevalencias diarias sobrestima el total ~ D = 7 veces
    cociente = prev_semanal.sum() / mu.sum()
    assert cociente == pytest.approx(1 / G, rel=0.02)


# --------------------------------------------------------------------------
# DISCREPANCIA encontrada: cancelación en incidencia_semanal con i0 diminuto
# --------------------------------------------------------------------------
# sir.py calcula mu_k como diferencia de s, que es O(1) y tiene error
# absoluto ~RTOL*s ~ 6e-11. Cuando la incidencia semanal Δs es comparable
# (inicio de una ola con i0 muy pequeño), el error RELATIVO de mu_k es
# grande. Medido contra una referencia que integra la incidencia acumulada
# c(t) (dc/dt = beta s i, c(0) = 0, sin cancelación):
#     i0 = 1e-10 -> 5 %,  1e-8 -> 0.35 %,  1e-6 -> 4e-5,  1e-5 -> 2e-6.
# Con i0 = 1e-5 (valor sintético del proyecto) es despreciable. Puede
# importar si el optimizador explora i0 << 1e-8 (la verosimilitud se vuelve
# "rugosa" en esa región). Arreglo posible: integrar c(t) como tercera
# variable en vez de diferenciar s.

def _mu_referencia(R0_, g, s0, i0, n):
    from scipy.integrate import solve_ivp

    f = lambda _t, y: [-R0_ * g * y[0] * np.exp(y[1]), R0_ * g * y[0] - g,
                       R0_ * g * y[0] * np.exp(y[1])]
    tt = 7.0 * np.arange(n + 1)
    ref = solve_ivp(f, (0, tt[-1]), [s0, np.log(i0), 0.0], t_eval=tt,
                    method="DOP853", rtol=1e-13, atol=1e-20)
    return np.diff(ref.y[2])


def test_incidencia_precisa_con_i0_del_proyecto():
    mu = sir.incidencia_semanal(R0_, G, S0, I0, 1.0, 1.0, 30)
    assert np.max(np.abs(mu / _mu_referencia(R0_, G, S0, I0, 30) - 1)) < 1e-5


@pytest.mark.xfail(strict=True, reason=(
    "DISCREPANCIA: incidencia_semanal = s_k - s_{k+1} sufre cancelación cuando "
    "Δs ~ RTOL*s; con i0 = 1e-10 el error relativo de las primeras semanas es ~5 %."))
def test_incidencia_precisa_con_i0_diminuto():
    i0 = 1e-10
    mu = sir.incidencia_semanal(R0_, G, S0, i0, 1.0, 1.0, 30)
    assert np.max(np.abs(mu / _mu_referencia(R0_, G, S0, i0, 30) - 1)) < 1e-5
