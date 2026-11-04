"""Paso 5: r con ventana fija, IC por perfil y bootstrap paramétrico, escenarios de D."""
import numpy as np
import pytest
from multiprocessing import get_context

from sirmx.crecimiento import D_ESCENARIOS, estimar_r, r_verdadero, ventana_fija
from sirmx.escenarios import ESCENARIOS_PASO3, SEMILLA, datos
from sirmx.verosimilitud import ajustar_ola

pytestmark = pytest.mark.usefixtures("paso3_aprobado")


def _k_ola(p, y, rng):
    a = ajustar_ola(y, D=p.D, N=p.N, cambios=p.cambios, rng=rng, n_inicios=3, calcular_cov=False)
    return float(np.exp(a.theta[3]))


def test_ventana_fija_no_depende_de_lo_posterior():
    rng = np.random.default_rng(SEMILLA)
    _, y, *_ = datos("subregistro", rng)
    a, b = ventana_fija(y)
    y2 = y.copy()
    y2[b:] = 0  # cambiar el futuro no mueve la ventana
    assert ventana_fija(y2) == (a, b) and b - a == 21


@pytest.mark.parametrize("nombre", ESCENARIOS_PASO3)
def test_r_semilla_fija(nombre):
    rng = np.random.default_rng(SEMILLA)
    p, y, mu, inc, S = datos(nombre, rng)
    e = estimar_r(y, rng, B=200, k_fijo=_k_ola(p, y, rng))
    rv = r_verdadero(p, S, e.ventana)
    assert e.ic_perfil[0] <= rv <= e.ic_perfil[1]
    assert e.ic_bootstrap[0] <= rv <= e.ic_bootstrap[1]
    ancho_p = e.ic_perfil[1] - e.ic_perfil[0]
    ancho_b = e.ic_bootstrap[1] - e.ic_bootstrap[0]
    assert 0.7 < ancho_b / ancho_p < 1.4


def _rep(s):
    rng = np.random.default_rng(1000 + s)
    p, y, mu, inc, S = datos("subregistro", rng)
    e = estimar_r(y, rng, B=0, k_fijo=_k_ola(p, y, rng))
    rv = r_verdadero(p, S, e.ventana)
    return e.ic_perfil[0] <= rv <= e.ic_perfil[1]


def test_cobertura_perfil_r():
    with get_context("spawn").Pool(4) as pool:
        cub = pool.map(_rep, range(120))
    assert 0.90 <= np.mean(cub) <= 0.99, np.mean(cub)


def test_escenarios_de_D():
    rng = np.random.default_rng(SEMILLA)
    p, y, mu, inc, S = datos("subregistro", rng)
    e = estimar_r(y, rng, B=200, k_fijo=_k_ola(p, y, rng))
    tabla = e.tabla_D()
    assert set(tabla) == set(D_ESCENARIOS)
    R = [tabla[D][0] for D in sorted(tabla)]
    assert R[0] < R[1] < R[2]  # R crece con D a r fijo
    # con el D verdadero (7) el IC de R cubre R_eff(0); con D = 5 o 10 lo excluye:
    # R depende de D, que los casos no informan (I3)
    _, lo7, hi7, _, _ = tabla[7.0]
    assert lo7 <= p.Reff0 <= hi7
    assert tabla[5.0][2] < p.Reff0 and tabla[10.0][1] > p.Reff0
