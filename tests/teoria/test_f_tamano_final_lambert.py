"""(f) Tamaño final y solución con la función W de Lambert.

Afirmación
----------
1. De H (derivación c) evaluada en t = 0 y t -> inf (i_inf = 0):
       ln(s_inf / s0) = -R0 (s0 + i0 - s_inf).
2. Solución explícita:
       s_inf = -W0( -R0 s0 exp(-R0 (s0 + i0)) ) / R0,
   con la rama PRINCIPAL W0. El argumento está en (-1/e, 0), donde hay dos
   ramas reales; W_{-1} da la otra raíz (s > 1/R0), que no es física.
3. Caso clásico s0 = 1, i0 -> 0: z = 1 - s_inf cumple z = 1 - exp(-R0 z),
   z = 1 + W0(-R0 e^{-R0}) / R0.
"""

import numpy as np
import pytest
import sympy as sp
from scipy.special import lambertw

from src import sir
from firma_sir import integrar_sir_frac

pytestmark = pytest.mark.teoria

R0, s0, i0, s_inf = sp.symbols("R_0 s_0 i_0 s_inf", positive=True)
X = -R0 * s0 * sp.exp(-R0 * (s0 + i0))
W = sp.LambertW(X)


def test_relacion_implicita_sale_de_H():
    H = lambda s, i: s + i - sp.log(s) / R0
    lhs = sp.expand_log(H(s0, i0) - H(s_inf, 0), force=True)
    # H(s0,i0) = H(s_inf,0)  <=>  ln(s_inf/s0) + R0 (s0 + i0 - s_inf) = 0 (por R0)
    objetivo = (sp.log(s_inf) - sp.log(s0) + R0 * (s0 + i0 - s_inf)) / R0
    assert sp.simplify(lhs - objetivo) == 0


def test_lambert_W_resuelve_la_ecuacion_implicita():
    """Sustituimos s_inf = -W/R0 y usamos la definición W e^W = X
    (es decir, e^{-W} = W/X). SymPy no aplica sola esa identidad."""
    s_sol = -W / R0
    # Exponenciamos ambos lados de ln(s/s0) = -R0(s0+i0-s).
    lhs = s_sol / s0
    # exp(-R0(s0+i0) + R0 s_sol) = exp(-R0(s0+i0)) * exp(-W); escrito ya factorizado.
    assert sp.simplify(R0 * s_sol + W) == 0
    rhs = sp.exp(-R0 * (s0 + i0)) * (W / X)
    assert sp.simplify(lhs - rhs) == 0


def test_identidad_W_por_exp_W_es_la_definicion():
    x = sp.Rational(-1, 5)
    w = sp.LambertW(x)
    assert abs(sp.N(w * sp.exp(w) - x, 30)) < 1e-28


def test_caso_clasico_z():
    z = 1 + sp.LambertW(-R0 * sp.exp(-R0)) / R0
    lhs = z
    Wc = sp.LambertW(-R0 * sp.exp(-R0))
    # exp(-R0 z) = exp(-R0) exp(-Wc), y exp(-Wc) = Wc / (-R0 e^{-R0}).
    assert sp.simplify(-R0 * z - (-R0 - Wc)) == 0
    rhs = 1 - sp.exp(-R0) * Wc / (-R0 * sp.exp(-R0))
    assert sp.simplify(lhs - rhs) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
def s_inf_lambert(R0_, s0_, i0_, rama=0):
    x = -R0_ * s0_ * np.exp(-R0_ * (s0_ + i0_))
    return float(-lambertw(x, rama).real / R0_)


@pytest.mark.parametrize("R0_,s0_,i0_", [(2.5, 0.6, 1e-5), (1.3, 1.0 - 1e-6, 1e-6), (6.0, 0.8, 1e-3)])
def test_lambert_W0_coincide_con_sir_py(R0_, s0_, i0_):
    x = -R0_ * s0_ * np.exp(-R0_ * (s0_ + i0_))
    assert -1 / np.e < x < 0
    s, i = integrar_sir_frac(R0_, 1 / 7, s0_, i0_, [0.0, 5000.0])
    assert i[-1] < 1e-12
    assert abs(s[-1] - s_inf_lambert(R0_, s0_, i0_)) < 1e-8
    # La otra rama da una raíz que no es la física.
    otra = s_inf_lambert(R0_, s0_, i0_, rama=-1)
    assert otra > 1 / R0_ and abs(otra - s[-1]) > 1e-2


def test_caso_clasico_contra_sir_py():
    R0_ = 2.0
    z = 1 + float(lambertw(-R0_ * np.exp(-R0_)).real) / R0_
    s, _ = integrar_sir_frac(R0_, 1 / 7, 1.0 - 1e-9, 1e-9, [0.0, 5000.0])
    assert abs((1 - s[-1]) - z) < 1e-7  # i0 = 1e-9 sesga z en O(i0)
