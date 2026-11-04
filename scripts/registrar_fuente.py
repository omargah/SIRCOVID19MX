#!/usr/bin/env python3
"""Registra la procedencia de archivos descargados a mano en data/raw.

Guarda en data/fuentes.csv: archivo, nivel de fuente (DGE / tablero),
URL, fecha de descarga, SHA-256, tamaño y nota.

Ejemplos
--------
Registrar el microdato vigente de la DGE::

    python scripts/registrar_fuente.py data/raw/dge/datos_abiertos_covid19.zip \\
        --nivel DGE \\
        --url https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip \\
        --fecha-descarga 2026-11-04

Registrar el CSV del tablero usado en el PT1::

    python scripts/registrar_fuente.py \\
        data/raw/tablero/Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv \\
        --nivel tablero --url https://datos.covid-19.conacyt.mx/ --fecha-descarga 2023-06-25

Varias versiones históricas a la vez (la URL se deduce del nombre)::

    python scripts/registrar_fuente.py data/raw/dge/historicos/*.zip \\
        --nivel DGE --url-historico --fecha-descarga 2026-11-04

Otras acciones::

    python scripts/registrar_fuente.py --verificar     # recalcula hashes
    python scripts/registrar_fuente.py --pendientes    # archivos sin registrar
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fuentes import (  # noqa: E402
    NIVELES, RAIZ, REGISTRO, Fuente, escribir_registro, leer_registro,
    ruta_relativa, sha256_archivo,
)

PATRON_HIST = re.compile(r"datos_abiertos_covid19_(\d{2})\.(\d{2})\.(\d{4})\.zip$")
URL_HIST = ("https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/"
            "historicos/{a}/{m}/datos_abiertos_covid19_{d}.{m}.{a}.zip")


def url_historico(nombre: str) -> str | None:
    m = PATRON_HIST.search(nombre)
    if not m:
        return None
    d, mes, a = m.groups()
    return URL_HIST.format(a=a, m=mes, d=d)


def validar_fecha(s: str) -> str:
    try:
        date.fromisoformat(s[:10])
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"fecha inválida: {s!r} (usa AAAA-MM-DD)") from e
    return s


def registrar(args) -> int:
    fuentes = leer_registro(args.registro)
    for archivo in args.archivos:
        ruta = Path(archivo)
        if not ruta.is_file():
            print(f"[error] no existe: {ruta}", file=sys.stderr)
            return 2
        url = args.url
        if args.url_historico:
            url = url_historico(ruta.name)
            if url is None:
                print(f"[error] {ruta.name} no sigue el patrón "
                      "datos_abiertos_covid19_DD.MM.AAAA.zip", file=sys.stderr)
                return 2
        rel = ruta_relativa(ruta)
        digest = sha256_archivo(ruta)
        nueva = Fuente(archivo=rel, nivel=args.nivel, url=url,
                       fecha_descarga=args.fecha_descarga, sha256=digest,
                       bytes=ruta.stat().st_size, nota=args.nota)
        previas = [x for x in fuentes if x.archivo == rel]
        if any(x.sha256 == digest for x in previas):
            fuentes = [x for x in fuentes if not (x.archivo == rel and x.sha256 == digest)]
            print(f"[actualizado] {rel}  sha256={digest[:16]}…")
        elif previas:
            print(f"[aviso] {rel} ya estaba registrado con OTRO hash: el archivo cambió. "
                  "Se conserva la fila anterior como historial.", file=sys.stderr)
        else:
            print(f"[nuevo] {rel}  sha256={digest[:16]}…")
        fuentes.append(nueva)
    escribir_registro(fuentes, args.registro)
    return 0


def verificar(args) -> int:
    fuentes = leer_registro(args.registro)
    vigentes: dict[str, list[Fuente]] = {}
    for x in fuentes:
        vigentes.setdefault(x.archivo, []).append(x)
    malos = 0
    for rel, filas in sorted(vigentes.items()):
        ruta = RAIZ / rel
        if not ruta.exists():
            print(f"[falta]  {rel}")
            malos += 1
            continue
        digest = sha256_archivo(ruta)
        if any(x.sha256 == digest for x in filas):
            print(f"[ok]     {rel}")
        else:
            print(f"[CAMBIÓ] {rel}: sha256 actual {digest[:16]}… no coincide con el registro")
            malos += 1
    return 1 if malos else 0


def pendientes(args) -> int:
    registrados = {x.archivo for x in leer_registro(args.registro)}
    crudo = RAIZ / "data" / "raw"
    faltan = sorted(ruta_relativa(p) for p in crudo.rglob("*")
                    if p.is_file() and not p.name.startswith(".")
                    and p.name != "README.md" and ruta_relativa(p) not in registrados)
    for f in faltan:
        print(f)
    if not faltan:
        print("(todos los archivos de data/raw están registrados)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivos", nargs="*", help="archivo(s) a registrar")
    p.add_argument("--nivel", choices=NIVELES, help="nivel de fuente")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--url", help="URL exacta de descarga")
    g.add_argument("--url-historico", action="store_true",
                   help="deducir la URL del histórico DGE a partir del nombre del archivo")
    p.add_argument("--fecha-descarga", type=validar_fecha,
                   help="fecha (AAAA-MM-DD) en que se descargó el archivo")
    p.add_argument("--nota", default="", help="comentario libre (p. ej. 'descargado vía navegador')")
    p.add_argument("--verificar", action="store_true", help="recalcular hashes de lo registrado")
    p.add_argument("--pendientes", action="store_true", help="listar archivos sin registrar")
    p.add_argument("--registro", type=Path, default=REGISTRO, help=argparse.SUPPRESS)
    args = p.parse_args(argv)

    if args.verificar:
        return verificar(args)
    if args.pendientes:
        return pendientes(args)
    if not args.archivos:
        p.error("indica al menos un archivo (o --verificar / --pendientes)")
    if not args.nivel or not args.fecha_descarga or not (args.url or args.url_historico):
        p.error("para registrar se requieren --nivel, --fecha-descarga y --url (o --url-historico)")
    return registrar(args)


if __name__ == "__main__":
    sys.exit(main())
