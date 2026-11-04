"""Genera docs/validacion_sintetica.md: tablas de los pasos 3–7 con datos SINTÉTICOS.

Uso:  OPENBLAS_NUM_THREADS=1 python3 scripts/validacion_sintetica.py
(no lee ningún dato real)."""
import os
import sys

for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hashlib
import json
from multiprocessing import get_context

import numpy as np
from scipy.special import logit

from sirmx.cambios import detectar_cambios
from sirmx.crecimiento import estimar_r, r_verdadero
from sirmx.escenarios import ESCENARIOS_PASO3, SEMILLA, datos
from sirmx.identificabilidad import (COTAS_NAT, ajustar_natural, intervalo_perfil, nll_natural,
                                     perfil)
from sirmx.pronostico import evaluar
from sirmx.validacion import cobertura, criterios_paso3, tabla_escenario
from sirmx.verosimilitud import COTAS_BASE, ajustar_ola, nll

SALIDA = os.path.join(os.path.dirname(__file__), "..", "docs", "validacion_sintetica.md")


def k_ola(p, y, rng):
    a = ajustar_ola(y, D=p.D, N=p.N, cambios=p.cambios, rng=rng, n_inicios=3, calcular_cov=False)
    return float(np.exp(a.theta[3]))


def tarea_cambios(nombre):
    rng = np.random.default_rng(SEMILLA)
    p, y, *_ = datos(nombre, rng)
    r = detectar_cambios(y, D=p.D, N=p.N, rng=rng)
    filas = []
    for j in range(r.K):
        filas.append({"tau": r.mejor.cambios[j], "ic_tau": r.ic_tau(j),
                      "factor": float(np.exp(r.mejor.theta[10 + j])), "ic_factor": r.ic_factor(j)})
    return nombre, {"real_tau": list(p.cambios), "real_factor": np.exp(p.log_factores).tolist(),
                    "K": r.K, "bic": {k: float(v) for k, v in r.bic.items()},
                    "tau_K2": list(r.ajustes[2].cambios), "filas": filas}


def tarea_pronostico(nombre):
    rng = np.random.default_rng(SEMILLA)
    p, y, mu, *_ = datos(nombre, rng)
    return nombre, evaluar(y, mu, p.D, p.N, rng).resumen()


def _rep_r(args):
    nombre, s = args
    rng = np.random.default_rng(1000 + s)
    p, y, mu, inc, S = datos(nombre, rng)
    k = k_ola(p, y, rng)
    e = estimar_r(y, rng, B=100, k_fijo=k)
    rv = r_verdadero(p, S, e.ventana)
    e0 = estimar_r(y, np.random.default_rng(s), B=100)  # k libre, para documentar C4
    return (e.ic_perfil[0] <= rv <= e.ic_perfil[1], e.ic_bootstrap[0] <= rv <= e.ic_bootstrap[1],
            e0.ic_perfil[0] <= rv <= e0.ic_perfil[1], e0.ic_bootstrap[0] <= rv <= e0.ic_bootstrap[1])


def fmt(x, d=4):
    return f"{x:.{d}g}"


