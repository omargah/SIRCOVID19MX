"""La regla (2) se hace cumplir en código."""

import pytest
import yaml

from src import datos


def test_sintetico_carga():
    p = datos.cargar_parametros("sintetico")
    assert p["gamma"] == pytest.approx(1 / 7)


def test_real_pendiente_se_rechaza():
    with pytest.raises(datos.ParametroSinFuente):
        datos.cargar_parametros("real")


def test_parametro_sin_fuente_se_rechaza(tmp_path):
    malo = {"sintetico": {"x": {"valor": 1.0, "unidad": "1", "fuente": {"tipo": "regla", "regla": ""}, "estado": "fijo"}}}
    archivo = tmp_path / "p.yaml"
    archivo.write_text(yaml.safe_dump(malo))
    with pytest.raises(datos.ParametroSinFuente):
        datos.cargar_parametros("sintetico", archivo)


def test_doi_sin_pagina_se_rechaza(tmp_path):
    malo = {"sintetico": {"x": {"valor": 1.0, "unidad": "1", "fuente": {"tipo": "doi", "doi": "10.1000/xyz"}, "estado": "fijo"}}}
    archivo = tmp_path / "p.yaml"
    archivo.write_text(yaml.safe_dump(malo))
    with pytest.raises(datos.ParametroSinFuente):
        datos.cargar_parametros("sintetico", archivo)
