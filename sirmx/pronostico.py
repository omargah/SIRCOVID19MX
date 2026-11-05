"""Pronóstico en tiempo simulado a 1–4 semanas: WIS, cobertura, error del pico (paso 7, I4)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .modelo import media_casos, muestra_binneg
from .verosimilitud import ajustar_ola, theta_a_params

NIVELES = np.array([0.01, 0.025] + [round(0.05 * i, 2) for i in range(1, 20)] + [0.975, 0.99])
HORIZONTES = (1, 2, 3, 4)


# ---------------------------------------------------------------- métricas
def wis(y, q, niveles=NIVELES):
    """Weighted interval score (Bracher et al. 2021) con K intervalos centrales + mediana.

    `q` son los cuantiles en `niveles` (simétricos, con 0.5). Se calcula directamente con
    la definición por intervalos."""
    niveles = np.asarray(niveles)
    q = np.asarray(q, float)
    m = q[np.argmin(np.abs(niveles - 0.5))]
    inferiores = niveles[niveles < 0.5]
    total = 0.5 * abs(y - m)
    for tau in inferiores:
        alfa = 2 * tau
        l = q[np.argmin(np.abs(niveles - tau))]
        u = q[np.argmin(np.abs(niveles - (1 - tau)))]
        IS = (u - l) + 2 / alfa * max(l - y, 0) + 2 / alfa * max(y - u, 0)
        total += alfa / 2 * IS
    return total / (len(inferiores) + 0.5)


def cubre(y, q, nivel_central, niveles=NIVELES):
    a = (1 - nivel_central) / 2
    l = q[np.argmin(np.abs(niveles - a))]
    u = q[np.argmin(np.abs(niveles - (1 - a)))]
    return bool(l <= y <= u)


def semanal(x, inicio, n_semanas):
    x = np.asarray(x, float)
    return np.array([x[inicio + 7 * h: inicio + 7 * (h + 1)].sum() for h in range(n_semanas)])


# ---------------------------------------------------------------- modelo SIR
def _cov_muestreable(cov, n):
    cov = np.where(np.isfinite(cov), cov, 0.0)
    cov = 0.5 * (cov + cov.T)
    w, V = np.linalg.eigh(cov)
    w = np.clip(w, 1e-10, 4.0)  # varianzas absurdas (no identificado) se acotan
    return (V * w) @ V.T


def pronostico_sir(y_hasta, T_total, D, N, d0, rng, n_tray=300, n_inicios=8):
    """Ajusta con y[:t0] y simula trayectorias hasta T_total. Devuelve (casos simulados
    (n_tray, T_total), medias (n_tray, T_total), ajuste)."""
    a = ajustar_ola(y_hasta, D=D, N=N, d0=d0, rng=rng, n_inicios=n_inicios)
    cov = _cov_muestreable(a.cov, len(a.theta))
    ths = rng.multivariate_normal(a.theta, cov, size=n_tray, method="eigh")
    ths[0] = a.theta
    mus = np.empty((n_tray, T_total))
    ys = np.empty((n_tray, T_total))
    for i, th in enumerate(ths):
        p = theta_a_params(th, D, N, d0)
        mus[i] = media_casos(p, T_total)[0]
        ys[i] = muestra_binneg(rng, mus[i], p.k)
    return ys, mus, a


# ---------------------------------------------------------------- persistencia
def pronostico_persistencia(y_hasta, rng, n_semanas=4, n_muestras=2000):
    """Baseline al estilo del COVID-19 Forecast Hub: mediana = último valor semanal;
    incertidumbre por diferencias semanales pasadas simetrizadas, sumadas h veces."""
    t0 = len(y_hasta)
    nsem = t0 // 7
    w = semanal(y_hasta, t0 - 7 * nsem, nsem)
    ultimo = w[-1]
    dif = np.diff(w)
    dif = np.concatenate([dif, -dif]) if len(dif) else np.zeros(1)
    qs = []
    for h in range(1, n_semanas + 1):
        tray = ultimo + rng.choice(dif, size=(n_muestras, h)).sum(axis=1)
        tray = np.maximum(tray, 0)
        q = np.quantile(tray, NIVELES)
        q[np.argmin(np.abs(NIVELES - 0.5))] = ultimo  # mediana exacta = persistencia
        qs.append(np.sort(q))
    return np.array(qs), ultimo


# ---------------------------------------------------------------- evaluación
@dataclass
class Evaluacion:
    origenes: list
    wis_modelo: np.ndarray        # (origen, horizonte)
    wis_persistencia: np.ndarray
    cob50_modelo: np.ndarray
    cob95_modelo: np.ndarray
    cob50_persistencia: np.ndarray
    cob95_persistencia: np.ndarray
    pico_real: tuple              # (día de inicio de la semana pico, altura)
    error_pico_modelo: list       # [(origen, error_días, error_relativo_altura)]
    error_pico_persistencia: list

    def resumen(self):
        f = lambda e: float(np.mean([abs(x[1]) for x in e])) if e else float("nan")
        g = lambda e: float(np.mean([abs(x[2]) for x in e])) if e else float("nan")
        return {
            "WIS_modelo_por_h": self.wis_modelo.mean(0).tolist(),
            "WIS_persistencia_por_h": self.wis_persistencia.mean(0).tolist(),
            "WIS_relativo": float(self.wis_modelo.mean() / self.wis_persistencia.mean()),
            "cob50_modelo": float(self.cob50_modelo.mean()),
            "cob95_modelo": float(self.cob95_modelo.mean()),
            "cob50_persistencia": float(self.cob50_persistencia.mean()),
            "cob95_persistencia": float(self.cob95_persistencia.mean()),
            "EAM_fecha_pico_modelo_dias": f(self.error_pico_modelo),
            "EAM_fecha_pico_persistencia_dias": f(self.error_pico_persistencia),
            "EAM_altura_pico_modelo_rel": g(self.error_pico_modelo),
            "EAM_altura_pico_persistencia_rel": g(self.error_pico_persistencia),
        }


def evaluar(y, mu_real, D, N, rng, d0=0, origenes=None, n_tray=300):
    """Evaluación en tiempo simulado. Las semanas se alinean al día 0."""
    y = np.asarray(y, float)
    T = len(y)
    if origenes is None:
        origenes = list(range(21, T - 28 + 1, 7))
    nsem_total = T // 7
    real_sem = semanal(mu_real, 0, nsem_total)
    sem_pico = int(np.argmax(real_sem))
    pico_real = (7 * sem_pico, float(real_sem[sem_pico]))
    H = len(HORIZONTES)
    W_m, W_p = np.zeros((len(origenes), H)), np.zeros((len(origenes), H))
    c50m, c95m = np.zeros((len(origenes), H)), np.zeros((len(origenes), H))
    c50p, c95p = np.zeros((len(origenes), H)), np.zeros((len(origenes), H))
    epm, epp = [], []
    for n, t0 in enumerate(origenes):
        ys, mus, _ = pronostico_sir(y[:t0], 7 * nsem_total, D, N, d0, rng, n_tray=n_tray)
        q_p, ultimo = pronostico_persistencia(y[:t0], rng)
        obs = semanal(y, t0, H)
        for h in range(H):
            sim = ys[:, t0 + 7 * h: t0 + 7 * (h + 1)].sum(axis=1)
            q_m = np.quantile(sim, NIVELES)
            W_m[n, h], W_p[n, h] = wis(obs[h], q_m), wis(obs[h], q_p[h])
            c50m[n, h], c95m[n, h] = cubre(obs[h], q_m, 0.5), cubre(obs[h], q_m, 0.95)
            c50p[n, h], c95p[n, h] = cubre(obs[h], q_p[h], 0.5), cubre(obs[h], q_p[h], 0.95)
        if t0 < pico_real[0] + 7:  # origen antes de terminar la semana pico
            med = np.median(np.array([semanal(m, 0, nsem_total) for m in mus]), axis=0)
            futuras = med.copy()
            futuras[: t0 // 7] = -np.inf  # el pico pronosticado se busca desde la semana actual
            sp = int(np.argmax(futuras))
            epm.append((t0, 7 * sp - pico_real[0], med[sp] / pico_real[1] - 1))
            sem_actual = (t0 - 7) // 7
            epp.append((t0, 7 * sem_actual - pico_real[0], ultimo / pico_real[1] - 1))
    return Evaluacion(origenes, W_m, W_p, c50m, c95m, c50p, c95p, pico_real, epm, epp)
