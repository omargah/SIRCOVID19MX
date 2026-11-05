"""Tabla valor real vs estimado (paso 3) y estudio de cobertura."""
from __future__ import annotations

import numpy as np

from .escenarios import ESCENARIOS_PASO3, SEMILLA, datos, escenario
from .verosimilitud import ajustar_ola, params_a_theta

# cantidad → (índice en θ, transformación al reportar)
PRINCIPALES = {"R_eff(0)": 0, "i0/s0": 1, "rho*s0": 2, "k": 3}


def fila(nombre, verdadero, est, lo, hi):
    return {"escenario": None, "parametro": nombre, "real": float(verdadero), "estimado": float(est),
            "ic_lo": float(lo), "ic_hi": float(hi), "cubre": bool(lo <= verdadero <= hi),
            "err_rel": float(est / verdadero - 1) if verdadero != 0 else float("nan")}


def tabla_escenario(nombre, rng=None, n_inicios=8):
    """Ajusta el escenario y devuelve (filas, ajuste, θ real). τ se toma como conocido en el paso 3
    (la detección de τ es el paso 6)."""
    rng = np.random.default_rng(SEMILLA) if rng is None else rng
    p, y, *_ = datos(nombre, rng)
    a = ajustar_ola(y, D=p.D, N=p.N, d0=p.d0, cambios=p.cambios, rng=rng, n_inicios=n_inicios)
    tv = params_a_theta(p)
    filas = []
    for q, j in PRINCIPALES.items():
        lo, hi = a.ic(a.nombres[j])
        filas.append(fila(q, np.exp(tv[j]), np.exp(a.theta[j]), np.exp(lo), np.exp(hi)))
    for c in range(len(p.cambios)):
        j = 10 + c
        lo, hi = a.ic(a.nombres[j])
        filas.append(fila(f"factor beta tau={p.cambios[c]}", np.exp(tv[j]), np.exp(a.theta[j]),
                          np.exp(lo), np.exp(hi)))
    for d in range(6):
        j = 4 + d
        lo, hi = a.ic(a.nombres[j])
        filas.append(fila(f"w_{d}", np.exp(tv[j]), np.exp(a.theta[j]), np.exp(lo), np.exp(hi)))
    # con s0 conocido de fuera (serología), ρ y R0 se recuperan por separado
    if p.s0 != 1.0 or p.rho != 1.0:
        lo, hi = a.ic("log_rho_s0")
        filas.append(fila("rho (s0 conocido)", p.rho, np.exp(a.theta[2]) / p.s0,
                          np.exp(lo) / p.s0, np.exp(hi) / p.s0))
        lo, hi = a.ic("log_Reff0")
        filas.append(fila("R0 (s0 conocido)", p.R0, np.exp(a.theta[0]) / p.s0,
                          np.exp(lo) / p.s0, np.exp(hi) / p.s0))
    for f in filas:
        f["escenario"] = nombre
    return filas, a, tv


def criterios_paso3(filas, a, tv):
    """Criterios 1–3 de I4. Devuelve lista de fallas (vacía = recuperado)."""
    fallas = []
    for f in filas:
        clave = f["parametro"]
        if clave in ("R_eff(0)", "rho*s0", "i0/s0", "k") or clave.startswith("factor"):
            if not f["cubre"]:
                fallas.append(f"{f['escenario']}: {clave} real {f['real']:.4g} fuera de IC")
        if clave in ("R_eff(0)", "rho*s0") or clave.startswith("factor"):
            if abs(f["err_rel"]) >= 0.10:
                fallas.append(f"{f['escenario']}: {clave} error relativo {f['err_rel']:.3f}")
    err_w = np.abs(a.theta[4:10] - tv[4:10])
    if err_w.max() >= 0.1:
        fallas.append(f"error en log w_d = {err_w.max():.3f}")
    if a.en_cota:
        fallas.append(f"parámetros en cota: {a.en_cota}")
    return fallas


def _una_replica(args):
    nombre, semilla = args
    rng = np.random.default_rng(semilla)
    p, y, *_ = datos(nombre, rng)
    a = ajustar_ola(y, D=p.D, N=p.N, d0=p.d0, cambios=p.cambios, rng=rng, n_inicios=4)
    tv = params_a_theta(p)
    return [bool(a.ic(n)[0] <= tv[j] <= a.ic(n)[1]) for j, n in enumerate(a.nombres)], list(a.nombres)


def cobertura(nombre, n_rep=40, semilla_base=SEMILLA, procesos=4):
    """Cobertura empírica del IC 95 % de Wald por parámetro (réplicas independientes)."""
    from multiprocessing import get_context
    tareas = [(nombre, semilla_base + 1 + i) for i in range(n_rep)]
    if procesos > 1:
        with get_context("spawn").Pool(procesos) as pool:
            res = pool.map(_una_replica, tareas)
    else:
        res = list(map(_una_replica, tareas))
    nombres = res[0][1]
    m = np.array([r[0] for r in res], float).mean(axis=0)
    return dict(zip(nombres, m.tolist()))
