"""Microdatos SINTÉTICOS con el formato de la DGE, solo para pruebas.

No contienen información real. Reproducen la estructura (columnas,
catálogos, '9999-99-99' para vivos, esquema antiguo con RESULTADO) y algunos
rasgos que la EDA debe detectar: efecto de día de la semana en el registro,
retraso inicio→ingreso, retraso de notificación (truncamiento al final) y
versiones sucesivas (instantáneas) del mismo universo de registros.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNAS_NUEVAS = [
    "FECHA_ACTUALIZACION", "ID_REGISTRO", "ORIGEN", "SECTOR", "ENTIDAD_UM", "SEXO",
    "ENTIDAD_NAC", "ENTIDAD_RES", "MUNICIPIO_RES", "TIPO_PACIENTE", "FECHA_INGRESO",
    "FECHA_SINTOMAS", "FECHA_DEF", "INTUBADO", "NEUMONIA", "EDAD", "NACIONALIDAD",
    "EMBARAZO", "HABLA_LENGUA_INDIG", "INDIGENA", "DIABETES", "EPOC", "ASMA",
    "INMUSUPR", "HIPERTENSION", "OTRA_COM", "CARDIOVASCULAR", "OBESIDAD",
    "RENAL_CRONICA", "TABAQUISMO", "OTRO_CASO", "TOMA_MUESTRA_LAB", "RESULTADO_LAB",
    "TOMA_MUESTRA_ANTIGENO", "RESULTADO_ANTIGENO", "CLASIFICACION_FINAL", "MIGRANTE",
    "PAIS_NACIONALIDAD", "PAIS_ORIGEN", "UCI",
]
COLUMNAS_ANTIGUAS = [
    "FECHA_ACTUALIZACION", "ID_REGISTRO", "ORIGEN", "SECTOR", "ENTIDAD_UM", "SEXO",
    "ENTIDAD_NAC", "ENTIDAD_RES", "MUNICIPIO_RES", "TIPO_PACIENTE", "FECHA_INGRESO",
    "FECHA_SINTOMAS", "FECHA_DEF", "INTUBADO", "NEUMONIA", "EDAD", "NACIONALIDAD",
    "EMBARAZO", "HABLA_LENGUA_INDIG", "DIABETES", "EPOC", "ASMA", "INMUSUPR",
    "HIPERTENSION", "OTRA_COM", "CARDIOVASCULAR", "OBESIDAD", "RENAL_CRONICA",
    "TABAQUISMO", "OTRO_CASO", "RESULTADO", "MIGRANTE", "PAIS_NACIONALIDAD",
    "PAIS_ORIGEN", "UCI",
]


def universo(inicio="2020-03-01", dias=300, seed=20200414, escala=60) -> pd.DataFrame:
    """Universo de registros con fecha en que 'aparecen' en la base."""
    rng = np.random.default_rng(seed)
    t = np.arange(dias)
    curva = escala * (np.exp(-((t - 90) / 30) ** 2) + 1.6 * np.exp(-((t - 220) / 25) ** 2)) + 5
    n_dia = rng.poisson(curva)
    fs = np.repeat(pd.date_range(inicio, periods=dias, freq="D").to_numpy(), n_dia)
    n = len(fs)
    ret_ingreso = rng.geometric(1 / 4.0, n) - 1
    fi = fs + ret_ingreso.astype("timedelta64[D]")
    # efecto de día de la semana: el domingo se registra menos; se corre al lunes
    dom = pd.DatetimeIndex(fi).weekday == 6
    mover = dom & (rng.random(n) < 0.5)
    fi = np.where(mover, fi + np.timedelta64(1, "D"), fi)
    ret_notif = rng.geometric(1 / 5.0, n) - 1
    aparece = fi + ret_notif.astype("timedelta64[D]")

    u = rng.random(n)
    clasif = np.select([u < 0.04, u < 0.06, u < 0.50, u < 0.55, u < 0.58, u < 0.70],
                       [1, 2, 3, 4, 5, 6], 7)
    hosp = rng.random(n) < np.where(np.isin(clasif, [1, 2, 3]), 0.18, 0.08)
    muere = hosp & (rng.random(n) < 0.35)
    fd = np.where(muere, fi + (rng.geometric(1 / 8.0, n)).astype("timedelta64[D]"),
                  np.datetime64("NaT", "ns"))
    res = rng.integers(1, 33, n)
    res[rng.random(n) < 0.004] = 99
    um = np.where(rng.random(n) < 0.03, rng.integers(1, 33, n), res)
    um[um == 99] = 9
    toma_lab = np.where(clasif == 3, rng.integers(1, 3, n), np.where(clasif == 1, 2, 1))
    toma_ag = np.where((clasif == 3) & (toma_lab == 2), 1, 2)
    return pd.DataFrame({
        "ID_REGISTRO": [f"z{seed % 997:03d}{i:07x}" for i in range(n)],
        "FECHA_SINTOMAS": fs, "FECHA_INGRESO": fi, "FECHA_DEF": fd, "APARECE": aparece,
        "CLASIFICACION_FINAL": clasif, "TIPO_PACIENTE": np.where(hosp, 2, 1),
        "UCI": np.where(hosp, np.where(rng.random(n) < 0.2, 1, 2), 97),
        "ENTIDAD_RES": res, "ENTIDAD_UM": um,
        "ORIGEN": np.where(rng.random(n) < 0.4, 1, 2),
        "TOMA_MUESTRA_LAB": toma_lab, "TOMA_MUESTRA_ANTIGENO": toma_ag,
        "EDAD": rng.integers(0, 95, n),
    })


def _fmt(s) -> pd.Series:
    s = pd.Series(pd.to_datetime(s))
    return s.dt.strftime("%Y-%m-%d").fillna("9999-99-99")


def instantanea(u: pd.DataFrame, corte: str, esquema: str = "nuevo") -> pd.DataFrame:
    corte_ts = pd.Timestamp(corte)
    v = u[u["APARECE"] <= corte_ts].copy()
    v.loc[v["FECHA_DEF"] > corte_ts, "FECHA_DEF"] = pd.NaT
    n = len(v)
    out = pd.DataFrame({c: "2" for c in COLUMNAS_NUEVAS}, index=v.index)
    out["FECHA_ACTUALIZACION"] = corte_ts.strftime("%Y-%m-%d")
    for c in ("ID_REGISTRO",):
        out[c] = v[c]
    for c in ("ORIGEN", "TIPO_PACIENTE", "UCI", "CLASIFICACION_FINAL",
              "TOMA_MUESTRA_LAB", "TOMA_MUESTRA_ANTIGENO", "EDAD"):
        out[c] = v[c].astype(str)
    out["ENTIDAD_RES"] = v["ENTIDAD_RES"].map(lambda x: f"{x:02d}")
    out["ENTIDAD_UM"] = v["ENTIDAD_UM"].map(lambda x: f"{x:02d}")
    out["ENTIDAD_NAC"] = out["ENTIDAD_RES"]
    out["MUNICIPIO_RES"] = "001"
    out["SECTOR"] = "12"
    for c in ("FECHA_SINTOMAS", "FECHA_INGRESO", "FECHA_DEF"):
        out[c] = _fmt(v[c]).to_numpy()
    cl = v["CLASIFICACION_FINAL"].to_numpy()
    out["RESULTADO_LAB"] = np.where(cl == 3, "1", np.where(cl == 7, "2", "97"))
    out["RESULTADO_ANTIGENO"] = "97"
    out["NACIONALIDAD"] = "1"
    out["PAIS_NACIONALIDAD"] = "México"
    out["PAIS_ORIGEN"] = "97"
    if esquema == "antiguo":
        out["RESULTADO"] = np.where(np.isin(cl, [1, 2, 3]), "1",
                                    np.where(cl == 7, "2", "3"))
        out = out[COLUMNAS_ANTIGUAS]
    assert len(out) == n
    return out.sort_values("ID_REGISTRO").reset_index(drop=True)


def escribir_zip(df: pd.DataFrame, ruta: Path, nombre_csv: str) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    zi = zipfile.ZipInfo(nombre_csv, date_time=(2020, 1, 1, 0, 0, 0))
    with zipfile.ZipFile(ruta, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(zi, buf.getvalue().encode("latin-1"))
    return ruta


def tablero(u: pd.DataFrame, corte: str, ruta: Path) -> Path:
    """CSV ancho con el formato del tablero CONAHCYT (cve_ent, poblacion, nombre, DD-MM-AAAA…)."""
    v = u[(u["APARECE"] <= pd.Timestamp(corte)) & u["CLASIFICACION_FINAL"].isin([1, 2, 3])
          & u["ENTIDAD_RES"].between(1, 32)]
    fechas = pd.date_range("2020-02-26", corte, freq="D")
    filas = []
    for ent in range(1, 33):
        cnt = v[v["ENTIDAD_RES"] == ent].groupby("FECHA_SINTOMAS").size().reindex(fechas, fill_value=0)
        filas.append([f"{ent:02d}", 4_000_000, f"ENTIDAD {ent:02d}", *cnt.tolist()])
    nac = np.sum([f[3:] for f in filas], axis=0).tolist()
    filas.append(["000", 126_014_024, "Nacional", *nac])
    cols = ["cve_ent", "poblacion", "nombre", *[d.strftime("%d-%m-%Y") for d in fechas]]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas, columns=cols).to_csv(ruta, index=False, lineterminator="\n")
    return ruta