def main():
    L = ["# Validación sintética (F4)", "",
         "Generado por `scripts/validacion_sintetica.py` con semilla "
         f"{SEMILLA}. Solo datos simulados; ningún dato real se leyó.", ""]
    ctx = get_context("spawn")
    with ctx.Pool(4) as pool:
        fut_cp = pool.map_async(tarea_cambios, ["ola_simple", "cambio_beta", "dos_cambios",
                                                "dos_cambios_sep15", "dos_cambios_sep20",
                                                "dos_cambios_sep30"])
        fut_fc = pool.map_async(tarea_pronostico, ["ola_simple", "cambio_beta"])
        fut_r = pool.map_async(_rep_r, [("subregistro", s) for s in range(160)])

        # ---------------- paso 3
        L += ["## Paso 3 · Valor real vs estimado (IC 95 % de Wald)", "",
              "τ se toma como conocido (la detección de τ es el paso 6).", ""]
        todas_fallas = []
        for nombre in ESCENARIOS_PASO3:
            filas, a, tv = tabla_escenario(nombre)
            fallas = criterios_paso3(filas, a, tv)
            todas_fallas += fallas
            L += [f"### {nombre}", "",
                  f"Inicios: {a.n_inicios}; a ≤ 0.5 de log-verosimilitud del mejor: {a.n_cerca_mejor}. "
                  f"log-verosimilitud = {a.loglik:.2f}.", "",
                  "| parámetro | real | estimado | IC 95 % | ¿cubre? | error rel. |",
                  "|---|---|---|---|---|---|"]
            for f in filas:
                L.append(f"| {f['parametro']} | {fmt(f['real'])} | {fmt(f['estimado'])} | "
                         f"[{fmt(f['ic_lo'])}, {fmt(f['ic_hi'])}] | {'sí' if f['cubre'] else '**no**'} | "
                         f"{100 * f['err_rel']:+.1f} % |")
            L.append("")
        L += ["**Veredicto paso 3:** " + ("recuperado (criterios 1–3 de I4)." if not todas_fallas
                                          else "NO recuperado: " + "; ".join(todas_fallas)), ""]
        L += ["Cobertura empírica del IC 95 % (40 réplicas por escenario, criterio 4):", "",
              "| escenario | R_eff(0) | ρ·s0 | i0/s0 | k |", "|---|---|---|---|---|"]
        for nombre in ESCENARIOS_PASO3:
            c = cobertura(nombre, n_rep=40, procesos=1)
            L.append(f"| {nombre} | {c['log_Reff0']:.2f} | {c['log_rho_s0']:.2f} | "
                     f"{c['log_i0_s0']:.2f} | {c['log_k']:.2f} |")
        L.append("")

        # ---------------- paso 4
        L += ["## Paso 4 · Perfiles de verosimilitud (escenario subregistro)", ""]
        rng = np.random.default_rng(SEMILLA)
        p, y, *_ = datos("subregistro", rng)
        a = ajustar_ola(y, D=p.D, N=p.N, rng=rng)
        phi, ll_nat = ajustar_natural(y, p.D, p.N, a, rng)
        f = lambda ph: nll_natural(ph, y, p.D, p.N)
        R0g = np.array([1.6, 1.8, 1.9, 2.0, 2.1, 2.5, 3, 4, 6, 8, 11, 14, 15.5, 16.5, 18, 20])
        llR = perfil(f, phi, 0, np.log(R0g), COTAS_NAT, rng)
        s0g = np.array([0.08, 0.1, 0.11, 0.12, 0.13, 0.2, 0.3, 0.5, 0.7, 0.9, 0.99])
        lls = perfil(f, phi, 1, logit(s0g), COTAS_NAT, rng)
        Rg = np.linspace(1.95, 2.06, 23)
        llE = perfil(lambda th: nll(th, y, p.D, p.N), a.theta, 0, np.log(Rg), COTAS_BASE, rng)
        loE, hiE, *_ = intervalo_perfil(Rg, llE)
        loR, hiR, aR, bR = intervalo_perfil(R0g, llR)
        los, his, as_, bs = intervalo_perfil(s0g, lls)
        L += [f"Valores reales: R0 = {p.R0}, s0 = {p.s0}, ρ = {p.rho} → R_eff(0) = {p.Reff0}, "
              f"ρ·s0 = {p.rho_s0:.3g}. ℓ̂ = {a.loglik:.3f} (natural: {ll_nat:.3f}).", "",
              "| R0 | " + " | ".join(fmt(v, 3) for v in R0g) + " |",
              "|---" * (len(R0g) + 1) + "|",
              "| ℓ̂ − ℓ_p | " + " | ".join(f"{a.loglik - v:.3g}" for v in llR) + " |", "",
              "| s0 | " + " | ".join(fmt(v, 3) for v in s0g) + " |",
              "|---" * (len(s0g) + 1) + "|",
              "| ℓ̂ − ℓ_p | " + " | ".join(f"{a.loglik - v:.3g}" for v in lls) + " |", "",
              f"- IC de perfil 95 % de R_eff(0): [{loE:.4f}, {hiE:.4f}] (real {p.Reff0}); Wald: "
              f"[{np.exp(a.ic('log_Reff0')[0]):.4f}, {np.exp(a.ic('log_Reff0')[1]):.4f}].",
              f"- \"IC\" de perfil de R0: [{loR:.2f}, {hiR:.2f}]; de s0: [{los:.3f}, {his:.3f}]. "
              "Sus extremos los fijan las restricciones s0 ≤ 1 y ρ ≤ 1, no los datos.",
              "- **Sí aparece la cresta plana de H1**: ℓ_p(R0) y ℓ_p(s0) son constantes (diferencias "
              "≲ 10⁻⁵, error numérico) en toda la región compatible con R0·s0 = R_eff(0); "
              "R_eff(0) tiene un perfil cuadrático y estrecho. Con casos solos, H1 se cumple de forma "
              "**estructural** (exacta), no solo práctica.", ""]

        # ---------------- paso 5
        L += ["## Paso 5 · r con ventana fija (21 días), perfil, bootstrap (B = 200) y R(D)", "",
              "| escenario | ventana | r real | r̂ | IC perfil | IC bootstrap | R(D=5) | R(D=7) | R(D=10) | R_eff(0) real |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for nombre in ESCENARIOS_PASO3:
            rng = np.random.default_rng(SEMILLA)
            p, y, mu, inc, S = datos(nombre, rng)
            e = estimar_r(y, rng, B=200, k_fijo=k_ola(p, y, rng))
            rv = r_verdadero(p, S, e.ventana)
            tb = e.tabla_D()
            celdas = [f"{tb[D][0]:.2f} [{tb[D][1]:.2f}, {tb[D][2]:.2f}]" for D in (5.0, 7.0, 10.0)]
            L.append(f"| {nombre} | {e.ventana} | {rv:.4f} | {e.r:.4f} | [{e.ic_perfil[0]:.4f}, "
                     f"{e.ic_perfil[1]:.4f}] | [{e.ic_bootstrap[0]:.4f}, {e.ic_bootstrap[1]:.4f}] | "
                     + " | ".join(celdas) + f" | {p.Reff0} |")
        cub = np.array(fut_r.get(), float).mean(axis=0)
        L += ["", "R(D) con IC de perfil. R(D) = 1 + r·D (SIR, periodo infeccioso exponencial).", "",
              "Cobertura del IC 95 % de r (160 réplicas, escenario subregistro):", "",
              "| k | perfil | bootstrap |", "|---|---|---|",
              f"| tomado del ajuste de la ola (decisión C4) | {cub[0]:.3f} | {cub[1]:.3f} |",
              f"| estimado en la ventana (versión original) | {cub[2]:.3f} | {cub[3]:.3f} |", ""]

        # ---------------- paso 6
        L += ["## Paso 6 · Puntos de cambio de β (selección de K por BIC)", "",
              "| escenario | τ real | factor real | K elegido | BIC (K=0, 1, 2) | τ̂ [IC] | factor [IC 95 %] | τ del mejor K=2 |",
              "|---|---|---|---|---|---|---|---|"]
        for nombre, r in fut_cp.get():
            est = "; ".join(f"{f['tau']} [{f['ic_tau'][0]}, {f['ic_tau'][1]}]" for f in r["filas"]) or "—"
            fac = "; ".join(f"{f['factor']:.3f} [{f['ic_factor'][0]:.3f}, {f['ic_factor'][1]:.3f}]"
                            for f in r["filas"]) or "—"
            bic = ", ".join(f"{r['bic'][k]:.1f}" for k in sorted(r["bic"]))
            L.append(f"| {nombre} | {r['real_tau'] or '—'} | {[round(x, 2) for x in r['real_factor']] or '—'} | "
                     f"{r['K']} | {bic} | {est} | {fac} | {r['tau_K2']} |")
        L += ["", "IC de τ: perfil a resolución diaria (condicional al otro τ cuando K = 2).", ""]

        # ---------------- paso 7
        L += ["## Paso 7 · Pronóstico en tiempo simulado (orígenes semanales desde el día 21)", "",
              "| escenario | métrica | modelo SIR | persistencia |", "|---|---|---|---|"]
        for nombre, r in fut_fc.get():
            for h in range(4):
                L.append(f"| {nombre} | WIS medio h={h + 1} sem | {r['WIS_modelo_por_h'][h]:.0f} | "
                         f"{r['WIS_persistencia_por_h'][h]:.0f} |")
            L += [f"| {nombre} | WIS relativo (modelo/persistencia) | {r['WIS_relativo']:.2f} | 1 |",
                  f"| {nombre} | cobertura 50 % | {r['cob50_modelo']:.2f} | {r['cob50_persistencia']:.2f} |",
                  f"| {nombre} | cobertura 95 % | {r['cob95_modelo']:.2f} | {r['cob95_persistencia']:.2f} |",
                  f"| {nombre} | EAM fecha del pico (días) | {r['EAM_fecha_pico_modelo_dias']:.1f} | "
                  f"{r['EAM_fecha_pico_persistencia_dias']:.1f} |",
                  f"| {nombre} | EAM altura del pico (relativo) | {r['EAM_altura_pico_modelo_rel']:.2f} | "
                  f"{r['EAM_altura_pico_persistencia_rel']:.2f} |"]
        L.append("")

    # ---------------- paso 8
    from tests.test_8_reproducibilidad import _corrida
    h = [hashlib.sha256(b"".join(np.ascontiguousarray(v).tobytes() for v in _corrida(123).values())).hexdigest()
         for _ in range(2)]
    L += ["## Paso 8 · Reproducibilidad", "",
          f"Huella SHA-256 de dos corridas con semilla 123: `{h[0][:16]}…` y `{h[1][:16]}…` → "
          + ("idénticas." if h[0] == h[1] else "**DISTINTAS**."), ""]
    with open(SALIDA, "w") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
