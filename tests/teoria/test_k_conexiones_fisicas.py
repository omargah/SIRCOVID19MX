"""(k) Conexiones físicas.

El texto del Cap. 2 todavía no está en el repositorio, así que "conexiones
físicas" se interpreta como estas tres afirmaciones (verificables):

k1. Cinética química / ley de acción de masas. El SIR es la red de reacciones
        S + I -> 2 I   (constante beta/N),      I -> R   (constante gamma).
    dX/dt = nu · v(X), con nu la matriz estequiométrica y v las velocidades de
    acción de masas, reproduce el SIR. La conservación de N (derivación b) es
    el vector (1,1,1) en el espacio nulo izquierdo de nu.

k2. Estructura hamiltoniana (de Poisson). Con H(s,i) = s + i - ln(s)/R0
    (derivación c) y la matriz antisimétrica
        J(s,i) = gamma R0 s i [[0, -1], [1, 0]],
    el campo es (ds/dt, di/dt) = J ∇H. H se conserva porque J es antisimétrica
    (∇H · J ∇H = 0), igual que la energía en mecánica.

k3. Umbral como transición de fase (bifurcación transcrítica). Con s0 = 1,
    i0 -> 0, el tamaño final z(R0) satisface z = 1 - exp(-R0 z) (la misma
    ecuación que la fracción de la componente gigante de una red de
    Erdős–Rényi con grado medio R0). z = 0 para R0 <= 1 y, con R0 = 1 + eps,
        z = 2 eps - (8/3) eps^2 + O(eps^3),
    es decir, exponente crítico de campo medio igual a 1.
"""

import numpy as np
import pytest
import sympy as sp
from scipy.special import lambertw

from src import sir

pytestmark = pytest.mark.teoria

beta, gamma, N, R0 = sp.symbols("beta gamma N R_0", positive=True)
S, I, R = sp.symbols("S I R", positive=True)


# --------------------------------------------------------------------------
# k1: acción de masas
# --------------------------------------------------------------------------
nu = sp.Matrix([[-1, 0], [1, -1], [0, 1]])          # columnas: reacciones; filas: S, I, R
v = sp.Matrix([beta / N * S * I, gamma * I])       # velocidades de acción de masas


def test_k1_red_de_reacciones_es_el_SIR():
    sir_rhs = sp.Matrix([-beta * S * I / N, beta * S * I / N - gamma * I, gamma * I])
    assert sp.simplify(nu * v - sir_rhs) == sp.zeros(3, 1)


def test_k1_conservacion_es_el_espacio_nulo_izquierdo():
    nulo = nu.T.nullspace()
    assert len(nulo) == 1
    assert sp.simplify(nulo[0] / nulo[0][0] - sp.Matrix([1, 1, 1])) == sp.zeros(3, 1)


# --------------------------------------------------------------------------
# k2: estructura de Poisson
# --------------------------------------------------------------------------
s, i = sp.symbols("s i", positive=True)
H = s + i - sp.log(s) / R0
J = gamma * R0 * s * i * sp.Matrix([[0, -1], [1, 0]])


def test_k2_campo_es_J_por_gradiente_de_H():
    gradH = sp.Matrix([sp.diff(H, s), sp.diff(H, i)])
    campo = sp.Matrix([-R0 * gamma * s * i, R0 * gamma * s * i - gamma * i])
    assert sp.simplify(J * gradH - campo) == sp.zeros(2, 1)
    assert sp.simplify(J + J.T) == sp.zeros(2, 2)
    assert sp.simplify((gradH.T * J * gradH)[0]) == 0


# --------------------------------------------------------------------------
# k3: umbral
# --------------------------------------------------------------------------
eps = sp.symbols("epsilon")


def test_k3_expansion_cerca_del_umbral():
    a1, a2 = sp.symbols("a1 a2")
    z = a1 * eps + a2 * eps**2
    residuo = sp.series(z - 1 + sp.exp(-(1 + eps) * z), eps, 0, 4).removeO()
    sols = sp.solve([residuo.coeff(eps, 2), residuo.coeff(eps, 3)], [a1, a2], dict=True)
    no_triviales = [d for d in sols if d[a1] != 0]
    assert no_triviales == [{a1: 2, a2: sp.Rational(-8, 3)}]


def test_k3_por_debajo_del_umbral_solo_z_igual_0():
    """Para R0 < 1, z = 1 - e^{-R0 z} solo tiene z = 0 en [0,1]:
    f(z) = 1 - e^{-R0 z} - z tiene f(0)=0 y f'(z) = R0 e^{-R0 z} - 1 < 0."""
    z = sp.symbols("z", nonnegative=True)
    R0s = sp.Rational(9, 10)
    fprima = sp.diff(1 - sp.exp(-R0s * z) - z, z)
    assert fprima.subs(z, 0) < 0 and sp.diff(fprima, z).is_negative


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
def test_k1_k2_sobre_trayectoria_de_sir_py():
    """J∇H y nu·v, evaluados sobre la trayectoria de sir.py, coinciden con
    la derivada numérica de esa trayectoria."""
    R0_, g = 2.5, 1 / 7
    tt = np.linspace(0.0, 200.0, 20001)
    s_, i_ = sir.integrar_sir(R0_, g, 0.6, 1e-5, tt)
    ds_num = np.gradient(s_, tt, edge_order=2)
    di_num = np.gradient(i_, tt, edge_order=2)
    pref = g * R0_ * s_ * i_
    dHds, dHdi = 1 - 1 / (R0_ * s_), np.ones_like(s_)
    np.testing.assert_allclose(-pref * dHdi, ds_num, atol=1e-8)
    np.testing.assert_allclose(pref * dHds, di_num, atol=1e-8)
    # nu·v en fracciones: dR/dt = gamma i y suma cero
    dr_num = np.gradient(1 - s_ - i_, tt, edge_order=2)
    np.testing.assert_allclose(dr_num, g * i_, atol=1e-8)


@pytest.mark.parametrize("ep", [0.05, 0.1])
def test_k3_tamano_final_cerca_del_umbral_en_sir_py(ep):
    R0_, i0 = 1 + ep, 1e-12
    s, i = sir.integrar_sir(R0_, 1 / 7, 1 - i0, i0, [0.0, 40000.0])
    assert i[-1] < 1e-14
    z_sir = 1 - s[-1]
    z_exacto = 1 + float(lambertw(-R0_ * np.exp(-R0_)).real) / R0_
    assert abs(z_sir - z_exacto) < 1e-8
    # La serie a 2.º orden tiene error O(eps^3)
    assert abs(z_sir - (2 * ep - 8 / 3 * ep**2)) < 3 * ep**3


def test_k3_debajo_del_umbral_no_hay_ola_en_sir_py():
    i0 = 1e-6
    s, _ = sir.integrar_sir(0.9, 1 / 7, 1 - i0, i0, [0.0, 4000.0])
    # Sin ola: solo se infecta una fracción O(i0) (≈ i0 R0/(1-R0) para s0≈1).
    assert 1 - s[-1] - i0 < 20 * i0
