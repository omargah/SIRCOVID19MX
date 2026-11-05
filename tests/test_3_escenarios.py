"""Paso 3: tres escenarios sintéticos con parámetros conocidos. Si fallan, no se avanza.

Los módulos de prueba de los pasos 4–7 importan `PASO3_OK`; si este archivo falla,
esas pruebas se omiten (la puerta de I4)."""
import numpy as np
import pytest

from sirmx.escenarios import ESCENARIOS_PASO3
from sirmx.validacion import cobertura, criterios_paso3, tabla_escenario


@pytest.mark.parametrize("nombre", ESCENARIOS_PASO3)
def test_recuperacion_semilla_fija(nombre):
    filas, a, tv = tabla_escenario(nombre)
    fallas = criterios_paso3(filas, a, tv)
    assert not fallas, "\n".join(fallas)


@pytest.mark.parametrize("nombre", ESCENARIOS_PASO3)
def test_cobertura_ic95(nombre):
    cob = cobertura(nombre, n_rep=40)
    for clave in ("log_Reff0", "log_rho_s0"):
        assert 0.85 <= cob[clave] <= 1.0, f"{nombre}: cobertura {clave} = {cob[clave]:.2f}"


def test_subregistro_rho_solo_con_s0_conocido():
    filas, a, tv = tabla_escenario("subregistro")
    d = {f["parametro"]: f for f in filas}
    assert d["rho (s0 conocido)"]["cubre"] and d["R0 (s0 conocido)"]["cubre"]
    # sin s0, el estimador de "ρ" sería ρ·s0 = 0.12, no ρ = 0.15: sesgo de −20 %
    assert abs(d["rho*s0"]["estimado"] / 0.15 - 1) > 0.15
