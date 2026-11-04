"""Pruebas de la regla de olas (python3 -m pytest tests/ o python3 tests/test_olas.py)."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import olas  # noqa: E402


def _serie(niveles_log):
    """Serie diaria suave que interpola log-incidencias en nodos cada 60 días."""
    x = np.arange(60 * (len(niveles_log) - 1) + 1)
    z = np.interp(x, x[::60], niveles_log)
    idx = pd.date_range("2020-03-01", periods=len(x), freq="D")
    return pd.Series(np.expm1(z), index=idx)


def test_prominencia_relativa_invariante_de_escala():
    # pico/valle = e^1.0 ≈ 2.72 > 2 en ambas series, aunque una sea 100x mayor
    a = _serie([0, 5, 4, 5.2, 0])
    b = _serie([0, 5 + math.log(100), 4 + math.log(100), 5.2 + math.log(100), 0])
    assert len(olas.delimitar(a, 2.0, 1).picos) == 2
    assert len(olas.delimitar(b, 2.0, 1).picos) == 2


def test_valle_somero_no_separa():
    # pico/valle = e^0.5 ≈ 1.65 < 2: una sola ola; con rho=1.5 sí se separan
    y = _serie([0, 5, 4.5, 5.2, 0])
    assert len(olas.delimitar(y, 2.0, 1).picos) == 1
    r = olas.delimitar(y, 1.5, 1)
    assert len(r.picos) == 2
    assert r.fronteras == [y.index[120]]


def test_prominencia_coincide_con_scipy():
    try:
        from scipy.signal import find_peaks, peak_prominences
    except ImportError:
        return
    rng = np.random.default_rng(0)
    z = np.cumsum(rng.normal(size=600))
    picos = olas.maximos_locales(z)
    ref, _ = find_peaks(z)
    assert set(picos) == set(ref)
    p_ref = peak_prominences(z, ref)[0]
    p = [olas.prominencia(z, i) for i in ref]
    assert np.allclose(p, p_ref)


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("ok", nombre)
