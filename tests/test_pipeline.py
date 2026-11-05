"""Pruebas del pipeline F3 con microdatos sintéticos en formato DGE."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import comparar_tablero, datos, eda  # noqa: E402
from tests import sintetico  # noqa: E402


def _modulo(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def universo():
    return sintetico.universo(dias=200, escala=40)


@pytest.fixture(scope="module")
def micro(universo, tmp_path_factory):
    d = tmp_path_factory.mktemp("micro")
    snap = sintetico.instantanea(universo, "2020-09-10")
    z = sintetico.escribir_zip(snap, d / "dge.zip", "200910COVID19MEXICO.csv")
    return z, snap


def test_registrar_y_verificar(tmp_path, micro):
    reg = _modulo(RAIZ / "scripts" / "registrar_fuente.py", "registrar_fuente")
    z, _ = micro
    registro = tmp_path / "fuentes.csv"
    assert reg.main([str(z), "--nivel", "DGE", "--url", "https://ejemplo/x.zip",
                     "--fecha-descarga", "2026-11-04", "--registro", str(registro)]) == 0
    filas = pd.read_csv(registro)
    assert len(filas) == 1
    assert filas.loc[0, "sha256"] == datos.sha256(z)
    assert filas.loc[0, "nivel"] == "DGE" and filas.loc[0, "fecha_descarga"] == "2026-11-04"
    assert reg.url_historico("datos_abiertos_covid19_14.04.2020.zip").endswith(
        "historicos/2020/04/datos_abiertos_covid19_14.04.2020.zip")


def test_serie_coincide_con_conteo_directo(micro, tmp_path):
    z, snap = micro
    m = datos.construir([z], tmp_path / "o", estricto=False, verbose=False)
    s = pd.read_csv(tmp_path / "o" / "serie_nacional_sintomas.csv", index_col="fecha")
    conf = snap[snap["CLASIFICACION_FINAL"].isin(["1", "2", "3"])
                & snap["ENTIDAD_RES"].astype(int).between(1, 32)]
    esperado = conf.groupby("FECHA_SINTOMAS").size()
    assert s["confirmados"].sum() == len(conf) == m["totales"]["confirmados"]
    assert (s.loc[esperado.index, "confirmados"] == esperado).all()
    h = pd.read_csv(tmp_path / "o" / "serie_nacional_hosp_def.csv", index_col="fecha")
    hosp = conf[conf["TIPO_PACIENTE"] == "2"].groupby("FECHA_INGRESO").size()
    assert (h.loc[hosp.index, "hospitalizados_confirmados"] == hosp).all()
    defs = conf[conf["FECHA_DEF"] != "9999-99-99"].groupby("FECHA_DEF").size()
    assert (h.loc[defs.index, "defunciones_confirmadas"] == defs).all()
    assert m["contadores"]["entidad_res_fuera_1_32"] > 0


def test_determinismo_independiente_de_chunksize(micro, tmp_path):
    z, _ = micro
    datos.construir([z], tmp_path / "a", chunksize=1_000, estricto=False, verbose=False)
    datos.construir([z], tmp_path / "b", chunksize=50_000, estricto=False, verbose=False)
    assert datos.hashes_directorio(tmp_path / "a") == datos.hashes_directorio(tmp_path / "b")
    assert datos.verificar_determinismo([z], 2_000, False) == 0


def test_esquema_antiguo(universo, tmp_path):
    snap = sintetico.instantanea(universo, "2020-07-14", esquema="antiguo")
    z = sintetico.escribir_zip(snap, tmp_path / "v.zip", "200714COVID19MEXICO.csv")
    m = datos.construir([z], tmp_path / "o", estricto=False, verbose=False)
    pos = snap[(snap["RESULTADO"] == "1") & snap["ENTIDAD_RES"].astype(int).between(1, 32)]
    assert m["totales"]["confirmados"] == len(pos)
    assert "RESULTADO (homologado)" in m["esquemas_detectados"]


def test_duplicados_entre_archivos(universo, tmp_path):
    a = sintetico.instantanea(universo, "2020-08-01")
    b = sintetico.instantanea(universo, "2020-09-01")
    za = sintetico.escribir_zip(a, tmp_path / "a.zip", "a.csv")
    zb = sintetico.escribir_zip(b, tmp_path / "b.zip", "b.csv")
    m = datos.construir([za, zb], tmp_path / "o", estricto=False, verbose=False)
    solo_b = datos.construir([zb], tmp_path / "ob", estricto=False, verbose=False)
    assert m["contadores"]["duplicados_id_descartados"] == len(a)
    assert m["totales"] == solo_b["totales"]
    assert m["orden_lectura"][0].endswith("b.zip")


def test_comparacion_tablero(universo, micro, tmp_path):
    z, _ = micro
    datos.construir([z], tmp_path / "o", estricto=False, verbose=False)
    serie = tmp_path / "o" / "serie_nacional_sintomas.csv"
    # tablero con el mismo corte → sin diferencias en el rango común
    t1 = sintetico.tablero(universo, "2020-09-10",
                           tmp_path / "Casos_Diarios_Estado_Nacional_Confirmados_20200910.csv")
    d, r = comparar_tablero.comparar(t1, serie, tmp_path / "o" / "manifiesto.json", estricto=False)
    h = {x["id"]: x for x in r["hallazgos"]}
    assert r["total_comun"]["dge"] == r["total_comun"]["tablero"]
    assert "+0 d" in h["D3"]["magnitud"] and "«confirmados»" in h["D4"]["causa"]
    # tablero de un corte anterior → la DGE tiene más casos al final (rezago)
    t2 = sintetico.tablero(universo, "2020-08-10",
                           tmp_path / "Casos_Diarios_Estado_Nacional_Confirmados_20200810.csv")
    d, r = comparar_tablero.comparar(t2, serie, tmp_path / "o" / "manifiesto.json", estricto=False)
    cola = d[(d["dias_antes_corte_tablero"] >= 0) & (d["dias_antes_corte_tablero"] < 14)]
    assert cola["diferencia"].sum() > 0
    assert "posterior" in r["hallazgos"][1]["causa"]
    comparar_tablero.escribir_nota(r, tmp_path / "nota.md", t2)
    texto = (tmp_path / "nota.md").read_text(encoding="utf-8")
    assert "Primaria — DGE" in texto and "Secundaria — tablero" in texto


def test_eda_con_historicos(universo, micro, tmp_path):
    z, _ = micro
    datos.construir([z], tmp_path / "o", estricto=False, verbose=False)
    for c in pd.date_range("2020-04-14", "2020-06-30", freq="7D"):
        zz = sintetico.escribir_zip(sintetico.instantanea(universo, str(c.date())),
                                    tmp_path / f"h{c:%Y%m%d}.zip", "x.csv")
        datos.construir([zz], tmp_path / "hist" / str(c.date()), estricto=False, verbose=False)
    eda.correr(tmp_path / "o", tmp_path / "docs" / "eda.md", tmp_path / "docs" / "figuras",
               tmp_path / "hist")
    texto = (tmp_path / "docs" / "eda.md").read_text(encoding="utf-8")
    for seccion in ("Día de la semana", "Retrasos", "Truncamiento", "Volumen de pruebas"):
        assert seccion.lower() in texto.lower()
    comp = pd.read_csv(tmp_path / "o" / "eda" / "completitud_historicos.csv")
    assert comp.loc[comp["d"] == 0, "mediana"].iloc[0] < comp.loc[comp["d"] == 28, "mediana"].iloc[0]


def test_inventario(universo, tmp_path, monkeypatch):
    inv = _modulo(RAIZ / "scripts" / "inventario_historicos.py", "inventario_historicos")
    hist = tmp_path / "historicos"
    for c, esq in (("2020-04-14", "antiguo"), ("2020-10-20", "nuevo")):
        ts = pd.Timestamp(c)
        sintetico.escribir_zip(sintetico.instantanea(universo, c, esq),
                               hist / f"datos_abiertos_covid19_{ts:%d.%m.%Y}.zip", "x.csv")
    monkeypatch.setattr(inv, "DIR_HIST", hist)
    monkeypatch.setattr(inv, "SALIDA_CSV", tmp_path / "inv.csv")
    monkeypatch.setattr(inv, "SALIDA_MD", tmp_path / "inv.md")
    monkeypatch.setattr(inv, "DIR_PROC_HIST", tmp_path / "nada")
    assert inv.main(["--hasta", "2023-06-27"]) == 0
    df = pd.read_csv(tmp_path / "inv.csv", dtype=str)
    assert (df["en_rejilla_semanal"] == "sí").sum() == 168
    pres = df[df["presente_local"] == "sí"]
    assert list(pres["version"]) == ["2020-04-14", "2020-10-20"]
    assert (pres["coincide_fecha"] == "sí").all()
    md = (tmp_path / "inv.md").read_text(encoding="utf-8")
    assert "CLASIFICACION_FINAL" in md and "RESULTADO" in md
