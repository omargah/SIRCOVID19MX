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

# Decisión I2 (Omar, 2026-11-03): se implementan y comparan DOS modelos de
# observación de los casos semanales y_k dada la media mu_k = rho*H_k
# (H_k = infecciones nuevas de la semana k):
#   "nb"      : y_k ~ BinNeg(media mu_k, tamaño k), Var = mu + mu^2/k
#               (King et al. 2016, K04, p. 32, ec. 17).
#   "poisson" : y_k ~ Poisson(mu_k), Var = mu   (K04, p. 23, ec. 13).
# Poisson es el límite k -> inf de la BinNeg y no tiene el parámetro k.
MODELOS = ("nb", "poisson")
PARAMETROS_POR_MODELO = {"nb": PARAMETROS, "poisson": ("R0", "s0", "i0", "rho")}

# Parámetro derivado que se puede fijar en un perfil: R_eff(0) = R0*S0/N.
# Con la convención s0 = (S0 + I0)/N (src/sir.py::estado_inicial),
# S0/N = s0 - i0, así que R_eff(0) = R0*(s0 - i0). Es lo que H1 dice que SÍ
# se identifica con casos solos ("replacement number" al tiempo cero,
# Hethcote 2000, B02, p. 607).
DERIVADOS = ("Reff",)

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


def logpmf_poisson(y, mu):
    """log P(Y = y) para Y ~ Poisson(mu): y*log(mu) - mu - log(y!).

    Misma protección que la BinNeg: mu >= MU_MIN y xlogy para y = 0.
    """
    y = np.asarray(y, dtype=float)
    mu = np.maximum(np.asarray(mu, dtype=float), MU_MIN)
    return xlogy(y, mu) - mu - gammaln(y + 1)


def reff(theta):
    """R_eff(0) = R0*S0/N = R0*(s0 - i0) (ver DERIVADOS)."""
    return theta["R0"] * (theta["s0"] - theta["i0"])


def media_casos(theta, gamma, N, n_semanas):
    """mu_k = rho*[S(t_k) - S(t_{k+1})], k = 0..n_semanas-1 (src/sir.py)."""
    return sir.incidencia_semanal(
        theta["R0"], gamma, theta["s0"], theta["i0"], theta["rho"], N, n_semanas
    )


def _validar_modelo(modelo):
    if modelo not in MODELOS:
        raise ValueError(f"modelo debe ser uno de {MODELOS}, no {modelo!r}")


def logvero_casos(theta, casos, gamma, N, modelo="nb"):
    """Log-verosimilitud de los casos semanales (semanas independientes).

    Independencia entre semanas dado el modelo es un supuesto: si hay
    autocorrelación en los residuos, los intervalos salen demasiado
    angostos. Por eso H2 mira los residuos y los intervalos finales se
    hacen por bootstrap paramétrico.
    """
    _validar_modelo(modelo)
    mu = media_casos(theta, gamma, N, len(casos))
    if modelo == "poisson":
        return float(np.sum(logpmf_poisson(casos, mu)))
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


def logvero_total(theta, datos, gamma, N, modelo="nb"):
    """Casos + serología (si la hay). Se suman porque son datos independientes."""
    lv = logvero_casos(theta, datos["casos"], gamma, N, modelo)
    if datos.get("sero"):
        lv += logvero_sero(theta, datos["sero"], gamma)
    return lv


# ---------------------------------------------------------------------------
# Máxima verosimilitud
# ---------------------------------------------------------------------------

def ajustar(datos, gamma, N, inicio, fijos=None, n_arranques=3, rng=None, modelo="nb"):
    """Maximiza la log-verosimilitud sobre los parámetros no fijos.

    inicio : dict con un valor inicial para cada parámetro.
    fijos : dict {nombre: valor} de parámetros que NO se optimizan
        (así se calcula un perfil). Puede incluir el derivado "Reff": entonces
        R0 deja de ser libre y se calcula como R0 = Reff/(s0 - i0).
    modelo : "nb" o "poisson" (decisión I2). Con "poisson" no hay k.
    n_arranques : arranques adicionales perturbados alrededor de `inicio`.
        Un solo arranque puede quedarse en un máximo local; varios
        arranques que coinciden dan confianza de que es el global.

    Estrategia: L-BFGS-B (rápido, usa gradiente numérico) seguido de
    Nelder-Mead desde el mejor punto (no usa gradientes; sirve de
    "pulido" y de verificación de que L-BFGS-B no se detuvo antes).
    """
    _validar_modelo(modelo)
    fijos = dict(fijos or {})
    con_reff = "Reff" in fijos
    if con_reff and "R0" in fijos:
        raise ValueError("No se pueden fijar a la vez R0 y Reff")
    libres = [
        p for p in PARAMETROS_POR_MODELO[modelo]
        if p not in fijos and not (con_reff and p == "R0")
    ]
    rng = rng if rng is not None else np.random.default_rng(0)

    def a_theta(z):
        theta = {p: v for p, v in fijos.items() if p not in DERIVADOS}
        for nombre, zi in zip(libres, z):
            theta[nombre] = de_libre(nombre, zi)
        if con_reff:
            if theta["s0"] <= theta["i0"]:
                raise ValueError("s0 <= i0")
            theta["R0"] = fijos["Reff"] / (theta["s0"] - theta["i0"])
        return theta

    def objetivo(z):
        try:
            valor = -logvero_total(a_theta(z), datos, gamma, N, modelo)
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

    return {
        "theta": a_theta(mejor.x), "logvero": -float(mejor.fun),
        "n_libres": len(libres), "modelo": modelo,
    }


