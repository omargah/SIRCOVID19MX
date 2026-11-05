"""Recuperación sintética: estructura de una réplica (la corrida completa es
scripts/recuperacion_sintetica.py; aquí solo una combinación y malla chica)."""

import numpy as np
import pytest

from src import parametros, recuperacion as R, verosimilitud as V

P = parametros.cargar_parametros("sintetico")


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
                  combinaciones=[("poisson", "poisson")])
    a = r["ajustes"]["poisson|poisson"]
    assert a["Reff"] == pytest.approx(r["Reff_verdad"], rel=0.05)
    assert set(a["perfiles"]) == {"R0", "s0", "Reff"}
    assert a["perfiles"]["s0"]["clase"] == "cresta_plana"  # H1: s0 no se acota con casos solos
    assert np.isfinite(a["aic"]) and a["dispersion_pearson"] > 0


def test_ic_perfil_raiz_extremos_en_el_umbral():
    """En cada extremo cerrado del IC, lp = lmax - 1.92 (K02 p. 88), hasta la bisección."""
    v = {"R0": 3.0, "s0": 0.6, "i0": P["i0"], "rho": P["rho"], "k": P["k"]}
    g = 1 / 4.7
    d = R.simular(v, g, P["N"], 16, "poisson", np.random.default_rng(3))
    mle = V.ajustar(d, g, P["N"], {k: v[k] for k in ("R0", "s0", "i0", "rho")},
                    modelo="poisson", rng=np.random.default_rng(0))
    ic = V.ic_perfil_raiz("Reff", d, g, P["N"], mle, (0.5 * V.reff(v), 2 * V.reff(v)), modelo="poisson")
    assert ic["clase"] == "identificable" and ic["inf"] < V.reff(mle["theta"]) < ic["sup"]
    for b in (ic["inf"], ic["sup"]):
        r = V.ajustar(d, g, P["N"], mle["theta"], fijos={"Reff": b}, n_arranques=0, modelo="poisson")
        assert abs(r["logvero"] - (mle["logvero"] - V.UMBRAL_95)) < 0.1


def test_reanudar_descarta_linea_incompleta(tmp_path):
    """Una corrida cortada a media escritura deja una línea rota: se descarta y se repite esa réplica."""
    import json
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import recuperacion_sintetica as RS
    f = tmp_path / "casos.jsonl"
    f.write_text(json.dumps({"escenario_id": 0, "replica": 0}) + "\n"
                 + json.dumps({"escenario_id": 1, "replica": 0}) + "\n"
                 + '{"escenario_id": 2, "repl')
    assert RS.leer_hechas(f) == {(0, 0), (1, 0)}
    assert len(f.read_text().splitlines()) == 2
