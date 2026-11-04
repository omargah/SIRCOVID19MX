"""Serie diaria nacional de incidencia por fecha de inicio de síntomas.

Fuente primaria: microdatos de la DGE (Secretaría de Salud), descargados a
mano en ``data/raw/dge/`` y registrados con ``scripts/registrar_fuente.py``.

Uso (regenera todo con un comando)::

    python -m src.datos                      # lee data/raw/dge/*.zip|*.csv
    python -m src.datos ARCHIVO [ARCHIVO…]   # entradas explícitas
    python -m src.datos --verificar-determinismo

Salidas (``data/processed/``):

* ``serie_nacional_sintomas.csv`` — serie principal (incidencia diaria).
* ``serie_nacional_hosp_def.csv`` — segunda serie: hospitalizaciones por
  fecha de ingreso y defunciones por fecha de defunción (mismo microdato).
* ``cubos/*.csv`` — agregados intermedios usados por la EDA y la comparación.
* ``manifiesto.json`` — procedencia (hashes de entrada y salida), parámetros
  y contadores de exclusión.

Determinismo: no se usan semillas, relojes ni orden de diccionarios; todo
se ordena explícitamente y se escribe con formato fijo. Dos corridas con
los mismos archivos de entrada producen archivos idénticos byte a byte
(``--verificar-determinismo`` lo comprueba).

Definición de caso confirmado (por omisión, la vigente desde oct-2020 en la
base DGE y la usada por el tablero): ``CLASIFICACION_FINAL ∈ {1, 2, 3}``
(asociación clínica-epidemiológica, dictaminación, laboratorio/antígeno), con
entidad de residencia 1–32. Ver ``docs/diccionario_datos.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src.fuentes import CITA_DGE, RAIZ, exigir_registro, ruta_relativa

DIR_ENTRADA = RAIZ / "data" / "raw" / "dge"
DIR_SALIDA = RAIZ / "data" / "processed"
FECHA_MIN = pd.Timestamp("2020-01-01")
RETRASO_MAX = 60  # días; retrasos mayores se agrupan en RETRASO_MAX

# Columnas que se leen del microdato (las ausentes se toleran según esquema).
COLUMNAS = {
    "FECHA_ACTUALIZACION", "ID_REGISTRO", "ORIGEN", "ENTIDAD_UM", "ENTIDAD_RES",
    "TIPO_PACIENTE", "FECHA_INGRESO", "FECHA_SINTOMAS", "FECHA_DEF", "UCI",
    "CLASIFICACION_FINAL", "RESULTADO_LAB", "RESULTADO", "TOMA_MUESTRA_LAB",
    "TOMA_MUESTRA_ANTIGENO", "RESULTADO_ANTIGENO",
}
OBLIGATORIAS = {"FECHA_ACTUALIZACION", "ID_REGISTRO", "ENTIDAD_RES",
                "FECHA_SINTOMAS", "FECHA_INGRESO", "FECHA_DEF", "TIPO_PACIENTE"}

# Equivalencia de esquemas antiguos a CLASIFICACION_FINAL (1–7).
#   RESULTADO (≤ oct-2020): 1 positivo, 2 no positivo, 3 pendiente
#   RESULTADO_LAB: 1 positivo, 2 no positivo, 3 pendiente, 4 no adecuado, 97 no aplica
MAPA_RESULTADO = {1: 3, 2: 7, 3: 6}
MAPA_RESULTADO_LAB = {1: 3, 2: 7, 3: 6, 4: 4, 97: 6}

CLAVES_SINTOMAS = ["fecha", "clasif", "res_valida", "um_valida", "tipo_paciente",
                   "origen", "muestra_lab", "muestra_ag", "fallecio"]
CLAVES_INGRESO = ["fecha", "clasif", "res_valida", "tipo_paciente", "uci",
                  "origen", "muestra_lab", "muestra_ag"]
CLAVES_DEF = ["fecha", "clasif", "res_valida"]
CLAVES_RETRASO = ["semana_sintomas", "clasif", "tipo_paciente", "retraso"]


# --------------------------------------------------------------------------
# Lectura
# --------------------------------------------------------------------------

def _miembro_csv(ruta: Path) -> str | None:
    if ruta.suffix.lower() != ".zip":
        return None
    with zipfile.ZipFile(ruta) as z:
        csvs = sorted(n for n in z.namelist() if n.lower().endswith(".csv"))
    if len(csvs) != 1:
        raise SystemExit(f"{ruta}: se esperaba exactamente un CSV dentro del zip, hay {csvs}")
    return csvs[0]


def _norm(c: str) -> str:
    """Nombre de columna normalizado (sin espacios ni BOM UTF-8 leído como latin-1)."""
    return c.strip().removeprefix("\ufeff").removeprefix("ï»¿").upper()


def leer_trozos(ruta: Path, chunksize: int):
    """Itera sobre trozos del microdato como DataFrame de cadenas."""
    miembro = _miembro_csv(ruta)
    # latin-1 decodifica cualquier byte; las columnas usadas son ASCII, así
    # que la codificación real del archivo (UTF-8 o latin-1) no afecta.
    opciones = dict(dtype=str, encoding="latin-1", chunksize=chunksize,
                    usecols=lambda c: _norm(c) in COLUMNAS,
                    keep_default_na=False)
    if miembro is None:
        fuente = open(ruta, "rb")
    else:
        fuente = zipfile.ZipFile(ruta).open(miembro)
    with fuente:
        for trozo in pd.read_csv(fuente, **opciones):
            trozo.columns = [_norm(c) for c in trozo.columns]
            yield trozo


def fecha_actualizacion(ruta: Path) -> str:
    trozo = next(leer_trozos(ruta, 1000))
    return str(parse_fecha(trozo["FECHA_ACTUALIZACION"]).max().date())


def parse_fecha(s: pd.Series) -> pd.Series:
    """AAAA-MM-DD (formato DGE) con respaldo DD/MM/AAAA; 9999-99-99 → NaT."""
    s = s.str.strip()
    f = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    resto = f.isna() & s.str.contains("/", regex=False)
    if resto.any():
        f[resto] = pd.to_datetime(s[resto], format="%d/%m/%Y", errors="coerce")
    return f


def _entero(df: pd.DataFrame, col: str, defecto=-1) -> pd.Series:
    if col not in df:
        return pd.Series(defecto, index=df.index, dtype="int64")
    return pd.to_numeric(df[col].str.strip(), errors="coerce").fillna(defecto).astype("int64")


# --------------------------------------------------------------------------
# Agregación por trozo
# --------------------------------------------------------------------------

@dataclass
class Acumulador:
    cubos: dict[str, list[pd.DataFrame]] = field(default_factory=lambda: {
        "por_sintomas": [], "por_ingreso": [], "por_defuncion": [],
        "retraso_ingreso": [], "retraso_defuncion": []})
    contadores: dict[str, int] = field(default_factory=dict)
    esquemas: set = field(default_factory=set)
    fecha_corte: pd.Timestamp | None = None
    vistos: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.uint64))

    def sumar(self, clave: str, n: int) -> None:
        self.contadores[clave] = self.contadores.get(clave, 0) + int(n)


def _contar(df: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    return df.groupby(claves, dropna=False, sort=False).size().rename("n").reset_index()


def procesar_trozo(df: pd.DataFrame, acc: Acumulador) -> None:
    faltan = OBLIGATORIAS - set(df.columns)
    if faltan:
        raise SystemExit(f"Faltan columnas obligatorias en el microdato: {sorted(faltan)}")
    acc.sumar("filas_leidas", len(df))

    # --- duplicados de ID_REGISTRO (dentro y entre archivos) -------------
    h = pd.util.hash_pandas_object(df["ID_REGISTRO"].str.strip(), index=False).to_numpy()
    dup = pd.Series(h).duplicated().to_numpy() | np.isin(h, acc.vistos)
    acc.sumar("duplicados_id_descartados", dup.sum())
    df, h = df.loc[~dup], h[~dup]
    acc.vistos = np.union1d(acc.vistos, h)

    # --- clasificación homologada ----------------------------------------
    if "CLASIFICACION_FINAL" in df:
        acc.esquemas.add("CLASIFICACION_FINAL")
        clasif = _entero(df, "CLASIFICACION_FINAL")
    elif "RESULTADO_LAB" in df:
        acc.esquemas.add("RESULTADO_LAB (homologado)")
        clasif = _entero(df, "RESULTADO_LAB").map(MAPA_RESULTADO_LAB).fillna(-1).astype("int64")
    elif "RESULTADO" in df:
        acc.esquemas.add("RESULTADO (homologado)")
        clasif = _entero(df, "RESULTADO").map(MAPA_RESULTADO).fillna(-1).astype("int64")
    else:
        raise SystemExit("El microdato no tiene CLASIFICACION_FINAL, RESULTADO_LAB ni RESULTADO")

    fa = parse_fecha(df["FECHA_ACTUALIZACION"])
    fs = parse_fecha(df["FECHA_SINTOMAS"])
    fi = parse_fecha(df["FECHA_INGRESO"])
    fd = parse_fecha(df["FECHA_DEF"])
    corte = fa.max()
    acc.fecha_corte = corte if acc.fecha_corte is None else max(acc.fecha_corte, corte)

    res = _entero(df, "ENTIDAD_RES")
    um = _entero(df, "ENTIDAD_UM")
    tm_lab = _entero(df, "TOMA_MUESTRA_LAB")
    tm_ag = _entero(df, "TOMA_MUESTRA_ANTIGENO")
    if "TOMA_MUESTRA_LAB" not in df:
        acc.esquemas.add("sin TOMA_MUESTRA_* (esquema 2020: muestra desconocida)")

    base = pd.DataFrame({
        "clasif": clasif.to_numpy(),
        "res_valida": res.between(1, 32).astype("int8").to_numpy(),
        "um_valida": um.between(1, 32).astype("int8").to_numpy(),
        "tipo_paciente": _entero(df, "TIPO_PACIENTE").to_numpy(),
        "origen": _entero(df, "ORIGEN").to_numpy(),
        "uci": _entero(df, "UCI").to_numpy(),
        "muestra_lab": tm_lab.to_numpy(),
        "muestra_ag": tm_ag.to_numpy(),
        "fallecio": fd.notna().astype("int8").to_numpy(),
    })

    # --- validez de fechas -----------------------------------------------
    fs_ok = fs.notna() & (fs >= FECHA_MIN) & (fs <= fa)
    acc.sumar("fecha_sintomas_invalida_o_fuera_de_rango", (~fs_ok).sum())
    acc.sumar("entidad_res_fuera_1_32", (base["res_valida"] == 0).sum())
    fs_ok = fs_ok.to_numpy()
    fi_ok = (fi.notna() & (fi >= FECHA_MIN) & (fi <= fa)).to_numpy()
    fd_ok = (fd.notna() & (fd >= FECHA_MIN) & (fd <= fa)).to_numpy()
    acc.sumar("fecha_ingreso_invalida_o_fuera_de_rango", (~fi_ok).sum())
    acc.sumar("fecha_def_fuera_de_rango", (fd.notna().to_numpy() & ~fd_ok).sum())

    c = acc.cubos
    b = base.assign(fecha=fs.to_numpy())[fs_ok]
    c["por_sintomas"].append(_contar(b, CLAVES_SINTOMAS))
    b = base.assign(fecha=fi.to_numpy())[fi_ok]
    c["por_ingreso"].append(_contar(b, CLAVES_INGRESO))
    b = base.assign(fecha=fd.to_numpy())[fd_ok]
    c["por_defuncion"].append(_contar(b, CLAVES_DEF))

    # --- retrasos (solo confirmados 1–3, residentes 1–32) ----------------
    conf = base["clasif"].isin([1, 2, 3]).to_numpy() & (base["res_valida"] == 1).to_numpy()
    semana = (fs - pd.to_timedelta(fs.dt.weekday, unit="D")).to_numpy()
    for nombre, f2, ok2 in (("retraso_ingreso", fi, fi_ok), ("retraso_defuncion", fd, fd_ok)):
        m = conf & fs_ok & ok2
        r = (f2 - fs).dt.days.to_numpy()[m]
        b = pd.DataFrame({"semana_sintomas": semana[m], "clasif": base["clasif"].to_numpy()[m],
                          "tipo_paciente": base["tipo_paciente"].to_numpy()[m],
                          "retraso": np.clip(r, -1, RETRASO_MAX)})
        c[nombre].append(_contar(b, CLAVES_RETRASO))


# --------------------------------------------------------------------------
# Consolidación y escritura
# --------------------------------------------------------------------------

def consolidar(partes: list[pd.DataFrame], claves: list[str]) -> pd.DataFrame:
    if not partes:
        return pd.DataFrame(columns=claves + ["n"])
    df = pd.concat(partes, ignore_index=True)
    df = df.groupby(claves, dropna=False, sort=True)["n"].sum().reset_index()
    return df.sort_values(claves, kind="mergesort").reset_index(drop=True)


def escribir_csv(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    df.to_csv(ruta, index=False, lineterminator="\n", encoding="utf-8")


def _suma_por_fecha(cubo: pd.DataFrame, mascara, indice) -> pd.Series:
    return (cubo[mascara].groupby("fecha")["n"].sum()
            .reindex(indice, fill_value=0).astype("int64"))


def armar_series(cubos: dict[str, pd.DataFrame], corte: pd.Timestamp):
    cs, ci, cd = cubos["por_sintomas"], cubos["por_ingreso"], cubos["por_defuncion"]
    inicio = min(x["fecha"].min() for x in (cs, ci) if len(x))
    idx = pd.date_range(inicio, corte, freq="D", name="fecha")

    res = cs["res_valida"] == 1
    conf = cs["clasif"].isin([1, 2, 3])
    muestra = (cs["muestra_lab"] == 1) | (cs["muestra_ag"] == 1)
    s = pd.DataFrame(index=idx)
    s["confirmados"] = _suma_por_fecha(cs, conf & res, idx)
    s["confirmados_lab_antigeno"] = _suma_por_fecha(cs, (cs["clasif"] == 3) & res, idx)
    s["confirmados_asoc_clin_epi"] = _suma_por_fecha(cs, (cs["clasif"] == 1) & res, idx)
    s["confirmados_dictaminacion"] = _suma_por_fecha(cs, (cs["clasif"] == 2) & res, idx)
    s["confirmados_todas_entidades"] = _suma_por_fecha(cs, conf, idx)
    s["confirmados_por_entidad_um"] = _suma_por_fecha(cs, conf & (cs["um_valida"] == 1), idx)
    s["sospechosos"] = _suma_por_fecha(cs, (cs["clasif"] == 6) & res, idx)
    s["negativos"] = _suma_por_fecha(cs, (cs["clasif"] == 7) & res, idx)
    s["registros"] = _suma_por_fecha(cs, res, idx)
    s["con_muestra"] = _suma_por_fecha(cs, muestra & res, idx)
    s["dias_antes_corte"] = (corte - idx).days.astype("int64")

    resi = ci["res_valida"] == 1
    confi = ci["clasif"].isin([1, 2, 3])
    hosp = ci["tipo_paciente"] == 2
    resd = cd["res_valida"] == 1
    h = pd.DataFrame(index=idx)
    h["hospitalizados_confirmados"] = _suma_por_fecha(ci, confi & resi & hosp, idx)
    h["uci_confirmados"] = _suma_por_fecha(ci, confi & resi & hosp & (ci["uci"] == 1), idx)
    h["hospitalizados_todos"] = _suma_por_fecha(ci, resi & hosp, idx)
    h["defunciones_confirmadas"] = _suma_por_fecha(cd, cd["clasif"].isin([1, 2, 3]) & resd, idx)
    h["defunciones_confirmadas_lab_antigeno"] = _suma_por_fecha(cd, (cd["clasif"] == 3) & resd, idx)
    h["defunciones_sospechosas"] = _suma_por_fecha(cd, (cd["clasif"] == 6) & resd, idx)
    h["defunciones_conf_por_fecha_sintomas"] = _suma_por_fecha(
        cs, conf & res & (cs["fallecio"] == 1), idx)
    h["dias_antes_corte"] = s["dias_antes_corte"]
    return s.reset_index(), h.reset_index()


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def construir(entradas: list[Path], salida: Path, chunksize: int = 500_000,
              estricto: bool = True, verbose: bool = True) -> dict:
    entradas = [Path(e) for e in entradas]
    if not entradas:
        raise SystemExit(
            f"No hay microdatos en {ruta_relativa(DIR_ENTRADA)}/. Descarga el archivo de la "
            "DGE (ver data/raw/README.md), regístralo y vuelve a correr.")
    procedencia = exigir_registro(entradas, estricto=estricto)

    # Orden determinista: versión más reciente primero (gana ante IDs repetidos),
    # desempate por nombre de archivo.
    fechas = {e: fecha_actualizacion(e) for e in entradas}
    entradas = sorted(entradas, key=lambda e: (-pd.Timestamp(fechas[e]).value, e.name))

    acc = Acumulador()
    for e in entradas:
        if verbose:
            print(f"Leyendo {ruta_relativa(e)} (actualización {fechas[e]})…", file=sys.stderr)
        for trozo in leer_trozos(e, chunksize):
            procesar_trozo(trozo, acc)

    claves = {"por_sintomas": CLAVES_SINTOMAS, "por_ingreso": CLAVES_INGRESO,
              "por_defuncion": CLAVES_DEF, "retraso_ingreso": CLAVES_RETRASO,
              "retraso_defuncion": CLAVES_RETRASO}
    cubos = {k: consolidar(v, claves[k]) for k, v in acc.cubos.items()}
    serie, serie2 = armar_series(cubos, acc.fecha_corte)

    salida.mkdir(parents=True, exist_ok=True)
    archivos = {
        "serie_nacional_sintomas.csv": serie,
        "serie_nacional_hosp_def.csv": serie2,
        **{f"cubos/{k}.csv": v for k, v in cubos.items()},
    }
    for nombre, df in archivos.items():
        escribir_csv(df, salida / nombre)

    fecha_rel = {ruta_relativa(e): f for e, f in fechas.items()}
    manifiesto = {
        "descripcion": "Serie diaria nacional de casos confirmados COVID-19 por fecha de "
                       "inicio de síntomas, construida desde el microdato DGE.",
        "cita_fuente_primaria": CITA_DGE,
        "fecha_corte_microdato": str(acc.fecha_corte.date()),
        "entradas": [{**p, "fecha_actualizacion": fecha_rel.get(p["archivo"])}
                     for p in procedencia],
        "orden_lectura": [ruta_relativa(e) for e in entradas],
        "esquemas_detectados": sorted(acc.esquemas),
        "definiciones": {
            "confirmados": "CLASIFICACION_FINAL in {1,2,3} y ENTIDAD_RES in 1..32, "
                           "contados en FECHA_SINTOMAS",
            "hospitalizados_confirmados": "confirmados con TIPO_PACIENTE=2, contados en FECHA_INGRESO",
            "defunciones_confirmadas": "confirmados con FECHA_DEF válida, contados en FECHA_DEF",
            "homologacion_esquemas_antiguos": {
                "RESULTADO": MAPA_RESULTADO, "RESULTADO_LAB": MAPA_RESULTADO_LAB},
            "rango_fechas_validas": f"[{FECHA_MIN.date()}, FECHA_ACTUALIZACION del registro]",
            "duplicados": "ID_REGISTRO repetido: se conserva el de la versión más reciente",
        },
        "contadores": dict(sorted(acc.contadores.items())),
        "totales": {
            "confirmados": int(serie["confirmados"].sum()),
            "hospitalizados_confirmados": int(serie2["hospitalizados_confirmados"].sum()),
            "defunciones_confirmadas": int(serie2["defunciones_confirmadas"].sum()),
        },
        "codigo_sha256": {"src/datos.py": sha256(Path(__file__))},
        "versiones": {"python": sys.version.split()[0], "pandas": pd.__version__,
                      "numpy": np.__version__},
        "salidas_sha256": {n: sha256(salida / n) for n in sorted(archivos)},
    }
    (salida / "manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    if verbose:
        print(f"Serie escrita en {ruta_relativa(salida)}/ — corte {manifiesto['fecha_corte_microdato']}, "
              f"{manifiesto['totales']['confirmados']:,} confirmados.", file=sys.stderr)
    return manifiesto


def entradas_por_omision() -> list[Path]:
    return sorted(p for p in DIR_ENTRADA.iterdir()
                  if p.is_file() and p.suffix.lower() in (".zip", ".csv")) \
        if DIR_ENTRADA.exists() else []


def hashes_directorio(d: Path) -> dict[str, str]:
    return {ruta_relativa(p).replace(ruta_relativa(d) + "/", ""): sha256(p)
            for p in sorted(d.rglob("*")) if p.is_file()}


def verificar_determinismo(entradas, chunksize, estricto) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        construir(entradas, a, chunksize, estricto, verbose=False)
        construir(entradas, b, chunksize, estricto, verbose=False)
        ha, hb = hashes_directorio(a), hashes_directorio(b)
    distintos = sorted(k for k in set(ha) | set(hb) if ha.get(k) != hb.get(k))
    if distintos:
        print("NO determinista; difieren:", *distintos, sep="\n  ")
        return 1
    print(f"Determinista: {len(ha)} archivos idénticos en dos corridas.")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Construye la serie nacional desde el microdato DGE.")
    p.add_argument("entradas", nargs="*", type=Path,
                   help="microdatos DGE (.zip o .csv); por omisión data/raw/dge/*")
    p.add_argument("--salida", type=Path, default=DIR_SALIDA)
    p.add_argument("--chunksize", type=int, default=500_000)
    p.add_argument("--permitir-no-registrados", action="store_true",
                   help="no exigir registro en data/fuentes.csv")
    p.add_argument("--verificar-determinismo", action="store_true",
                   help="correr dos veces en directorios temporales y comparar hashes")
    a = p.parse_args(argv)
    entradas = a.entradas or entradas_por_omision()
    if a.verificar_determinismo:
        return verificar_determinismo(entradas, a.chunksize, not a.permitir_no_registrados)
    construir(entradas, a.salida, a.chunksize, not a.permitir_no_registrados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
