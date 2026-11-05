"""Regla de olas (src/olas.py) sobre series sintéticas de forma conocida."""

import numpy as np
import pandas as pd
import pytest

from src import olas_provisional as olas

INICIO = "2020-02-23"


def _curva():
    t = np.arange(600)
    y = 20 + sum(a * np.exp(-0.5 * ((t - c) / s) ** 2)
                 for a, c, s in [(1000, 120, 25), (3000, 300, 30), (8000, 480, 25)])
    return pd.Series(y, index=pd.date_range(INICIO, periods=t.size))


def _tres_olas(semilla=0, ciclo_semanal=True):
    """Tres olas gaussianas: picos 1000, 3000 y 8000 casos/día en los días 120, 300 y 480.

    Valle 1 (día ~210): prominencia ~980 = 12 % del máximo global (8000).
    Valle 2 (día ~390): prominencia ~2980 = 37 %.
    Con 5 % y 10 % entran los dos; con 15 % solo el segundo.
    """
    t = np.arange(600)
    y = 20 + sum(a * np.exp(-0.5 * ((t - c) / s) ** 2)
                 for a, c, s in [(1000, 120, 25), (3000, 300, 30), (8000, 480, 25)])
    fechas = pd.date_range(INICIO, periods=t.size)
    if ciclo_semanal:  # domingos con menos registro, como en los datos reales
        y = y * np.where(fechas.day_of_week == 6, 0.6, 1.07)
    rng = np.random.default_rng(semilla)
    return pd.Series(rng.poisson(y).astype(float), index=fechas)


def test_media_movil_centrada():
    s = pd.Series(np.arange(14.0), index=pd.date_range(INICIO, periods=14))
    mm = olas.media_movil_centrada(s)
    assert mm.iloc[:3].isna().all() and mm.iloc[-3:].isna().all()
    assert mm.iloc[3] == pytest.approx(3.0)  # promedio de 0..6


def test_serie_con_huecos_se_rechaza():
    s = _tres_olas().drop(pd.Timestamp("2020-05-01"))
    with pytest.raises(ValueError, match="continua"):
        olas.media_movil_centrada(s)


def test_detecta_los_dos_valles_y_frontera_en_domingo():
    s = _tres_olas()
    fr = olas.detectar_fronteras(s)
    assert len(fr) == 2
    dias = (fr["minimo"] - pd.Timestamp(INICIO)).dt.days.to_numpy()
    # Cada mínimo cae entre los dos picos que separa y en el fondo del valle:
    # la curva sin ruido vale ahí a lo más 1.5 veces su mínimo en ese valle.
    sin_ruido = olas.media_movil_centrada(_curva())
    assert 120 < dias[0] < 300 and 300 < dias[1] < 480
    for d, (a, b) in zip(dias, [(120, 300), (300, 480)]):
        fondo = sin_ruido.iloc[a:b].min()
        assert sin_ruido.iloc[d] <= 1.5 * fondo
    assert (fr["frontera"].dt.day_name() == "Sunday").all()
    # La frontera es el domingo de la semana que contiene el mínimo.
    assert ((fr["minimo"] - fr["frontera"]).dt.days.between(0, 6)).all()
    assert fr["umbral"].iloc[0] == pytest.approx(0.10 * olas.media_movil_centrada(s).max())


def test_etiquetado_cubre_toda_la_serie_sin_huecos():
    s = _tres_olas()
    t = olas.etiquetar_olas(s)
    assert list(t["ola"]) == [1, 2, 3]
    assert t["inicio"].iloc[0] == s.index.min() and t["fin"].iloc[-1] == s.index.max()
    assert ((t["inicio"].iloc[1:].to_numpy() - t["fin"].iloc[:-1].to_numpy())
            == np.timedelta64(1, "D")).all()


def test_sensibilidad_mas_menos_5_puntos():
    largo, resumen, conteo = olas.sensibilidad_prominencia(_tres_olas())
    assert conteo == {0.05: 2, 0.1: 2, 0.15: 1}
    assert set(largo["prominencia_frac"]) == {0.05, 0.1, 0.15}
    # La frontera del valle 2 no se mueve; la del valle 1 desaparece con 15 %
    # (su vecina más cercana es la del valle 2, ~26 semanas después).
    assert resumen["corrimiento_semanas_0.05"].tolist() == [0.0, 0.0]
    assert resumen["corrimiento_semanas_0.15"].iloc[1] == 0.0
    assert abs(resumen["corrimiento_semanas_0.15"].iloc[0]) > 20


def test_separacion_minima_de_60_dias():
    """Dos valles a 40 días: solo queda el más profundo."""
    t = np.arange(400)
    y = 30 + sum(a * np.exp(-0.5 * ((t - c) / s) ** 2)
                 for a, c, s in [(2000, 80, 15), (1500, 150, 10), (2000, 220, 15), (3000, 330, 20)])
    s = pd.Series(y, index=pd.date_range(INICIO, periods=t.size))
    fr = olas.detectar_fronteras(s)
    assert (np.diff(fr["minimo"].to_numpy()) >= np.timedelta64(60, "D")).all()
    sin_regla = olas.detectar_fronteras(s, separacion_min_dias=1)
    assert len(sin_regla) > len(fr)
