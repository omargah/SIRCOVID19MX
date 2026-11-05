"""Pruebas de H1 sobre datos sintéticos (regla 3: primero sintético)."""

import numpy as np
import pytest

from src import datos, identificabilidad as ident, sir, verosimilitud as V

P = datos.cargar_parametros("sintetico")
VERDAD = {n: P[n] for n in V.PARAMETROS}


@pytest.mark.parametrize("c", [0.7, 2.0, 5.0])
def test_simetria_de_escala_es_exacta(c):
    """Parámetros transformados dan la misma incidencia (hasta error numérico)."""
    d = ident.diferencia_maxima_simetria(VERDAD, c, P["gamma"], P["N"], P["n_semanas"])
    # Medido: ~4e-9 del pico (error del integrador). Umbral 1e-7 deja margen
    # entre plataformas; una simetría falsa daría diferencias O(1).
    assert d < 1e-7


def test_serologia_rompe_la_simetria():
    """El aumento de seroprevalencia SÍ cambia bajo la transformación (se divide entre c)."""
    c = 1.5
    t2 = ident.transformar(VERDAD, c)
    a = sir.infectados_entre(VERDAD["R0"], P["gamma"], VERDAD["s0"], VERDAD["i0"], 0, 182)
    b = sir.infectados_entre(t2["R0"], P["gamma"], t2["s0"], t2["i0"], 0, 182)
    assert abs(b - a / c) < 1e-8


def _datos_sinteticos(con_sero, semilla):
    rng = np.random.default_rng(semilla)
    mu = sir.incidencia_semanal(VERDAD["R0"], P["gamma"], VERDAD["s0"], VERDAD["i0"],
                                VERDAD["rho"], P["N"], P["n_semanas"])
    d = {"casos": sir.simular_casos(mu, VERDAD["k"], rng)}
    if con_sero:
        d["sero"] = []
        for t_a, t_b, _, ee in P["sero"]:
            delta = sir.infectados_entre(VERDAD["R0"], P["gamma"], VERDAD["s0"], VERDAD["i0"], t_a, t_b)
            d["sero"].append((t_a, t_b, delta + rng.normal(0, ee), ee))
    return d


def test_casos_solos_recuperan_Reff_pero_no_R0():
    """Con casos solos: R_eff(0) dentro de 5 % de la verdad y perfil de R0 plano."""
    d = _datos_sinteticos(con_sero=False, semilla=1)
    mle = V.ajustar(d, P["gamma"], P["N"], VERDAD)
    reff = mle["theta"]["R0"] * mle["theta"]["s0"]
    assert abs(reff / (VERDAD["R0"] * VERDAD["s0"]) - 1) < 0.05
    # Perfil de R0 en puntos bien dentro del rango no identificable [1.5, 25]:
    valores = np.array([2.0, 4.0, 8.0])
    lp, _ = V.perfil("R0", valores, d, P["gamma"], P["N"], mle)
    assert np.max(mle["logvero"] - lp) < 0.05  # plano: muy por debajo de 1.92


def test_con_serologia_R0_queda_acotado():
    """Con serología, R0 = 8 queda fuera del intervalo de perfil del 95 %."""
    d = _datos_sinteticos(con_sero=True, semilla=1)
    mle = V.ajustar(d, P["gamma"], P["N"], VERDAD)
    assert abs(mle["theta"]["R0"] / VERDAD["R0"] - 1) < 0.25
    lp, _ = V.perfil("R0", np.array([8.0]), d, P["gamma"], P["N"], mle)
    assert mle["logvero"] - lp[0] > ident.UMBRAL_95


def test_intervalo_perfil_interpolacion():
    """Perfil cuadrático conocido: lp = -(x-3)^2/2 da IC 3 ± 1.96."""
    x = np.linspace(0, 6, 601)
    lp = -0.5 * (x - 3) ** 2
    inf, sup, aa, ab = ident.intervalo_perfil(x, lp, 0.0)
    assert abs(inf - (3 - 1.96)) < 1e-3 and abs(sup - (3 + 1.96)) < 1e-3
    assert not aa and not ab


def test_clasificar_perfil_cuadratico_es_identificable():
    x = np.linspace(0, 6, 61)
    c = ident.clasificar_perfil(x, -0.5 * (x - 3) ** 2, 0.0)
    assert c["clase"] == "identificable" and c["caida_max"] == pytest.approx(4.5)


def test_clasificar_perfil_plano_es_cresta():
    x = np.linspace(1, 25, 30)
    c = ident.clasificar_perfil(x, np.full(x.size, -10.0) - 1e-3 * (x - 1), -10.0)
    assert c["clase"] == "cresta_plana" and c["abierto_abajo"] and c["abierto_arriba"]


def test_clasificar_perfil_abierto_de_un_lado():
    """No identificabilidad práctica (Raue, Def. 1): acotado abajo, abierto arriba."""
    x = np.linspace(0, 10, 101)
    lp = -5.0 * np.exp(-x)  # sube y se aplana
    c = ident.clasificar_perfil(x, lp, 0.0)
    assert c["clase"] == "cresta_plana" and not c["abierto_abajo"] and c["abierto_arriba"]


def test_fraccion_rango_cubierta():
    assert ident.fraccion_rango_cubierta(1.0, 100.0, 1.0, 100.0) == pytest.approx(1.0)
    assert ident.fraccion_rango_cubierta(1.0, 10.0, 1.0, 100.0) == pytest.approx(0.5)
    assert ident.fraccion_rango_cubierta(200.0, 300.0, 1.0, 100.0) == 0.0