def perfil(nombre, valores, datos, gamma, N, mle, modelo="nb"):
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
    v_mle = reff(mle["theta"]) if nombre == "Reff" else mle["theta"][nombre]
    centro = np.argmin(np.abs(valores - v_mle))
    for orden in (range(centro, valores.size), range(centro - 1, -1, -1)):
        inicio = mle["theta"]
        for j in orden:
            r = ajustar(datos, gamma, N, inicio, fijos={nombre: valores[j]}, n_arranques=0,
                        modelo=modelo)
            lp[j], thetas[j] = r["logvero"], r["theta"]
            inicio = r["theta"]
    return lp, thetas


def bootstrap_parametrico(mle, datos, gamma, N, B, rng, modelo="nb"):
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
        if modelo == "poisson":
            sim = {"casos": sir.simular_casos_poisson(mu, rng)}
        else:
            sim = {"casos": sir.simular_casos(mu, theta["k"], rng)}
        if datos.get("sero"):
            sim["sero"] = []
            for t_a, t_b, _, ee in datos["sero"]:
                delta = sir.infectados_entre(
                    theta["R0"], gamma, theta["s0"], theta["i0"], t_a, t_b
                )
                sim["sero"].append((t_a, t_b, delta + rng.normal(0, ee), ee))
        replicas.append(
            ajustar(sim, gamma, N, theta, n_arranques=0, rng=rng, modelo=modelo)["theta"]
        )
    return replicas


# ---------------------------------------------------------------------------
# Comparación NB contra Poisson (decisión I2)
# ---------------------------------------------------------------------------

def residuos_pearson(y, mu, modelo, k=None):
    """r_k = (y_k - mu_k)/sqrt(V(mu_k)), con V = mu (Poisson) o mu + mu^2/k (NB)."""
    _validar_modelo(modelo)
    y = np.asarray(y, dtype=float)
    mu = np.maximum(np.asarray(mu, dtype=float), MU_MIN)
    var = mu if modelo == "poisson" else mu + mu**2 / k
    return (y - mu) / np.sqrt(var)


def dispersion_pearson(y, mu, modelo, n_parametros, k=None):
    """Estadístico de sobredispersión declarado de antemano (decisión I2):

        phi = sum_k r_k^2 / (n - p),

    con r_k los residuos de Pearson del modelo ajustado, n el número de
    semanas y p el número de parámetros libres. Bajo el modelo correcto
    phi ≈ 1; phi >> 1 bajo Poisson indica sobredispersión.
    Fuente con página PENDIENTE: el índice del PDF de Pawitan 2001 (LIB03)
    pone "4.5 Poisson with overdispersion" en la p. 84, pero la copia en
    Drive solo trae las primeras ~55 páginas; no está verificado.
    """
    r = residuos_pearson(y, mu, modelo, k)
    gl = r.size - n_parametros
    if gl <= 0:
        raise ValueError("No quedan grados de libertad (n <= p)")
    return float(np.sum(r**2) / gl)


def aic(logvero, n_parametros):
    """AIC = 2p - 2 log L. Pawitan 2001 (LIB03) §13.5, p. 375 según su índice;
    la sección no está en la copia de Drive (no verificado)."""
    return 2.0 * n_parametros - 2.0 * logvero


def bic(logvero, n_parametros, n_datos):
    """BIC = p log(n) - 2 log L, n = número de semanas.
    SIN FUENTE con PDF en la bibliografía (decisión I4 lo pide junto al AIC):
    pedir al chat 01 una fuente con página."""
    return n_parametros * np.log(n_datos) - 2.0 * logvero


# ---------------------------------------------------------------------------
# IC95 por perfil buscando directamente los extremos
# ---------------------------------------------------------------------------

UMBRAL_95 = 1.920729410347062  # chi2_{1,0.95}/2 (= identificabilidad.UMBRAL_95)


