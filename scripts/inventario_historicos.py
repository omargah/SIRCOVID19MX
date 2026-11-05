#!/usr/bin/env python3
"""Inventario de las versiones históricas semanales del microdato DGE.

SOLO INVENTARIO: no decide cómo se tratarán las versiones (vintage
analysis, nowcasting, etc.). Para cada martes desde el 14-abr-2020 lista el
archivo esperado, su URL en el repositorio de históricos de la DGE y, si
Omar ya lo descargó en ``data/raw/dge/historicos/``, su tamaño, hash,
registro de procedencia, fecha de actualización interna y esquema de
columnas.

Uso::

    python scripts/inventario_historicos.py [--hasta 2023-06-27] [--contar-filas]
    python scripts/inventario_historicos.py --urls-faltantes > faltantes.txt

Salidas: ``data/inventario_historicos.csv`` y ``docs/inventario_historicos.md``.

Fuente: DGE, Datos Abiertos COVID-19, directorio de históricos
(https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/historicos/).
El patrón de URL debe confirmarse con el primer archivo descargado.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fuentes import CITA_DGE, RAIZ, leer_registro, ruta_relativa, sha256_archivo  # noqa: E402

DIR_HIST = RAIZ / "data" / "raw" / "dge" / "historicos"
DIR_PROC_HIST = RAIZ / "data" / "processed" / "historicos"
SALIDA_CSV = RAIZ / "data" / "inventario_historicos.csv"
SALIDA_MD = RAIZ / "docs" / "inventario_historicos.md"
INICIO = date(2020, 4, 14)
URL = ("https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/historicos/"
       "{a:04d}/{m:02d}/datos_abiertos_covid19_{d:02d}.{m:02d}.{a:04d}.zip")
PATRON = re.compile(r"datos_abiertos_covid19_(\d{2})\.(\d{2})\.(\d{4})\.zip$")
CAMPOS = ["version", "dia_semana", "en_rejilla_semanal", "nombre_esperado", "url_esperada",
          "presente_local", "archivo_local", "bytes", "sha256", "registrado",
          "fecha_actualizacion_interna", "coincide_fecha", "n_columnas", "esquema",
          "firma_columnas", "filas", "procesado"]


def nombre(f: date) -> str:
    return f"datos_abiertos_covid19_{f.day:02d}.{f.month:02d}.{f.year:04d}.zip"


def url(f: date) -> str:
    return URL.format(a=f.year, m=f.month, d=f.day)


def etiqueta_esquema(cols: list[str]) -> str:
    c = set(cols)
    partes = []
    if "CLASIFICACION_FINAL" in c:
        partes.append("CLASIFICACION_FINAL")
    elif "RESULTADO_LAB" in c:
        partes.append("RESULTADO_LAB")
    elif "RESULTADO" in c:
        partes.append("RESULTADO")
    if "TOMA_MUESTRA_ANTIGENO" in c or "RESULTADO_ANTIGENO" in c:
        partes.append("+antígeno")
    if "TOMA_MUESTRA_LAB" in c or "TOMA_MUESTRA" in c:
        partes.append("+toma_muestra")
    return " ".join(partes) or "desconocido"


def inspeccionar(ruta: Path, contar: bool) -> dict:
    info = {"bytes": ruta.stat().st_size, "sha256": sha256_archivo(ruta)}
    try:
        with zipfile.ZipFile(ruta) as z:
            csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
            with z.open(csvs[0]) as f:
                t = io.TextIOWrapper(f, encoding="latin-1", newline="")
                lector = csv.reader(t)
                cols = [c.strip().removeprefix("\ufeff").removeprefix("ï»¿").upper() for c in next(lector)]
                fila = next(lector, None)
                n = 1 + sum(1 for _ in lector) if contar and fila is not None else None
    except (zipfile.BadZipFile, IndexError, StopIteration) as e:
        info.update(esquema=f"ERROR: {type(e).__name__}")
        return info
    fa = ""
    if fila is not None and "FECHA_ACTUALIZACION" in cols:
        fa = fila[cols.index("FECHA_ACTUALIZACION")].strip()
    info.update(n_columnas=len(cols), esquema=etiqueta_esquema(cols),
                firma_columnas=hashlib.sha256(",".join(cols).encode()).hexdigest()[:12],
                fecha_actualizacion_interna=fa, filas="" if n is None else n, _cols=cols)
    return info


def construir(hasta: date, contar: bool) -> tuple[list[dict], dict[str, list[str]]]:
    registrados = {x.archivo for x in leer_registro()}
    locales = {}
    if DIR_HIST.exists():
        for p in DIR_HIST.rglob("*.zip"):
            m = PATRON.search(p.name)
            if m:
                d, mm, a = map(int, m.groups())
                locales[date(a, mm, d)] = p
    rejilla = []
    f = INICIO
    while f <= hasta:
        rejilla.append(f)
        f += timedelta(days=7)
    fechas = sorted(set(rejilla) | set(locales))
    filas, columnas = [], {}
    for f in fechas:
        fila = {k: "" for k in CAMPOS}
        fila.update(version=f.isoformat(), dia_semana=["lun", "mar", "mié", "jue", "vie",
                                                        "sáb", "dom"][f.weekday()],
                    en_rejilla_semanal="sí" if f in rejilla else "no",
                    nombre_esperado=nombre(f), url_esperada=url(f),
                    presente_local="no", registrado="",
                    procesado="sí" if (DIR_PROC_HIST / f.isoformat() / "manifiesto.json").exists() else "no")
        if f in locales:
            p = locales[f]
            info = inspeccionar(p, contar)
            cols = info.pop("_cols", None)
            if cols:
                columnas[f.isoformat()] = cols
            fila.update(info)
            fila.update(presente_local="sí", archivo_local=ruta_relativa(p),
                        registrado="sí" if ruta_relativa(p) in registrados else "no")
            fa = fila.get("fecha_actualizacion_interna", "")
            fila["coincide_fecha"] = "" if not fa else ("sí" if fa == f.isoformat() else "no")
        filas.append(fila)
    return filas, columnas


def escribir(filas, columnas, hasta: date) -> None:
    SALIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)

    rej = [x for x in filas if x["en_rejilla_semanal"] == "sí"]
    pres = [x for x in rej if x["presente_local"] == "sí"]
    falt = [x for x in rej if x["presente_local"] == "no"]
    extra = [x for x in filas if x["en_rejilla_semanal"] == "no"]
    noreg = [x for x in filas if x["presente_local"] == "sí" and x["registrado"] == "no"]
    malf = [x for x in filas if x["coincide_fecha"] == "no"]

    # cronología de esquemas
    crono, previo = [], None
    for v in sorted(columnas):
        cols = columnas[v]
        if previo is None or cols != previo[1]:
            mas = sorted(set(cols) - set(previo[1])) if previo else []
            menos = sorted(set(previo[1]) - set(cols)) if previo else []
            crono.append((v, etiqueta_esquema(cols), len(cols), mas, menos))
        previo = (v, cols)

    L = [
        "# Inventario de versiones históricas del microdato DGE",
        "",
        "> Generado por `python scripts/inventario_historicos.py`. **Solo inventario**: "
        "el tratamiento de las versiones (análisis por versión, nowcasting, elección de "
        "versión de referencia) queda pendiente de decisión.",
        "",
        f"**Fuente:** {CITA_DGE} Directorio de históricos: "
        "https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/historicos/ "
        "(patrón `historicos/AAAA/MM/datos_abiertos_covid19_DD.MM.AAAA.zip`; "
        "**confirmar** con el primer archivo descargado — si difiere, corregir `URL` en el script).",
        "",
        "## Resumen",
        "",
        f"- Rejilla semanal: martes desde {INICIO.isoformat()} hasta {hasta.isoformat()} "
        f"→ **{len(rej)} versiones esperadas**.",
        f"- Presentes en `data/raw/dge/historicos/`: **{len(pres)}**; faltan **{len(falt)}**.",
        f"- Versiones locales fuera de la rejilla (otro día): {len(extra)}.",
        f"- Presentes sin registro de procedencia: {len(noreg)}"
        + (" — registrar con `python scripts/registrar_fuente.py data/raw/dge/historicos/*.zip "
           "--nivel DGE --url-historico --fecha-descarga AAAA-MM-DD`." if noreg else "."),
        f"- `FECHA_ACTUALIZACION` interna distinta a la fecha del nombre: {len(malf)}"
        + (": " + ", ".join(x["version"] for x in malf) if malf else "."),
        "",
        "Detalle por versión (URL, hash, esquema, etc.): `data/inventario_historicos.csv`.",
        "Lista de URLs faltantes: `python scripts/inventario_historicos.py --urls-faltantes`.",
        "",
        "## Cronología de esquemas observada en los archivos locales",
        "",
    ]
    if crono:
        L += ["| Primera versión | Esquema | Nº columnas | Columnas nuevas | Columnas retiradas |",
              "|---|---|---|---|---|"]
        for v, e, n, mas, menos in crono:
            L.append(f"| {v} | {e} | {n} | {', '.join(mas) or '—'} | {', '.join(menos) or '—'} |")
        L.append("")
        L.append("(Basada solo en las versiones descargadas; un cambio puede haber ocurrido "
                 "entre dos versiones locales no consecutivas.)")
    else:
        L.append("Sin archivos locales todavía: la cronología se llena al descargar versiones.")
    L += [
        "",
        "## Cambios de esquema esperados (a contrastar con la cronología observada)",
        "",
        "Ver `docs/diccionario_datos.md` §4. En particular: `RESULTADO` → `RESULTADO_LAB` + "
        "`CLASIFICACION_FINAL` (otoño 2020) y alta de `TOMA_MUESTRA_ANTIGENO`/"
        "`RESULTADO_ANTIGENO` (fines de 2020–inicios de 2021).",
        "",
        "## Estado por versión (rejilla semanal)",
        "",
        "| Versión | Local | Registrado | Esquema | Procesado |",
        "|---|---|---|---|---|",
    ]
    for x in rej:
        L.append(f"| {x['version']} | {x['presente_local']} | {x['registrado'] or '—'} | "
                 f"{x['esquema'] or '—'} | {x['procesado']} |")
    if extra:
        L += ["", "## Versiones locales fuera de la rejilla", "",
              *[f"- {x['version']} ({x['dia_semana']}): `{x['archivo_local']}`" for x in extra]]
    L.append("")
    SALIDA_MD.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_MD.write_text("\n".join(L), encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hasta", type=date.fromisoformat, default=date(2023, 6, 27),
                   help="última fecha de la rejilla (por omisión 2023-06-27, la semana del CSV del tablero)")
    p.add_argument("--contar-filas", action="store_true", help="contar filas de cada archivo (lento)")
    p.add_argument("--urls-faltantes", action="store_true",
                   help="imprimir solo las URLs de versiones de la rejilla que faltan localmente")
    a = p.parse_args(argv)
    filas, columnas = construir(a.hasta, a.contar_filas)
    if a.urls_faltantes:
        for x in filas:
            if x["en_rejilla_semanal"] == "sí" and x["presente_local"] == "no":
                print(x["url_esperada"])
        return 0
    escribir(filas, columnas, a.hasta)
    n = sum(1 for x in filas if x["en_rejilla_semanal"] == "sí")
    print(f"Inventario: {n} versiones semanales → {ruta_relativa(SALIDA_MD)}, {ruta_relativa(SALIDA_CSV)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
