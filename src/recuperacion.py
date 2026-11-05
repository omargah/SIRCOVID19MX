"""Recuperación de parámetros conocidos en datos sintéticos (regla 3, F4).

Qué hace una réplica
--------------------
Para un escenario (R0, s0, D) y una semilla:
  1. Calcula la incidencia esperada mu_k sin ruido y la longitud de la serie
     (semanas_hasta_fin: primera semana después del pico con mu < 1 % del
     pico; decisión de Omar 2026-11-04).
  2. Simula DOS series de casos con la misma mu: una con ruido BinNeg(k) y
     otra con ruido Poisson (decisión I2: comparar los dos modelos).
  3. Ajusta cada serie con las DOS verosimilitudes (NB y Poisson): 4
     combinaciones ruido x modelo.
  4. En cada combinación: MLE, IC95 por perfil de R0, s0 y R_eff(0)
     buscando los extremos (umbral 1.92, Raue 2009 J01 p. 1924, ec. 8;
     Venzon y Moolgavkar 1988 K02 p. 88), clase del perfil (identificable /
     cresta_plana), AIC, BIC y dispersión de Pearson.
  5. Opcionalmente agrega una encuesta serológica (escenario "casos_sero").

Los resúmenes (sesgo, cobertura) se calculan aparte, a partir de las
réplicas guardadas (scripts/resumen_recuperacion.py): ninguna cifra se
escribe a mano.

Cobertura con IC abierto: si el perfil no cruza el umbral antes del límite
del recorrido, el extremo es ese límite (limites_perfil). La
verdad "queda cubierta" si cae entre los extremos reportados; para R0 y
s0 con casos solos eso es casi trivial y por eso se reporta aparte la
fracción de IC abiertos.
"""

from __future__ import annotations

import numpy as np

from src import identificabilidad as ident
from src import sir
from src import verosimilitud as V

RUIDOS = ("nb", "poisson")


def semanas_hasta_fin(theta, gamma, N, fraccion_pico, max_semanas=520):
    """Número de semanas de la serie: hasta la primera semana DESPUÉS del
    pico en que la incidencia esperada baja de fraccion_pico * pico.

    Se usa la incidencia sin ruido, así que la longitud no depende de los
    datos simulados. Lanza error si la ola no termina en max_semanas.
    """
    mu = V.media_casos(theta, gamma, N, max_semanas)
    pico = int(np.argmax(mu))
    bajo = np.flatnonzero(mu[pico:] < fraccion_pico * mu[pico])
    if bajo.size == 0:
        raise ValueError("La ola no termina dentro de max_semanas")
    return pico + int(bajo[0]) + 1


def limites_perfil(mle_theta):
    """Límites del recorrido de cada perfil, de cantidades identificables de la MLE.

    Por la simetría de escala de H1 (src/identificabilidad.py), con casos
    solos R0 puede valer c*R0 con c en [s0, 1/rho], es decir R0 en
    [Reff, Reff/(rho*s0)], y s0 en [rho*s0, 1]. Reff y rho*s0 son
    invariantes, así que se toman de la MLE. Los límites rebasan esos rangos
    (factores 0.8 y 1.5; 0.7 para s0) para ver dónde el perfil deja de ser
    plano; s0 no puede pasar de 1. Reff (identificable): 0.5 a 2 veces su MLE.
    """
    reff = V.reff(mle_theta)
    rho_s0 = mle_theta["rho"] * mle_theta["s0"]
    return {
        "R0": (0.8 * reff, 1.5 * reff / rho_s0),
        "s0": (0.7 * rho_s0, 1.0),
        "Reff": (0.5 * reff, 2.0 * reff),
    }


def simular(theta, gamma, N, n_semanas, ruido, rng, sero_diseno=None):
    """Datos sintéticos: casos semanales (ruido nb o poisson) y, si se pide, serología."""
    mu = V.media_casos(theta, gamma, N, n_semanas)
    if ruido == "nb":
        casos = sir.simular_casos(mu, theta["k"], rng)
    elif ruido == "poisson":
        casos = sir.simular_casos_poisson(mu, rng)
    else:
        raise ValueError(f"ruido debe ser uno de {RUIDOS}")
    d = {"casos": casos}
    if sero_diseno:
        d["sero"] = []
        for t_a, t_b, _, ee in sero_diseno:
            delta = sir.infectados_entre(theta["R0"], gamma, theta["s0"], theta["i0"], t_a, t_b)
            d["sero"].append((t_a, t_b, float(delta + rng.normal(0, ee)), ee))
    return d