def _inicio_sobre_la_cresta(nombre, b, theta):
    """Punto de arranque para el ajuste con nombre = b, sobre la cresta de H1.

    Con casos solos, (R0, s0, i0, rho) y (c*R0, s0/c, i0/c, c*rho) dan la
    MISMA incidencia (src/identificabilidad.py). Al fijar R0 = b se toma
    c = b/R0; al fijar s0 = b, c = s0/b. Ese arranque ya está en el máximo
    condicional (casos solos) o cerca (con serología), y evita que el
    optimizador se quede varado lejos de la cresta: medido el 2026-11-04,
    fijar R0 = 6 desde la MLE (R0 = 2) sin este arranque agotó 8105
    evaluaciones y quedó en log L = -2.8e6. c se recorta para no violar
    s0 <= 1 ni rho < 1. Para "Reff" no se cambia nada (R0 se deriva).
    """
    if nombre not in ("R0", "s0"):
        return theta
    c = b / theta["R0"] if nombre == "R0" else theta["s0"] / b
    c = min(max(c, theta["s0"] * (1 + 1e-9)), (1 - 1e-6) / theta["rho"])
    nuevo = dict(theta)
    nuevo["R0"], nuevo["s0"] = theta["R0"] * c, theta["s0"] / c
    nuevo["i0"], nuevo["rho"] = theta["i0"] / c, theta["rho"] * c
    return nuevo


def ic_perfil_raiz(nombre, datos, gamma, N, mle, limites, modelo="nb", lmax=None,
                   paso_inicial=0.002, n_biseccion=8):
    """Extremos del IC95 por perfil como ceros de lp(b) - l*, l* = lmax - 1.92.

    Es el procedimiento "derivado directamente de la definición" que
    describen Venzon y Moolgavkar 1988 (K02, p. 88): buscar los ceros de
    lp(b) - l*, con l* = l(MLE) - q_1(0.95)/2 (umbral de Raue 2009, J01,
    p. 1924, ec. 8). No usa una malla fija: con una malla, un IC más angosto
    que el paso de la malla no se puede ubicar (fue el error de la primera
    corrida, 2026-11-04).

    Por cada lado: desde el valor de la MLE se avanza en escala log,
    b_j = v * exp(+-paso_inicial * 2^j), hasta que lp(b) < l* (cruce
    encontrado: bisección n_biseccion veces entre el último punto dentro y
    el primero fuera) o hasta el límite (si lp(límite) >= l*, el IC queda
    ABIERTO de ese lado y su extremo es el límite). Cada ajuste arranca del
    anterior del mismo lado (continuación).

    limites : (lo, hi) del recorrido; el extremo abierto se reporta ahí.
    Devuelve dict con inf, sup, abierto_abajo, abierto_arriba, clase,
    caida_max (lmax - lp mínimo evaluado), evaluaciones [(b, lp)] y
    mejor = (lp, theta) del mejor punto visto (si supera a lmax, la MLE no
    era el máximo global y quien llama debe reajustar).
    """
    lmax = mle["logvero"] if lmax is None else lmax
    nivel = lmax - UMBRAL_95
    v0 = reff(mle["theta"]) if nombre == "Reff" else mle["theta"][nombre]
    lo, hi = limites
    evals, mejor = [], (mle["logvero"], mle["theta"])

    def lp_en(b, inicio):
        inicio = _inicio_sobre_la_cresta(nombre, b, inicio)
        r = ajustar(datos, gamma, N, inicio, fijos={nombre: b}, n_arranques=0, modelo=modelo)
        evals.append((float(b), r["logvero"]))
        return r["logvero"], r["theta"]

    extremos = {}
    for signo, limite in ((-1, lo), (+1, hi)):
        b_in, th_in, j = v0, mle["theta"], 0
        while True:
            b = v0 * np.exp(signo * paso_inicial * 2.0**j)
            llego = (b <= limite) if signo < 0 else (b >= limite)
            if llego:
                b = limite
            lp, th = lp_en(b, th_in)
            if lp > mejor[0]:
                mejor = (lp, th)
            if lp < nivel:
                # Cruce entre b_in (dentro) y b (fuera): bisección en escala log.
                a_, c_ = b_in, b
                for _ in range(n_biseccion):
                    m = np.sqrt(a_ * c_)
                    lpm, thm = lp_en(m, th_in)
                    if lpm > mejor[0]:
                        mejor = (lpm, thm)
                    if lpm >= nivel:
                        a_, th_in = m, thm
                    else:
                        c_ = m
                extremos[signo] = (float(np.sqrt(a_ * c_)), False)
                break
            if llego:
                extremos[signo] = (float(limite), True)
                break
            b_in, th_in, j = b, th, j + 1
    caida = float(lmax - min(l for _, l in evals)) if evals else 0.0
    inf, aa = extremos[-1]
    sup, ab = extremos[+1]
    return {"inf": inf, "sup": sup, "abierto_abajo": aa, "abierto_arriba": ab,
            "clase": "cresta_plana" if (aa or ab) else "identificable",
            "caida_max": caida, "evaluaciones": evals, "mejor": mejor}
