"""Resumen de la recuperación sintética: sesgo, cobertura, perfiles, NB vs Poisson.

Uso:
    python scripts/resumen_recuperacion.py            # todos los .jsonl que haya
    python scripts/resumen_recuperacion.py --datos casos

Lee reports/resultados/recuperacion/<datos>.jsonl (una réplica por línea) y
escribe:
    reports/resultados/recuperacion/resumen_<datos>.json   (todas las cifras)
    reports/recuperacion_sintetica_<datos>.md               (informe con tablas)
Toda cifra del informe sale de aquí (regla: ninguna cifra a mano). Funciona
con resultados parciales: el informe dice cuántas réplicas tiene cada celda.

Definiciones (fijadas antes de ver los resultados):
  * sesgo relativo: mediana y media de (estimado - verdad)/verdad de la MLE.
  * cobertura del IC95 por perfil: fracción de réplicas cuya verdad cae entre
    los extremos del IC (si el IC es abierto, el extremo es el borde de la
    malla; por eso se reporta también la fracción de IC abiertos).
    Error Monte Carlo de una cobertura p con n réplicas: sqrt(p(1-p)/n).
  * cresta plana: clase "cresta_plana" de src/identificabilidad.py
    (IC95 abierto en algún lado de la malla; Raue 2009, J01, pp. 1925-1926).
  * fracción del rango analítico cubierta por el IC de R0 y de s0.
  * cociente de amplitudes relativas IC(R0)/IC(R_eff(0)) (criterio de H1).
  * NB vs Poisson (decisión I2): fracción de réplicas en que el AIC elige
    NB; mediana de la dispersión de Pearson de cada verosimilitud.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "reports" / "resultados" / "recuperacion"
COMBOS = ("nb|nb", "nb|poisson", "poisson|nb", "poisson|poisson")
PARAMS = ("Reff", "R0", "s0")


def _leer(datos):
    filas = [json.loads(l) for l in (DIR / f"{datos}.jsonl").read_text().splitlines() if l.strip()]
    ok = [f for f in filas if not f.get("error")]
    return filas, ok


def _verdad(f, p):
    return f["Reff_verdad"] if p == "Reff" else f["verdad"][p]


def _est(a, p):
    return a["Reff"] if p == "Reff" else a["theta"][p]


def _me(p, n):
    return math.sqrt(p * (1 - p) / n) if n else float("nan")


def resumir(datos):
    filas, ok = _leer(datos)
    esc_ids = sorted({f["escenario_id"] for f in filas})
    out = {"datos": datos, "n_lineas": len(filas), "n_errores": len(filas) - len(ok),
           "errores": [f["error"] for f in filas if f.get("error")][:20], "celdas": []}
    for eid in esc_ids:
        fe = [f for f in ok if f["escenario_id"] == eid]
        if not fe:
            continue
        esc = fe[0]["escenario"]
        for combo in COMBOS:
            fc = [f for f in fe if combo in f["ajustes"]]
            n = len(fc)
            if n == 0:
                continue
            celda = {"escenario_id": eid, "esc_R0": esc["R0"], "esc_s0": esc["s0"], "esc_D": esc["D"],
                     "Reff_verdad": fc[0]["Reff_verdad"],
                     "n_semanas": fc[0]["n_semanas"], "combo": combo, "n": n}
            for p in PARAMS:
                v = np.array([_verdad(f, p) for f in fc])
                e = np.array([_est(f["ajustes"][combo], p) for f in fc])
                rel = (e - v) / v
                pf = [f["ajustes"][combo]["perfiles"][p] for f in fc]
                cub = np.array([pp["inf"] <= vv <= pp["sup"] for pp, vv in zip(pf, v)])
                abierto = np.array([pp["abierto_abajo"] or pp["abierto_arriba"] for pp in pf])
                cresta = np.array([pp["clase"] == "cresta_plana" for pp in pf])
                celda[p] = {
                    "sesgo_rel_mediana": float(np.median(rel)), "sesgo_rel_media": float(np.mean(rel)),
                    "cobertura": float(cub.mean()), "cobertura_error_mc": _me(float(cub.mean()), n),
                    "frac_ic_abierto": float(abierto.mean()), "frac_cresta_plana": float(cresta.mean()),
                    "amplitud_rel_mediana": float(np.median([pp["amplitud_relativa"] for pp in pf])),
                }
                fr = [pp.get("fraccion_rango_cubierta") for pp in pf if "fraccion_rango_cubierta" in pp]
                if fr:
                    celda[p]["frac_rango_analitico_cubierto_mediana"] = float(np.median(fr))
            cociente = [f["ajustes"][combo]["perfiles"]["R0"]["amplitud_relativa"]
                        / f["ajustes"][combo]["perfiles"]["Reff"]["amplitud_relativa"] for f in fc]
            celda["cociente_amplitud_R0_Reff_mediana"] = float(np.median(cociente))
            celda["dispersion_pearson_mediana"] = float(np.median(
                [f["ajustes"][combo]["dispersion_pearson"] for f in fc]))
            celda["frac_mle_no_global"] = float(np.mean([f["ajustes"][combo]["mle_no_era_global"] for f in fc]))
            out["celdas"].append(celda)
        # NB contra Poisson por ruido: ¿qué elige el AIC (y el BIC)?
        for ruido in ("nb", "poisson"):
            fc = [f for f in fe if f"{ruido}|nb" in f["ajustes"] and f"{ruido}|poisson" in f["ajustes"]]
            if not fc:
                continue
            elige_nb_aic = np.mean([f["ajustes"][f"{ruido}|nb"]["aic"] < f["ajustes"][f"{ruido}|poisson"]["aic"] for f in fc])
            elige_nb_bic = np.mean([f["ajustes"][f"{ruido}|nb"]["bic"] < f["ajustes"][f"{ruido}|poisson"]["bic"] for f in fc])
            out.setdefault("comparacion_modelos", []).append({
                "escenario_id": eid, **esc, "ruido": ruido, "n": len(fc),
                "frac_aic_elige_nb": float(elige_nb_aic), "frac_bic_elige_nb": float(elige_nb_bic)})
    return out


def _f(x, d=3):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def informe(r):
    L = [f"# Recuperación sintética — datos: `{r['datos']}`", "",
         "Generado por `scripts/resumen_recuperacion.py` a partir de "
         f"`reports/resultados/recuperacion/{r['datos']}.jsonl`. No editar a mano.", "",
         f"Réplicas leídas: {r['n_lineas']}; con error: {r['n_errores']}.", ""]
    if r["errores"]:
        L += ["Errores (primeros):", *[f"- `{e}`" for e in r["errores"]], ""]
    L += ["Combo = `ruido|verosimilitud`. Sesgo = mediana de (MLE − verdad)/verdad. "
          "Cob = cobertura del IC95 por perfil (± error Monte Carlo). "
          "Abierto = fracción de IC95 abiertos en la malla. "
          "Rango = mediana de la fracción del rango no identificable analítico cubierta por el IC.", ""]
    for p in PARAMS:
        L += [f"## {p}", "",
              "| R0 | s0 | D | sem | combo | n | sesgo | cob | ± | abierto | cresta | rango |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in r["celdas"]:
            q = c[p]
            L.append(f"| {c['esc_R0']:g} | {c['esc_s0']:g} | {c['esc_D']:g} | {c['n_semanas']} | {c['combo']} | {c['n']} | "
                     f"{_f(q['sesgo_rel_mediana'])} | {_f(q['cobertura'], 2)} | {_f(q['cobertura_error_mc'], 2)} | "
                     f"{_f(q['frac_ic_abierto'], 2)} | {_f(q['frac_cresta_plana'], 2)} | "
                     f"{_f(q.get('frac_rango_analitico_cubierto_mediana'), 2)} |")
        L.append("")
    L += ["## H1: cociente de amplitudes relativas IC(R0) / IC(R_eff(0)) y dispersión de Pearson", "",
          "| R0 | s0 | D | combo | n | cociente (mediana) | phi Pearson (mediana) | MLE no global |",
          "|---|---|---|---|---|---|---|---|"]
    for c in r["celdas"]:
        L.append(f"| {c['esc_R0']:g} | {c['esc_s0']:g} | {c['esc_D']:g} | {c['combo']} | {c['n']} | "
                 f"{_f(c['cociente_amplitud_R0_Reff_mediana'], 1)} | {_f(c['dispersion_pearson_mediana'], 2)} | "
                 f"{_f(c['frac_mle_no_global'], 2)} |")
    L += ["", "## NB contra Poisson: fracción de réplicas en que cada criterio elige NB", "",
          "| R0 | s0 | D | ruido | n | AIC elige NB | BIC elige NB |", "|---|---|---|---|---|---|---|"]
    for c in r.get("comparacion_modelos", []):
        L.append(f"| {c['R0']:g} | {c['s0']:g} | {c['D']:g} | {c['ruido']} | {c['n']} | "
                 f"{_f(c['frac_aic_elige_nb'], 2)} | {_f(c['frac_bic_elige_nb'], 2)} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", choices=["casos", "casos_sero"], default=None)
    a = ap.parse_args()
    todos = [a.datos] if a.datos else [d for d in ("casos", "casos_sero") if (DIR / f"{d}.jsonl").exists()]
    for d in todos:
        r = resumir(d)
        (DIR / f"resumen_{d}.json").write_text(json.dumps(r, indent=1))
        (RAIZ / "reports" / f"recuperacion_sintetica_{d}.md").write_text(informe(r))
        print(f"{d}: {r['n_lineas']} réplicas, {len(r['celdas'])} celdas -> reports/recuperacion_sintetica_{d}.md")


if __name__ == "__main__":
    main()
