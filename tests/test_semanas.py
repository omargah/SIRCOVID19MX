"""Semana epidemiológica domingo-sábado (src/semanas.py)."""

import numpy as np
import pandas as pd
import pytest

from src import semanas


def test_definicion_domingo_a_sabado():
    """Del domingo 22 al sábado 28 de marzo de 2020 es una sola semana."""
    inicio = pd.Timestamp("2020-03-22")
    assert inicio.day_name() == "Sunday"
    for d in pd.date_range("2020-03-22", "2020-03-28"):
        assert semanas.inicio_semana(d) == inicio
    assert semanas.inicio_semana("2020-03-29") == pd.Timestamp("2020-03-29")
    assert semanas.inicio_semana("2020-03-21") == pd.Timestamp("2020-03-15")


def test_23_y_24_de_marzo_misma_semana():
    """Las dos fechas candidatas de la medida (sin citar aún) caen en la misma semana."""
    assert semanas.misma_semana("2020-03-23", "2020-03-24")
    assert not semanas.misma_semana("2020-03-28", "2020-03-29")


def test_inicio_siempre_es_domingo():
    fechas = pd.date_range("2019-12-25", "2023-03-01")
    ini = semanas.inicio_semana(fechas)
    assert set(ini.day_name()) == {"Sunday"}
    assert ((fechas - ini).days >= 0).all() and ((fechas - ini).days <= 6).all()


def test_agregar_semanal_suma_y_marca_incompletas():
    # Del miércoles 18 de marzo al martes 31 de marzo de 2020: la primera y la
    # última semana quedan incompletas, la del 22 al 28 está completa.
    dias = pd.date_range("2020-03-18", "2020-03-31")
    s = pd.Series(np.arange(len(dias), dtype=float), index=dias)
    sem = semanas.agregar_semanal(s)
    assert list(sem.index) == [pd.Timestamp(x) for x in ("2020-03-15", "2020-03-22", "2020-03-29")]
    assert list(sem["n_dias"]) == [4, 7, 3]
    assert list(sem["completa"]) == [False, True, False]
    assert sem["casos"].sum() == s.sum()
    assert sem.loc["2020-03-22", "casos"] == s["2020-03-22":"2020-03-28"].sum()
    assert list(semanas.solo_completas(sem).index) == [pd.Timestamp("2020-03-22")]


def test_fechas_repetidas_se_rechazan():
    s = pd.Series([1.0, 2.0], index=pd.to_datetime(["2020-03-22", "2020-03-22"]))
    with pytest.raises(ValueError):
        semanas.agregar_semanal(s)


def test_semanas_entre():
    assert semanas.semanas_entre("2020-03-22", "2020-04-05") == 2
    assert semanas.semanas_entre("2020-03-24", "2020-03-28") == 0
