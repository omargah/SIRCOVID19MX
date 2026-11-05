"""Paso 4: perfiles de verosimilitud de R0, S0/N y R_eff(0). ¿Aparece la cresta plana de H1?"""
import numpy as np
import pytest
from scipy.special import logit

from sirmx.escenarios import SEMILLA, datos
from sirmx.identificabilidad import (COTAS_NAT, ajustar_natural, intervalo_perfil, nll_natural,
                                     perfil)
from sirmx.verosimilitud import COTAS_BASE, ajustar_ola, nll

pytestmark = pytest.mark.usefixtures("paso3_aprobado")


@pytest.fixture(scope="module")
def caso():
    rng = np.random.default_rng(SEMILLA)
    p, y, *_ = datos("subregistro", rng)
    a = ajustar_ola(y, D=p.D, N=p.N, rng=rng)
    phi, ll_nat = ajustar_natural(y, p.D, p.N, a, rng)
    return p, y, a, phi, ll_nat, rng


def test_maximo_natural_igual_al_identificable(caso):
    p, y, a, phi, ll_nat, rng = caso
    assert abs(ll_nat - a.loglik) < 1e-4


def test_cresta_plana_en_R0(caso):
    p, y, a, phi, ll_nat, rng = caso
    reff, rs0 = np.exp(a.theta[0]), np.exp(a.theta[2])
    lo, hi = reff, reff / rs0                         # límites que imponen s0 ≤ 1 y ρ ≤ 1
    dentro = np.geomspace(lo * 1.05, hi * 0.95, 6)
    fuera = np.array([lo * 0.85, hi * 1.25])
    f = lambda ph: nll_natural(ph, y, p.D, p.N)
    ll_in = perfil(f, phi, 0, np.log(dentro), COTAS_NAT, rng)
    ll_out = perfil(f, phi, 0, np.log(fuera), COTAS_NAT, rng)
    assert np.max(a.loglik - ll_in) < 1e-3, "el perfil de R0 no es plano dentro de la cresta"
    assert np.all(a.loglik - ll_out > 1.92), "la cresta no está acotada por s0≤1, ρ≤1"
    # R0 abarca un factor ~1/(ρ·s0) ≈ 8: no identificable con casos solos
    assert hi / lo > 5 and lo * 0.85 < p.R0 < hi * 1.25


def test_cresta_plana_en_s0(caso):
    p, y, a, phi, ll_nat, rng = caso
    rs0 = np.exp(a.theta[2])
    s0s = np.array([rs0 * 1.1, 0.3, 0.6, 0.8, 0.95])
    f = lambda ph: nll_natural(ph, y, p.D, p.N)
    ll = perfil(f, phi, 1, logit(s0s), COTAS_NAT, rng)
    assert np.max(a.loglik - ll) < 1e-3
    ll_bajo = perfil(f, phi, 1, logit(np.array([rs0 * 0.7])), COTAS_NAT, rng)
    assert a.loglik - ll_bajo[0] > 1.92  # s0 < ρ·s0 exigiría ρ > 1


def test_R_eff0_si_es_identificable(caso):
    p, y, a, phi, ll_nat, rng = caso
    rejilla = np.linspace(1.95, 2.06, 23)
    ll = perfil(lambda th: nll(th, y, p.D, p.N), a.theta, 0, np.log(rejilla), COTAS_BASE, rng)
    lo, hi, abierto_lo, abierto_hi = intervalo_perfil(rejilla, ll)
    assert not abierto_lo and not abierto_hi, "IC de perfil no cerrado"
    assert lo <= p.Reff0 <= hi
    assert (hi - lo) / p.Reff0 < 0.05
    wlo, whi = np.exp(a.ic("log_Reff0"))
    assert abs(lo - wlo) < 0.1 * (hi - lo) and abs(hi - whi) < 0.1 * (hi - lo)
