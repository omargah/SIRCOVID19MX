"""Modelo SIR determinista (en personas) y su modelo de observación.

Ecuaciones (Kermack y McKendrick 1927, bibliografía B01):
    dS/dt = -beta * S * I / N
    dI/dt =  beta * S * I / N - gamma * I
    dR/dt =  gamma * I
con gamma = 1/D (D = periodo infeccioso medio, días) y beta = R0 * gamma.

Resultados exactos que usan las pruebas (tests/test_sir.py):
  [E1] S + I + R = N para todo t (sumar las tres ecuaciones da 0).
  [E2] H = S + I - (N/R0) * ln S es constante. Prueba:
       dH/dt = dS/dt + dI/dt - (N/R0) (dS/dt)/S
             = -gamma*I - (N/R0)(-beta*I/N) = -gamma*I + gamma*I = 0.
  [E3] Tamaño final (I -> 0 cuando t -> inf). Igualando H en t=0 y t=inf:
       ln(S0/S_inf) = (R0/N) * (S0 + I0 - S_inf).
  [E4] Fase exponencial: mientras S ≈ S0, dI/dt ≈ (beta*S0/N - gamma) I,
       así que I crece con tasa r = gamma*(R0*S0/N - 1), es decir
       R0 * S0 / N = 1 + r*D.
       OJO: R0 = exp(r*D)/s0 (lo que usaba el código viejo) es la relación
       para un tiempo de generación FIJO igual a D (Wallinga y Lipsitch 2007,
       bibliografía F01). En el SIR el tiempo que uno pasa infeccioso es
       exponencial con media D, y para esa distribución la relación es
       1 + r*D. Usar la otra sobrestima R0 (BA.1: 4.28 en vez de ~2.94).

Decisiones numéricas (para poder defenderlas)
---------------------------------------------
* Integramos (S, ln I, R) en vez de (S, I, R). La solución exacta tiene
  I > 0 siempre, pero cuando I decae a ~1e-20 personas un integrador en I
  puede devolver valores negativos (lo vimos: -1e-6 personas con S0 = 1).
  Con u = ln I, du/dt = (dI/dt)/I (regla de la cadena) y I = exp(u) > 0 por
  construcción. Las derivadas salen del MISMO rhs_sir; solo se divide la
  segunda entre I. R se integra (no se calcula como N - S - I) para que la
  conservación [E1] sea una verificación y no una identidad.
* Tolerancias explícitas: RTOL = 1e-10 relativo; absolutas
  ATOL_RELATIVA_A_N * N personas para S y R (1e-7 personas si N = 1e7) y
  RTOL para ln I (equivale a error relativo 1e-10 en I). Así el error del
  integrador queda órdenes de magnitud debajo del ruido de los datos. Las
  pruebas verifican [E1]-[E4]; si alguien afloja las tolerancias, fallan.
* LSODA: cambia solo entre un método para problemas no rígidos y uno
  para rígidos. Una ola típica no es rígida, pero durante la estimación el
  optimizador prueba valores extremos (beta enorme) donde el SIR sí se
  vuelve rígido; con un método explícito (probamos DOP853) esos puntos
  tardan minutos y la estimación se atasca.
* beta por tramos: en un cambio de beta el lado derecho es discontinuo. El
  control de error de un integrador supone un lado derecho suave, así que
  integramos cada tramo por separado y reiniciamos en el cambio con el
  estado final del tramo anterior (no "saltamos" la discontinuidad).
* Incidencia como diferencia de S: las nuevas infecciones entre t_k y
  t_{k+1} son S(t_k) - S(t_{k+1}); no hace falta integrar beta*S*I/N otra vez.
* Semanas y no días: los casos diarios tienen ciclo semanal de registro que
  el SIR no modela; sumar por semana lo quita sin agregar parámetros.
* Binomial negativa y no Poisson: Var = mu + mu^2/k, con k -> inf = Poisson.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

RTOL = 1e-10
ATOL_RELATIVA_A_N = 1e-14  # tolerancia absoluta = ATOL_RELATIVA_A_N * N personas
METODO = "LSODA"


# ---------------------------------------------------------------------------
# Ecuaciones y relaciones exactas
# ---------------------------------------------------------------------------

def tasas(R0, D):
    """(beta, gamma) a partir de R0 y del periodo infeccioso D (días)."""
    gamma = 1.0 / D
    return R0 * gamma, gamma


def rhs_sir(t, y, beta, gamma, N):
    """Lado derecho del SIR en personas. y = [S, I, R]."""
    S, I, R = y
    infecciones = beta * S * I / N  # personas que pasan de S a I por día
    recuperaciones = gamma * I      # personas que pasan de I a R por día
    return [-infecciones, infecciones - recuperaciones, recuperaciones]


def cantidad_conservada(S, I, R0, N):
    """H = S + I - (N/R0) ln S, constante en el SIR con beta fijo [E2]."""
    return S + I - (N / R0) * np.log(S)


def tamano_final(R0, S0, I0, N):
    """S_inf como raíz de ln(S0/S) - (R0/N)(S0 + I0 - S) = 0 [E3].

    La raíz física está en (0, N/R0): S_inf debe quedar debajo del umbral
    N/R0 (si no, la epidemia seguiría creciendo). En S -> 0 la función tiende
    a +inf y en S = N/R0 es <= 0 (porque ln x <= x - 1), así que brentq tiene
    un intervalo con cambio de signo garantizado.
    """
    f = lambda S: np.log(S0 / S) - (R0 / N) * (S0 + I0 - S)
    return brentq(f, 1e-12 * N, min(S0, N / R0), xtol=1e-12 * N, rtol=1e-14)


def R0_desde_tasa_crecimiento(r, D, s0):
    """R0 a partir de la tasa de crecimiento r (1/día) [E4]: R0 = (1 + r*D)/s0.

    s0 = S0/N es la fracción susceptible al inicio de la ola.
    NO usar exp(r*D)/s0: es la relación de otro modelo (ver docstring del módulo).
    """
    return (1.0 + r * D) / s0


# ---------------------------------------------------------------------------
# Integración
# ---------------------------------------------------------------------------

def _rhs_log(t, y, beta, gamma, N):
    """Lado derecho en (S, u = ln I, R), construido a partir de rhs_sir."""
    S, u, R = y
    I = np.exp(u)
    dS, dI, dR = rhs_sir(t, [S, I, R], beta, gamma, N)
    return [dS, dI / I, dR]


def integrar_sir_tramos(R0_tramos, t_cambios, D, S0, I0, N, t):
    """Integra el SIR con R0 (y por tanto beta) constante por tramos.

    R0_tramos : [R0_1, ..., R0_m], uno por tramo.
    t_cambios : [tau_1, ..., tau_{m-1}], días en que cambia R0; deben estar
                estrictamente dentro de (t[0], t[-1]) y en orden creciente.
    D, S0, I0, N : periodo infeccioso (días), susceptibles e infecciosos
                iniciales (personas), población. R(0) = N - S0 - I0.
    t : tiempos (días, crecientes) donde se reporta la solución.

    Devuelve S, I, R (arreglos del tamaño de t).
    """
    t = np.asarray(t, dtype=float)
    t_cambios = list(t_cambios)
    if len(R0_tramos) != len(t_cambios) + 1:
        raise ValueError("Debe haber un R0 por tramo: len(R0_tramos) = len(t_cambios) + 1")
    if not (S0 > 0 and I0 > 0 and S0 + I0 <= N):
        raise ValueError(f"Estado inicial inválido: S0={S0}, I0={I0}, N={N}")
    bordes = [t[0], *t_cambios, t[-1]]
    if np.any(np.diff(bordes) <= 0):
        raise ValueError("Los cambios deben estar dentro de (t[0], t[-1]) y en orden creciente")

    salida = np.empty((3, t.size))
    y = np.array([S0, np.log(I0), N - S0 - I0])  # variables (S, ln I, R)
    atol = [ATOL_RELATIVA_A_N * N, RTOL, ATOL_RELATIVA_A_N * N]
    _, gamma = tasas(1.0, D)
    for j, R0 in enumerate(R0_tramos):
        a, b = bordes[j], bordes[j + 1]
        ultimo = j == len(R0_tramos) - 1
        # Los tiempos de t que pertenecen a este tramo: [a, b) o, en el
        # último tramo, [a, b]. Así cada tiempo se asigna una sola vez.
        en_tramo = (t >= a) & ((t <= b) if ultimo else (t < b))
        t_eval = t[en_tramo]
        if t_eval.size == 0 or t_eval[-1] < b:
            t_eval = np.append(t_eval, b)  # necesitamos el estado en b para seguir
        sol = solve_ivp(
            _rhs_log, (a, b), y, t_eval=t_eval, args=(R0 * gamma, gamma, N),
            method=METODO, rtol=RTOL, atol=atol,
        )
        if not sol.success:
            raise RuntimeError(f"El integrador falló en el tramo {j}: {sol.message}")
        salida[:, en_tramo] = sol.y[:, : en_tramo.sum()]
        y = sol.y[:, -1]  # estado en b: condición inicial del siguiente tramo
    return salida[0], np.exp(salida[1]), salida[2]


def integrar_sir(R0, D, S0, I0, N, t):
    """SIR con beta constante: caso particular de un solo tramo."""
    return integrar_sir_tramos([R0], [], D, S0, I0, N, t)


# ---------------------------------------------------------------------------
# Modelo de observación (lo usan verosimilitud.py e identificabilidad.py)
# Trabajan en fracciones s0 = S0/N, i0 = I0/N y con gamma, porque así se
# parametriza la estimación; aquí solo se traduce a personas y a D = 1/gamma.
# ---------------------------------------------------------------------------

def incidencia_semanal(R0, gamma, s0, i0, rho, N, n_semanas):
    """Casos reportados esperados por semana: mu_k = rho * [S(t_k) - S(t_{k+1})].

    rho = fracción de infecciones que se reporta como caso (subregistro),
    supuesta constante durante la ola.
    """
    t = 7.0 * np.arange(n_semanas + 1)  # bordes de las semanas, en días
    S, _, _ = integrar_sir(R0, 1.0 / gamma, s0 * N, i0 * N, N, t)
    nuevas = -np.diff(S)
    # Cuando la ola ya terminó, -diff puede dar -1e-9 por redondeo; se
    # recorta a 0 para que la media de la binomial negativa sea válida.
    return rho * np.clip(nuevas, 0.0, None)


def infectados_entre(R0, gamma, s0, i0, t_a, t_b, N=1.0):
    """Fracción de la población infectada entre los días t_a y t_b: [S(t_a)-S(t_b)]/N.

    Se compara con el aumento de seroprevalencia entre dos encuestas.
    Supuestos: toda infección seroconvierte, sin serorreversión, retraso de
    seroconversión despreciable. El resultado no depende de N (el SIR en
    fracciones no tiene N), por eso N tiene un valor por omisión.
    """
    if t_a == 0:
        # Los tiempos deben ser crecientes; en t = 0 sabemos que S = S0.
        S, _, _ = integrar_sir(R0, 1.0 / gamma, s0 * N, i0 * N, N, [0.0, t_b])
        return (s0 * N - S[-1]) / N
    S, _, _ = integrar_sir(R0, 1.0 / gamma, s0 * N, i0 * N, N, [0.0, t_a, t_b])
    return (S[1] - S[2]) / N


def simular_casos(mu, k, rng):
    """Una realización de casos semanales ~ BinNeg(media mu, tamaño k).

    numpy usa (n, p); con n = k, p = k/(k+mu) la media es
    n(1-p)/p = k * (mu/(k+mu)) / (k/(k+mu)) = mu.
    """
    mu = np.asarray(mu, dtype=float)
    return rng.negative_binomial(k, k / (k + mu))
