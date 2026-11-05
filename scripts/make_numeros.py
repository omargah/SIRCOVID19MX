"""Genera reports/numeros.tex: TODAS las cifras que cita el escrito.

Regla (1): ninguna cifra se escribe a mano en el LaTeX. El escrito usa
macros como \\SintReffMLE; este script las define a partir de los
resultados guardados. Si un resultado cambia, se corre `make` y el texto
se actualiza solo.

Los nombres de macro en LaTeX no pueden tener dígitos, por eso "R0" se
escribe "Rcero", "s0" -> "scero", etc.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import parametros  # noqa: E402

ENTRADA = parametros.RAIZ / "reports" / "resultados" / "sintetico_h1.json"
SALIDA = parametros.RAIZ / "reports" / "numeros.tex"

NOMBRE_LATEX = {"R0": "Rcero", "s0": "scero", "i0": "icero", "rho": "rho", "k": "k"}


def fmt(x, cifras=3):
    """Formato con cifras significativas; notación científica si es muy chico."""
    if x != 0 and abs(x) < 1e-3:
        mant, exp = f"{x:.{cifras - 1}e}".split("e")
        return rf"\ensuremath{{{mant}\times 10^{{{int(exp)}}}}}"
    return f"{x:.{cifras}g}"


def main():
    r = json.loads(ENTRADA.read_text())
    macros = {}
    for p, v in r["verdad"].items():
        macros[f"SintVerdad{NOMBRE_LATEX[p]}"] = fmt(v)
    macros["SintVerdadReff"] = fmt(r["verdad"]["R0"] * r["verdad"]["s0"])
    macros["SintGammaInv"] = fmt(1 / r["gamma"])
    macros["SintN"] = fmt(r["N"])
    macros["SintB"] = str(r["B"])
    macros["SintRangoRceroInf"] = fmt(r["rango_R0_analitico"][0])
    macros["SintRangoRceroSup"] = fmt(r["rango_R0_analitico"][1])
    macros["SintMallaRceroInf"] = fmt(r["malla_R0"][0])
    macros["SintMallaRceroSup"] = fmt(r["malla_R0"][-1])
    for esc, pref in (("casos", "Casos"), ("casos_sero", "Sero")):
        e = r[esc]
        for p, v in e["mle"].items():
            macros[f"Sint{pref}MLE{NOMBRE_LATEX[p]}"] = fmt(v)
        macros[f"Sint{pref}MLEReff"] = fmt(e["Reff_mle"])
        macros[f"Sint{pref}BootReffInf"] = fmt(e["ic_boot_Reff"][0])
        macros[f"Sint{pref}BootReffSup"] = fmt(e["ic_boot_Reff"][1])
        macros[f"Sint{pref}BootRceroInf"] = fmt(e["ic_boot_R0"][0])
        macros[f"Sint{pref}BootRceroSup"] = fmt(e["ic_boot_R0"][1])
        inf, sup, aa, ab = e["ic_perfil_R0"]
        # Un extremo "abierto" no es un número: el escrito debe decirlo.
        macros[f"Sint{pref}PerfilRceroInf"] = r"\text{abierto}" if aa else fmt(inf)
        macros[f"Sint{pref}PerfilRceroSup"] = r"\text{abierto}" if ab else fmt(sup)

    lineas = ["% ARCHIVO GENERADO por scripts/make_numeros.py. NO EDITAR A MANO.",
              f"% Fuente: {ENTRADA.relative_to(parametros.RAIZ)}"]
    lineas += [rf"\newcommand{{\{k}}}{{{v}}}" for k, v in sorted(macros.items())]
    SALIDA.write_text("\n".join(lineas) + "\n")
    print(f"Escrito {SALIDA} ({len(macros)} macros)")


if __name__ == "__main__":
    main()
