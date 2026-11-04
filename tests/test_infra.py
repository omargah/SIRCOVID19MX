"""Prueba trivial de infraestructura: el entorno tiene lo que pide environment.yml.

Si `make env` funcionó, todos estos imports pasan. Si alguno falla, el
problema es el entorno, no el código del proyecto.
"""

import importlib
import sys
from pathlib import Path

import pytest

# Nombre de importación (no siempre coincide con el del paquete: pyyaml -> yaml).
MODULOS = ["numpy", "scipy", "pandas", "matplotlib", "sympy", "yaml", "pytest"]


@pytest.mark.parametrize("modulo", MODULOS)
def test_dependencia_importa(modulo):
    importlib.import_module(modulo)


def test_deps_pip_sale_de_environment_yml():
    """La lista para pip se lee de environment.yml (una sola fuente de verdad)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import deps_pip

    nombres = {d.split(">")[0].split("=")[0] for d in deps_pip.dependencias()}
    assert nombres == {"numpy", "scipy", "pandas", "matplotlib", "sympy", "pyyaml", "pytest"}
