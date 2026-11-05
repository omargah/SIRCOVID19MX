"""Registro de procedencia de archivos crudos (data/fuentes.csv).

Cada archivo que entra al pipeline debe estar registrado con:
  - nivel de fuente (``DGE`` = fuente primaria; ``tablero`` = fuente
    secundaria derivada de la DGE, p. ej. el tablero CONAHCYT),
  - URL de donde se descargó,
  - fecha de descarga,
  - hash SHA-256 y tamaño en bytes.

El registro es un CSV ordenado y en UTF-8 con saltos de línea ``\\n``
para que los diffs en git sean legibles y estables.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, asdict, fields
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "data" / "fuentes.csv"
NIVELES = ("DGE", "tablero", "otro")

# Citas de los dos niveles de fuente. Se repiten en manifiestos y notas.
CITA_DGE = (
    "Secretaría de Salud, Dirección General de Epidemiología (DGE). "
    "Datos Abiertos — Información referente a casos COVID-19 en México "
    "(microdatos SISVER/SINAVE). "
    "https://www.gob.mx/salud/documentos/datos-abiertos-152127"
)
CITA_TABLERO = (
    "CONAHCYT (antes CONACYT) / Centro de Investigación en Ciencias de "
    "Información Geoespacial. COVID-19 Tablero México, sección Descarga "
    "de datos, archivo Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv. "
    "https://datos.covid-19.conacyt.mx/ (fuente primaria declarada: DGE)."
)


@dataclass
class Fuente:
    archivo: str          # ruta relativa a la raíz del repo
    nivel: str            # DGE | tablero | otro
    url: str
    fecha_descarga: str   # AAAA-MM-DD (o AAAA-MM-DDTHH:MM si se conoce)
    sha256: str
    bytes: int
    nota: str = ""


CAMPOS = [f.name for f in fields(Fuente)]


def sha256_archivo(ruta: Path, bloque: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def ruta_relativa(ruta: Path) -> str:
    ruta = Path(ruta).resolve()
    try:
        return ruta.relative_to(RAIZ).as_posix()
    except ValueError:
        return ruta.as_posix()


def leer_registro(registro: Path = REGISTRO) -> list[Fuente]:
    if not registro.exists():
        return []
    with open(registro, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return [Fuente(**{**r, "bytes": int(r["bytes"])}) for r in filas]


def escribir_registro(fuentes: list[Fuente], registro: Path = REGISTRO) -> None:
    registro.parent.mkdir(parents=True, exist_ok=True)
    fuentes = sorted(fuentes, key=lambda x: (x.archivo, x.fecha_descarga, x.sha256))
    with open(registro, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        for x in fuentes:
            w.writerow(asdict(x))


def buscar(ruta: Path, registro: Path = REGISTRO) -> Fuente | None:
    """Devuelve el registro vigente (mismo archivo y mismo hash) o None."""
    rel = ruta_relativa(ruta)
    digest = sha256_archivo(ruta)
    for x in leer_registro(registro):
        if x.archivo == rel and x.sha256 == digest:
            return x
    return None


def exigir_registro(rutas: list[Path], estricto: bool = True,
                    registro: Path = REGISTRO) -> list[dict]:
    """Verifica que cada archivo de entrada esté registrado con su hash actual.

    Devuelve la lista de registros (como dict) para incluirla en el
    manifiesto de salida. Con ``estricto`` lanza error si falta alguno.
    """
    salida = []
    faltan = []
    for r in rutas:
        x = buscar(Path(r), registro)
        if x is None:
            faltan.append(ruta_relativa(Path(r)))
            salida.append({"archivo": ruta_relativa(Path(r)),
                           "sha256": sha256_archivo(Path(r)),
                           "nivel": "NO REGISTRADO", "url": "", "fecha_descarga": ""})
        else:
            salida.append(asdict(x))
    if faltan and estricto:
        raise SystemExit(
            "Archivos sin registro de procedencia (o con hash distinto al registrado):\n  "
            + "\n  ".join(faltan)
            + "\nRegístralos con: python scripts/registrar_fuente.py ARCHIVO "
              "--nivel DGE --url URL --fecha-descarga AAAA-MM-DD\n"
              "(o usa --permitir-no-registrados bajo tu responsabilidad)."
        )
    return salida
