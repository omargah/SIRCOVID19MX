"""Paso 7: pronóstico en tiempo simulado a 1–4 semanas: WIS, cobertura, error del pico."""
import numpy as np
import pytest

from sirmx.escenarios import SEMILLA, datos
from sirmx.pronostico import NIVELES, cubre, evaluar, pronostico_persistencia, wis


def test_wis_coincide_con_suma_de_perdidas_cuantilicas():
    rng = np.random.default_rng(0)
    for _ in range(50):
        q = np.sort(rng.normal(100, 20, size=len(NIVELES)))
        y = rng.normal(100, 30)
        pinball = np.sum([(float(y < qi) - t) * (qi - y) for qi, t in zip(q, NIVELES)])
        assert abs(wis(y, q) - pinball / (11 + 0.5)) < 1e-9


def test_wis_valor_a_mano():
    niv = np.array([0.25, 0.5, 0.75])
    # K=1: α=0.5, l=8, m=10, u=12, y=15 → [0.5·5 + 0.25·(4 + 4·3)] / 1.5 = 6.5/1.5
    assert abs(wis(15.0, np.array([8.0, 10.0, 12.0]), niv) - 6.5 / 1.5) < 1e-12


def test_persistencia_mediana_es_ultimo_valor():
    y = np.arange(70, dtype=float)
    q, ultimo = pronostico_persistencia(y, np.random.default_rng(1))
    assert ultimo == y[-7:].sum()
    assert np.all(q[:, NIVELES.tolist().index(0.5)] == ultimo)


def test_cubre():
    q = np.linspace(0, 100, len(NIVELES))
    assert cubre(50, q, 0.95) and not cubre(-1, q, 0.95)


@pytest.mark.usefixtures("paso3_aprobado")
def test_ola_simple_modelo_supera_persistencia():
    rng = np.random.default_rng(SEMILLA)
    p, y, mu, *_ = datos("ola_simple", rng)
    ev = evaluar(y, mu, p.D, p.N, rng)
    r = ev.resumen()
    assert r["WIS_relativo"] < 1
    assert all(m < q for m, q in zip(r["WIS_modelo_por_h"], r["WIS_persistencia_por_h"]))
    assert r["cob95_modelo"] >= 0.80
    assert r["EAM_fecha_pico_modelo_dias"] < r["EAM_fecha_pico_persistencia_dias"]
    # el pronóstico solo usa datos hasta el origen: cambiar el futuro no cambia el pronóstico
    assert ev.origenes[0] == 21
