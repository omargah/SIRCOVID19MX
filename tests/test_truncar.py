"""truncar_corte (decisión I3): quitar las últimas N semanas completas."""

import numpy as np
import pandas as pd
import pytest

from src import semanas
from src.truncar import semanas_desde_dias, truncar_corte


def _semanal(n):
    dias = pd.date_range("2020-03-22", periods=7 * n)
    return semanas.agregar_semanal(pd.Series(1.0, index=dias))


def test_N_cero_no_cambia_nada():
    s = _semanal(5)
    t = truncar_corte(s, 0)
    pd.testing.assert_frame_equal(t, s)
    assert t is not s  # copia, no la misma tabla


def test_quita_exactamente_las_ultimas_N():
    s = _semanal(6)
    t = truncar_corte(s, 2)
    assert len(t) == 4 and list(t.index) == list(s.index[:4])
    a = np.arange(10)
    assert list(truncar_corte(a, 3)) == list(range(7))


@pytest.mark.parametrize("N", [-1, 1.5, "2", True])
def test_N_invalido_se_rechaza(N):
    with pytest.raises(ValueError):
        truncar_corte(np.arange(5), N)


def test_no_puede_quedar_vacia():
    with pytest.raises(ValueError):
        truncar_corte(np.arange(3), 3)


def test_semana_incompleta_se_rechaza():
    dias = pd.date_range("2020-03-22", periods=10)  # 1 semana completa + 3 días
    with pytest.raises(ValueError, match="incompletas"):
        truncar_corte(semanas.agregar_semanal(pd.Series(1.0, index=dias)), 0)


def test_dias_a_semanas_hacia_arriba():
    assert [semanas_desde_dias(d)[0] for d in (0, 1, 6, 7, 8, 14, 15)] == [0, 1, 1, 1, 2, 2, 3]
    assert semanas_desde_dias(9) == (2, 9)  # se registra el valor original en días
    with pytest.raises(ValueError):
        semanas_desde_dias(-1)
