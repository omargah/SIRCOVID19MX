"""Paso 1: modelo de observación casos = ρ × incidencia, BinNeg y día de semana."""
import numpy as np
import pytest
from scipy.optimize import brentq
from scipy.stats import nbinom

from sirmx.modelo import (ParamsOla, efecto_semana, logpmf_binneg, media_casos,
                          muestra_binneg, sir_incidencia, _sir_rk4)


def test_logpmf_coincide_con_scipy():
    y = np.arange(0, 400)
    mu, k = 57.3, 4.2
    p = k / (k + mu)
    np.testing.assert_allclose(logpmf_binneg(y, mu, k), nbinom.logpmf(y, k, p), rtol=1e-10, atol=1e-10)


def test_muestreo_binneg_media_y_varianza():
    rng = np.random.default_rng(1)
    mu, k = 200.0, 15.0
    x = muestra_binneg(rng, np.full(200_000, mu), k)
    assert abs(x.mean() / mu - 1) < 0.005
    assert abs(x.var() / (mu + mu ** 2 / k) - 1) < 0.02


def test_efecto_semana_suma_cero():
    lw = efecto_semana(np.array([0.1, -0.2, 0.3, 0.0, 0.05, -0.1]))
    assert len(lw) == 7 and abs(lw.sum()) < 1e-15


def test_tamano_final_coincide_con_ecuacion_trascendente():
    # SIR: z = 1 − exp(−R0 z) para s0 = 1, i0 → 0
    R0, T = 2.0, 400
    inc, S, I = sir_incidencia(np.full(T, R0 / 7), 1 / 7, 1 - 1e-8, 1e-8)
    z = brentq(lambda z: z - 1 + np.exp(-R0 * z), 1e-6, 1)
    assert abs(inc.sum() - z) < 1e-5
    assert I[-1] < 1e-8


def test_rk4_compilado_identico_a_python():
    beta = np.r_[np.full(50, 0.35), np.full(150, 0.2)]
    S1, I1 = _sir_rk4(beta, 1 / 7, 0.8, 1e-5, 4)
    _, S2, I2 = sir_incidencia(beta, 1 / 7, 0.8, 1e-5)
    assert np.array_equal(S1, S2) and np.array_equal(I1, I2)


def test_media_es_rho_por_incidencia_por_semana():
    lw = efecto_semana(np.array([0.2, 0.1, 0.0, 0.0, -0.1, -0.3]))
    p = ParamsOla(R0=2.2, s0=0.9, rho=0.25, i0=1e-5, k=10, log_w=lw, d0=3)
    mu, inc, _ = media_casos(p, 150)
    dow = (np.arange(150) + 3) % 7
    np.testing.assert_allclose(mu, 0.25 * inc * np.exp(lw[dow]), rtol=1e-12)
    # sin efecto de semana, el total semanal es ρ × infecciones de la semana
    p0 = ParamsOla(R0=2.2, s0=0.9, rho=0.25, i0=1e-5, k=10)
    mu0, inc0, _ = media_casos(p0, 150)
    np.testing.assert_allclose(mu0.sum(), 0.25 * inc0.sum(), rtol=1e-12)


def test_beta_por_tramos():
    p = ParamsOla(R0=2.5, s0=1, rho=1, i0=1e-5, k=10, cambios=(40,), log_factores=(np.log(0.6),))
    mu_a, _, _ = media_casos(p, 40)
    p_sin = ParamsOla(R0=2.5, s0=1, rho=1, i0=1e-5, k=10)
    mu_b, _, _ = media_casos(p_sin, 40)
    np.testing.assert_array_equal(mu_a, mu_b)  # antes de τ no cambia nada
    mu_c, _, _ = media_casos(p, 120)
    mu_d, _, _ = media_casos(p_sin, 120)
    assert mu_c[60] < mu_d[60]
