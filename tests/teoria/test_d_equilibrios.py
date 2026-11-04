"""(d) Equilibrios y ausencia de equilibrio endémico.

Afirmación
----------
1. Los equilibrios del SIR (sin nacimientos ni pérdida de inmunidad) son
   exactamente la recta {I = 0} (cualquier S): un continuo de equilibrios
   libres de enfermedad.
2. No hay equilibrio con I > 0: di/dt = 0 con I > 0 exige S = gamma N/beta,
   pero entonces dS/dt = -gamma I != 0.
3. Linealizando en (s*, 0): autovalores {0, gamma (R0 s* - 1)}. La parte de
   la recta con s* < 1/R0 es (neutralmente) estable; con s* > 1/R0 es
   inestable. Toda ola termina en s_inf < 1/R0.
4. Control: si se agregan nacimientos/muertes (tasa mu, reponiendo
   susceptibles) sí aparece un equilibrio endémico cuando beta/(gamma+mu) > 1.
   La ausencia en (2) se debe a que el SIR de una ola no repone susceptibles.
"""

import numpy as np
import pytest
import sympy as sp

from src import sir

pytestmark = pytest.mark.teoria

beta, gamma, N, mu = sp.symbols("beta gamma N mu", positive=True)
S, I = sp.symbols("S I", real=True)

dS = -beta * S * I / N
dI = beta * S * I / N - gamma * I


def test_equilibrios_son_la_recta_I_igual_cero():
    sol = sp.solve([dS, dI], [S, I], dict=True)
    # SymPy devuelve {I: 0} (S libre); no hay ninguna solución con I != 0.
    assert all(sp.simplify(d[I]) == 0 for d in sol)
    assert any(S not in d for d in sol)  # S queda libre en al menos una


def test_no_hay_equilibrio_con_I_positivo():
    Ip = sp.symbols("I_p", positive=True)
    Sp = sp.symbols("S_p", positive=True)
    sol = sp.solve([dS.subs({S: Sp, I: Ip}), dI.subs({S: Sp, I: Ip})], [Sp, Ip], dict=True)
    assert sol == []


def test_autovalores_en_la_recta_de_equilibrios():
    s_est, R0 = sp.symbols("s_* R_0", positive=True)
    s, i = sp.symbols("s i")
    f = sp.Matrix([-R0 * gamma * s * i, R0 * gamma * s * i - gamma * i])
    J = f.jacobian([s, i]).subs({s: s_est, i: 0})
    autovalores = {sp.expand(ev) for ev in J.eigenvals()}
    assert autovalores == {0, sp.expand(gamma * (R0 * s_est - 1))}


def test_control_con_demografia_si_hay_endemico():
    """dS = mu N - beta S I/N - mu S,  dI = beta S I/N - (gamma+mu) I."""
    Sp, Ip = sp.symbols("S_p I_p", positive=True)
    eqs = [mu * N - beta * Sp * Ip / N - mu * Sp, beta * Sp * Ip / N - (gamma + mu) * Ip]
    sol = sp.solve(eqs, [Sp, Ip], dict=True)
    assert len(sol) == 1
    R0d = beta / (gamma + mu)
    assert sp.simplify(sol[0][Sp] - N / R0d) == 0
    assert sp.simplify(sol[0][Ip] - mu * N / beta * (R0d - 1)) == 0


# --------------------------------------------------------------------------
# Numérico contra src/sir.py
# --------------------------------------------------------------------------
@pytest.mark.parametrize("R0,s0,i0", [(2.5, 0.6, 1e-5), (4.0, 1.0, 1e-6), (1.8, 0.9, 0.05)])
def test_sir_py_termina_en_la_rama_estable(R0, s0, i0):
    tt = np.linspace(0.0, 3000.0, 3001)
    s, i = sir.integrar_sir(R0, 1 / 7, s0, i0, tt)
    assert i[-1] < 1e-12             # llega a la recta I = 0
    assert s[-1] < 1.0 / R0          # del lado estable
    assert abs(s[-1] - s[-500]) < 1e-12  # y ahí se queda


def test_sir_py_sin_brote_si_R0_s0_menor_que_uno():
    """Arrancando en la rama estable (R0 s0 < 1), I decrece desde t = 0."""
    tt = np.linspace(0.0, 200.0, 401)
    _, i = sir.integrar_sir(2.5, 1 / 7, 0.3, 1e-3, tt)
    assert np.all(np.diff(i) < 0)
