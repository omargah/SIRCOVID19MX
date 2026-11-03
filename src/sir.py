"""Modelo SIR determinista y su modelo de observación.

Qué hace este módulo
--------------------
1. Integra el SIR en fracciones de población:
       ds/dt = -beta * s * i
       di/dt =  beta * s * i - gamma * i
   con beta = R0 * gamma. r = 1 - s - i no se integra porque no
   retroalimenta a s ni a i (se obtiene por conservación).
2. Convierte la trayectoria en *incidencia semanal esperada* de casos
   reportados: mu_k = rho * N * [s(t_k) - s(t_{k+1})].
3. Simula observaciones con ruido binomial negativo.

Por qué estas decisiones (para poder defenderlas)
-------------------------------------------------
* Fracciones en vez de conteos: s e i son O(1) o pequeños, lo que hace
  más fácil fijar tolerancias del integrador. N solo multiplica al final.
* Integramos log(i) en vez de i: al inicio de una ola i ~ 1e-6, y un
  integrador con tolerancia absoluta podría devolver i < 0. Con
  u = log(i) la ecuación es du/dt = beta*s - gamma (regla de la cadena:
  du/dt = (di/dt)/i), que es suave y nunca produce i negativo.
* Incidencia como diferencia de s: las nuevas infecciones entre t_k y
  t_{k+1} son exactamente lo que salió de S, s(t_k) - s(t_{k+1}). Así no
  hay que integrar numéricamente la tasa beta*s*i otra vez.
* Semanas y no días: los casos diarios de la SSA tienen un ciclo de
  día de la semana (menos registro en fines de semana) que el SIR no
  modela; sumar por semana lo elimina sin agregar parámetros.
* Binomial negativa y no Poisson: los conteos reales tienen varianza
  mucho mayor que la media. Con media mu y tamaño k,
  Var = mu + mu^2/k; k -> infinito recupera Poisson.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

# Tolerancias del integrador. Se eligieron para que el error numérico
# (~1e-10 relativo) sea órdenes de magnitud menor que el ruido de
# observación; tests/test_sir.py verifica contra la solución exacta del
# tamaño final, así que si alguien las afloja, el test lo detecta.
RTOL = 1e-10
ATOL = 1e-12


def _derivadas(t, y, beta, gamma):
    """Lado derecho del SIR en variables (s, u = log i)."""
    s, u = y
    i = np.exp(u)
    return [-beta * s * i, beta * s - gamma]


def integrar_sir(R0, gamma, s0, i0, t):
    """Integra el SIR y devuelve s(t) e i(t) en los tiempos pedidos.

    Parámetros
    ----------
    R0 : número reproductivo básico (adimensional). beta = R0 * gamma.
    gamma : tasa de recuperación (1/día); 1/gamma es el periodo infeccioso.
    s0 : fracción susceptible al inicio de la ola (0 < s0 <= 1).
    i0 : fracción infecciosa al inicio de la ola (0 < i0 << 1).
    t : arreglo creciente de tiempos (días) donde se evalúa la solución;
        t[0] es el inicio de la ola.

    Devuelve
    --------
    s, i : arreglos del mismo tamaño que t.
    """
    t = np.asarray(t, dtype=float)
    # El optimizador puede proponer i0 tan chico que exp() da 0 exacto
    # (underflow, i0 < 1e-308). Eso no es un estado inicial válido.
    if not (s0 > 0 and i0 > 0):
        raise ValueError(f"Estado inicial inválido: s0={s0}, i0={i0}")
    beta = R0 * gamma
    sol = solve_ivp(
        _derivadas,
        (t[0], t[-1]),
        [s0, np.log(i0)],
        t_eval=t,
        args=(beta, gamma),
        # LSODA cambia solo entre método rígido y no rígido. El SIR no es
        # rígido en general, pero la fase final de una ola (i decayendo
        # exponencialmente) lo vuelve ligeramente rígido; LSODA lo maneja.
        method="LSODA",
        rtol=RTOL,
        atol=ATOL,
    )
    if not sol.success:
        raise RuntimeError(f"El integrador falló: {sol.message}")
    s, u = sol.y
    return s, np.exp(u)


def incidencia_semanal(R0, gamma, s0, i0, rho, N, n_semanas):
    """Casos reportados esperados por semana: mu_k = rho*N*(s_k - s_{k+1}).

    rho es la fracción de infecciones que termina como caso confirmado
    (subregistro). Se supone constante durante la ola: es una de las
    simplificaciones del modelo y se discute en el escrito.
    """
    t = 7.0 * np.arange(n_semanas + 1)  # bordes de las semanas, en días
    s, _ = integrar_sir(R0, gamma, s0, i0, t)
    nuevas_infecciones = -np.diff(s)  # s decrece, así que -diff >= 0
    # Por redondeo numérico, -diff puede dar -1e-17 cuando la ola ya
    # terminó; lo recortamos a 0 para que la media sea válida.
    return rho * N * np.clip(nuevas_infecciones, 0.0, None)


def infectados_entre(R0, gamma, s0, i0, t_a, t_b):
    """Fracción de la población infectada entre los días t_a y t_b.

    Es s(t_a) - s(t_b): lo que salió de S en ese intervalo. Se compara
    con el *aumento* de seroprevalencia entre dos encuestas. Supuestos
    (se registran en el escrito): toda infección seroconvierte, no hay
    serorreversión y el retraso de seroconversión es despreciable frente
    a la duración de la ola.
    """
    if t_a == 0:
        # solve_ivp exige tiempos estrictamente crecientes, así que no
        # podemos pedir [0, 0, t_b]; en t = 0 sabemos que s = s0.
        s, _ = integrar_sir(R0, gamma, s0, i0, [0.0, t_b])
        return s0 - s[-1]
    s, _ = integrar_sir(R0, gamma, s0, i0, [0.0, t_a, t_b])
    return s[1] - s[2]


def simular_casos(mu, k, rng):
    """Una realización de casos semanales ~ BinNeg(media mu, tamaño k).

    numpy parametriza la binomial negativa con (n, p); la traducción a
    media/tamaño es n = k, p = k / (k + mu). Verificación: la media de
    BinNeg(n, p) es n(1-p)/p = k * (mu/(k+mu)) / (k/(k+mu)) = mu.
    """
    mu = np.asarray(mu, dtype=float)
    p = k / (k + mu)
    return rng.negative_binomial(k, p)
