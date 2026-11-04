"""Pruebas de src/sir.py. Cada prueba cita la ecuación que verifica.

Numeración de ecuaciones: la del docstring de src/sir.py ([E1]-[E4]).
Tolerancias: el integrador usa rtol = 1e-10; las pruebas piden errores
relativos de 1e-8 (100 veces más holgadas que rtol, porque el error global
acumula el error local de muchos pasos). Si fallan con estas tolerancias,
hay un error de modelo o de integración, no "ruido numérico".
"""

import numpy as np
import pytest

from src import sir

# Una ola tipo: N = 1e7, D = 7 días, R0 = 2.5, 60 % susceptible, 100 infecciosos.
N, D, R0, S0, I0 = 1e7, 7.0, 2.5, 6e6, 100.0
T = np.linspace(0.0, 400.0, 801)  # 400 días: la ola termina de sobra


@pytest.fixture(scope="module")
def ola():
    return sir.integrar_sir(R0, D, S0, I0, N, T)


def test_a_poblacion_se_conserva(ola):
    """(a) [E1] S + I + R = N para todo t."""
    S, I, R = ola
    assert np.max(np.abs(S + I + R - N)) / N < 1e-8


def test_b_positividad_y_simplex(ola):
    """(b) S >= 0, I >= 0, R >= 0 y el punto (S, I, R)/N se queda en el
    símplex {x_j >= 0, sum x_j = 1}. Además S es no creciente y R no
    decreciente (dS/dt = -beta S I/N <= 0, dR/dt = gamma I >= 0)."""
    S, I, R = ola
    assert S.min() >= 0 and I.min() >= 0 and R.min() >= 0
    assert np.all(np.diff(S) <= 1e-10 * N)
    assert np.all(np.diff(R) >= -1e-10 * N)
    x = np.vstack([S, I, R]) / N
    assert np.all(x >= 0) and np.allclose(x.sum(axis=0), 1.0, rtol=0, atol=1e-8)


def test_b_simplex_desde_condiciones_extremas():
    """(b) [E1] también en los bordes del símplex: casi todos susceptibles
    (S0 = N - 1) y casi nadie susceptible (S0 = 1 persona). En el segundo
    caso I decae ~400 días hasta ~1e-20 personas: es justo donde un
    integrador en I (y no en ln I) daba valores negativos."""
    for S0_, I0_ in [(N - 1.0, 1.0), (1.0, 1e3)]:
        S, I, R = sir.integrar_sir(R0, D, S0_, I0_, N, T)
        assert S.min() >= 0 and I.min() > 0 and R.min() >= 0
        assert abs((S + I + R)[-1] - N) / N < 1e-8


def test_c_cantidad_conservada(ola):
    """(c) [E2] H = S + I - (N/R0) ln S es constante.
    Tolerancia documentada: |H(t) - H(0)| / N < 1e-8 (H es O(N))."""
    S, I, _ = ola
    H = sir.cantidad_conservada(S, I, R0, N)
    assert np.max(np.abs(H - H[0])) / N < 1e-8


def test_d_tamano_final(ola):
    """(d) [E3] ln(S0/S_inf) = (R0/N)(S0 + I0 - S_inf).
    Usamos I0 grande (1 % de N) para que el término I0 importe."""
    I0_grande = 1e5
    S, I, _ = sir.integrar_sir(R0, D, S0, I0_grande, N, [0.0, 2000.0])
    assert I[-1] / N < 1e-12  # la ola terminó, I ≈ 0
    S_inf_exacto = sir.tamano_final(R0, S0, I0_grande, N)
    assert abs(S[-1] - S_inf_exacto) / N < 1e-8
    # Y la ecuación misma se cumple con el S_inf numérico:
    residuo = np.log(S0 / S[-1]) - (R0 / N) * (S0 + I0_grande - S[-1])
    assert abs(residuo) < 1e-7


def test_e_fase_exponencial():
    """(e) [E4] Mientras S ≈ S0, I crece con tasa r y R0*S0/N = 1 + r*D.
    I0 = 1e-3 personas (formal: el modelo es continuo) para que S casi no
    cambie en 20 días; r se mide como pendiente de ln I."""
    t = np.array([5.0, 25.0])
    _, I, _ = sir.integrar_sir(R0, D, S0, 1e-3, N, t)
    r = np.log(I[1] / I[0]) / (t[1] - t[0])
    assert abs(R0 * S0 / N - (1 + r * D)) < 1e-6
    # Y la función que usa el proyecto devuelve el R0 verdadero:
    assert sir.R0_desde_tasa_crecimiento(r, D, S0 / N) == pytest.approx(R0, rel=1e-6)


