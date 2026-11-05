"""Paso 6: detección de puntos de cambio de β (fecha y tamaño), incluidos dos cambios cercanos."""
import numpy as np
import pytest

from sirmx.cambios import detectar_cambios
from sirmx.escenarios import SEMILLA, datos

pytestmark = pytest.mark.usefixtures("paso3_aprobado")


def _detectar(nombre):
    rng = np.random.default_rng(SEMILLA)
    p, y, *_ = datos(nombre, rng)
    return p, detectar_cambios(y, D=p.D, N=p.N, rng=rng)


def test_sin_cambio_no_detecta():
    p, r = _detectar("ola_simple")
    assert r.K == 0


def test_un_cambio_fecha_y_tamano():
    p, r = _detectar("cambio_beta")
    assert r.K == 1
    tau = r.mejor.cambios[0]
    assert abs(tau - p.cambios[0]) <= 3
    lo, hi = r.ic_tau(0)
    assert lo <= p.cambios[0] <= hi
    flo, fhi = r.ic_factor(0)
    assert flo <= np.exp(p.log_factores[0]) <= fhi


def test_dos_cambios_separados_15_dias():
    p, r = _detectar("dos_cambios_sep15")
    assert r.K == 2
    for j in range(2):
        assert abs(r.mejor.cambios[j] - p.cambios[j]) <= 3
        flo, fhi = r.ic_factor(j)
        assert flo <= np.exp(p.log_factores[j]) <= fhi


def test_dos_cambios_separados_10_dias_limite_de_resolucion():
    """Resultado registrado (C3): a 10 días los dos cambios de 0.7 no se distinguen por BIC
    de un solo cambio de ≈0.49. La búsqueda K=2 sí encuentra el par correcto; lo que falta es
    información, no búsqueda. El cambio único queda entre ambos."""
    p, r = _detectar("dos_cambios")
    a2 = r.ajustes[2]
    assert all(abs(a2.cambios[j] - p.cambios[j]) <= 1 for j in range(2))
    assert abs(r.bic[2] - r.bic[1]) < 2
    assert r.K == 1
    assert p.cambios[0] <= r.mejor.cambios[0] <= p.cambios[1]
    assert abs(np.exp(r.mejor.theta[10]) / 0.49 - 1) < 0.10
