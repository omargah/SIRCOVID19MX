"""Imprime las dependencias de environment.yml en formato de pip.

Lo usa `make env` cuando no hay conda. Lee el archivo como texto (no con
pyyaml) porque se ejecuta ANTES de instalar nada. Omite `python`, que no
se instala con pip.

Uso:  python3 scripts/deps_pip.py   ->   numpy>=2.0 scipy>=1.13 ...
"""

from pathlib import Path

ARCHIVO = Path(__file__).resolve().parent.parent / "environment.yml"


def dependencias():
    deps, dentro = [], False
    for linea in ARCHIVO.read_text(encoding="utf-8").splitlines():
        if linea.startswith("dependencies:"):
            dentro = True
            continue
        if dentro:
            if not linea.startswith("  - "):
                break  # terminó la lista
            paquete = linea[4:].split("#")[0].strip()
            if not paquete.startswith("python"):
                deps.append(paquete)
    return deps


if __name__ == "__main__":
    print(" ".join(dependencias()))
