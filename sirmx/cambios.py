"""Detección de puntos de cambio de β: fecha y tamaño (paso 6, decisión I4).

β(t) = β0 · exp(Σ δ_j 1[t ≥ τ_j]), K ∈ {0, 1, 2}, selección por BIC (τ cuenta como parámetro).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .verosimilitud import Ajuste, ajustar_ola

PASO = 2
SEP_MIN = 5
SEPARACIONES_INICIO = (3, 5, 8, 12)
CHI2_95 = 3.841459


def rango_activo(y, frac=0.05):
    """Días donde la media móvil centrada de 7 días es ≥ frac·máximo: fuera de ahí no hay
    información sobre β y un cambio no es identificable."""
    y = np.asarray(y, float)
    mm = np.convolve(y, np.ones(7) / 7, mode="same")
    idx = np.where(mm >= frac * mm.max())[0]
    return int(idx[0]) + 1, int(idx[-1])


def _ajuste_fijo(y, D, N, d0, cambios, inicios, rng):
    return ajustar_ola(y, D=D, N=N, d0=d0, cambios=tuple(cambios), rng=rng, n_inicios=0,
                       inicios_extra=inicios, calcular_cov=False)


def _barrido(y, D, N, d0, fijos, base: Ajuste, candidatos, rng, extra=None):
    """Agrega un cambio en cada τ candidato (los `fijos` se mantienen). Devuelve dict τ→Ajuste."""
    out = {}
    previo = extra
    for tau in candidatos:
        if any(abs(tau - f) < SEP_MIN for f in fijos):
            continue
        cambios = sorted(list(fijos) + [tau])
        pos = cambios.index(tau)

        def con_delta(theta_base, delta=0.0):
            d = list(theta_base[10:])
            d.insert(pos, delta)
            return np.concatenate([theta_base[:10], d])

        inicios = [con_delta(base.theta)]
        if previo is not None and len(previo.theta) == 10 + len(cambios):
            inicios.append(previo.theta)
        a = _ajuste_fijo(y, D, N, d0, cambios, inicios, rng)
        out[tau] = a
        previo = a
    return out


@dataclass
class ResultadoCambios:
    ajustes: dict          # K → Ajuste (con covarianza)
    bic: dict              # K → BIC
    K: int
    perfiles_tau: dict = field(default_factory=dict)  # j → (taus, loglik)

    @property
    def mejor(self) -> Ajuste:
        return self.ajustes[self.K]

    def ic_tau(self, j):
        taus, ll = self.perfiles_tau[j]
        dentro = taus[2 * (ll.max() - ll) <= CHI2_95]
        return int(dentro.min()), int(dentro.max())

    def ic_factor(self, j):
        lo, hi = self.mejor.ic(f"delta{j + 1}")
        return float(np.exp(lo)), float(np.exp(hi))


def _mejor_K(y, D, N, d0, base, fijos, candidatos, rng):
    barr = _barrido(y, D, N, d0, fijos, base, candidatos, rng)
    tau = max(barr, key=lambda t: barr[t].loglik)
    # refinamiento a resolución diaria
    finos = [t for t in range(tau - PASO + 1, tau + PASO) if t not in barr and candidatos[0] <= t <= candidatos[-1]]
    barr.update(_barrido(y, D, N, d0, fijos, base, finos, rng, extra=barr[tau]))
    tau = max(barr, key=lambda t: barr[t].loglik)
    return tau, barr[tau]


def detectar_cambios(y, D=7.0, N=1e7, d0=0, rng=None, Kmax=2, max_barridos=4):
    rng = np.random.default_rng(0) if rng is None else rng
    y = np.asarray(y, float)
    a, b = rango_activo(y)
    candidatos = list(range(a, b + 1, PASO))
    ajustes = {0: ajustar_ola(y, D=D, N=N, d0=d0, rng=rng, n_inicios=8, calcular_cov=False)}
    taus = {0: ()}
    if Kmax >= 1:
        t1, a1 = _mejor_K(y, D, N, d0, ajustes[0], [], candidatos, rng)
        ajustes[1], taus[1] = a1, (t1,)
    if Kmax >= 2:
        t1 = taus[1][0]
        # arranques: (a) codicioso, τ1 fijo + mejor τ2; (b) partir τ1 en dos cambios
        # simétricos (τ1−s, τ1+s), cada uno con la mitad del log-factor (cambios cercanos)
        t2, a2 = _mejor_K(y, D, N, d0, ajustes[1], [t1], candidatos, rng)
        actual = sorted([t1, t2])
        d1 = ajustes[1].theta[10]
        for sep in SEPARACIONES_INICIO:
            par = [t1 - sep, t1 + sep]
            if par[0] < a or par[1] > b:
                continue
            ai = _ajuste_fijo(y, D, N, d0, par, [np.r_[ajustes[1].theta[:10], d1 / 2, d1 / 2]], rng)
            if ai.loglik > a2.loglik:
                a2, actual = ai, par
        # descenso coordenado: re-optimiza cada τ con el otro fijo
        for _ in range(max_barridos):
            cambio = False
            for j in range(2):
                otro = [actual[1 - j]]
                quitar = list(a2.theta[:10]) + [a2.theta[10 + (1 - j)]]
                base = _ajuste_fijo(y, D, N, d0, otro, [np.array(quitar)], rng)
                tj, aj = _mejor_K(y, D, N, d0, base, otro, candidatos, rng)
                if aj.loglik > a2.loglik + 1e-6:
                    a2, actual, cambio = aj, sorted(otro + [tj]), True
            if not cambio:
                break
        ajustes[2], taus[2] = a2, tuple(actual)
    # covarianzas en los τ elegidos
    for K in ajustes:
        ajustes[K] = ajustar_ola(y, D=D, N=N, d0=d0, cambios=taus[K], rng=rng, n_inicios=0,
                                 inicios_extra=[ajustes[K].theta])
    bic = {K: ajustes[K].bic for K in ajustes}
    K = min(bic, key=bic.get)
    res = ResultadoCambios(ajustes=ajustes, bic=bic, K=K)
    # perfil de cada τ (condicional a los demás) a resolución diaria, ±10 días
    for j, tj in enumerate(taus[K]):
        otros = [t for i, t in enumerate(taus[K]) if i != j]
        base_th = np.delete(ajustes[K].theta, 10 + j)
        base = _ajuste_fijo(y, D, N, d0, otros, [base_th], rng)
        cand = [t for t in range(tj - 10, tj + 11) if a <= t <= b]
        barr = _barrido(y, D, N, d0, otros, base, cand, rng)
        ts = np.array(sorted(barr))
        res.perfiles_tau[j] = (ts, np.array([barr[t].loglik for t in ts]))
    return res
