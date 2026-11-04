"""La regla (2) se hace cumplir en código: el cargador rechaza parámetros sin fuente."""

import copy

import pytest
import yaml

from src import datos

REGLA = {"tipo": "regla", "regla": "valor de diseño"}


def _escribir(tmp_path, contenido):
    archivo = tmp_path / "p.yaml"
    archivo.write_text(yaml.safe_dump(contenido, allow_unicode=True), encoding="utf-8")
    return archivo


def _entrada(**cambios):
    base = {"valor": 1.0, "unidad": "1", "supuesto": False, "fuente": dict(REGLA)}
    base.update(cambios)
    return base


def _rechaza(tmp_path, entradas, mensaje=None):
    archivo = _escribir(tmp_path, {"s": entradas})
    with pytest.raises(datos.ParametroSinFuente, match=mensaje):
        datos.cargar_parametros("s", archivo, permitir_pendientes=True)


# --- El archivo real del repositorio --------------------------------------

def test_archivo_del_repo_es_valido():
    datos.cargar_entradas()


def test_sintetico_carga():
    p = datos.cargar_parametros("sintetico")
    assert p["gamma"] == pytest.approx(1 / 7)


def test_real_pendiente_se_rechaza():
    with pytest.raises(datos.ParametroSinFuente, match="pendientes"):
        datos.cargar_parametros("real")


def test_real_supuestos_entran_a_sensibilidad():
    entradas = datos.cargar_entradas()["real"]
    rangos = datos.rangos_sensibilidad("real")
    supuestos = {n for n, e in entradas.items() if e["supuesto"]}
    assert set(rangos) == supuestos
    # Desde 2026-11-04 D_ola3 y D_ola4 tienen fuente (G05, G06); D_ola1,
    # D_ola2 y D_ola5 siguen como supuestos (decisiones de Omar).
    assert {"D_ola1", "D_ola2", "D_ola5", "rho_ola2_5"} <= supuestos
    assert not entradas["D_ola4"]["supuesto"]


def test_real_D_un_solo_tipo_y_no_incubacion():
    entradas = datos.cargar_entradas()["real"]
    ds = {n: e for n, e in entradas.items() if n.startswith("D_")}
    assert set(ds) == {f"D_ola{i}" for i in range(1, 6)}
    assert {e["definicion"] for e in ds.values()} == {"intervalo_generacion"}
    assert "gamma" not in entradas


def test_real_N_tiene_anio():
    fuente = datos.cargar_entradas()["real"]["N"]["fuente"]
    assert fuente["tipo"] == "institucional" and isinstance(fuente["anio"], int)


# --- Sin fuente: rechazado -------------------------------------------------

def test_sin_fuente_se_rechaza(tmp_path):
    e = _entrada()
    del e["fuente"]
    _rechaza(tmp_path, {"x": e}, "fuente")


def test_sin_campo_supuesto_se_rechaza(tmp_path):
    e = _entrada()
    del e["supuesto"]
    _rechaza(tmp_path, {"x": e}, "supuesto")


def test_regla_vacia_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"x": _entrada(fuente={"tipo": "regla", "regla": "  "})}, "regla")


def test_tipo_de_fuente_desconocido_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"x": _entrada(fuente={"tipo": "wikipedia"})}, "tipo de fuente")


def test_doi_sin_pagina_se_rechaza(tmp_path):
    f = {"tipo": "doi", "clave": "G01", "doi": "10.7326/M20-0504"}
    _rechaza(tmp_path, {"x": _entrada(fuente=f)}, "página")


def test_doi_mal_formado_se_rechaza(tmp_path):
    f = {"tipo": "doi", "clave": "G01", "doi": "doi.org/M20-0504", "pagina": "1"}
    _rechaza(tmp_path, {"x": _entrada(fuente=f)}, "DOI")


def test_doi_con_clave_inexistente_se_rechaza(tmp_path):
    f = {"tipo": "doi", "clave": "Z99", "doi": "10.7326/M20-0504", "pagina": "1"}
    _rechaza(tmp_path, {"x": _entrada(fuente=f)}, "INDICE")


def test_doi_distinto_al_indice_se_rechaza(tmp_path):
    f = {"tipo": "doi", "clave": "G01", "doi": "10.1000/otro", "pagina": "1"}
    _rechaza(tmp_path, {"x": _entrada(fuente=f)}, "no coincide")


def test_doi_completo_se_acepta(tmp_path):
    f = {"tipo": "doi", "clave": "G01", "doi": "10.7326/M20-0504", "pagina": "p. 3"}
    archivo = _escribir(tmp_path, {"s": {"x": _entrada(fuente=f)}})
    assert datos.cargar_parametros("s", archivo) == {"x": 1.0}


def test_institucional_sin_anio_se_rechaza(tmp_path):
    f = {"tipo": "institucional", "institucion": "INEGI", "documento": "Censo", "ubicacion": "t1"}
    _rechaza(tmp_path, {"N": _entrada(fuente=f)}, "anio")


def test_regla_con_dependencia_inexistente_se_rechaza(tmp_path):
    f = {"tipo": "regla", "regla": "1 - sero", "depende_de": ["sero"]}
    _rechaza(tmp_path, {"s0": _entrada(fuente=f)}, "depende")


# --- Supuestos: aceptados solo con justificación y rango -------------------

def _supuesto(**cambios):
    base = {"valor": 0.3, "unidad": "1", "supuesto": True,
            "justificacion": "sin fuente todavía", "sensibilidad": {"min": 0.1, "max": 0.5}}
    base.update(cambios)
    return base


def test_supuesto_completo_se_acepta_y_va_a_sensibilidad(tmp_path):
    archivo = _escribir(tmp_path, {"s": {"rho": _supuesto(), "N": _entrada()}})
    assert datos.cargar_parametros("s", archivo)["rho"] == 0.3
    assert datos.rangos_sensibilidad("s", archivo) == {"rho": (0.1, 0.5)}


