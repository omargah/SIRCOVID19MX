"""Semana epidemiológica: UNA sola definición para todo el proyecto.

Definición (decisión de Omar, 2026-11-04)
-----------------------------------------
Una semana va de DOMINGO a SÁBADO (semana epidemiológica, la que usa la DGE
en sus boletines). Cada semana se identifica por la fecha de su domingo
(`inicio`). Así:

  * la verosimilitud semanal (src/verosimilitud.py) suma casos diarios por
    estas semanas;
  * truncar_corte (src/truncar.py) quita N semanas completas de esta clase;
  * el punto de cambio tau de H5 se compara por semana: la medida "cae" en
    la semana que la contiene.

Lo que este módulo NO hace: numerar las semanas dentro del año ("SE 13 de
2020"). La regla de numeración del SINAVE (qué semana es la 1 de cada año)
no está en ninguna fuente con PDF de la bibliografía; identificar la semana
por su domingo no depende de esa regla, así que no la necesitamos. Si hace
falta para comparar con boletines, se agrega con su fuente.

Ejemplo usado en los tests: el domingo 22 y el sábado 28 de marzo de 2020
delimitan una semana; el 23 (lunes) y el 24 (martes) caen en ella.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DIAS_POR_SEMANA = 7
# pandas (day_of_week): lunes = 0, ..., domingo = 6.


def inicio_semana(fechas):
    """Domingo de la semana epidemiológica (dom-sáb) de cada fecha.

    Para una fecha con día de la semana w (lunes = 0, domingo = 6), los días
    transcurridos desde el domingo anterior (o el mismo día, si es domingo)
    son (w + 1) mod 7. Restarlos da el domingo de inicio.
    Acepta una fecha suelta o una colección; devuelve el mismo tipo
    (Timestamp o DatetimeIndex).
    """
    escalar = np.ndim(fechas) == 0
    f = pd.DatetimeIndex(pd.to_datetime([fechas] if escalar else fechas)).normalize()
    dias_desde_domingo = (f.day_of_week + 1) % DIAS_POR_SEMANA
    inicio = f - pd.to_timedelta(dias_desde_domingo, unit="D")
    return inicio[0] if escalar else inicio


def agregar_semanal(serie_diaria):
    """Suma una serie diaria por semana epidemiológica.

    serie_diaria : pd.Series indexada por fecha (un valor por día; días
        faltantes simplemente no aparecen).
    Devuelve un DataFrame indexado por el domingo de cada semana con:
        casos   : suma de los días presentes,
        n_dias  : cuántos días de esa semana hay en la serie,
        completa: n_dias == 7.
    Solo las semanas completas entran a la verosimilitud: una semana parcial
    (al principio o al final del corte) tendría menos casos por construcción
    y sesgaría el ajuste.
    """
    s = pd.Series(serie_diaria)
    s.index = pd.DatetimeIndex(pd.to_datetime(s.index)).normalize()
    if s.index.has_duplicates:
        raise ValueError("La serie diaria tiene fechas repetidas")
    semana = inicio_semana(s.index)
    g = s.groupby(semana)
    out = pd.DataFrame({"casos": g.sum(), "n_dias": g.size()})
    out.index.name = "inicio"
    out["completa"] = out["n_dias"] == DIAS_POR_SEMANA
    return out


def solo_completas(semanal):
    """Filas de `agregar_semanal` con semana completa."""
    return semanal[semanal["completa"]]


def misma_semana(fecha_a, fecha_b):
    """¿Las dos fechas caen en la misma semana epidemiológica?"""
    return inicio_semana(fecha_a) == inicio_semana(fecha_b)


def semanas_entre(inicio_a, inicio_b):
    """Número de semanas de inicio_a a inicio_b (ambos domingos)."""
    a, b = inicio_semana(inicio_a), inicio_semana(inicio_b)
    return int((b - a).days // DIAS_POR_SEMANA)
