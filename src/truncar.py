"""Truncamiento de las últimas semanas de cada corte histórico (decisión I3).

Por qué truncar
---------------
En cada versión de la base de la DGE, los últimos días todavía no tienen
todos sus casos: los casos de esas fechas se siguen registrando en
versiones posteriores (retraso de notificación). Ajustar el SIR con esos
días incompletos haría ver una caída que no existe.

Decisión I3 (Omar, 2026-11-03): NO se hace nowcasting. Se quitan los
últimos N días de cada corte antes de ajustar. Gostic et al. 2020
(clave M07; en Drive: fuentes/_sin_clave/) describe esta opción como "la
más simple": "drop estimates on the last few dates or flag them as
unreliable" (p. 13), y advierte que con retrasos largos o variables los
métodos simples no bastan "when aiming to infer the timing of changes in
Rt accurately" (p. 10). Por eso la fecha del punto de cambio de H5 puede
quedar corrida por el retraso (decisión I4: se declara, no se corrige).
Bastos 2019 (M23) y McGough 2020 (M24) son solo referencia del nowcasting
que NO se hace.

Unidades: la verosimilitud es SEMANAL, así que N está en semanas
completas. Si el N estimado de las versiones de la DGE sale en días, se
redondea HACIA ARRIBA a semanas (semanas_desde_dias) y se registra el valor
en días original.

N todavía NO se conoce: se estima en F4 comparando versiones sucesivas de
las bases históricas de la DGE (publicadas desde el 14 abr 2020), con un
procedimiento y un umbral de "estabilizado" escritos ANTES de calcularlo y
antes de ver cualquier ajuste del SIR. Este módulo solo aplica el N.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def semanas_desde_dias(n_dias):
    """Semanas completas que cubren n_dias, redondeando hacia arriba.

    Devuelve (n_semanas, n_dias) para que el valor original quede registrado.
    Ejemplos: 0 -> 0, 1..7 -> 1, 8 -> 2.
    """
    if isinstance(n_dias, bool) or not isinstance(n_dias, (int, np.integer)) or n_dias < 0:
        raise ValueError(f"n_dias debe ser un entero >= 0 (recibí {n_dias!r})")
    return math.ceil(n_dias / 7), int(n_dias)


def truncar_corte(serie, N):
    """Quita las últimas N semanas de una serie semanal de un corte.

    serie : serie SEMANAL de semanas completas, en orden cronológico
        (pd.Series, pd.DataFrame de src/semanas.agregar_semanal o arreglo).
        Si es un DataFrame con columna `completa`, se exige que todas las
        filas sean semanas completas: una semana parcial al final se debe
        quitar ANTES (src/semanas.solo_completas), porque no es lo mismo que
        una semana completa con retraso de notificación.
    N : entero >= 0, número de semanas completas a quitar.

    Devuelve una copia del mismo tipo con len(serie) - N elementos.
    Lanza ValueError si N no es un entero >= 0 o si no queda nada.
    """
    if isinstance(N, bool) or not isinstance(N, (int, np.integer)) or N < 0:
        raise ValueError(f"N debe ser un entero >= 0 de semanas (recibí {N!r})")
    if isinstance(serie, pd.DataFrame) and "completa" in serie.columns:
        if not serie["completa"].all():
            raise ValueError("La serie tiene semanas incompletas: quítalas antes de truncar")
    n = len(serie)
    if N >= n:
        raise ValueError(f"Truncar N={N} semanas no deja datos (la serie tiene {n})")
    if isinstance(serie, (pd.Series, pd.DataFrame)):
        if isinstance(serie.index, pd.DatetimeIndex) and not serie.index.is_monotonic_increasing:
            raise ValueError("La serie debe estar en orden cronológico")
        return serie.iloc[: n - N].copy()
    return np.asarray(serie)[: n - N].copy()
