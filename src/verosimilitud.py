"""Verosimilitud, máxima verosimilitud, perfiles y bootstrap paramétrico.

Parámetros del modelo de una ola (todos en `PARAMETROS`):
    R0   número reproductivo básico
    s0   fracción susceptible al inicio de la ola
    i0   fracción infecciosa al inicio de la ola
    rho  fracción de infecciones reportadas como caso (subregistro)
    k    tamaño de la binomial negativa (sobredispersión; k grande ~ Poisson)
gamma y N NO se estiman: vienen de config/parametros.yaml con su fuente.

Datos de una ola (diccionario):
    "casos": arreglo de casos semanales, semana 0 = inicio de la ola.
    "sero" (opcional): lista de tuplas (t_a, t_b, delta_obs, ee), donde
        delta_obs es el aumento de seroprevalencia observado entre los días
        t_a y t_b (contados desde el inicio de la ola) y ee su error estándar.

Por qué optimizamos en un espacio "libre"
-----------------------------------------
Los parámetros tienen restricciones (R0 > 0, 0 < s0 <= 1, ...). En vez de
pasar cotas al optimizador, transformamos: log para positivos, logit para
fracciones. Así cualquier vector real es un parámetro válido y el
optimizador nunca propone valores imposibles. La MLE no depende de la
parametrización (invariancia de la MLE), así que esto no cambia el
resultado, solo hace la búsqueda más estable.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln, logit, xlogy

from src import sir

PARAMETROS = ("R0", "s0", "i0", "rho", "k")

# Qué transformación usa cada parámetro para pasar al espacio libre.
_TRANSFORMACION = {"R0": "log", "s0": "logit", "i0": "log", "rho": "logit", "k": "log"}

# Media mínima de casos. Si el modelo predice mu = 0 en una semana con
# casos > 0, la log-verosimilitud sería -inf y algunos optimizadores se
# rompen. Con 1e-10 el castigo sigue siendo enorme (~ y*log(1e-10)) pero
# finito. No afecta ningún ajuste razonable, donde mu >> 1.
MU_MIN = 1e-10


def a_libre(nombre, valor):
    """Valor natural -> espacio libre (log o logit)."""
    return np.log(valor) if _TRANSFORMACION[nombre] == "log" else logit(valor)


def de_libre(nombre, z):
    """Espacio libre -> valor natural (exp o logística)."""
    return float(np.exp(z) if _TRANSFORMACION[nombre] == "log" else expit(z))


# ---------------------------------------------------------------------------
# Log-verosimilitudes
# ---------------------------------------------------------------------------

def logpmf_binneg(y, mu, k):
    """log P(Y = y) para Y ~ BinNeg(media mu, tamaño k).

    P(y) = Γ(y+k) / (Γ(k) y!) * (k/(k+mu))^k * (mu/(k+mu))^y.
    Usamos gammaln (log Γ) para no desbordar con conteos grandes, y xlogy
    para que 0*log(0) valga 0 cuando y = 0.
    """
    y = np.asarray(y, dtype=float)
    mu = np.maximum(np.asarray(mu, dtype=float), MU_MIN)
    return (
        gammaln(y + k) - gammaln(k) - gammaln(y + 1)
        + k * np.log(k / (k + mu))
        + xlogy(y, mu / (k + mu))
    )


def logvero_casos(theta, casos, gamma, N):
    """Log-verosimilitud de los casos semanales (semanas independientes).

    Independencia entre semanas dado el modelo es un supuesto: si hay
    autocorrelación en los residuos, los intervalos salen demasiado
    angostos. Por eso H2 mira los residuos y los intervalos finales se
    hacen por bootstrap paramétrico.
    """
    mu = sir.incidencia_semanal(
        theta["R0"], gamma, theta["s0"], theta["i0"], theta["rho"], N, len(casos)
    )
    return float(np.sum(logpmf_binneg(casos, mu, theta["k"])))


def logvero_sero(theta, sero, gamma):
    """Log-verosimilitud normal de los aumentos de seroprevalencia.

    Cada encuesta da un estimador con su error estándar (ENSANUT reporta
    intervalos de diseño). Aproximación normal: delta_obs ~ N(delta_mod, ee^2).
    Omitimos la constante -log(ee*sqrt(2*pi)) porque no depende de theta.
    """
    total = 0.0
    for t_a, t_b, delta_obs, ee in sero:
        delta_mod = sir.infectados_entre(
            theta["R0"], gamma, theta["s0"], theta["i0"], t_a, t_b
        )
        total += -0.5 * ((delta_obs - delta_mod) / ee) ** 2
    return total


def logvero_total(theta, datos, gamma, N):
    """Casos + serología (si la hay). Se suman porque son datos independientes."""
    lv = logvero_casos(theta, datos["casos"], gamma, N)
    if datos.get("sero"):
        lv += logvero_sero(theta, datos["sero"], gamma)
    return lv


# ---------------------------------------------------------------------------
# Máxima verosimilitud
# ---------------------------------------------------------------------------

def ajustar(datos, gamma, N, inicio, fijos=None, n_arranques=3, rng=None):
    """Maximiza la log-verosimilitud sobre los parámetros no fijos.

    inicio : dict con un valor inicial para cada parámetro.
    fijos : dict {nombre: valor} de parámetros que NO se optimizan
        (así se calcula un perfil).
    n_arranques : arranques adicionales perturbados alrededor de `inicio`.
        Un solo arranque puede quedarse en un máximo local; varios
        arranques que coinciden dan confianza de que es el global.

    Estrategia: L-BFGS-B (rápido, usa gradiente numérico) seguido de
    Nelder-Mead desde el mejor punto (no usa gradientes; sirve de
    "pulido" y de verificación de que L-BFGS-B no se detuvo antes).
    """
    fijos = dict(fijos or {})
    libres = [p for p in PARAMETROS if p not in fijos]
    rng = rng if rng is not None else np.random.default_rng(0)

    def a_theta(z):
        theta = dict(fijos)
        for nombre, zi in zip(libres, z):
            theta[nombre] = de_libre(nombre, zi)
        return theta

    def objetivo(z):
        try:
            valor = -logvero_total(a_theta(z), datos, gamma, N)
        except (RuntimeError, ValueError):
            # Punto inválido (integrador falló o estado inicial imposible):
            # devolvemos un valor enorme para que el optimizador lo evite.
            return 1e300
        return valor if np.isfinite(valor) else 1e300

    z0 = np.array([a_libre(p, inicio[p]) for p in libres])
    # Arranque 0: el dado; los demás: perturbaciones de ~0.5 en el espacio
    # libre (≈ factor 1.6 en parámetros log), suficientes para salir de una
    # cuenca local sin ir a valores absurdos.
    arranques = [z0] + [z0 + rng.normal(0, 0.5, size=z0.size) for _ in range(n_arranques)]

    mejor = None
    for za in arranques:
        r = minimize(objetivo, za, method="L-BFGS-B")
        if mejor is None or r.fun < mejor.fun:
            mejor = r
    pulido = minimize(
        objetivo, mejor.x, method="Nelder-Mead",
        options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000, "maxfev": 8000},
    )
    if pulido.fun < mejor.fun:
        mejor = pulido

    return {"theta": a_theta(mejor.x), "logvero": -float(mejor.fun)}


def perfil(nombre, valores, datos, gamma, N, mle):
    """Perfil de verosimilitud: lp(v) = max_{otros} logvero(nombre = v).

    Recorremos la malla desde el valor más cercano a la MLE hacia afuera,
    en cada dirección, usando la solución del punto anterior como inicio
    ("continuación"). Esto es mucho más estable que arrancar siempre desde
    la MLE, porque los demás parámetros cambian suavemente a lo largo del
    perfil.
    """
    valores = np.asarray(valores, dtype=float)
    lp = np.full(valores.size, np.nan)
    thetas = [None] * valores.size
    centro = np.argmin(np.abs(valores - mle["theta"][nombre]))
    for orden in (range(centro, valores.size), range(centro - 1, -1, -1)):
        inicio = mle["theta"]
        for j in orden:
            r = ajustar(datos, gamma, N, inicio, fijos={nombre: valores[j]}, n_arranques=0)
            lp[j], thetas[j] = r["logvero"], r["theta"]
            inicio = r["theta"]
    return lp, thetas


def bootstrap_parametrico(mle, datos, gamma, N, B, rng):
    """Re-estimación sobre B conjuntos simulados desde la MLE.

    Por qué bootstrap paramétrico: si el modelo es correcto, la
    distribución de las re-estimaciones aproxima la distribución muestral
    del estimador sin depender de la aproximación cuadrática (Hessiano),
    que falla justo cuando hay crestas de no identificabilidad (H1).
    Los intervalos se toman como percentiles 2.5 y 97.5.
    """
    theta = mle["theta"]
    mu = sir.incidencia_semanal(
        theta["R0"], gamma, theta["s0"], theta["i0"], theta["rho"], N, len(datos["casos"])
    )
    replicas = []
    for _ in range(B):
        sim = {"casos": sir.simular_casos(mu, theta["k"], rng)}
        if datos.get("sero"):
            sim["sero"] = []
            for t_a, t_b, _, ee in datos["sero"]:
                delta = sir.infectados_entre(
                    theta["R0"], gamma, theta["s0"], theta["i0"], t_a, t_b
                )
                sim["sero"].append((t_a, t_b, delta + rng.normal(0, ee), ee))
        replicas.append(ajustar(sim, gamma, N, theta, n_arranques=0, rng=rng)["theta"])
    return replicas
