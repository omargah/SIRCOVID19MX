# Une el conftest de la rama de integración y el de kind-newton (F4).
import os
import sys
from pathlib import Path

# Permite "from src import ..." al correr pytest desde la raíz del repo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Un hilo de BLAS por proceso: con varios hilos L-BFGS-B se vuelve ~4x más lento por contención.
for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")

import pytest


@pytest.fixture(scope="session")
def paso3_aprobado():
    """Puerta de I4: si los tres escenarios no se recuperan con la semilla fijada, los
    pasos 4–7 no se ejecutan (quedan omitidos y test_3_escenarios.py falla)."""
    from sirmx.escenarios import ESCENARIOS_PASO3
    from sirmx.validacion import criterios_paso3, tabla_escenario
    fallas = []
    for nombre in ESCENARIOS_PASO3:
        fallas += criterios_paso3(*tabla_escenario(nombre))
    if fallas:
        pytest.skip("paso 3 no aprobado; no se avanza: " + "; ".join(fallas))
    return True
