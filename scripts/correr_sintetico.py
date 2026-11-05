"""Experimento sintético de H1 (F4): ¿recupera el método parámetros conocidos?

Genera UNA ola sintética con los valores de config/parametros.yaml
(sección 'sintetico') y la ajusta dos veces:
  A) solo casos;   B) casos + una encuesta serológica.
Para cada caso calcula la MLE, el perfil de R0 y un bootstrap paramétrico.
Guarda todo en reports/resultados/sintetico_h1.json, que leen los scripts
make_numeros.py, make_figuras.py y make_tablas.py. Separar el cálculo
(lento) de la presentación (rápida) permite rehacer figuras sin reajustar.

Uso:  python scripts/correr_sintetico.py
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import parametros, identificabilidad as ident, sir, verosimilitud as V  # noqa: E402

SALIDA = parametros.RAIZ / "reports" / "resultados" / "sintetico_h1.json"


def intervalo_percentil(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def main():
    P = parametros.cargar_parametros("sintetico")
    rng = np.random.default_rng(P["semilla"])
    verdad = {n: P[n] for n in V.PARAMETROS}
    gamma, N = P["gamma"], P["N"]

    # --- Datos sintéticos -------------------------------------------------
    mu = sir.incidencia_semanal(verdad["R0"], gamma, verdad["s0"], verdad["i0"],
                                verdad["rho"], N, P["n_semanas"])
    casos = sir.simular_casos(mu, verdad["k"], rng)
    sero = []
    for t_a, t_b, _, ee in P["sero"]:
        delta = sir.infectados_entre(verdad["R0"], gamma, verdad["s0"], verdad["i0"], t_a, t_b)
        sero.append((t_a, t_b, float(delta + rng.normal(0, ee)), ee))

    escenarios = {"casos": {"casos": casos}, "casos_sero": {"casos": casos, "sero": sero}}

    # Malla logarítmica para el perfil de R0: el rango no identificable
    # analítico es [R0*s0, R0/rho] = [1.5, 25]; la malla lo rebasa por
    # ambos lados para que se vea dónde el perfil deja de ser plano.
    malla_R0 = np.geomspace(1.1, 40.0, 41)

    resultados = {
        "verdad": verdad, "gamma": gamma, "N": N,
        "casos_observados": casos.tolist(), "mu_verdad": mu.tolist(), "sero": sero,
        "rango_R0_analitico": list(ident.rango_R0_no_identificable(verdad)),
        "malla_R0": malla_R0.tolist(), "B": P["B_bootstrap"],
    }
    for nombre, d in escenarios.items():
        print(f"[{nombre}] MLE ...", flush=True)
        # Arrancamos LEJOS de la verdad (factor ~2 en cada parámetro) para
        # que la recuperación no sea un artefacto de empezar en la respuesta.
        inicio = {"R0": 4.0, "s0": 0.9, "i0": 3e-6, "rho": 0.3, "k": 5.0}
        mle = V.ajustar(d, gamma, N, inicio, n_arranques=5, rng=rng)
        print(f"[{nombre}] perfil de R0 ...", flush=True)
        lp, _ = V.perfil("R0", malla_R0, d, gamma, N, mle)
        # Si algún punto del perfil supera a la MLE, la MLE no era el
        # máximo global: lo reportamos como máximo y lo dejamos registrado.
        lmax = max(mle["logvero"], float(np.nanmax(lp)))
        ic = ident.intervalo_perfil(malla_R0, lp, lmax)
        print(f"[{nombre}] bootstrap B={P['B_bootstrap']} ...", flush=True)
        reps = V.bootstrap_parametrico(mle, d, gamma, N, P["B_bootstrap"], rng)
        reff = np.array([r["R0"] * r["s0"] for r in reps])
        R0b = np.array([r["R0"] for r in reps])
        resultados[nombre] = {
            "mle": mle["theta"], "logvero_mle": mle["logvero"], "lmax_perfil": lmax,
            "perfil_R0": lp.tolist(), "ic_perfil_R0": ic,
            "Reff_mle": mle["theta"]["R0"] * mle["theta"]["s0"],
            "ic_boot_Reff": intervalo_percentil(reff),
            "ic_boot_R0": intervalo_percentil(R0b),
            "boot_Reff": reff.tolist(), "boot_R0": R0b.tolist(),
        }

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultados, indent=1))
    print(f"Escrito {SALIDA}")


if __name__ == "__main__":
    main()
