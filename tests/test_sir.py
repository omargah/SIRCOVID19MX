"""Pruebas del integrador SIR contra resultados exactos conocidos."""

import numpy as np
from scipy.optimize import brentq

from src import sir


def test_tamano_final_contra_ecuacion_implicita():
    """El tamaño final z = s0 - s_inf satisface la relación clásica
    (Kermack-McKendrick) log(s_inf/s0) = -R0 * (s0 + i0 - s_inf),
    que sale de dividir ds/dt entre dr/dt e integrar. Comparamos el
    resultado numérico a tiempo largo contra la raíz de esa ecuación."""
    R0, gamma, s0, i0 = 2.5, 1 / 7, 0.6, 1e-5
    s, i = sir.integrar_sir(R0, gamma, s0, i0, [0.0, 2000.0])
    f = lambda s_inf: np.log(s_inf / s0) + R0 * (s0 + i0 - s_inf)
    s_inf_exacto = brentq(f, 1e-9, 1 / R0)  # la raíz física está debajo de 1/R0
    assert i[-1] < 1e-12  # la ola terminó
    assert abs(s[-1] - s_inf_exacto) < 1e-8


def test_crecimiento_inicial_exponencial():
    """Al inicio s ≈ s0, así que i crece como exp(gamma*(R0*s0 - 1)*t)."""
    R0, gamma, s0, i0 = 2.5, 1 / 7, 0.6, 1e-9
    t = np.array([0.0, 10.0])
    _, i = sir.integrar_sir(R0, gamma, s0, i0, t)
    r = gamma * (R0 * s0 - 1)
    assert abs(np.log(i[1] / i0) / 10.0 - r) < 1e-6


def test_incidencia_suma_al_tamano_final():
    """La suma de incidencias semanales es rho*N*(s0 - s(T))."""
    R0, gamma, s0, i0, rho, N = 2.5, 1 / 7, 0.6, 1e-5, 0.1, 1e7
    mu = sir.incidencia_semanal(R0, gamma, s0, i0, rho, N, 30)
    assert abs(mu.sum() - rho * N * sir.infectados_entre(R0, gamma, s0, i0, 0.0, 210.0)) < 1e-6


def test_binomial_negativa_media_y_varianza():
    """La parametrización (mu, k) da media mu y varianza mu + mu^2/k."""
    rng = np.random.default_rng(1)
    mu, k = 500.0, 20.0
    y = sir.simular_casos(np.full(200_000, mu), k, rng)
    assert abs(y.mean() - mu) / mu < 0.01
    assert abs(y.var() - (mu + mu**2 / k)) / (mu + mu**2 / k) < 0.03
