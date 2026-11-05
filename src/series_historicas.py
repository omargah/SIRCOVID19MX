"""Construye la serie para cada versión histórica descargada (insumo de la EDA §3).

Uso::

    python -m src.series_historicas

Para cada ``data/raw/dge/historicos/datos_abiertos_covid19_DD.MM.AAAA.zip``
escribe ``data/processed/historicos/AAAA-MM-DD/`` con la misma salida que
``src.datos``. Omite versiones ya procesadas con el mismo hash de entrada.
No decide el tratamiento de las versiones; solo las deja listas para
describirlas.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date

from src.datos import RAIZ, construir
from src.fuentes import sha256_archivo

DIR = RAIZ / "data" / "raw" / "dge" / "historicos"
SALIDA = RAIZ / "data" / "processed" / "historicos"
PATRON = re.compile(r"datos_abiertos_covid19_(\d{2})\.(\d{2})\.(\d{4})\.zip$")


def main() -> int:
    archivos = sorted(DIR.glob("*.zip")) if DIR.exists() else []
    if not archivos:
        print(f"No hay versiones en {DIR.relative_to(RAIZ)}/", file=sys.stderr)
        return 0
    for z in archivos:
        m = PATRON.search(z.name)
        if not m:
            continue
        d, mm, a = map(int, m.groups())
        out = SALIDA / date(a, mm, d).isoformat()
        man = out / "manifiesto.json"
        if man.exists():
            previo = json.loads(man.read_text(encoding="utf-8"))
            if [e["sha256"] for e in previo["entradas"]] == [sha256_archivo(z)]:
                continue
        construir([z], out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
