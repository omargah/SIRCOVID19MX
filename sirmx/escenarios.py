"""Escenarios sintéticos con parámetros conocidos (paso 3). Ningún dato real."""
from __future__ import annotations

import numpy as np

from .modelo import ParamsOla, simular_casos

SEMILLA = 20261104
LOG_W = np.log(np.array([1.15, 1.10, 1.05, 1.05, 1.00, 0.80, 0.70]))
LOG_W = LOG_W - LOG_W.mean()


def escenario(nombre: str) -> tuple[ParamsOla, int]:
    if nombre == "ola_simple":
        return ParamsOla(R0=2.0, s0=1.0, rho=0.5, i0=1e-5, k=20.0, D=7.0, N=1e7,
                         log_w=LOG_W.copy()), 200
    if nombre == "subregistro":
        # ρ = 0.15 y s0 = 0.8 → R_eff(0) = 2.0, ρ·s0 = 0.12
        return ParamsOla(R0=2.5, s0=0.8, rho=0.15, i0=2e-5, k=20.0, D=7.0, N=1e7,
                         log_w=LOG_W.copy()), 200
    if nombre == "cambio_beta":
        return ParamsOla(R0=2.5, s0=1.0, rho=0.3, i0=1e-5, k=20.0, D=7.0, N=1e7,
                         log_w=LOG_W.copy(), cambios=(40,), log_factores=(np.log(0.6),)), 200
    if nombre == "dos_cambios":
        return ParamsOla(R0=2.5, s0=1.0, rho=0.3, i0=1e-5, k=20.0, D=7.0, N=1e7,
                         log_w=LOG_W.copy(), cambios=(35, 45),
                         log_factores=(np.log(0.7), np.log(0.7))), 200
    if nombre.startswith("dos_cambios_sep"):
        sep = int(nombre.removeprefix("dos_cambios_sep"))
        return ParamsOla(R0=2.5, s0=1.0, rho=0.3, i0=1e-5, k=20.0, D=7.0, N=1e7,
                         log_w=LOG_W.copy(), cambios=(35, 35 + sep),
                         log_factores=(np.log(0.7), np.log(0.7))), 200
    raise KeyError(nombre)


ESCENARIOS_PASO3 = ("ola_simple", "subregistro", "cambio_beta")


def datos(nombre: str, rng: np.random.Generator):
    p, T = escenario(nombre)
    y, mu, inc, S = simular_casos(p, T, rng)
    return p, y, mu, inc, S
