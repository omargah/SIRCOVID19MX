"""Tasa de crecimiento r con ventana fija, IC por perfil, bootstrap paramétrico y R(D) (paso 5, I3)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize

from .modelo import efecto_semana, logpmf_binneg, muestra_binneg

LONGITUD = 21
UMBRAL = 20.0
D_ESCENARIOS = (5.0, 7.0, 10.0)
CHI2_95 = 3.841459


def ventana_fija(y, longitud=LONGITUD, umbral=UMBRAL):
    """Primer día t0 en que la media móvil de 7 días (días t0-6..t0) alcanza `umbral`;
    si eso ocurre antes del día 6, t0 = 0. La ventana es [t0, t0 + longitud)."""
    y = np.asarray(y, float)
    mm = np.convolve(y, np.ones(7) / 7, mode="valid")  # mm[j] = media de y[j..j+6]
    j = np.where(mm >= umbral)[0]
    if len(j) == 0:
        raise ValueError("la serie nunca alcanza el umbral")
    t0 = int(j[0])
    if t0 + longitud > len(y):
        raise ValueError("ventana fuera de la serie")
    return t0, t0 + longitud


def _nll(par, y, t, dow, logk_fijo=None):
    a, r = par[0], par[1]
    logk = par[2] if logk_fijo is None else logk_fijo
    lw = efecto_semana(par[3:9])
    mu = np.exp(a + r * t + lw[dow])
    return -np.sum(logpmf_binneg(y, mu, np.exp(logk)))


def _ajustar(y, t, dow, r_fijo=None, x0=None, logk_fijo=None):
    y = np.asarray(y, float)
    if x0 is None:
        b = np.polyfit(t, np.log(y + 0.5), 1)
        x0 = np.concatenate([[b[1], b[0], np.log(20.0)], np.zeros(6)])
    if logk_fijo is not None:
        x0 = np.array(x0, float)
        x0[2] = logk_fijo
    if r_fijo is None:
        f = lambda p: _nll(p, y, t, dow, logk_fijo)
        z0 = x0
    else:
        f = lambda q: _nll(np.concatenate([[q[0], r_fijo], q[1:]]), y, t, dow, logk_fijo)
        z0 = np.delete(x0, 1)
    res = minimize(f, z0, method="BFGS", options={"gtol": 1e-7, "maxiter": 2000})
    if r_fijo is None:
        return res.x, res.fun
    return np.concatenate([[res.x[0], r_fijo], res.x[1:]]), res.fun


@dataclass
class EstimacionR:
    r: float
    ic_perfil: tuple
    ic_bootstrap: tuple
    ventana: tuple
    r_boot: np.ndarray
    par: np.ndarray

    def R_de_D(self, D):
        """SIR (periodo infeccioso exponencial): R = 1 + r·D."""
        return (1 + self.r * D, 1 + self.ic_perfil[0] * D, 1 + self.ic_perfil[1] * D,
                1 + self.ic_bootstrap[0] * D, 1 + self.ic_bootstrap[1] * D)

    def tabla_D(self, Ds=D_ESCENARIOS):
        return {D: self.R_de_D(D) for D in Ds}


def estimar_r(y, rng: np.random.Generator, d0=0, B=200, longitud=LONGITUD, umbral=UMBRAL,
              k_fijo=None):
    """`k_fijo`: dispersión tomada del ajuste de la ola completa (decisión C4). En ventanas
    cortas de conteos bajos el MLE de k está muy sesgado hacia arriba y subestima la varianza."""
    lk = None if k_fijo is None else float(np.log(k_fijo))
    a, b = ventana_fija(y, longitud, umbral)
    yw = np.asarray(y[a:b], float)
    t = np.arange(b - a, dtype=float)
    dow = (np.arange(a, b) + d0) % 7
    par, f0 = _ajustar(yw, t, dow, logk_fijo=lk)
    r_hat = par[1]

    # IC por perfil: raíces de 2(ℓ̂ − ℓ_p(r)) = χ²₁
    def dev(r):
        _, fr = _ajustar(yw, t, dow, r_fijo=r, x0=par, logk_fijo=lk)
        return 2 * (fr - f0) - CHI2_95

    paso = 0.02
    lo_ext = r_hat - paso
    while dev(lo_ext) < 0:
        lo_ext -= paso
    hi_ext = r_hat + paso
    while dev(hi_ext) < 0:
        hi_ext += paso
    ic_p = (brentq(dev, lo_ext, r_hat, xtol=1e-7), brentq(dev, r_hat, hi_ext, xtol=1e-7))

    # bootstrap paramétrico desde el ajuste BinNeg
    mu = np.exp(par[0] + par[1] * t + efecto_semana(par[3:9])[dow])
    k = np.exp(par[2] if lk is None else lk)
    rb = np.empty(B)
    for i in range(B):
        yb = muestra_binneg(rng, mu, k)
        rb[i] = _ajustar(yb, t, dow, x0=par, logk_fijo=lk)[0][1]
    ic_b = tuple(np.percentile(rb, [2.5, 97.5])) if B > 0 else (np.nan, np.nan)
    return EstimacionR(r=r_hat, ic_perfil=ic_p, ic_bootstrap=ic_b, ventana=(a, b), r_boot=rb, par=par)


def r_verdadero(p, S, ventana):
    """Promedio en la ventana de la tasa instantánea γ(R0·s(t)·β(t)/β0 − 1)."""
    a, b = ventana
    from .modelo import beta_por_tramos
    beta = beta_por_tramos(p.R0 * p.gamma, len(S) - 1, p.cambios, p.log_factores)
    s = 0.5 * (S[a:b] + S[a + 1:b + 1])
    return float(np.mean(beta[a:b] * s - p.gamma))