def test_f_no_usar_exp_rD():
    """(f) [E4] Regresión del error del código viejo.

    v0-anterior/, "Captura de pantalla 2025-08-08 ...pdf" (código y Tabla 4.1):
    para la Ola 4 (Ómicron BA.1) usaba D = 7, S0/N = 0.718 y
    R0 = exp(r*D)/(S0/N), y reportó R0 = 4.28. La relación correcta del SIR
    es R0 = (1 + r*D)/(S0/N) [E4], que da ~2.94.

    Prueba: simulamos un SIR con R0 = 2.94 y esos D y S0/N, medimos r, e
    invertimos con sir.R0_desde_tasa_crecimiento. Si alguien cambia esa
    función por exp(r*D)/s0, devuelve ~4.2 y esta prueba FALLA.
    """
    D_ba1, s0_ba1, R0_verdadero = 7.0, 0.718, 2.94
    t = np.array([5.0, 25.0])
    _, I, _ = sir.integrar_sir(R0_verdadero, D_ba1, s0_ba1 * N, 1e-3, N, t)
    r = np.log(I[1] / I[0]) / (t[1] - t[0])

    assert sir.R0_desde_tasa_crecimiento(r, D_ba1, s0_ba1) == pytest.approx(R0_verdadero, rel=1e-5)
    # La fórmula vieja da un número muy distinto (cerca del 4.28 reportado;
    # no idéntico porque aquel era la media de un Monte Carlo):
    R0_viejo = np.exp(r * D_ba1) / s0_ba1
    assert R0_viejo > 1.4 * R0_verdadero


def test_g_beta_por_tramos_rompe_H():
    """(g) [E2] solo vale con beta constante. Con R0 = 2.5 hasta el día 60 y
    R0 = 1.2 después:
      - H calculada con R0_1 se conserva antes del cambio y deja de
        conservarse después;
      - H calculada con R0_2 se conserva dentro del segundo tramo
        (cada tramo es un SIR con su propia H)."""
    tau = 60.0
    S, I, R = sir.integrar_sir_tramos([2.5, 1.2], [tau], D, S0, I0, N, T)
    antes, despues = T <= tau, T >= tau
    H1 = sir.cantidad_conservada(S, I, 2.5, N)
    H2 = sir.cantidad_conservada(S, I, 1.2, N)
    assert np.ptp(H1[antes]) / N < 1e-8   # se conserva en el tramo 1
    assert np.ptp(H1[despues]) / N > 1e-3  # deja de conservarse
    assert np.ptp(H2[despues]) / N < 1e-8  # el tramo 2 conserva su propia H
    assert abs((S + I + R)[-1] - N) / N < 1e-8  # [E1] sigue valiendo


def test_tramos_con_un_tramo_igual_a_beta_constante(ola):
    """Consistencia: integrar_sir_tramos con un solo R0 = integrar_sir."""
    S, I, R = sir.integrar_sir_tramos([R0], [], D, S0, I0, N, T)
    assert np.allclose(S, ola[0], rtol=0, atol=0)


def test_incidencia_suma_al_tamano_de_la_ola():
    """[E1] La suma de la incidencia semanal es rho * (S(0) - S(T))."""
    rho = 0.1
    mu = sir.incidencia_semanal(R0, 1 / D, S0 / N, I0 / N, rho, N, 30)
    S, _, _ = sir.integrar_sir(R0, D, S0, I0, N, [0.0, 210.0])
    assert abs(mu.sum() - rho * (S0 - S[-1])) / (rho * S0) < 1e-10


def test_binomial_negativa_media_y_varianza():
    """Modelo de observación: media mu y Var = mu + mu^2/k."""
    rng = np.random.default_rng(1)
    mu, k = 500.0, 20.0
    y = sir.simular_casos(np.full(200_000, mu), k, rng)
    assert abs(y.mean() - mu) / mu < 0.01
    assert abs(y.var() - (mu + mu**2 / k)) / (mu + mu**2 / k) < 0.03
