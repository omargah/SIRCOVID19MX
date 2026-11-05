"""Adaptador entre las pruebas de teoría (a–k) y la firma actual de src/sir.py.

Las pruebas se escribieron contra la versión anterior de src/sir.py:

    integrar_sir(R0, gamma, s0, i0, t) -> (s, i)        # fracciones, s0 = susceptibles

La versión actual (commit f9745f7) es:

    integrar_sir(R0, D, S0, I0, N, t) -> (S, I, R)      # personas, D = 1/gamma
    incidencia_semanal(R0, gamma, s0, i0, rho, N, n_semanas)
                       # aquí s0 = (S0 + I0)/N: fracción NO inmune, incluye a I0

Este módulo solo traduce las llamadas. No cambia ecuaciones, integrador ni
tolerancias: cada prueba sigue comprobando lo mismo que antes.

Traducción:
  * Se usa N = 1: S, I quedan en fracciones, igual que antes. (Las pruebas
    que necesitan otra N pasan por incidencia_semanal, que ya recibe N.)
  * gamma -> D = 1/gamma.
  * s0 y i0 se toman como antes (S0 = s0, I0 = i0). El sir.py actual exige
    S0 + I0 <= N. Los datos de prueba que antes sumaban más de 1 (s0 = 1.0
    con i0 > 0) se cambiaron en la propia prueba a s0 = 1 - i0. Aquí solo se
    corrige el redondeo de punto flotante (S0 + I0 pasa de 1 por 1 ulp).
  * Se descarta R, que las pruebas calculan como 1 - s - i.
"""
import numpy as np

from src import sir


def integrar_sir_frac(R0, gamma, s0, i0, t):
    """Misma firma que tenía sir.integrar_sir. Devuelve (s, i)."""
    S0 = s0
    if s0 > 0 and i0 > 0 and s0 + i0 - 1.0 <= 1e-15:
        while S0 + i0 > 1.0:  # guarda de redondeo, como en sir.estado_inicial
            S0 = np.nextafter(S0, 0.0)
    S, I, _ = sir.integrar_sir(R0, 1.0 / gamma, S0, i0, 1.0, t)
    return S, I


def incidencia_semanal_frac(R0, gamma, s0, i0, rho, N, n_semanas):
    """Misma semántica de s0 que la firma vieja (s0 = susceptibles).

    sir.incidencia_semanal espera s0 = (S0 + I0)/N, así que se le pasa s0 + i0.
    """
    return sir.incidencia_semanal(R0, gamma, s0 + i0, i0, rho, N, n_semanas)
