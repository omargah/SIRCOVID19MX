"""Análisis exploratorio de la serie DGE: artefactos de medición.

Fuente primaria: DGE, microdato COVID-19 (vía los agregados que produce
``python -m src.datos`` en ``data/processed/``).

Uso::

    python -m src.eda                          # una sola versión del microdato
    python -m src.eda --historicos data/processed/historicos

Con ``--historicos`` se usan las series construidas a partir de versiones
semanales anteriores (cada subdirectorio = salida de ``src.datos`` para una
versión) para medir el rezago de notificación real (triángulo de reporte).

Salidas: ``docs/eda.md``, ``docs/figuras/eda_*.png``, ``data/processed/eda/*.csv``.

Temas:
  1. efecto del día de la semana;
  2. retrasos (inicio de síntomas → ingreso/registro; → defunción);
  3. truncamiento al final de la serie;
  4. cambios en el volumen de pruebas, positividad y mezcla de clasificaciones.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.fuentes import CITA_DGE, RAIZ, ruta_relativa

PROC = RAIZ / "data" / "processed"
DOC = RAIZ / "docs" / "eda.md"
FIG = RAIZ / "docs" / "figuras"
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _guardar(fig, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.text(0.01, 0.005, "Fuente: DGE, Datos Abiertos COVID-19 (microdato). Elaboración propia.",
             fontsize=7)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ruta, dpi=150, metadata={"Software": None})
    _plt().close(fig)


def tabla_md(df: pd.DataFrame, dec: int = 2) -> str:
    def f(x):
        if isinstance(x, (float, np.floating)):
            return "—" if not np.isfinite(x) else f"{x:,.{dec}f}"
        if isinstance(x, (int, np.integer)):
            return f"{x:,}"
        return str(x)
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f(v) for v in fila) + " |" for fila in df.itertuples(index=False)]
    return "\n".join(out)


# --------------------------------------------------------------------------
# 1. Día de la semana
# --------------------------------------------------------------------------

def efecto_dia_semana(y: pd.Series, corte: pd.Timestamp, excluir: int = 28,
                      minimo: float = 5.0) -> pd.DataFrame:
    """Cociente y(t) / media móvil centrada de 7 días, promediado por día y año."""
    y = y[y.index <= corte - pd.Timedelta(days=excluir)].astype(float)
    m7 = y.rolling(7, center=True).mean()
    r = (y / m7)[m7 >= minimo]
    df = pd.DataFrame({"r": r, "dia": r.index.weekday, "anio": r.index.year})
    t = df.groupby(["anio", "dia"])["r"].mean().unstack("dia").reindex(columns=range(7))
    t.columns = DIAS
    t.index = t.index.astype(str)
    t.loc["Todo"] = df.groupby("dia")["r"].mean().reindex(range(7)).to_numpy()
    t["max/min"] = t[DIAS].max(axis=1) / t[DIAS].min(axis=1)
    return t.reset_index().rename(columns={"anio": "Año"})


# --------------------------------------------------------------------------
# 2. Retrasos
# --------------------------------------------------------------------------

def cuantil_hist(retraso: np.ndarray, n: np.ndarray, q: float) -> float:
    o = np.argsort(retraso, kind="mergesort")
    r, c = retraso[o], np.cumsum(n[o])
    if c[-1] == 0:
        return np.nan
    return float(r[np.searchsorted(c, q * c[-1])])


def resumen_retrasos(cubo: pd.DataFrame, freq: str = "QS") -> pd.DataFrame:
    if cubo.empty:
        return pd.DataFrame()
    c = cubo.copy()
    c["periodo"] = pd.to_datetime(c["semana_sintomas"]).dt.to_period(freq[0]).dt.start_time
    filas = []
    for (per,), g in c.groupby(["periodo"], sort=True):
        r, n = g["retraso"].to_numpy(), g["n"].to_numpy()
        filas.append({"Periodo": str(per.date()), "n": int(n.sum()),
                      "Mediana": cuantil_hist(r, n, 0.5), "P90": cuantil_hist(r, n, 0.9),
                      "P95": cuantil_hist(r, n, 0.95),
                      "% ≥ 14 d": 100 * n[r >= 14].sum() / n.sum(),
                      "% negativo": 100 * n[r < 0].sum() / n.sum()})
    return pd.DataFrame(filas)


def distribucion_acumulada(cubo: pd.DataFrame) -> pd.Series:
    h = cubo.groupby("retraso")["n"].sum().sort_index()
    return (h.cumsum() / h.sum()).rename("F")


# --------------------------------------------------------------------------
# 3. Truncamiento
# --------------------------------------------------------------------------

def completitud_historicos(dir_hist: Path, ref: pd.DataFrame, corte_ref: pd.Timestamp,
                           max_d: int = 60, col: str = "confirmados") -> pd.DataFrame:
    """Triángulo de reporte: conteo en la versión s / conteo en la versión de referencia."""
    filas = []
    ref_c = ref.set_index("fecha")[col]
    for sub in sorted(p for p in dir_hist.iterdir() if (p / "serie_nacional_sintomas.csv").exists()):
        m = json.loads((sub / "manifiesto.json").read_text(encoding="utf-8"))
        corte = pd.Timestamp(m["fecha_corte_microdato"])
        if corte > corte_ref - pd.Timedelta(days=max_d + 30):
            continue  # la referencia aún no está completa para esta versión
        s = pd.read_csv(sub / "serie_nacional_sintomas.csv", parse_dates=["fecha"]).set_index("fecha")
        for d in range(0, max_d + 1):
            # se agrupa por semana de retraso para reducir ruido diario
            t = corte - pd.Timedelta(days=d)
            if t in s.index and t in ref_c.index and ref_c[t] > 0:
                filas.append({"version": str(corte.date()), "d": d,
                              "cociente": s.at[t, col] / ref_c[t]})
    if not filas:
        return pd.DataFrame()
    df = pd.DataFrame(filas)
    return (df.groupby("d")["cociente"]
              .agg(versiones="count", mediana="median",
                   p10=lambda x: x.quantile(0.1), p90=lambda x: x.quantile(0.9))
              .reset_index())


# --------------------------------------------------------------------------
# 4. Pruebas
# --------------------------------------------------------------------------

def pruebas_semanales(ci: pd.DataFrame) -> pd.DataFrame:
    c = ci[ci["res_valida"] == 1].copy()
    c["semana"] = c["fecha"] - pd.to_timedelta(c["fecha"].dt.weekday, unit="D")
    lab = c["muestra_lab"] == 1
    ag = c["muestra_ag"] == 1
    conf = c["clasif"].isin([1, 2, 3])
    g = lambda m: c[m].groupby("semana")["n"].sum()  # noqa: E731
    w = pd.DataFrame({
        "registros": g(slice(None)),
        "muestra_lab": g(lab), "muestra_antigeno": g(ag), "con_muestra": g(lab | ag),
        "confirmados": g(conf), "conf_lab_antigeno": g(c["clasif"] == 3),
        "conf_asoc_clin_epi": g(c["clasif"] == 1), "conf_dictaminacion": g(c["clasif"] == 2),
        "usmer": g(c["origen"] == 1),
    }).fillna(0).astype("int64")
    w["positividad"] = w["conf_lab_antigeno"] / w["con_muestra"].replace(0, np.nan)
    w["frac_asoc_clin_epi"] = w["conf_asoc_clin_epi"] / w["confirmados"].replace(0, np.nan)
    w["frac_usmer"] = w["usmer"] / w["registros"].replace(0, np.nan)
    w["frac_antigeno"] = w["muestra_antigeno"] / w["con_muestra"].replace(0, np.nan)
    return w.reset_index()


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------

def cargar(proc: Path):
    rd = lambda n: pd.read_csv(proc / n, parse_dates=["fecha"])  # noqa: E731
    s, h = rd("serie_nacional_sintomas.csv"), rd("serie_nacional_hosp_def.csv")
    cubos = {n: pd.read_csv(proc / "cubos" / f"{n}.csv") for n in
             ("por_ingreso", "retraso_ingreso", "retraso_defuncion")}
    cubos["por_ingreso"]["fecha"] = pd.to_datetime(cubos["por_ingreso"]["fecha"])
    man = json.loads((proc / "manifiesto.json").read_text(encoding="utf-8"))
    return s, h, cubos, man


def correr(proc: Path, doc: Path, fig: Path, dir_hist: Path | None) -> None:
    plt = _plt()
    s, h, cubos, man = cargar(proc)
    corte = pd.Timestamp(man["fecha_corte_microdato"])
    out = proc / "eda"
    out.mkdir(parents=True, exist_ok=True)
    S, H = s.set_index("fecha"), h.set_index("fecha")
    ci = cubos["por_ingreso"]
    reg_ingreso = (ci[ci["res_valida"] == 1].groupby("fecha")["n"].sum()
                   .reindex(S.index, fill_value=0))

    # 1 --------------------------------------------------------------------
    dsem = {
        "Confirmados por inicio de síntomas": efecto_dia_semana(S["confirmados"], corte),
        "Registros por fecha de ingreso": efecto_dia_semana(reg_ingreso, corte),
        "Hospitalizaciones confirmadas por ingreso": efecto_dia_semana(H["hospitalizados_confirmados"], corte),
        "Defunciones confirmadas por fecha de defunción": efecto_dia_semana(H["defunciones_confirmadas"], corte),
    }
    for i, (k, t) in enumerate(dsem.items()):
        t.to_csv(out / f"dia_semana_{i+1}.csv", index=False, lineterminator="\n")
    f, ax = plt.subplots(figsize=(8, 4))
    for k, t in dsem.items():
        fila = t[t["Año"] == "Todo"]
        if len(fila):
            ax.plot(DIAS, fila[DIAS].iloc[0].to_numpy(), marker="o", label=k)
    ax.axhline(1, color="k", lw=0.5)
    ax.set_ylabel("y(t) / media móvil 7 d")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Efecto del día de la semana")
    _guardar(f, fig / "eda_dia_semana.png")

    # 2 --------------------------------------------------------------------
    rti = resumen_retrasos(cubos["retraso_ingreso"])
    rtd = resumen_retrasos(cubos["retraso_defuncion"])
    rti.to_csv(out / "retraso_sintomas_ingreso.csv", index=False, lineterminator="\n")
    rtd.to_csv(out / "retraso_sintomas_defuncion.csv", index=False, lineterminator="\n")
    F = distribucion_acumulada(cubos["retraso_ingreso"]) if len(cubos["retraso_ingreso"]) else pd.Series(dtype=float)
    d95 = int(F[F >= 0.95].index.min()) if len(F) and (F >= 0.95).any() else None
    d99 = int(F[F >= 0.99].index.min()) if len(F) and (F >= 0.99).any() else None
    por_tipo = []
    for tp, nombre in ((1, "Ambulatorio"), (2, "Hospitalizado")):
        g = cubos["retraso_ingreso"]
        g = g[g["tipo_paciente"] == tp]
        if len(g):
            r, n = g["retraso"].to_numpy(), g["n"].to_numpy()
            por_tipo.append({"Tipo": nombre, "n": int(n.sum()), "Mediana": cuantil_hist(r, n, .5),
                             "P90": cuantil_hist(r, n, .9), "P95": cuantil_hist(r, n, .95)})
    por_tipo = pd.DataFrame(por_tipo)
    f, ax = plt.subplots(figsize=(8, 4))
    if len(rti):
        x = pd.to_datetime(rti["Periodo"])
        ax.plot(x, rti["Mediana"], marker="o", label="Mediana síntomas→ingreso")
        ax.plot(x, rti["P90"], marker="o", label="P90 síntomas→ingreso")
    if len(rtd):
        x = pd.to_datetime(rtd["Periodo"])
        ax.plot(x, rtd["Mediana"], marker="s", ls="--", label="Mediana síntomas→defunción")
    ax.set_ylabel("días")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Retrasos por trimestre de inicio de síntomas (confirmados)")
    _guardar(f, fig / "eda_retrasos.png")

    # 3 --------------------------------------------------------------------
    cola = S[S["dias_antes_corte"] < 42][["confirmados", "dias_antes_corte"]].copy()
    ref = S[(S["dias_antes_corte"] >= 42) & (S["dias_antes_corte"] < 56)]["confirmados"].mean()
    cola["cociente_vs_ref"] = cola["confirmados"] / ref if ref else np.nan
    if len(F):
        cola["F_ingreso"] = [float(F[F.index <= d].iloc[-1]) if (F.index <= d).any() else 0.0
                             for d in cola["dias_antes_corte"]]
    cola.reset_index().to_csv(out / "cola_final.csv", index=False, lineterminator="\n")
    comp = pd.DataFrame()
    if dir_hist and dir_hist.exists():
        comp = completitud_historicos(dir_hist, s, corte)
        if len(comp):
            comp.to_csv(out / "completitud_historicos.csv", index=False, lineterminator="\n")
    d_comp = (int(comp.loc[comp["mediana"] >= 0.95, "d"].min())
              if len(comp) and (comp["mediana"] >= 0.95).any() else None)
    f, ax = plt.subplots(1, 2, figsize=(10, 4))
    ult = S[S["dias_antes_corte"] < 120]
    ax[0].bar(ult.index, ult["confirmados"], width=1, color="#c7c7c7")
    ax[0].plot(ult.index, ult["confirmados"].rolling(7, center=True, min_periods=1).mean(), color="#0d3b66")
    ax[0].set_title("Últimos 120 días antes del corte")
    ax[0].tick_params(axis="x", rotation=45)
    if len(F):
        ax[1].step(F.index, F.to_numpy(), where="post", label="F síntomas→ingreso (una versión)")
    if len(comp):
        ax[1].plot(comp["d"], comp["mediana"], marker=".", label="Completitud (versiones históricas)")
        ax[1].fill_between(comp["d"], comp["p10"], comp["p90"], alpha=0.2)
    ax[1].axhline(0.95, color="k", lw=0.5, ls=":")
    ax[1].set_xlim(0, 60)
    ax[1].set_xlabel("días antes del corte")
    ax[1].set_title("Completitud")
    ax[1].legend(frameon=False, fontsize=8)
    _guardar(f, fig / "eda_truncamiento.png")

    # 4 --------------------------------------------------------------------
    w = pruebas_semanales(ci)
    w.to_csv(out / "pruebas_semanales.csv", index=False, lineterminator="\n")
    f, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    ax[0].plot(w["semana"], w["registros"], label="Registros")
    ax[0].plot(w["semana"], w["con_muestra"], label="Con muestra (lab o antígeno)")
    ax[0].plot(w["semana"], w["muestra_antigeno"], label="Con muestra de antígeno")
    ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_ylabel("por semana de ingreso")
    ax[1].plot(w["semana"], 100 * w["positividad"], color="#d62828")
    ax[1].set_ylabel("Positividad %")
    ax[2].plot(w["semana"], 100 * w["frac_asoc_clin_epi"], label="% confirmados por asoc. clín.-epi.")
    ax[2].plot(w["semana"], 100 * w["frac_usmer"], label="% registros USMER")
    ax[2].legend(frameon=False, fontsize=8)
    ax[2].set_ylabel("%")
    _guardar(f, fig / "eda_pruebas.png")
    con_ag = w[w["muestra_antigeno"] > 0]
    primera_ag = str(con_ag["semana"].min().date()) if len(con_ag) else "—"
    wv = w[w["registros"] >= 100].copy()
    wv["cambio_log"] = np.log(wv["registros"]).diff()
    saltos = wv.reindex(wv["cambio_log"].abs().sort_values(ascending=False).index).head(8)
    saltos = saltos.sort_values("semana")[["semana", "registros", "cambio_log", "positividad"]]
    saltos["semana"] = saltos["semana"].dt.strftime("%Y-%m-%d")
    wp = w[w["con_muestra"] >= 100]
    pos_max = wp.loc[wp["positividad"].idxmax()] if wp["positividad"].notna().any() else None

    # Documento -------------------------------------------------------------
    rel = lambda p: Path(ruta_relativa(p)).relative_to("docs").as_posix() \
        if ruta_relativa(p).startswith("docs/") else ruta_relativa(p)  # noqa: E731
    L = [
        "# EDA: artefactos de medición en la serie DGE",
        "",
        "> Generado por `python -m src.eda`. No editar a mano.",
        "",
        f"**Fuente primaria:** {CITA_DGE}",
        f"Versión del microdato: corte **{man['fecha_corte_microdato']}** "
        f"(entradas: {', '.join('`' + e['archivo'] + '`' for e in man['entradas'])}).",
        "Este análisis no usa el tablero CONAHCYT (fuente secundaria); ver "
        "`docs/nota_diferencias.md`.",
        "",
        "## 1. Efecto del día de la semana",
        "",
        "Cociente entre el conteo diario y su media móvil centrada de 7 días, promediado por "
        "día de la semana (se excluyen los últimos 28 días antes del corte y días con media < 5). "
        "Un valor de 1 = sin efecto. La fecha de inicio de síntomas la reporta el paciente, "
        "por lo que su efecto debería ser menor que el de la fecha de ingreso, que refleja la "
        "operación de las unidades (fines de semana).",
        "",
        f"![día de la semana]({rel(fig / 'eda_dia_semana.png')})",
        "",
    ]
    for k, t in dsem.items():
        L += [f"**{k}**", "", tabla_md(t, 3), ""]
    L += [
        "## 2. Retrasos",
        "",
        "Retraso = `FECHA_INGRESO − FECHA_SINTOMAS` (días) en confirmados residentes, por trimestre "
        f"de inicio de síntomas; los valores > {60} se agrupan en 60 y los negativos en −1. "
        "`FECHA_INGRESO` es la fecha de ingreso a la unidad/registro, no la fecha de aparición en "
        "la base; el rezago adicional de notificación (registro → publicación) solo es medible "
        "con versiones históricas (sección 3).",
        "",
        f"![retrasos]({rel(fig / 'eda_retrasos.png')})",
        "",
        "**Síntomas → ingreso**", "", tabla_md(rti, 1) if len(rti) else "(sin datos)", "",
        "**Por tipo de paciente**", "", tabla_md(por_tipo, 1) if len(por_tipo) else "(sin datos)", "",
        "**Síntomas → defunción**", "", tabla_md(rtd, 1) if len(rtd) else "(sin datos)", "",
        "## 3. Truncamiento al final",
        "",
        f"- Con una sola versión, el 95 % de los confirmados ingresa a ≤ **{d95}** días del inicio "
        f"de síntomas (99 %: ≤ {d99} d). Es una **cota inferior** del truncamiento: los últimos "
        f"{d95} días antes del corte están incompletos aun antes de sumar el rezago de "
        "notificación.",
    ]
    if len(comp):
        L += [f"- Con {int(comp['versiones'].max())} versiones históricas, la mediana de completitud "
              f"alcanza 95 % a **{d_comp}** días antes del corte (tabla en "
              "`data/processed/eda/completitud_historicos.csv`).",
              "", tabla_md(comp[comp["d"] % 7 == 0], 3)]
    else:
        L += ["- Sin versiones históricas procesadas: el rezago de notificación real no se "
              "estimó. Ver `docs/inventario_historicos.md` y "
              "`python -m src.eda --historicos data/processed/historicos`."]
    L += ["", f"![truncamiento]({rel(fig / 'eda_truncamiento.png')})", "",
          "## 4. Volumen de pruebas, positividad y mezcla de clasificaciones",
          "",
          "Por semana de `FECHA_INGRESO`, residentes 1–32. Positividad = confirmados por "
          "laboratorio/antígeno (`CLASIFICACION_FINAL=3`) / registros con muestra "
          "(`TOMA_MUESTRA_LAB=1` o `TOMA_MUESTRA_ANTIGENO=1`). En versiones del esquema 2020 "
          "(sin `TOMA_MUESTRA_*`) la positividad no es calculable.",
          "",
          f"- Primera semana con muestras de antígeno: **{primera_ag}**.",
          (f"- Positividad máxima (semanas con ≥ 100 muestras): "
           f"**{100*pos_max['positividad']:.1f} %** en la semana del "
           f"{pos_max['semana'].date()}." if pos_max is not None else "- Positividad: no calculable."),
          "- Semanas con los mayores cambios relativos de volumen de registros (|Δ log|):",
          "", tabla_md(saltos, 3), "",
          f"![pruebas]({rel(fig / 'eda_pruebas.png')})", "",
          "## Implicaciones para el ajuste del SIR (a discutir, no decididas)",
          "",
          "- Usar la serie por inicio de síntomas (efecto de día de la semana pequeño) o "
          "suavizar con media de 7 días si se usa fecha de ingreso.",
          f"- Descartar al menos los últimos {d_comp or d95} días antes del corte o corregirlos "
          "(nowcasting).",
          "- La positividad y la fracción por asociación clínico-epidemiológica cambian en el "
          "tiempo: la razón casos confirmados / infecciones no es constante (subregistro "
          "variable), lo cual afecta la identificabilidad de S₀ y ρ.",
          ""]
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(L), encoding="utf-8")
    print(f"EDA escrita en {ruta_relativa(doc)}", file=sys.stderr)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="EDA de artefactos de medición (DGE).")
    p.add_argument("--procesados", type=Path, default=PROC)
    p.add_argument("--doc", type=Path, default=DOC)
    p.add_argument("--figuras", type=Path, default=FIG)
    p.add_argument("--historicos", type=Path, default=None,
                   help="directorio con salidas de src.datos por versión histórica")
    a = p.parse_args(argv)
    if not (a.procesados / "manifiesto.json").exists():
        raise SystemExit(f"No existe {a.procesados}/manifiesto.json; corre antes `python -m src.datos`.")
    correr(a.procesados, a.doc, a.figuras, a.historicos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
