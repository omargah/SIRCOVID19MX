"""Figuras del escrito a partir de reports/resultados/*.json.

Regla (5): las figuras muestran todos los puntos calculados; no se recorta
la malla ni se quitan puntos para que la curva "se vea mejor".
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo escribe archivos
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import parametros, identificabilidad as ident  # noqa: E402

ENTRADA = parametros.RAIZ / "reports" / "resultados" / "sintetico_h1.json"
CARPETA = parametros.RAIZ / "reports" / "figuras"


def figura_perfil_R0(r):
    """Perfil de R0 con y sin serología, y la banda analítica de H1."""
    fig, ax = plt.subplots(figsize=(6, 3.8))
    malla = np.array(r["malla_R0"])
    a, b = r["rango_R0_analitico"]
    ax.axvspan(a, b, color="0.9", label="rango no identificable (analítico)")
    for esc, etiqueta, estilo in (("casos", "solo casos", "o-"), ("casos_sero", "casos + serología", "s-")):
        e = r[esc]
        ax.plot(malla, np.array(e["perfil_R0"]) - e["lmax_perfil"], estilo, ms=3, label=etiqueta)
    ax.axhline(-ident.UMBRAL_95, color="k", ls="--", lw=0.8, label="umbral IC 95 %")
    ax.axvline(r["verdad"]["R0"], color="k", ls=":", lw=0.8, label="R0 verdadero")
    ax.set_xscale("log")
    ax.set_xlabel(r"$R_0$ (fijo)")
    ax.set_ylabel(r"$\ell_p(R_0) - \ell_{\max}$")
    # Recortamos solo el eje (no los datos): debajo de -20 todo es "excluido".
    ax.set_ylim(-20, 1)
    ax.legend(fontsize=7, loc="lower center")
    fig.tight_layout()
    fig.savefig(CARPETA / "perfil_R0_sintetico.pdf")
    plt.close(fig)


def figura_ajuste(r):
    """Casos sintéticos, media verdadera y media ajustada."""
    from src import sir
    fig, ax = plt.subplots(figsize=(6, 3.5))
    y = np.array(r["casos_observados"])
    semanas = np.arange(y.size)
    ax.plot(semanas, y, "k.", label="casos simulados")
    ax.plot(semanas, r["mu_verdad"], "-", label="media verdadera")
    th = r["casos"]["mle"]
    mu = sir.incidencia_semanal(th["R0"], r["gamma"], th["s0"], th["i0"], th["rho"], r["N"], y.size)
    ax.plot(semanas, mu, "--", label="media ajustada (solo casos)")
    ax.set_xlabel("semana desde el inicio de la ola")
    ax.set_ylabel("casos por semana")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(CARPETA / "ajuste_sintetico.pdf")
    plt.close(fig)


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    r = json.loads(ENTRADA.read_text())
    figura_perfil_R0(r)
    figura_ajuste(r)
    print(f"Figuras en {CARPETA}")


if __name__ == "__main__":
    main()
