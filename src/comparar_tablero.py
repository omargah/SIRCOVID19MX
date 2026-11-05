"""Compara la serie propia (microdato DGE) contra el CSV del tablero CONAHCYT.

Fuentes:
  1. Primaria — DGE, microdato (``data/processed/serie_nacional_sintomas.csv``,
     generado por ``python -m src.datos``).
  2. Secundaria — tablero CONAHCYT,
     ``data/raw/tablero/Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv``
     (el archivo que usó el PT1 original), que a su vez deriva de la DGE.

Uso::

    python -m src.comparar_tablero [--tablero RUTA] [--serie RUTA]

Escribe ``data/processed/comparacion_tablero.csv``,
``docs/figuras/comparacion_tablero.png`` y la nota
``docs/nota_diferencias.md`` (se regenera en cada corrida).

Cada diferencia se clasifica con una causa. Las causas se diagnostican con
pruebas explícitas y reproducibles (no a ojo):

* D1 cobertura temporal (fechas presentes en una sola fuente);
* D2 corte de versión distinto (fecha de actualización del microdato vs.
  fecha del archivo del tablero) → truncamiento/rezago al final;
* D3 fecha de referencia (desfase de días que minimiza la discrepancia);
* D4 definición de caso / ámbito geográfico (qué variante de la serie
  propia se acerca más al tablero);
* D5 reclasificación retroactiva entre versiones (residuo lejos del corte);
* D6 consistencia interna del tablero (Nacional vs. suma de entidades);
* D7 reproducción de las cifras del PT1 (confirma que es el mismo archivo).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.fuentes import CITA_DGE, CITA_TABLERO, RAIZ, exigir_registro, ruta_relativa

DIR_TABLERO = RAIZ / "data" / "raw" / "tablero"
SERIE = RAIZ / "data" / "processed" / "serie_nacional_sintomas.csv"
MANIFIESTO = RAIZ / "data" / "processed" / "manifiesto.json"
SALIDA_CSV = RAIZ / "data" / "processed" / "comparacion_tablero.csv"
NOTA = RAIZ / "docs" / "nota_diferencias.md"
FIGURA = RAIZ / "docs" / "figuras" / "comparacion_tablero.png"

# Cifras publicadas en el PT1 original (v0-anterior/Proyecto_Terminal_1 (3).pdf,
# Tabla 2), calculadas con el CSV del tablero 20230625.
PT1 = {"inicio": "2020-02-26", "fin": "2023-06-24", "total": 7_633_355,
       "pico_suavizado": 62_299, "fecha_pico": "2022-01-15"}

VARIANTES = {
    "confirmados": "CLASIFICACION_FINAL 1–3, residencia 1–32 (definición por omisión)",
    "confirmados_lab_antigeno": "solo CLASIFICACION_FINAL 3 (laboratorio/antígeno)",
    "confirmados_todas_entidades": "CLASIFICACION_FINAL 1–3, cualquier ENTIDAD_RES",
    "confirmados_por_entidad_um": "CLASIFICACION_FINAL 1–3, por entidad de la unidad médica 1–32",
}


def leer_tablero(ruta: Path) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    df = pd.read_csv(ruta, dtype={"cve_ent": str})
    cols_fecha = [c for c in df.columns if re.fullmatch(r"\d{2}-\d{2}-\d{4}", c)]
    if not cols_fecha:
        raise SystemExit(f"{ruta}: no encontré columnas de fecha DD-MM-AAAA")
    fechas = pd.to_datetime(cols_fecha, format="%d-%m-%Y")
    nac = df[df["nombre"].str.strip().str.lower() == "nacional"]
    if len(nac) != 1:
        raise SystemExit(f"{ruta}: se esperaba una fila 'Nacional', hay {len(nac)}")
    serie = pd.Series(nac[cols_fecha].iloc[0].astype(float).to_numpy(), index=fechas, name="tablero")
    estados = df[df["nombre"].str.strip().str.lower() != "nacional"]
    suma = pd.Series(estados[cols_fecha].astype(float).sum().to_numpy(), index=fechas)
    return serie, suma, df


def corte_de_nombre(ruta: Path) -> pd.Timestamp | None:
    m = re.search(r"(20\d{6})", ruta.name)
    return pd.Timestamp(m.group(1)) if m else None


def mejor_desfase(a: pd.Series, b: pd.Series, max_lag: int = 7) -> tuple[int, dict[int, float]]:
    """Desfase k (días) que minimiza sum|a(t) - b(t+k)| en el rango común."""
    l1 = {}
    for k in range(-max_lag, max_lag + 1):
        bk = b.shift(-k)
        m = a.notna() & bk.notna()
        l1[k] = float((a[m] - bk[m]).abs().sum())
    return min(l1, key=lambda k: (l1[k], abs(k))), l1


def fmt(x, dec=0) -> str:
    if isinstance(x, (float, np.floating)) and not np.isfinite(x):
        return "—"
    return f"{x:,.{dec}f}"


def comparar(tablero_csv: Path, serie_csv: Path, manifiesto: Path, estricto: bool = True) -> dict:
    proc = exigir_registro([tablero_csv], estricto=estricto)[0]
    tab, suma_estados, _ = leer_tablero(tablero_csv)
    s = pd.read_csv(serie_csv, parse_dates=["fecha"]).set_index("fecha")
    man = json.loads(manifiesto.read_text(encoding="utf-8")) if manifiesto.exists() else {}
    corte_dge = pd.Timestamp(man.get("fecha_corte_microdato", s.index.max()))
    corte_tab = corte_de_nombre(tablero_csv) or tab.index.max()

    idx = s.index.union(tab.index)
    comun = s.index.intersection(tab.index)
    d = pd.DataFrame(index=idx)
    d.index.name = "fecha"
    d["serie_dge"] = s["confirmados"].reindex(idx)
    d["tablero"] = tab.reindex(idx)
    d["diferencia"] = d["serie_dge"] - d["tablero"]
    d["dias_antes_corte_tablero"] = (corte_tab - idx).days
    for v in VARIANTES:
        if v != "confirmados" and v in s:
            d[v] = s[v].reindex(idx)
    d_c = d.loc[comun]

    hallazgos = []

    # D1 cobertura
    solo_dge = s.index.difference(tab.index)
    solo_tab = tab.index.difference(s.index)
    casos_solo_dge = int(s.loc[solo_dge, "confirmados"].sum())
    casos_solo_tab = int(tab.loc[solo_tab].sum())
    hallazgos.append({
        "id": "D1", "tema": "Cobertura temporal",
        "magnitud": f"{len(solo_dge)} días solo en DGE ({fmt(casos_solo_dge)} casos); "
                    f"{len(solo_tab)} días solo en tablero ({fmt(casos_solo_tab)} casos)",
        "causa": "El tablero inicia su serie el "
                 f"{tab.index.min().date()} y termina el {tab.index.max().date()}; la serie DGE "
                 f"va de {s.index.min().date()} al corte del microdato ({corte_dge.date()}). "
                 "Los casos con inicio de síntomas anterior al inicio del tablero quedan fuera "
                 "de éste; los posteriores a su corte no existían cuando se generó.",
    })

    # D2 corte / truncamiento
    ventanas = [14, 30, 90]
    filas_v = []
    for w in ventanas:
        m = (d_c["dias_antes_corte_tablero"] >= 0) & (d_c["dias_antes_corte_tablero"] < w)
        filas_v.append((w, d_c.loc[m, "serie_dge"].sum(), d_c.loc[m, "tablero"].sum()))
    lejos = d_c["dias_antes_corte_tablero"] >= 90
    rel_cola = [(a - b) / b if b else np.nan for _, a, b in filas_v]
    if corte_dge == corte_tab:
        causa_d2 = "Mismo corte: la cola no se explica por versiones distintas."
    elif corte_dge < corte_tab:
        causa_d2 = (f"El microdato es ANTERIOR ({corte_dge.date()}) al tablero ({corte_tab.date()}): "
                    "en la cola el tablero incluye notificaciones tardías que el microdato aún no "
                    "tenía (rezago de notificación en la serie propia). Usar un microdato "
                    "posterior o igual al corte del tablero para la comparación.")
    else:
        causa_d2 = (
                    f"El microdato es posterior ({corte_dge.date()}) al tablero ({corte_tab.date()}): "
                    "los casos con síntomas en las semanas previas al corte del tablero aún no "
                    "estaban notificados cuando éste se generó (rezago de notificación / "
                    "truncamiento por la derecha). La discrepancia relativa debe crecer al "
                    "acercarse al corte del tablero.")
    hallazgos.append({
        "id": "D2", "tema": "Corte de versión y truncamiento al final",
        "magnitud": "; ".join(f"últimos {w} d: DGE {fmt(a)} vs tablero {fmt(b)} ({fmt(100*r,1)} %)"
                              for (w, a, b), r in zip(filas_v, rel_cola)),
        "causa": causa_d2,
    })

    # D3 desfase de fecha
    k, l1 = mejor_desfase(d_c["serie_dge"][lejos], d_c["tablero"][lejos])
    hallazgos.append({
        "id": "D3", "tema": "Fecha de referencia",
        "magnitud": f"desfase óptimo {k:+d} d (L1 con k=0: {fmt(l1[0])}; con k={k:+d}: {fmt(l1[k])})",
        "causa": ("Ambas series usan fecha de inicio de síntomas (desfase óptimo 0)."
                  if k == 0 else
                  f"La discrepancia mínima se obtiene desplazando {k:+d} días: indica una "
                  "fecha de referencia distinta (p. ej. ingreso vs. síntomas) o un corrimiento "
                  "en el encabezado de fechas del CSV del tablero. Revisar antes de usar."),
    })

    # D4 definición de caso / ámbito
    dist = {}
    for v in VARIANTES:
        col = "serie_dge" if v == "confirmados" else v
        if col in d_c:
            dist[v] = float((d_c.loc[lejos, col] - d_c.loc[lejos, "tablero"]).abs().sum())
    mejor = min(dist, key=dist.get) if dist else None
    hallazgos.append({
        "id": "D4", "tema": "Definición de caso y ámbito geográfico",
        "magnitud": "; ".join(f"{v}: L1={fmt(x)}" for v, x in dist.items()),
        "causa": (f"La variante más cercana al tablero es «{mejor}» ({VARIANTES.get(mejor)}). "
                  + ("Coincide con la definición por omisión." if mejor == "confirmados" else
                     "El tablero usa una definición/ámbito distinto al de la serie por omisión."))
        if mejor else "No evaluable.",
    })

    # D5 reclasificación retroactiva
    dif_lejos = d_c.loc[lejos, "diferencia"]
    por_anio = dif_lejos.groupby(dif_lejos.index.year).agg(["sum", lambda x: x.abs().sum()])
    por_anio.columns = ["neta", "absoluta"]
    tot_tab_lejos = d_c.loc[lejos, "tablero"].sum()
    hallazgos.append({
        "id": "D5", "tema": "Reclasificación retroactiva (lejos del corte)",
        "magnitud": f"diferencia neta {fmt(dif_lejos.sum())} "
                    f"({fmt(100*dif_lejos.sum()/tot_tab_lejos if tot_tab_lejos else np.nan, 2)} % del "
                    f"tablero) en días a ≥ 90 d del corte; por año: "
                    + ", ".join(f"{a}: {fmt(r.neta)}" for a, r in por_anio.iterrows()),
        "causa": "Fuera de la ventana de rezago, las diferencias provienen de cambios a "
                 "registros ya existentes entre la versión usada por el tablero y la del "
                 "microdato: resultados pendientes que se resuelven, dictaminaciones tardías, "
                 "depuración de duplicados y correcciones de fecha de síntomas o de entidad. "
                 "Una diferencia ≈ 0 indica que ambas fuentes provienen de versiones "
                 "equivalentes.",
    })

    # D6 consistencia interna
    dif_int = (tab - suma_estados).abs().sum()
    hallazgos.append({
        "id": "D6", "tema": "Consistencia interna del tablero",
        "magnitud": f"Σ|Nacional − Σ entidades| = {fmt(dif_int)}",
        "causa": "Cero: la fila Nacional es la suma de las 32 entidades por residencia." if dif_int == 0
        else "La fila Nacional no es la suma de entidades (posibles registros sin entidad o "
             "extranjeros incluidos solo en Nacional).",
    })

    # D7 reproducción PT1
    r = tab.loc[PT1["inicio"]:PT1["fin"]]
    suav = tab.rolling(7, center=True, min_periods=1).mean()
    pico, fpico = suav.max(), suav.idxmax()
    reproduce = int(r.sum()) == PT1["total"]
    hallazgos.append({
        "id": "D7", "tema": "Reproducción de cifras del PT1",
        "magnitud": f"total {PT1['inicio']}…{PT1['fin']}: {fmt(r.sum())} (PT1: {fmt(PT1['total'])}); "
                    f"pico suavizado {fmt(pico)} el {fpico.date()} (PT1: {fmt(PT1['pico_suavizado'])} "
                    f"el {PT1['fecha_pico']})",
        "causa": "El CSV registrado es el mismo que usó el PT1." if reproduce else
                 "El CSV registrado NO reproduce el total del PT1: no es el mismo archivo o "
                 "no cubre el periodo; la comparación no aplica al PT1.",
    })

    tot = {"dge": float(d_c["serie_dge"].sum()), "tablero": float(d_c["tablero"].sum())}
    resumen = {
        "corte_dge": str(corte_dge.date()), "corte_tablero": str(corte_tab.date()),
        "rango_comun": [str(comun.min().date()), str(comun.max().date())],
        "total_comun": tot, "dias_distintos": int((d_c["diferencia"] != 0).sum()),
        "dias_comunes": len(comun), "hallazgos": hallazgos,
        "fuente_tablero": proc, "entradas_dge": man.get("entradas", []),
        "por_anio": por_anio, "ventanas": filas_v, "desfase_l1": l1,
    }
    return d, resumen


def figura(d: pd.DataFrame, ruta: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    m7 = d[["serie_dge", "tablero"]].rolling(7, center=True, min_periods=1).mean()
    ax[0].plot(m7.index, m7["serie_dge"], label="Microdato DGE (propia)", lw=1.4)
    ax[0].plot(m7.index, m7["tablero"], label="Tablero CONAHCYT", lw=1.0, ls="--")
    ax[0].set_ylabel("Casos/día (media 7 d)")
    ax[0].legend(frameon=False)
    ax[1].bar(d.index, d["diferencia"], width=1.0, color="#7a5195")
    ax[1].axhline(0, color="k", lw=0.5)
    ax[1].set_ylabel("DGE − tablero")
    fig.text(0.01, 0.005, "Fuentes: DGE, Datos Abiertos COVID-19 (microdato); "
             "CONAHCYT, COVID-19 Tablero México (derivado de DGE).", fontsize=7)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ruta, dpi=150, metadata={"Software": None})
    plt.close(fig)


def escribir_nota(res: dict, ruta: Path, tablero_csv: Path) -> None:
    t = res["total_comun"]
    ft = res["fuente_tablero"]
    lineas = [
        "# Nota de diferencias: serie propia (microdato DGE) vs. tablero CONAHCYT",
        "",
        "> Archivo generado por `python -m src.comparar_tablero` (no editar a mano; "
        "las interpretaciones adicionales van en `docs/diccionario_datos.md`).",
        "",
        "## Fuentes (dos niveles)",
        "",
        f"1. **Primaria — DGE.** {CITA_DGE}",
    ]
    for e in res["entradas_dge"]:
        lineas.append(f"   - `{e.get('archivo')}` · actualización {e.get('fecha_actualizacion')} · "
                      f"descarga {e.get('fecha_descarga') or '—'} · sha256 `{e.get('sha256', '')[:16]}…` · "
                      f"{e.get('url') or 'URL no registrada'}")
    lineas += [
        f"2. **Secundaria — tablero.** {CITA_TABLERO}",
        f"   - `{ft.get('archivo')}` · descarga {ft.get('fecha_descarga') or '—'} · "
        f"sha256 `{ft.get('sha256', '')[:16]}…` · {ft.get('url') or 'URL no registrada'}",
        "",
        "## Resumen",
        "",
        f"- Corte del microdato DGE: **{res['corte_dge']}**; corte del tablero: **{res['corte_tablero']}**.",
        f"- Rango común: {res['rango_comun'][0]} a {res['rango_comun'][1]} "
        f"({res['dias_comunes']} días; {res['dias_distintos']} con diferencia ≠ 0).",
        f"- Total en el rango común: DGE {fmt(t['dge'])} vs. tablero {fmt(t['tablero'])} "
        f"(diferencia {fmt(t['dge'] - t['tablero'])}, "
        f"{fmt(100 * (t['dge'] - t['tablero']) / t['tablero'] if t['tablero'] else np.nan, 2)} %).",
        "",
        "![Comparación](figuras/comparacion_tablero.png)",
        "",
        "## Diferencias y su causa",
        "",
        "| ID | Tema | Magnitud | Causa diagnosticada |",
        "|---|---|---|---|",
    ]
    for h in res["hallazgos"]:
        lineas.append(f"| {h['id']} | {h['tema']} | {h['magnitud']} | {h['causa']} |")
    lineas += [
        "",
        "## Detalle",
        "",
        "### Diferencia lejos del corte (≥ 90 d), por año de inicio de síntomas",
        "",
        "| Año | Neta (DGE − tablero) | Absoluta |",
        "|---|---|---|",
        *[f"| {a} | {fmt(r.neta)} | {fmt(r.absoluta)} |" for a, r in res["por_anio"].iterrows()],
        "",
        "### Discrepancia L1 según desfase de fecha (días a ≥ 90 d del corte)",
        "",
        "| Desfase (d) | L1 |",
        "|---|---|",
        *[f"| {k:+d} | {fmt(v)} |" for k, v in res["desfase_l1"].items()],
        "",
        "## Método",
        "",
        "- Serie propia: `CLASIFICACION_FINAL ∈ {1,2,3}`, `ENTIDAD_RES ∈ 1..32`, por "
        "`FECHA_SINTOMAS` (ver `docs/diccionario_datos.md`). Variantes alternativas en "
        "`data/processed/serie_nacional_sintomas.csv`.",
        f"- Tablero: fila «Nacional» de `{ruta_relativa(tablero_csv)}`; encabezados `DD-MM-AAAA`.",
        "- Diferencia diaria = DGE − tablero; detalle por día en "
        "`data/processed/comparacion_tablero.csv`.",
        "- D3/D4/D5 se evalúan solo en días a ≥ 90 d del corte del tablero para aislar el "
        "rezago de notificación (D2).",
        "",
    ]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(lineas), encoding="utf-8")


def tablero_por_omision() -> Path:
    c = sorted(DIR_TABLERO.glob("Casos_Diarios_Estado_Nacional_Confirmados_*.csv")) \
        if DIR_TABLERO.exists() else []
    if not c:
        raise SystemExit(
            "No encontré data/raw/tablero/Casos_Diarios_Estado_Nacional_Confirmados_*.csv. "
            "Copia ahí el CSV usado en el PT1 y regístralo con scripts/registrar_fuente.py "
            "--nivel tablero.")
    return c[-1]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compara la serie DGE contra el tablero CONAHCYT.")
    p.add_argument("--tablero", type=Path)
    p.add_argument("--serie", type=Path, default=SERIE)
    p.add_argument("--manifiesto", type=Path, default=None)
    p.add_argument("--salida-csv", type=Path, default=SALIDA_CSV)
    p.add_argument("--nota", type=Path, default=NOTA)
    p.add_argument("--figura", type=Path, default=FIGURA)
    p.add_argument("--permitir-no-registrados", action="store_true")
    a = p.parse_args(argv)
    tablero_csv = a.tablero or tablero_por_omision()
    if not a.serie.exists():
        raise SystemExit(f"No existe {a.serie}; corre antes `python -m src.datos`.")
    manifiesto = a.manifiesto or a.serie.parent / "manifiesto.json"
    d, res = comparar(tablero_csv, a.serie, manifiesto, not a.permitir_no_registrados)
    a.salida_csv.parent.mkdir(parents=True, exist_ok=True)
    d.reset_index().to_csv(a.salida_csv, index=False, lineterminator="\n", float_format="%.0f")
    figura(d, a.figura)
    escribir_nota(res, a.nota, tablero_csv)
    print(f"Nota escrita en {ruta_relativa(a.nota)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
