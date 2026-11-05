"""Etiquetado de olas con una regla declarada ANTES de ajustar (F3/F4).

Regla provisional (acordada con Omar; no se hereda prominence=2500 ni las
fechas fijas de official_waves.csv del código viejo):

  1. Serie diaria de casos -> media móvil de 7 días CENTRADA (cada día
     promedia del día -3 al +3; los 3 primeros y los 3 últimos días quedan
     sin valor y no se usan).
  2. Candidatos a frontera = mínimos locales de esa media móvil.
  3. Un mínimo cuenta si su PROMINENCIA es >= 10 % del pico del periodo,
     donde "pico del periodo" = máximo GLOBAL de la media móvil en todo el
     periodo analizado (decisión de Omar, 2026-11-04).
  4. Separación mínima de 60 días entre mínimos aceptados.
  5. Frontera de la ola = DOMINGO de la semana epidemiológica que contiene
     el mínimo (decisión de Omar, 2026-11-04): la verosimilitud es semanal
     (src/semanas.py) y esa semana es la primera de la ola nueva.

Sensibilidad: la prominencia se mueve +-5 puntos porcentuales (5 % y 15 %).

Prominencia (definición topográfica de scipy.signal.find_peaks aplicada a
-media_movil): para un valle, la diferencia entre el valle y el MÁS BAJO de
los dos "bordes" que hay que subir para llegar a un punto todavía más bajo
a cada lado. Es una definición de software (SciPy), no de la bibliografía.
`distance` de find_peaks impone la separación mínima: si dos mínimos están a
menos de 60 días, se queda el más profundo.

Este módulo NO se ha aplicado a datos reales: la red de esta sesión no
alcanza a la DGE (ver HANDOFF.md). Las pruebas usan series sintéticas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from src.semanas import inicio_semana

VENTANA_DIAS = 7
SEPARACION_MIN_DIAS = 60
PROMINENCIA_BASE = 0.10
DELTA_SENSIBILIDAD = 0.05


def media_movil_centrada(serie_diaria, ventana=VENTANA_DIAS):
    """Media móvil centrada; NaN donde la ventana no está completa.

    Exige una serie diaria continua (sin días faltantes): con huecos, una
    ventana de 7 filas no serían 7 días.
    """
    s = pd.Series(serie_diaria, dtype=float)
    s.index = pd.DatetimeIndex(pd.to_datetime(s.index)).normalize()
    esperado = pd.date_range(s.index.min(), s.index.max(), freq="D")
    if len(s.index) != len(esperado) or not (s.index == esperado).all():
        raise ValueError("La serie diaria debe ser continua (un valor por día, sin huecos)")
    return s.rolling(ventana, center=True, min_periods=ventana).mean()


def detectar_fronteras(serie_diaria, prominencia_frac=PROMINENCIA_BASE,
                       separacion_min_dias=SEPARACION_MIN_DIAS):
    """Mínimos que cumplen la regla y la frontera semanal de cada uno.

    Devuelve un DataFrame (una fila por frontera, en orden) con:
        minimo      fecha del mínimo de la media móvil,
        valor_mm    valor de la media móvil en el mínimo,
        prominencia prominencia del valle (casos/día),
        umbral      prominencia_frac * máximo global,
        frontera    domingo de la semana epidemiológica que contiene el mínimo.
    """
    mm = media_movil_centrada(serie_diaria).dropna()
    if mm.empty:
        raise ValueError("La serie es más corta que la ventana de la media móvil")
    umbral = prominencia_frac * float(mm.max())
    idx, props = find_peaks(-mm.to_numpy(), prominence=umbral, distance=separacion_min_dias)
    minimos = mm.index[idx]
    return pd.DataFrame({
        "minimo": minimos,
        "valor_mm": mm.to_numpy()[idx],
        "prominencia": props["prominences"],
        "umbral": umbral,
        "frontera": inicio_semana(minimos) if len(minimos) else pd.DatetimeIndex([]),
    })


def etiquetar_olas(serie_diaria, prominencia_frac=PROMINENCIA_BASE,
                   separacion_min_dias=SEPARACION_MIN_DIAS):
    """Tabla de olas: número, inicio y fin (fechas incluidas).

    La ola 1 empieza el primer día de la serie y la última termina el último
    día; entre ellas, cada ola nueva empieza en una frontera (domingo) y la
    anterior termina el sábado previo.
    """
    s = pd.Series(serie_diaria, dtype=float)
    s.index = pd.DatetimeIndex(pd.to_datetime(s.index)).normalize()
    fr = detectar_fronteras(s, prominencia_frac, separacion_min_dias)
    inicios = [s.index.min(), *fr["frontera"]]
    fines = [f - pd.Timedelta(days=1) for f in fr["frontera"]] + [s.index.max()]
    return pd.DataFrame({"ola": np.arange(1, len(inicios) + 1), "inicio": inicios, "fin": fines})


def sensibilidad_prominencia(serie_diaria, base=PROMINENCIA_BASE, delta=DELTA_SENSIBILIDAD,
                             separacion_min_dias=SEPARACION_MIN_DIAS):
    """Fronteras con prominencia base - delta, base y base + delta.

    Devuelve un DataFrame largo (prominencia_frac, frontera, minimo, ...) y,
    para cada frontera de la regla base, la frontera más cercana con las
    otras dos prominencias y su corrimiento en semanas (NaN si no hay
    ninguna). No se elige el resultado "mejor": se reportan los tres.
    """
    tablas = {}
    for p in (base - delta, base, base + delta):
        t = detectar_fronteras(serie_diaria, p, separacion_min_dias)
        t.insert(0, "prominencia_frac", round(p, 10))
        tablas[round(p, 10)] = t
    largo = pd.concat(tablas.values(), ignore_index=True)
    base_t = tablas[round(base, 10)]
    filas = []
    for _, fila in base_t.iterrows():
        d = {"frontera_base": fila["frontera"]}
        for p, t in tablas.items():
            if p == round(base, 10):
                continue
            if t.empty:
                d[f"corrimiento_semanas_{p:g}"] = np.nan
                continue
            dif = (t["frontera"] - fila["frontera"]).dt.days.to_numpy()
            j = int(np.argmin(np.abs(dif)))
            d[f"corrimiento_semanas_{p:g}"] = dif[j] / 7.0
        filas.append(d)
    resumen = pd.DataFrame(filas)
    conteo = {p: len(t) for p, t in tablas.items()}
    return largo, resumen, conteo
