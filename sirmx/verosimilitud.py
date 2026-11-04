"""Verosimilitud BinNeg y ajuste MLE por ola (parametrización identificable, decisión I2).

θ = [log R_eff(0), log(i0/s0), log(ρ·s0), log k, log w_0..log w_5, δ_1..δ_K]
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .modelo import (ParamsOla, efecto_semana, logpmf_binneg, media_casos)

NOMBRES_BASE = ["log_Reff0", "log_i0_s0", "log_rho_s0", "log_k"] + [f"lw{d}" for d in range(6)]
COTAS_BASE = ([(np.log(0.3), np.log(15.0)), (np.log(1e-10), np.log(0.1)),
               (np.log(1e-6), 0.0), (np.log(0.1), np.log(1e4))] + [(-2.0, 2.0)] * 6)
COTA_DELTA = (-3.0, 3.0)


def theta_a_params(theta, D, N, d0=0, cambios=()):
    """Mapea θ a ParamsOla con s0 = 1 (equivalente exacto por la reescala x = s/s0, j = i/s0)."""
    th = np.asarray(theta, float)
    K = len(cambios)
    return ParamsOla(R0=np.exp(th[0]), s0=1.0, rho=np.exp(th[2]), i0=np.exp(th[1]),
                     k=np.exp(th[3]), D=D, N=N, log_w=efecto_semana(th[4:10]),
                     cambios=tuple(cambios), log_factores=tuple(th[10:10 + K]), d0=d0)


def params_a_theta(p: ParamsOla):
    lw = np.asarray(p.log_w, float)
    lw = lw - lw.mean()
    return np.concatenate([[np.log(p.Reff0), np.log(p.i0 / p.s0), np.log(p.rho_s0), np.log(p.k)],
                           lw[:6], np.asarray(p.log_factores, float)])


def nll(theta, y, D, N, d0=0, cambios=()):
    p = theta_a_params(theta, D, N, d0, cambios)
    mu, _, _ = media_casos(p, len(y))
    v = -np.sum(logpmf_binneg(y, mu, p.k))
    return v if np.isfinite(v) else 1e300


def hessiana(f, x, h=1e-4):
    x = np.asarray(x, float)
    n = len(x)
    H = np.empty((n, n))
    f0 = f(x)
    E = np.eye(n) * h
    fp = np.array([f(x + E[i]) for i in range(n)])
    fm = np.array([f(x - E[i]) for i in range(n)])
    for i in range(n):
        H[i, i] = (fp[i] - 2 * f0 + fm[i]) / h ** 2
        for j in range(i + 1, n):
            H[i, j] = H[j, i] = (f(x + E[i] + E[j]) - fp[i] - fp[j] + f0) / (2 * h * h) \
                + (f(x - E[i] - E[j]) - fm[i] - fm[j] + f0) / (2 * h * h)
    return H


@dataclass
class Ajuste:
    theta: np.ndarray
    nombres: list
    loglik: float
    cov: np.ndarray
    n_inicios: int
    n_cerca_mejor: int
    en_cota: list
    D: float
    N: float
    d0: int
    cambios: tuple
    n_obs: int

    @property
    def se(self):
        return np.sqrt(np.clip(np.diag(self.cov), 0, np.inf))

    def ic(self, nombre, z=1.959964):
        j = self.nombres.index(nombre)
        return self.theta[j] - z * self.se[j], self.theta[j] + z * self.se[j]

    @property
    def n_par(self):
        return len(self.theta)

    @property
    def bic(self):
        # cada cambio cuenta τ y δ (decisión I4)
        return -2 * self.loglik + (self.n_par + len(self.cambios)) * np.log(self.n_obs)

    def params(self):
        return theta_a_params(self.theta, self.D, self.N, self.d0, self.cambios)


def _inicio_aleatorio(rng, K):
    return np.concatenate([[np.log(rng.uniform(1.1, 4.0)), rng.uniform(np.log(1e-7), np.log(1e-3)),
                            rng.uniform(np.log(0.01), np.log(1.0)) - 1e-3,
                            rng.uniform(np.log(2.0), np.log(100.0))],
                           np.zeros(6), np.zeros(K)])


def ajustar_ola(y, D=7.0, N=1e7, d0=0, cambios=(), rng=None, n_inicios=8,
                inicios_extra=(), calcular_cov=True, tol_cerca=0.5):
    """MLE con múltiples inicios. `inicios_extra` permite arranques en caliente."""
    y = np.asarray(y, float)
    K = len(cambios)
    cotas = COTAS_BASE + [COTA_DELTA] * K
    nombres = NOMBRES_BASE + [f"delta{j + 1}" for j in range(K)]
    if rng is None:
        rng = np.random.default_rng(0)
    f = lambda th: nll(th, y, D, N, d0, cambios)
    inicios = [np.asarray(x, float) for x in inicios_extra]
    inicios += [_inicio_aleatorio(rng, K) for _ in range(n_inicios)]
    res = []
    for x0 in inicios:
        x0 = np.clip(x0, [c[0] + 1e-6 for c in cotas], [c[1] - 1e-6 for c in cotas])
        r = minimize(f, x0, method="L-BFGS-B", bounds=cotas,
                     options={"maxiter": 2000, "ftol": 1e-12, "gtol": 1e-7})
        res.append(r)
    vals = np.array([r.fun for r in res])
    mejor = res[int(np.argmin(vals))]
    # pulido final
    r2 = minimize(f, mejor.x, method="L-BFGS-B", bounds=cotas,
                  options={"maxiter": 2000, "ftol": 1e-14, "gtol": 1e-9})
    if r2.fun <= mejor.fun:
        mejor = r2
    th = mejor.x
    en_cota = [nombres[j] for j in range(len(th))
               if min(th[j] - cotas[j][0], cotas[j][1] - th[j]) < 1e-3]
    cov = np.full((len(th), len(th)), np.nan)
    if calcular_cov:
        H = hessiana(f, th)
        try:
            cov = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            cov = np.linalg.pinv(H)
    return Ajuste(theta=th, nombres=nombres, loglik=-mejor.fun, cov=cov,
                  n_inicios=len(inicios), n_cerca_mejor=int(np.sum(vals - mejor.fun <= tol_cerca)),
                  en_cota=en_cota, D=D, N=N, d0=d0, cambios=tuple(cambios), n_obs=len(y))
