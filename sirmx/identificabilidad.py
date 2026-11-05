"""Perfiles de verosimilitud (paso 4, H1).

Los perfiles de R0 y s0 se calculan en la parametrización *natural*
φ = [log R0, logit s0, log i0, logit ρ, log k, lw0..lw5], optimizando de verdad los
demás parámetros (no se usa la reescala analítica), para que la prueba de la cresta
plana sea empírica.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit

from .modelo import ParamsOla, efecto_semana, logpmf_binneg, media_casos
from .verosimilitud import Ajuste, COTAS_BASE, nll

NOMBRES_NAT = ["log_R0", "logit_s0", "log_i0", "logit_rho", "log_k"] + [f"lw{d}" for d in range(6)]
COTAS_NAT = [(np.log(0.3), np.log(60.0)), (-12.0, 12.0), (np.log(1e-10), np.log(0.1)),
             (-14.0, 12.0)] + COTAS_BASE[3:]


def phi_a_params(phi, D, N, d0=0):
    f = np.asarray(phi, float)
    return ParamsOla(R0=np.exp(f[0]), s0=expit(f[1]), i0=np.exp(f[2]), rho=expit(f[3]),
                     k=np.exp(f[4]), D=D, N=N, log_w=efecto_semana(f[5:11]), d0=d0)


def nll_natural(phi, y, D, N, d0=0):
    p = phi_a_params(phi, D, N, d0)
    if p.s0 + p.i0 > 1:
        return 1e300
    mu, _, _ = media_casos(p, len(y))
    v = -np.sum(logpmf_binneg(y, mu, p.k))
    return v if np.isfinite(v) else 1e300


def _opt(f, x0, cotas):
    x0 = np.clip(x0, [c[0] + 1e-6 for c in cotas], [c[1] - 1e-6 for c in cotas])
    return minimize(f, x0, method="L-BFGS-B", bounds=cotas,
                    options={"maxiter": 3000, "ftol": 1e-13, "gtol": 1e-8})


def perfil(f, theta_hat, j, valores, cotas, rng, n_aleatorios=2, escalas=(0.05, 0.5)):
    """Perfil de log-verosimilitud del parámetro j.

    La rejilla se recorre desde el valor más cercano al MLE hacia afuera (a cada lado), con
    arranque en caliente desde el punto vecino ya resuelto, desde el MLE y desde
    perturbaciones aleatorias a dos escalas; en cada punto se queda el mejor óptimo."""
    theta_hat = np.asarray(theta_hat, float)
    valores = np.asarray(valores, float)
    libres = [i for i in range(len(theta_hat)) if i != j]
    cot = [cotas[i] for i in libres]
    out = np.full(len(valores), np.nan)
    orden = np.argsort(valores)
    c = int(np.argmin(np.abs(valores[orden] - theta_hat[j])))
    for lado in (orden[c::-1], orden[c + 1:]):
        previo = theta_hat[libres].copy()
        for n in lado:
            v = valores[n]

            def g(z, v=v):
                th = theta_hat.copy()
                th[j] = v
                th[libres] = z
                return f(th)

            inicios = [previo, theta_hat[libres]]
            for e in escalas:
                inicios += [previo + e * rng.normal(size=len(libres)) for _ in range(n_aleatorios)]
            r = min((_opt(g, x0, cot) for x0 in inicios), key=lambda r: r.fun)
            previo = r.x
            out[n] = -r.fun
    return out


def ajustar_natural(y, D, N, ajuste_ident: Ajuste, rng, s0_ini=0.9):
    """MLE en la parametrización natural, arrancando desde un punto de la cresta."""
    th = ajuste_ident.theta
    s0 = s0_ini
    rho = min(np.exp(th[2]) / s0, 0.999)
    phi0 = np.concatenate([[th[0] - np.log(s0), logit(s0), th[1] + np.log(s0), logit(rho), th[3]],
                           th[4:10]])
    f = lambda ph: nll_natural(ph, y, D, N, ajuste_ident.d0)
    r = _opt(f, phi0, COTAS_NAT)
    return r.x, -r.fun


def intervalo_perfil(valores, ll, umbral=1.920729):
    """Conjunto {v : ℓ_max − ℓ(v) ≤ umbral} con interpolación lineal en los bordes.
    Devuelve (lo, hi, abierto_lo, abierto_hi): abierto = la región toca el borde de la rejilla."""
    valores = np.asarray(valores)
    d = ll.max() - ll
    dentro = d <= umbral
    idx = np.where(dentro)[0]
    a, b = idx[0], idx[-1]

    def cruce(i_in, i_out):
        x0, x1, d0, d1 = valores[i_in], valores[i_out], d[i_in], d[i_out]
        return x0 + (umbral - d0) * (x1 - x0) / (d1 - d0)

    lo = cruce(a, a - 1) if a > 0 else valores[0]
    hi = cruce(b, b + 1) if b < len(valores) - 1 else valores[-1]
    return lo, hi, a == 0, b == len(valores) - 1
