"""Identificabilidad del SIR con subregistro: simetría de escala y perfiles.

Resultado analítico (H1), derivado en escrito/capitulos/identificabilidad.tex
---------------------------------------------------------------------------
Con solo casos reportados, para cualquier c > 0 los parámetros

    (R0, s0, i0, rho)   y   (c*R0, s0/c, i0/c, c*rho)

producen EXACTAMENTE la misma incidencia reportada esperada.

Demostración (cabe en pocas líneas). Sea (s, i) la solución con
(beta, s0, i0) y definamos s' = s/c, i' = i/c. Entonces
    ds'/dt = -beta*s*i/c = -(c*beta) * s' * i'
    di'/dt = (beta*s*i - gamma*i)/c = (c*beta) * s' * i' - gamma * i'
    s'(0) = s0/c,  i'(0) = i0/c,
o sea, (s', i') es LA solución del SIR con (c*beta, s0/c, i0/c) (por
unicidad de soluciones de la EDO). Los casos esperados del sistema
transformado son (c*rho)*N*[s'(t_k) - s'(t_{k+1})] = rho*N*[s(t_k) - s(t_{k+1})],
idénticos a los originales. Combinaciones invariantes:
    R_eff(0) = R0*s0,   rho*s0,   i0/s0.
Por eso con casos solo se identifica R_eff(0), no R0 ni s0 por separado.

Las restricciones s0 <= 1 y rho <= 1 acotan c: s0 <= c <= 1/rho. Entonces
R0 solo queda acotado a [R_eff(0), R0/rho] (el perfil es plano ahí).

La serología rompe la simetría: el aumento de seroprevalencia es
s(t_a) - s(t_b), que bajo la transformación se divide entre c. Esto NO
depende de la binomial negativa ni de usar semanas; es una propiedad del
SIR con subregistro desconocido.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import chi2

from src import sir

# Umbral del perfil para un intervalo de confianza del 95 %: por el teorema
# de Wilks, 2*(lmax - lp) ~ chi^2 con 1 grado de libertad, cuyo cuantil
# 0.95 es 3.84; dividido entre 2 da 1.92 en unidades de log-verosimilitud.
UMBRAL_95 = chi2.ppf(0.95, df=1) / 2.0


def transformar(theta, c):
    """Aplica la simetría de escala con factor c (devuelve un dict nuevo)."""
    nuevo = dict(theta)
    nuevo["R0"] = theta["R0"] * c
    nuevo["s0"] = theta["s0"] / c
    nuevo["i0"] = theta["i0"] / c
    nuevo["rho"] = theta["rho"] * c
    return nuevo


def rango_c_admisible(theta):
    """Valores de c que mantienen s0' <= 1 y rho' <= 1: [s0, 1/rho].

    (s0/c <= 1  <=>  c >= s0;   rho*c <= 1  <=>  c <= 1/rho.)
    Con la convención s0 = (S0 + I0)/N (src/sir.py::estado_inicial) la cota
    s0' <= 1 es exactamente S0' + I0' <= N; i0' < s0' se conserva porque
    ambos se dividen entre c.
    """
    return theta["s0"], 1.0 / theta["rho"]


def rango_R0_no_identificable(theta):
    """Intervalo de R0 indistinguible con casos solos: R0*[s0, 1/rho]."""
    c_min, c_max = rango_c_admisible(theta)
    return theta["R0"] * c_min, theta["R0"] * c_max


def diferencia_maxima_simetria(theta, c, gamma, N, n_semanas):
    """Máxima diferencia en la incidencia esperada entre theta y su
    transformado, relativa al PICO de la incidencia.

    Por qué relativa al pico y no semana por semana: la incidencia es una
    resta S(t_k) - S(t_{k+1}) de dos números ~N. En la cola de la ola esa
    resta es chica y hereda el error absoluto de S (~rtol * N), así que su
    error relativo semana a semana crece sin que el modelo esté mal. Respecto
    al pico, el error debe ser del orden de la tolerancia del integrador."""
    a = sir.incidencia_semanal(theta["R0"], gamma, theta["s0"], theta["i0"], theta["rho"], N, n_semanas)
    t2 = transformar(theta, c)
    b = sir.incidencia_semanal(t2["R0"], gamma, t2["s0"], t2["i0"], t2["rho"], N, n_semanas)
    return float(np.max(np.abs(a - b)) / np.max(a))


def intervalo_perfil(valores, lp, lmax):
    """Intervalo de confianza 95 % por perfil de verosimilitud.

    Devuelve (inferior, superior, abierto_abajo, abierto_arriba). Los
    bordes se obtienen por interpolación lineal donde el perfil cruza
    lmax - 1.92. Si el perfil NO cruza el umbral dentro de la malla, el
    extremo correspondiente se reporta como el borde de la malla y se
    marca como "abierto": eso significa que los datos no acotan el
    parámetro por ese lado (no identificable en la práctica) y NO debe
    leerse como un intervalo finito.
    """
    valores = np.asarray(valores, dtype=float)
    dentro = lp >= lmax - UMBRAL_95
    if not np.any(dentro):
        raise ValueError("Ningún punto del perfil está dentro del umbral; revisar la MLE.")
    idx = np.flatnonzero(dentro)
    j0, j1 = idx[0], idx[-1]
    nivel = lmax - UMBRAL_95

    def cruce(ja, jb):
        # Interpolación lineal entre un punto dentro (ja) y uno fuera (jb).
        fa, fb = lp[ja] - nivel, lp[jb] - nivel
        return valores[ja] + (valores[jb] - valores[ja]) * fa / (fa - fb)

    abierto_abajo = j0 == 0
    abierto_arriba = j1 == valores.size - 1
    inf = valores[0] if abierto_abajo else cruce(j0, j0 - 1)
    sup = valores[-1] if abierto_arriba else cruce(j1, j1 + 1)
    return float(inf), float(sup), bool(abierto_abajo), bool(abierto_arriba)


def clasificar_perfil(valores, lp, lmax):
    """Clasifica un perfil de verosimilitud según Raue et al. 2009 (J01).

    Criterio (sin umbrales nuevos: solo el 1.92 de UMBRAL_95):
      * "identificable": el perfil cruza lmax - 1.92 por ambos lados dentro
        de la malla; el IC95 por perfil es finito (J01, p. 1924, sec. 2.3:
        "identifiable, if the confidence interval ... is finite").
      * "cresta_plana": el perfil NO cruza el umbral por al menos un lado de
        la malla; el IC95 queda abierto (J01, p. 1925, Definición 1, y
        p. 1926: un parámetro estructuralmente no identificable tiene
        perfil plano). Es el resultado que H1 predice para R0 y s0 con
        casos solos.
    La malla debe cubrir el rango no identificable analítico
    (rango_R0_no_identificable) con holgura; un IC "abierto" solo dice que
    los datos no lo acotan DENTRO de la malla.

    Devuelve dict con la clase, el intervalo (inf, sup, abierto_abajo,
    abierto_arriba) y la caída máxima del perfil dentro de la malla.
    """
    inf, sup, aa, ab = intervalo_perfil(valores, lp, lmax)
    caida = float(np.nanmax(lmax - np.asarray(lp, dtype=float)))
    clase = "cresta_plana" if (aa or ab) else "identificable"
    return {"clase": clase, "inf": inf, "sup": sup,
            "abierto_abajo": aa, "abierto_arriba": ab, "caida_max": caida}
