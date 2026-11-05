"""Verosimilitudes NB y Poisson, dispersión de Pearson, AIC/BIC y perfil de R_eff(0)."""

import numpy as np
import pytest

from src import datos, sir, verosimilitud as V

P = datos.cargar_parametros("sintetico")
VERDAD = {n: P[n] for n in V.PARAMETROS}


def test_pmf_suman_uno():
    y = np.arange(0, 400)
    assert np.exp(V.logpmf_poisson(y, 37.3)).sum() == pytest.approx(1.0, abs=1e-12)
    assert np.exp(V.logpmf_binneg(y, 37.3, 5.0)).sum() == pytest.approx(1.0, abs=1e-9)


def test_binneg_tiende_a_poisson():
    """k -> inf: BinNeg(mu, k) -> Poisson(mu) (K04, pp. 23 y 32)."""
    y = np.arange(0, 200)
    d = np.max(np.abs(V.logpmf_binneg(y, 50.0, 1e9) - V.logpmf_poisson(y, 50.0))[:120])
    assert d < 1e-5


def test_modelo_invalido_se_rechaza():
    with pytest.raises(ValueError):
        V.logvero_casos(VERDAD, np.ones(5), P["gamma"], P["N"], modelo="normal")


def test_dispersion_pearson_cerca_de_uno_bajo_el_modelo_correcto():
    rng = np.random.default_rng(3)
    mu = rng.uniform(50, 5000, size=4000)
    y_p = sir.simular_casos_poisson(mu, rng)
    y_nb = sir.simular_casos(mu, 20.0, rng)
    assert V.dispersion_pearson(y_p, mu, "poisson", 0) == pytest.approx(1.0, abs=0.06)
    assert V.dispersion_pearson(y_nb, mu, "nb", 0, k=20.0) == pytest.approx(1.0, abs=0.06)
    # Datos NB leídos como Poisson: sobredispersión clara (E[phi] = 1 + mu/k).
    assert V.dispersion_pearson(y_nb, mu, "poisson", 0) > 10


def test_aic_bic():
    assert V.aic(-100.0, 4) == 208.0
    assert V.bic(-100.0, 4, 30) == pytest.approx(4 * np.log(30) + 200.0)


def test_fijar_Reff_respeta_la_restriccion():
    rng = np.random.default_rng(4)
    mu = V.media_casos(VERDAD, P["gamma"], P["N"], P["n_semanas"])
    d = {"casos": sir.simular_casos_poisson(mu, rng)}
    r = V.ajustar(d, P["gamma"], P["N"], VERDAD, fijos={"Reff": 1.4}, n_arranques=0, modelo="poisson")
    assert V.reff(r["theta"]) == pytest.approx(1.4, rel=1e-12)
    assert "k" not in r["theta"] and r["n_libres"] == 3


def test_poisson_recupera_Reff_en_datos_poisson():
    """Recuperación de una réplica (la cobertura va en scripts/recuperacion_sintetica.py)."""
    rng = np.random.default_rng(5)
    mu = V.media_casos(VERDAD, P["gamma"], P["N"], P["n_semanas"])
    d = {"casos": sir.simular_casos_poisson(mu, rng)}
    inicio = {"R0": 4.0, "s0": 0.9, "i0": 3e-6, "rho": 0.3}
    mle = V.ajustar(d, P["gamma"], P["N"], inicio, modelo="poisson", rng=rng)
    assert V.reff(mle["theta"]) == pytest.approx(V.reff(VERDAD), rel=0.02)


def test_k_tiene_tope_y_no_desborda():
    """Con datos Poisson, la MLE de k de la BinNeg tiende a infinito: se topa en K_MAX."""
    assert V.de_libre("k", 1e6) == V.K_MAX
    assert V.de_libre("R0", 1e6) < float("inf")
    rng = np.random.default_rng(8)
    mu = V.media_casos(VERDAD, P["gamma"], P["N"], P["n_semanas"])
    d = {"casos": sir.simular_casos_poisson(mu, rng)}
    r = V.ajustar(d, P["gamma"], P["N"], VERDAD, n_arranques=0, modelo="nb")
    assert np.isfinite(r["logvero"]) and r["theta"]["k"] <= V.K_MAX
