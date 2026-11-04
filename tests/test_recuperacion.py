"""Recuperación sintética: estructura de una réplica (la corrida completa es
scripts/recuperacion_sintetica.py; aquí solo una combinación y malla chica)."""

import numpy as np
import pytest

from src import datos, recuperacion as R, verosimilitud as V

P = datos.cargar_parametros("sintetico")


def test_semanas_hasta_fin_termina_despues_del_pico():
    v = {"R0": 3.0, "s0": 1.0, "i0": P["i0"], "rho": P["rho"], "k": P["k"]}
    n = R.semanas_hasta_fin(v, 1 / 4.7, P["N"], 0.01)
    mu = V.media_casos(v, 1 / 4.7, P["N"], n)
    assert mu[-1] < 0.01 * mu.max() and mu[-2] >= 0.01 * mu.max()


def test_simulacion_reproducible():
    v = {"R0": 2.0, "s0": 0.6, "i0": P["i0"], "rho": P["rho"], "k": P["k"]}
    a = R.simular(v, 1 / 5.0, P["N"], 20, "nb", np.random.default_rng(7))
    b = R.simular(v, 1 / 5.0, P["N"], 20, "nb", np.random.default_rng(7))
    assert np.array_equal(a["casos"], b["casos"])


def test_replica_poisson_recupera_Reff_y_cresta_en_s0():
    r = R.replica({"R0": 3.0, "s0": 0.6, "D": 4.7}, P, semilla=11, con_sero=False,
                  n_puntos=5, combinaciones=[("poisson", "poisson")])
    a = r["ajustes"]["poisson|poisson"]
    assert a["Reff"] == pytest.approx(r["Reff_verdad"], rel=0.05)
    assert set(a["perfiles"]) == {"R0", "s0", "Reff"}
    assert a["perfiles"]["s0"]["clase"] == "cresta_plana"  # H1: s0 no se acota con casos solos
    assert np.isfinite(a["aic"]) and a["dispersion_pearson"] > 0
