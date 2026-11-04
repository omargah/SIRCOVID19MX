"""Paso 2: verosimilitud y ajuste por ola (MLE, múltiples inicios)."""
import numpy as np
from scipy.stats import chi2

from sirmx.escenarios import SEMILLA, datos, escenario
from sirmx.modelo import media_casos
from sirmx.verosimilitud import ajustar_ola, nll, params_a_theta, theta_a_params


def test_reparametrizacion_identificable_es_exacta():
    for nombre in ("ola_simple", "subregistro", "cambio_beta"):
        p, T = escenario(nombre)
        q = theta_a_params(params_a_theta(p), p.D, p.N, p.d0, p.cambios)
        a, _, _ = media_casos(p, T)
        b, _, _ = media_casos(q, T)
        np.testing.assert_allclose(a, b, rtol=1e-9)


def test_valor_real_dentro_de_region_conjunta():
    """ℓ̂ ≥ ℓ(θ real) y 2(ℓ̂ − ℓ(θ real)) < χ²_p(0.99): el valor real está en la región conjunta."""
    rng = np.random.default_rng(SEMILLA)
    p, y, *_ = datos("ola_simple", rng)
    th = params_a_theta(p)
    a = ajustar_ola(y, D=p.D, N=p.N, rng=rng, calcular_cov=False)
    f_real = nll(th, y, p.D, p.N)
    assert -a.loglik <= f_real + 1e-9
    assert 2 * (f_real + a.loglik) < chi2.ppf(0.99, len(th))


def test_mle_sin_ruido_recupera_exacto():
    p, T = escenario("subregistro")
    mu, _, _ = media_casos(p, T)
    y = np.round(mu)  # datos "sin ruido": el MLE debe caer prácticamente en el valor real
    a = ajustar_ola(y, D=p.D, N=p.N, rng=np.random.default_rng(3), n_inicios=4, calcular_cov=False)
    tv = params_a_theta(p)
    np.testing.assert_allclose(a.theta[[0, 1, 2]], tv[[0, 1, 2]], atol=2e-3)
    np.testing.assert_allclose(a.theta[4:10], tv[4:10], atol=2e-3)


def test_multiples_inicios_convergen_al_mismo_optimo():
    rng = np.random.default_rng(SEMILLA)
    p, y, *_ = datos("cambio_beta", rng)
    a = ajustar_ola(y, D=p.D, N=p.N, cambios=p.cambios, rng=rng, calcular_cov=False)
    assert a.n_inicios == 8
    assert a.n_cerca_mejor >= 6, "multimodalidad: pocos inicios llegan al mejor óptimo"
    assert not a.en_cota
