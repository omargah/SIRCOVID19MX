"""Modelo SIR por ola con observación casos = ρ × incidencia (BinNeg + día de semana).

Ver docs/decisiones.md (D0, I2) para las convenciones.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.special import gammaln

NSUB = 4  # subpasos RK4 por día


def _sir_rk4(beta_dia, gamma, s0, i0, nsub):
    """Integra el SIR (fracciones) con RK4; devuelve la incidencia diaria por habitante.

    beta_dia: arreglo de longitud T con β constante en cada día.
    Devuelve S (T+1,), I (T+1,).
    """
    T = len(beta_dia)
    h = 1.0 / nsub
    g = float(gamma)
    s = float(s0)
    i = float(i0)
    S = np.empty(T + 1)
    I = np.empty(T + 1)
    S[0], I[0] = s, i
    for t in range(T):
        b = float(beta_dia[t])
        for _ in range(nsub):
            f1 = b * s * i
            k1s, k1i = -f1, f1 - g * i
            s2, i2 = s + 0.5 * h * k1s, i + 0.5 * h * k1i
            f2 = b * s2 * i2
            k2s, k2i = -f2, f2 - g * i2
            s3, i3 = s + 0.5 * h * k2s, i + 0.5 * h * k2i
            f3 = b * s3 * i3
            k3s, k3i = -f3, f3 - g * i3
            s4, i4 = s + h * k3s, i + h * k3i
            f4 = b * s4 * i4
            k4s, k4i = -f4, f4 - g * i4
            s += h / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
            i += h / 6.0 * (k1i + 2 * k2i + 2 * k3i + k4i)
        S[t + 1], I[t + 1] = s, i
    return S, I


try:  # numba es opcional: misma aritmética, ~100x más rápido
    from numba import njit
    _sir_rk4_rapido = njit(cache=True)(_sir_rk4)
except ImportError:  # pragma: no cover
    _sir_rk4_rapido = _sir_rk4


def sir_incidencia(beta_dia, gamma, s0, i0, nsub=NSUB):
    """Incidencia diaria por habitante inc_t = s(t) − s(t+1); devuelve inc, S, I."""
    S, I = _sir_rk4_rapido(np.ascontiguousarray(beta_dia, dtype=np.float64),
                           float(gamma), float(s0), float(i0), int(nsub))
    inc = S[:-1] - S[1:]
    return np.maximum(inc, 0.0), S, I


def beta_por_tramos(beta0, T, cambios=(), log_factores=()):
    """β(t) = β0 · exp(Σ_j δ_j · 1[t ≥ τ_j])."""
    lb = np.full(T, np.log(beta0))
    for tau, d in zip(cambios, log_factores):
        lb[int(tau):] += d
    return np.exp(lb)


def efecto_semana(log_w6):
    """6 parámetros libres → 7 log-efectos con suma cero."""
    lw = np.empty(7)
    lw[:6] = log_w6
    lw[6] = -np.sum(log_w6)
    return lw


@dataclass
class ParamsOla:
    """Parámetros "naturales" de una ola. Con casos solos, solo R0*s0 y rho*s0 son identificables."""

    R0: float
    s0: float
    rho: float
    i0: float
    k: float
    D: float = 7.0
    N: float = 1e7
    log_w: np.ndarray = field(default_factory=lambda: np.zeros(7))  # suma cero
    cambios: tuple = ()
    log_factores: tuple = ()
    d0: int = 0  # día de la semana del día 0

    @property
    def gamma(self):
        return 1.0 / self.D

    @property
    def Reff0(self):
        return self.R0 * self.s0

    @property
    def rho_s0(self):
        return self.rho * self.s0


def media_casos(p: ParamsOla, T: int):
    """μ_t = ρ · N · inc_t · w_{dow(t)} y la incidencia real (infecciones/día)."""
    beta = beta_por_tramos(p.R0 * p.gamma, T, p.cambios, p.log_factores)
    inc, S, I = sir_incidencia(beta, p.gamma, p.s0, p.i0)
    dow = (np.arange(T) + p.d0) % 7
    mu = p.rho * p.N * inc * np.exp(np.asarray(p.log_w)[dow])
    return mu, p.N * inc, S


def logpmf_binneg(y, mu, k):
    mu = np.maximum(mu, 1e-12)
    return (gammaln(y + k) - gammaln(k) - gammaln(y + 1)
            + k * (np.log(k) - np.log(k + mu)) + y * (np.log(mu) - np.log(k + mu)))


def muestra_binneg(rng: np.random.Generator, mu, k):
    """BinNeg(media mu, dispersión k) como mezcla Gamma-Poisson."""
    lam = rng.gamma(shape=k, scale=np.maximum(mu, 0.0) / k)
    return rng.poisson(lam)


def simular_casos(p: ParamsOla, T: int, rng: np.random.Generator):
    mu, inc, S = media_casos(p, T)
    y = muestra_binneg(rng, mu, p.k)
    return y, mu, inc, S
