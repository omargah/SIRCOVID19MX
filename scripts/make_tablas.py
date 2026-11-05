"""Tablas LaTeX del escrito a partir de reports/resultados/*.json."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import parametros  # noqa: E402
from make_numeros import fmt  # noqa: E402  (mismo formato que numeros.tex)

ENTRADA = parametros.RAIZ / "reports" / "resultados" / "sintetico_h1.json"
CARPETA = parametros.RAIZ / "reports" / "tablas"

SIMBOLO = {"R0": r"$R_0$", "s0": r"$s_0$", "i0": r"$i_0$", "rho": r"$\rho$", "k": r"$k$"}


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    r = json.loads(ENTRADA.read_text())
    filas = []
    for p in ("R0", "s0", "i0", "rho", "k"):
        filas.append(f"{SIMBOLO[p]} & {fmt(r['verdad'][p])} & "
                     f"{fmt(r['casos']['mle'][p])} & {fmt(r['casos_sero']['mle'][p])} \\\\")
    reff_v = r["verdad"]["R0"] * r["verdad"]["s0"]
    filas.append(rf"$R_{{\mathrm{{eff}}}}(0)=R_0 s_0$ & {fmt(reff_v)} & "
                 f"{fmt(r['casos']['Reff_mle'])} & {fmt(r['casos_sero']['Reff_mle'])} \\\\")
    tabla = "\n".join([
        "% GENERADO por scripts/make_tablas.py. NO EDITAR A MANO.",
        r"\begin{tabular}{lccc}",
        r"\hline",
        r"Parámetro & Verdad & MLE (casos) & MLE (casos + serología) \\",
        r"\hline",
        *filas,
        r"\hline",
        r"\end{tabular}",
    ])
    (CARPETA / "recuperacion_sintetica.tex").write_text(tabla + "\n")
    print(f"Tabla en {CARPETA}")


if __name__ == "__main__":
    main()
