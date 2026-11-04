"""Cruce de config/parametros.yaml con su fuente: qué tiene fuente y qué no.

Uso: python scripts/listar_supuestos.py
Escribe reports/parametros_fuentes.md (generado; no editar a mano).
Valida el archivo con src/datos.py (truena si algo viola la regla 2).
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import datos  # noqa: E402


def _fuente(e):
    f = e.get("fuente") or {}
    t = f.get("tipo")
    if t == "doi":
        return f"{f['clave']}, {f['pagina']}"
    if t == "institucional":
        return f"{f['institucion']}, {f['documento']} ({f['anio']}), {f['ubicacion']}"
    if t == "regla":
        return "regla: " + f["regla"]
    return ""


def main():
    todo = datos.cargar_entradas()
    L = ["# Parámetros y su fuente", "",
         "Generado por `scripts/listar_supuestos.py` desde `config/parametros.yaml` "
         "(validado por `src/datos.py`). No editar a mano.", ""]
    for sec, entradas in todo.items():
        sin = {n: e for n, e in entradas.items() if e["supuesto"]}
        pend = [n for n, e in entradas.items() if e["valor"] is None]
        L += [f"## Sección `{sec}`", "",
              f"Entradas: {len(entradas)}; supuestos (sin fuente, entran a sensibilidad): {len(sin)}; "
              f"con valor pendiente (null): {len(pend)}.", "",
              "| parámetro | valor | ¿fuente? | fuente o justificación |", "|---|---|---|---|"]
        for n, e in entradas.items():
            v = "pendiente" if e["valor"] is None else e["valor"]
            if e["supuesto"]:
                cand = e.get("fuente_candidata") or {}
                txt = e["justificacion"] + (f" (candidata: {cand.get('clave', cand.get('institucion', ''))})" if cand else "")
                L.append(f"| `{n}` | {v} | **supuesto** | {txt} |")
            else:
                L.append(f"| `{n}` | {v} | sí | {_fuente(e)} |")
        L.append("")
    out = RAIZ / "reports" / "parametros_fuentes.md"
    out.write_text("\n".join(L) + "\n")
    print(f"Escrito {out}")


if __name__ == "__main__":
    main()
