"""Paso 8: dos corridas con la misma semilla dan lo mismo (bit a bit)."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]


def _corrida(semilla):
    from sirmx.crecimiento import estimar_r
    from sirmx.escenarios import datos
    from sirmx.identificabilidad import perfil
    from sirmx.pronostico import pronostico_persistencia, pronostico_sir
    from sirmx.verosimilitud import COTAS_BASE, ajustar_ola, nll
    rng = np.random.default_rng(semilla)
    p, y, mu, *_ = datos("cambio_beta", rng)
    a = ajustar_ola(y, D=p.D, N=p.N, cambios=p.cambios, rng=rng)
    e = estimar_r(y, rng, B=30, k_fijo=float(np.exp(a.theta[3])))
    pr = perfil(lambda th: nll(th, y, p.D, p.N, 0, p.cambios), a.theta, 0,
                a.theta[0] + np.array([-0.01, 0.0, 0.01]), COTAS_BASE + [(-3, 3)], rng, n_aleatorios=1)
    ys, mus, _ = pronostico_sir(y[:56], 84, p.D, p.N, 0, rng, n_tray=50, n_inicios=3)
    qp, _ = pronostico_persistencia(y[:56], rng)
    return {"y": y, "theta": a.theta, "cov": a.cov, "r": e.r, "rb": e.r_boot, "perfil": pr,
            "ys": ys, "qp": qp}


def test_misma_semilla_mismo_resultado():
    a, b = _corrida(123), _corrida(123)
    for k in a:
        assert np.array_equal(a[k], b[k]), k


def test_semilla_distinta_resultado_distinto():
    a, b = _corrida(123), _corrida(124)
    assert not np.array_equal(a["y"], b["y"])


def test_reproducible_entre_procesos():
    """Dos intérpretes nuevos (PYTHONHASHSEED distinto) dan la misma salida."""
    cod = ("import sys, json, numpy as np; sys.path.insert(0, %r);"
           "from tests.test_8_reproducibilidad import _corrida;"
           "r = _corrida(7); print(json.dumps({k: np.asarray(v).tolist() for k, v in r.items()}))"
           % str(RAIZ))
    salidas = []
    for hs in ("1", "2"):
        env = {"PYTHONHASHSEED": hs, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
               "PATH": "/usr/bin:/bin"}
        out = subprocess.run([sys.executable, "-c", cod], capture_output=True, text=True,
                             env=env, cwd=RAIZ, check=True)
        salidas.append(out.stdout)
    assert salidas[0] == salidas[1] and json.loads(salidas[0])