def ajustar_y_perfilar(d, gamma, N, modelo, inicio, rng, perfiles=("R0", "s0", "Reff"),
                       max_rondas=3, paso_inicial=0.002, n_biseccion=8, pulir_perfil=False):
    """MLE + IC95 por perfil (ic_perfil_raiz) + criterios de comparación.

    Si algún perfil encuentra un punto con más verosimilitud que la MLE, la
    MLE no era el máximo global: se reajusta desde ese punto y se repiten
    los perfiles (hasta max_rondas). Se registra cuántas rondas hubo.
    """
    ini = {p: inicio[p] for p in V.PARAMETROS_POR_MODELO[modelo]}
    mle = V.ajustar(d, gamma, N, ini, n_arranques=3, rng=rng, modelo=modelo)
    for ronda in range(1, max_rondas + 1):
        th = mle["theta"]
        lim = limites_perfil(th)
        pfs = {nm: V.ic_perfil_raiz(nm, d, gamma, N, mle, lim[nm], modelo=modelo,
                                    paso_inicial=paso_inicial, n_biseccion=n_biseccion,
                                    pulir=pulir_perfil)
               for nm in perfiles}
        lp_mejor, th_mejor = max((pf["mejor"] for pf in pfs.values()), key=lambda x: x[0])
        if lp_mejor <= mle["logvero"] + 1e-3 or ronda == max_rondas:
            break
        mle = V.ajustar(d, gamma, N, th_mejor, n_arranques=0, rng=rng, modelo=modelo)
    out = {"theta": th, "Reff": V.reff(th), "logvero": mle["logvero"], "n_libres": mle["n_libres"],
           "rondas": ronda, "mle_no_era_global": bool(lp_mejor > mle["logvero"] + 1e-3), "perfiles": {}}
    reff, rho_s0 = V.reff(th), th["rho"] * th["s0"]
    rango = {"R0": (reff, reff / rho_s0), "s0": (rho_s0, 1.0)}
    valor_mle = {"R0": th["R0"], "s0": th["s0"], "Reff": reff}
    for nm, pf in pfs.items():
        pf = dict(pf)
        pf.pop("mejor")
        pf["limites"] = list(lim[nm])
        # Amplitud relativa del IC95 (criterio de rechazo de H1: comparar la
        # de R0 con la de R_eff(0)). Se reporta; el umbral de "comparable"
        # no está fijado.
        pf["amplitud_relativa"] = (pf["sup"] - pf["inf"]) / valor_mle[nm]
        if nm in rango and rango[nm][0] < rango[nm][1]:
            pf["rango_analitico"] = list(rango[nm])
            pf["fraccion_rango_cubierta"] = ident.fraccion_rango_cubierta(pf["inf"], pf["sup"], *rango[nm])
        out["perfiles"][nm] = pf
    n = len(d["casos"])
    mu = V.media_casos(th, gamma, N, n)
    p = mle["n_libres"]
    out["aic"] = V.aic(mle["logvero"], p)
    out["bic"] = V.bic(mle["logvero"], p, n)
    out["dispersion_pearson"] = V.dispersion_pearson(d["casos"], mu, modelo, p, k=th.get("k"))
    return out


def replica(escenario, P, semilla, con_sero, combinaciones=None):
    """Una réplica completa de un escenario. Devuelve un dict serializable.

    escenario : {"R0", "s0", "D"}; el resto de la verdad (i0, rho, k, N)
        sale de la sección `sintetico` de config/parametros.yaml (P).
    semilla : entero o numpy SeedSequence (reproducible).
    combinaciones : lista de (ruido, modelo); por omisión las 4.
    """
    rng = np.random.default_rng(semilla)
    gamma = 1.0 / escenario["D"]
    N = P["N"]
    verdad = {"R0": escenario["R0"], "s0": escenario["s0"], "i0": P["i0"],
              "rho": P["rho"], "k": P["k"]}
    n_semanas = semanas_hasta_fin(verdad, gamma, N, P["fin_ola_fraccion_pico"])
    combinaciones = combinaciones or [(r, m) for r in RUIDOS for m in V.MODELOS]
    # Arranque lejos de la verdad (no centrado en la respuesta) e igual en
    # todos los escenarios: R0 = 4, s0 = 0.8, i0 = i0/3, rho = 0.3, k = 5.
    inicio = {"R0": 4.0, "s0": 0.8, "i0": P["i0"] / 3, "rho": 0.3, "k": 5.0}
    sero = P["sero"] if con_sero else None
    # Orden fijo (no un set: su orden cambia entre corridas y rompería la
    # reproducibilidad de la semilla).
    ruidos = [r for r in RUIDOS if r in {c[0] for c in combinaciones}]
    series = {r: simular(verdad, gamma, N, n_semanas, r, rng, sero) for r in ruidos}
    res = {"escenario": dict(escenario), "verdad": verdad, "Reff_verdad": V.reff(verdad),
           "n_semanas": n_semanas, "con_sero": bool(con_sero), "ajustes": {}}
    for ruido, modelo in combinaciones:
        clave = f"{ruido}|{modelo}"
        try:
            res["ajustes"][clave] = ajustar_y_perfilar(
                series[ruido], gamma, N, modelo, inicio, rng,
                paso_inicial=P["perfil_paso_inicial"], n_biseccion=P["perfil_biseccion"],
                pulir_perfil=P["perfil_pulir"])
        except Exception as e:  # se registra por combinación; no se descarta la réplica
            res.setdefault("errores_ajuste", {})[clave] = f"{type(e).__name__}: {e}"
    return res