def test_supuesto_sin_justificacion_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"x": _supuesto(justificacion="")}, "justificacion")


def test_supuesto_sin_rango_se_rechaza(tmp_path):
    e = _supuesto()
    del e["sensibilidad"]
    _rechaza(tmp_path, {"x": e}, "sensibilidad")


def test_supuesto_fuera_de_rango_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"x": _supuesto(valor=0.9)}, "fuera")


# --- D: el mismo para estimar y simular; nunca incubación ------------------

def _D(definicion="intervalo_generacion", valor=5.0, estimador="intrinseco"):
    # `estimador` es obligatorio desde 2026-11-04 (D = GI intrínseco).
    return _entrada(valor=valor, unidad="dia", definicion=definicion, estimador=estimador)


def test_D_incubacion_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"D_ola1": _D("incubacion", 5.1)}, "incubación")


def test_D_definiciones_mezcladas_se_rechazan(tmp_path):
    _rechaza(tmp_path, {"D_ola1": _D("intervalo_generacion"),
                        "D_ola2": _D("periodo_infeccioso")}, "mezclan")


def test_D_con_gamma_aparte_se_rechaza(tmp_path):
    _rechaza(tmp_path, {"D_ola1": _D(), "gamma": _entrada(valor=1 / 3.0)}, "gamma")


def test_gamma_se_deriva_de_D(tmp_path):
    archivo = _escribir(tmp_path, {"s": {"D_ola1": _D(valor=5.0)}})
    p = datos.cargar_parametros("s", archivo)
    assert datos.gamma_ola(p, "ola1") == pytest.approx(0.2)


def test_rechaza_tambien_errores_en_otra_seccion(tmp_path):
    malo = copy.deepcopy({"a": {"x": _entrada()}, "b": {"y": _entrada(fuente=None)}})
    archivo = _escribir(tmp_path, malo)
    with pytest.raises(datos.ParametroSinFuente, match="b.y"):
        datos.cargar_parametros("a", archivo)


# --- D por variante y sensibilidad con fuente (2026-11-04) ---------------

def test_real_D_valores_y_fuentes():
    """Valores verificados contra los PDF: G02 p. 1, G05 p. 603, G06 p. 1."""
    e = datos.cargar_entradas()["real"]
    assert [e[f"D_ola{i}"]["valor"] for i in range(1, 6)] == [5.20, 5.20, 4.7, 6.84, 6.84]
    assert e["D_ola3"]["fuente"]["clave"] == "G05" and e["D_ola4"]["fuente"]["clave"] == "G06"
    # Ganyani (G02) no es intrínseco: solo puede ser supuesto.
    assert e["D_ola1"]["estimador"] == "realizado_bajo_contencion" and e["D_ola1"]["supuesto"]


def test_real_D_nunca_valores_prohibidos():
    """Ningún D base es la incubación (6.4), dos PCR negativas (13.4) ni el GI realizado (3.59)."""
    e = datos.cargar_entradas()["real"]
    for i in range(1, 6):
        assert e[f"D_ola{i}"]["valor"] not in (6.4, 13.4, 3.59)


def test_real_D_sensibilidad_CrI_mas_Byrne():
    """Cada D trae su CrI95 y el rango de Byrne (G04, 6.5-9.5), rotulados con fuente."""
    det = datos.rangos_sensibilidad_detalle("real")
    for i in range(1, 6):
        rangos = det[f"D_ola{i}"]
        assert any(r["tipo"] == "CrI95" for r in rangos)
        byrne = [r for r in rangos if r["clave"] == "G04"]
        assert len(byrne) == 1 and (byrne[0]["min"], byrne[0]["max"]) == (6.5, 9.5)
        assert all(r["tipo"] != "IC95" for r in rangos)  # son CrI, no IC


def test_D_no_intrinseco_con_fuente_se_rechaza(tmp_path):
    e = _D(estimador="realizado_bajo_contencion")
    _rechaza(tmp_path, {"D_ola1": e}, "intrínseco")


def test_D_sin_estimador_se_rechaza(tmp_path):
    e = _D()
    del e["estimador"]
    _rechaza(tmp_path, {"D_ola1": e}, "estimador")


def test_sensibilidad_lista_sin_fuente_se_rechaza(tmp_path):
    e = _entrada(supuesto=True, justificacion="x",
                 sensibilidad=[{"min": 0.1, "max": 0.5, "tipo": "CrI95", "pagina": "p. 1"}])
    del e["fuente"]
    _rechaza(tmp_path, {"x": e}, "clave")


def test_sensibilidad_lista_con_clave_inexistente_se_rechaza(tmp_path):
    e = _entrada(sensibilidad=[{"min": 0.1, "max": 5, "tipo": "CrI95", "clave": "ZZ99", "pagina": "p. 1"}])
    _rechaza(tmp_path, {"x": e}, "INDICE")


def test_sensibilidad_lista_envolvente_y_detalle(tmp_path):
    e = _entrada(valor=0.3, supuesto=True, justificacion="x", sensibilidad=[
        {"min": 0.1, "max": 0.4, "tipo": "CrI95", "clave": "G02", "pagina": "p. 1"},
        {"min": 0.35, "max": 0.9, "tipo": "rango", "clave": "G04", "pagina": "p. 1"}])
    del e["fuente"]
    archivo = _escribir(tmp_path, {"s": {"x": e}})
    assert datos.rangos_sensibilidad("s", archivo) == {"x": (0.1, 0.9)}
    assert [r["clave"] for r in datos.rangos_sensibilidad_detalle("s", archivo)["x"]] == ["G02", "G04"]
