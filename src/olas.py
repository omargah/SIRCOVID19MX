#!/usr/bin/env python3
"""Delimitación de olas de COVID-19 en México con la regla declarada en
docs/regla_olas.md (R1–R7, §4) y su enmienda A1 (§7).

Uso:
    python3 src/olas.py              # usa los CSV versionados en data/
    python3 src/olas.py --descargar  # vuelve a descargar las fuentes

Salidas en resultados/olas/{declarada,A1}/.
Dependencias: numpy, pandas, matplotlib (solo para la figura).
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
SALIDA = RAIZ / "resultados" / "olas"

URL_JHU = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
           "csse_covid_19_data/csse_covid_19_time_series/"
           "time_series_covid19_confirmed_global.csv")
URL_DGE = ("https://raw.githubusercontent.com/mexicovid19/Mexico-datos/master/"
           "datos_abiertos/series_de_tiempo/nuevos/covid19_mex_confirmados.csv")
ARCH_JHU = DATOS / "jhu_mexico_confirmados_acumulados.csv"
ARCH_DGE = DATOS / "dge_mexico_confirmados_por_ingreso.csv"

# --- Parámetros declarados (docs/regla_olas.md) -----------------------------
INICIO = pd.Timestamp("2020-02-27")       # §2
FIN = pd.Timestamp("2023-02-28")          # §2
CORTE_DGE = pd.Timestamp("2022-01-19")    # §4
DESCARTE_DGE = 14                         # §4
FECHA_LOTE = pd.Timestamp("2020-10-05")   # §7 A1.a

SENS_RHO = [1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
SENS_SUAV = ["media", "mediana"]
REJILLA_W = [7, 14, 21, 28, 35, 42]
EMPAREJAR_MAX_DIAS = 60
ROBUSTA_DIAS = 14


@dataclass(frozen=True)
class Config:
    nombre: str
    rho: float
    w: int
    metodo: str
    corregir_lote: bool
    sens_w: list = field(default_factory=list)


DECLARADA = Config("declarada", 2.0, 7, "media", False, [7, 14, 21])   # §3–§4
A1 = Config("A1", 2.0, 28, "media", True, [21, 28, 35])                 # §7

# §7: periodos de dominancia (aproximados, por verificar con CoViGen-Mex/InDRE)
PERIODOS = [
    ("2020-02-27", "2020-11-30", 1, "Ancestrales (B.1, B.1.1, B.1.1.222; D614G)",
     "Taboada et al. 2021"),
    ("2020-12-01", "2021-05-31", 2, "B.1.1.519 (Alpha y Gamma no dominaron)",
     "Zárate et al. 2022 (doi:10.1128/spectrum.02240-21); Taboada et al. 2021"),
    ("2021-06-01", "2021-12-14", 3, "Delta (B.1.617.2, AY.*)",
     "Taboada et al. 2022 (por verificar); CoViGen-Mex"),
    ("2021-12-15", "2022-04-30", 4, "Ómicron BA.1/BA.1.1",
     "CoViGen-Mex / InDRE (por verificar)"),
    ("2022-05-01", "2022-10-31", 5, "Ómicron BA.4/BA.5",
     "CoViGen-Mex / InDRE (por verificar)"),
    ("2022-11-01", "2023-02-28", 5, "Ómicron BQ.1, XBB.1.5",
     "CoViGen-Mex / InDRE (por verificar)"),
]
SUPUESTOS = {
    4: "vacunación; escape inmune; pruebas caseras",
    5: "vacunación (con refuerzos); escape inmune; pruebas caseras",
}


# --- Datos ------------------------------------------------------------------
def descargar() -> None:
    DATOS.mkdir(exist_ok=True)
    d = pd.read_csv(URL_JHU)
    m = d[(d["Country/Region"] == "Mexico") & d["Province/State"].isna()].iloc[0, 4:]
    pd.DataFrame({
        "fecha": pd.to_datetime(m.index, format="%m/%d/%y").strftime("%Y-%m-%d"),
        "confirmados_acumulados": m.astype(int).values,
    }).to_csv(ARCH_JHU, index=False)
    g = pd.read_csv(URL_DGE)[["Fecha", "Nacional"]]
    g.columns = ["fecha", "confirmados_nuevos"]
    g.to_csv(ARCH_DGE, index=False)


def serie_jhu(corregir_lote: bool = False) -> pd.Series:
    """R1 (+ A1.a): incidencia diaria por fecha de reporte, negativos a cero."""
    d = pd.read_csv(ARCH_JHU, parse_dates=["fecha"]).set_index("fecha")
    y = d["confirmados_acumulados"].diff().clip(lower=0).astype(float)
    if corregir_lote:
        vecinos = y.loc[FECHA_LOTE - pd.Timedelta(days=3):FECHA_LOTE + pd.Timedelta(days=3)]
        y.loc[FECHA_LOTE] = float(vecinos.median())
    return y.loc[INICIO:FIN]


def serie_dge() -> pd.Series:
    d = pd.read_csv(ARCH_DGE, parse_dates=["fecha"]).set_index("fecha")
    y = d["confirmados_nuevos"].clip(lower=0).astype(float).iloc[:-DESCARTE_DGE]
    return y.loc[INICIO:FIN].asfreq("D", fill_value=0.0)


def racha_max_ceros(y: pd.Series) -> pd.Series:
    """Diagnóstico de §7: racha más larga de días con cero reporte, por trimestre."""
    z = (y == 0).astype(int)
    grupo = (z != z.shift()).cumsum()
    rachas = z.groupby(grupo).agg(["first", "size"])
    inicios = z.groupby(grupo).apply(lambda s: s.index[0])
    r = pd.Series(rachas["size"].where(rachas["first"] == 1, 0).values, index=inicios.values)
    return r.groupby(pd.Grouper(freq="QS")).max()


# --- Regla ------------------------------------------------------------------
def suavizar(y: pd.Series, w: int, metodo: str) -> pd.Series:
    """R2: ventana centrada; en los bordes se usa la ventana parcial."""
    r = y.rolling(w, center=True, min_periods=1)
    return r.mean() if metodo == "media" else r.median()


def maximos_locales(z: np.ndarray) -> list[int]:
    """R4: máximos locales; una meseta cuenta una vez, en su punto medio."""
    n, i, picos = len(z), 1, []
    while i < n - 1:
        if z[i] > z[i - 1]:
            j = i
            while j + 1 < n and z[j + 1] == z[i]:
                j += 1
            if j + 1 < n and z[j + 1] < z[i]:
                picos.append((i + j) // 2)
            i = j + 1
        else:
            i += 1
    return picos


def prominencia(z: np.ndarray, i: int, con_bases: bool = False):
    """R5: prominencia topográfica de z[i] (y, opcionalmente, sus valles base)."""
    h = z[i]
    k = i
    while k > 0 and z[k - 1] <= h:
        k -= 1
    bi = k + int(np.argmin(z[k:i + 1]))
    k = i
    while k < len(z) - 1 and z[k + 1] <= h:
        k += 1
    bd = i + int(np.argmin(z[i:k + 1]))
    p = h - max(z[bi], z[bd])
    return (p, bi, bd) if con_bases else p


@dataclass
class Resultado:
    ybar: pd.Series
    picos: list
    fronteras: list   # valles interiores v_1..v_{K-1}


def delimitar(y: pd.Series, rho: float, w: int, metodo: str = "media") -> Resultado:
    ybar = suavizar(y, w, metodo)                                   # R2
    z = np.log1p(ybar.to_numpy())                                   # R3
    acept = [i for i in maximos_locales(z) if prominencia(z, i) >= math.log(rho)]
    v = ybar.to_numpy()
    fronteras = [ybar.index[a + 1 + int(np.argmin(v[a + 1:b]))]    # R6
                 for a, b in zip(acept[:-1], acept[1:])]
    return Resultado(ybar, [ybar.index[i] for i in acept], fronteras)


def tabla_olas(y: pd.Series, r: Resultado) -> pd.DataFrame:
    bordes = [y.index[0]] + r.fronteras + [y.index[-1] + pd.Timedelta(days=1)]
    filas = []
    for k, (a, b, p) in enumerate(zip(bordes[:-1], bordes[1:], r.picos), start=1):
        fin = b - pd.Timedelta(days=1)
        filas.append(dict(
            ola=k, inicio=a.date(), pico=p.date(), fin=fin.date(),
            duracion_dias=(b - a).days,
            incidencia_pico=round(float(r.ybar.loc[p])),
            casos_en_ola=int(y.loc[a:fin].sum()),
        ))
    return pd.DataFrame(filas)


def periodo(fecha) -> tuple:
    f = pd.Timestamp(fecha)
    for ini, fin, *resto in PERIODOS:
        if pd.Timestamp(ini) <= f <= pd.Timestamp(fin):
            return (ini, fin, *resto)
    raise ValueError(fecha)


def etiquetar(t: pd.DataFrame) -> pd.DataFrame:
    """§7: etiqueta por el periodo que contiene el pico; lista los abarcados."""
    t = t.copy()
    conv, var, fte, abarca, est, sup = [], [], [], [], [], []
    for _, f in t.iterrows():
        _, _, n, v, s = periodo(f.pico)
        conv.append(n)
        var.append(v)
        fte.append(s)
        a = sorted({p[2] for p in PERIODOS
                    if pd.Timestamp(p[0]) <= pd.Timestamp(f.fin)
                    and pd.Timestamp(p[1]) >= pd.Timestamp(f.inicio)})
        abarca.append(",".join(map(str, a)))
        est.append("primario" if n <= 3 else "secundario (supuestos violados)")
        sup.append(SUPUESTOS.get(n, ""))
    t["ola_convencional"] = conv
    t["periodos_abarcados"] = abarca
    t["variante_dominante_en_pico"] = var
    t["fuente_variante"] = fte
    t["estatus"] = est
    t["supuestos_violados"] = sup
    return t


# --- Sensibilidad -------------------------------------------------------------
def emparejar(base: list, otra: list):
    desp, usadas = [], set()
    for f in base:
        cand = [(abs((g - f).days), j) for j, g in enumerate(otra)
                if j not in usadas and abs((g - f).days) <= EMPAREJAR_MAX_DIAS]
        if cand:
            _, j = min(cand)
            usadas.add(j)
            desp.append((otra[j] - f).days)
        else:
            desp.append(None)
    return desp, [otra[j] for j in range(len(otra)) if j not in usadas]


def variantes_sens(cfg: Config) -> list:
    v = [("rho", r, replace(cfg, rho=r), "JHU") for r in SENS_RHO]
    v += [("w", w, replace(cfg, w=w), "JHU") for w in cfg.sens_w]
    v += [("suavizador", m, replace(cfg, metodo=m), "JHU") for m in SENS_SUAV]
    v += [("fuente", "JHU (reporte)", cfg, "JHU"), ("fuente", "DGE (ingreso)", cfg, "DGE")]
    return v


def sensibilidad(cfg: Config, y_jhu, y_dge, base: Resultado):
    filas, olas_largas = [], []
    for factor, valor, c, fuente in variantes_sens(cfg):
        y = y_jhu if fuente == "JHU" else y_dge
        r = delimitar(y, c.rho, c.w, c.metodo)
        fb, fo, picos = base.fronteras, r.fronteras, r.picos
        if factor == "fuente":
            fb = [f for f in fb if f < CORTE_DGE]
            fo = [f for f in fo if f < CORTE_DGE]
            picos = [p for p in picos if p < CORTE_DGE]
        desp, nuevas = emparejar(fb, fo)
        fila = dict(factor=factor, valor=valor, n_olas=len(picos),
                    fronteras=" | ".join(str(f.date()) for f in fo))
        for k, d in enumerate(desp, start=1):
            fila[f"desp_v{k}"] = "desaparece" if d is None else int(d)
        fila["fronteras_nuevas"] = " | ".join(str(f.date()) for f in nuevas)
        nums = [abs(d) for d in desp if d is not None]
        fila["max_abs_desp_dias"] = max(nums) if nums else 0
        filas.append(fila)
        t = tabla_olas(y, r)
        if factor == "fuente":
            t = t[pd.to_datetime(t.pico) < CORTE_DGE]
        t.insert(0, "valor", valor)
        t.insert(0, "factor", factor)
        olas_largas.append(t)
    return pd.DataFrame(filas), pd.concat(olas_largas, ignore_index=True)


def robustez(sens: pd.DataFrame, base: Resultado) -> pd.DataFrame:
    """§4: robusta si |desp| <= 14 d en w y suavizador, y existe para rho en [1.5, 3]."""
    filas = []
    es_rho = sens.factor == "rho"
    en_rango = sens[es_rho][sens[es_rho].valor.astype(float).between(1.5, 3.0)]
    otros = sens[sens.factor.isin(["w", "suavizador"])]
    for k, f in enumerate(base.fronteras, start=1):
        c = f"desp_v{k}"
        ok_s = all(v != "desaparece" and abs(int(v)) <= ROBUSTA_DIAS for v in otros[c])
        ok_r = all(v != "desaparece" for v in en_rango[c])
        filas.append(dict(frontera=f"v{k}", fecha=f.date(), estable_w_suavizador=ok_s,
                          existe_rho_1p5_a_3=ok_r, robusta=ok_s and ok_r))
    return pd.DataFrame(filas)


def rho_critico(cfg: Config, y, n: int = 8) -> pd.DataFrame:
    """Para cada pico candidato, rho* = exp(prominencia): el pico es ola si y solo
    si rho <= rho*. Resume la sensibilidad completa al parámetro de la regla."""
    ybar = suavizar(y, cfg.w, cfg.metodo)
    z = np.log1p(ybar.to_numpy())
    filas = []
    for i in maximos_locales(z):
        p, bi, bd = prominencia(z, i, con_bases=True)
        filas.append(dict(pico=ybar.index[i].date(), rho_critico=round(math.exp(p), 3),
                          incidencia_pico=round(float(ybar.iloc[i])),
                          valle_izq=ybar.index[bi].date(), valle_der=ybar.index[bd].date(),
                          ola_convencional=periodo(ybar.index[i])[2]))
    t = pd.DataFrame(filas).sort_values("rho_critico", ascending=False).head(n)
    t.insert(0, "rango", range(1, len(t) + 1))
    t["es_ola_con_rho_base"] = t.rho_critico >= cfg.rho
    return t


def rejilla(cfg: Config, y) -> pd.DataFrame:
    """Exploratorio (§7): número de olas en la rejilla rho × w."""
    return pd.DataFrame(
        {f"w={w}": [len(delimitar(y, r, w, cfg.metodo).picos) for r in SENS_RHO]
         for w in REJILLA_W},
        index=pd.Index(SENS_RHO, name="rho"))


# --- Figura -----------------------------------------------------------------
def figura(cfg: Config, y, base: Resultado, ruta: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True,
                                 gridspec_kw=dict(height_ratios=[3, 1.4]))
    a1.plot(y.index, y.values, color="#bbbbbb", lw=0.5, label="diario (reporte)")
    a1.plot(base.ybar.index, base.ybar.values, color="#1f4e79", lw=1.6,
            label=f"media móvil {cfg.w} d")
    for f in base.fronteras:
        a1.axvline(f, color="#c0392b", ls="--", lw=1)
    for k, p in enumerate(base.picos, start=1):
        a1.annotate(str(k), (p, base.ybar.loc[p]), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=10,
                    fontweight="bold")
    a1.set_yscale("log")
    a1.set_ylim(10, None)
    a1.set_ylabel("casos confirmados / día")
    a1.set_title(f"Regla {cfg.nombre}: ρ = {cfg.rho:g}, w = {cfg.w} d"
                 + (", lote 2020-10-05 corregido" if cfg.corregir_lote else ""))
    a1.legend(loc="lower right", fontsize=8)
    for j, rho in enumerate(SENS_RHO):
        fr = delimitar(y, rho, cfg.w, cfg.metodo).fronteras
        a2.scatter(fr, [j] * len(fr), s=14,
                   color="#c0392b" if rho == cfg.rho else "#555555")
    a2.set_yticks(range(len(SENS_RHO)))
    a2.set_yticklabels([f"ρ={r:g}" for r in SENS_RHO], fontsize=8)
    a2.set_ylabel("fronteras")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def ejecutar(cfg: Config, figura_on: bool = True) -> dict:
    out = SALIDA / cfg.nombre
    out.mkdir(parents=True, exist_ok=True)
    y_jhu, y_dge = serie_jhu(cfg.corregir_lote), serie_dge()
    base = delimitar(y_jhu, cfg.rho, cfg.w, cfg.metodo)
    t = etiquetar(tabla_olas(y_jhu, base))
    sens, olas_sens = sensibilidad(cfg, y_jhu, y_dge, base)
    rob = robustez(sens, base)
    rej = rejilla(cfg, y_jhu)
    crit = rho_critico(cfg, y_jhu)
    crit.to_csv(out / "rho_critico.csv", index=False)
    rho_critico(cfg, y_dge).to_csv(out / "rho_critico_dge.csv", index=False)
    t.to_csv(out / "olas.csv", index=False)
    sens.to_csv(out / "sensibilidad.csv", index=False)
    olas_sens.to_csv(out / "olas_por_variante_sensibilidad.csv", index=False)
    rob.to_csv(out / "robustez_fronteras.csv", index=False)
    rej.to_csv(out / "rejilla_rho_w.csv")
    if figura_on:
        figura(cfg, y_jhu, base, out / "olas.png")
    return dict(olas=t, sens=sens, rob=rob, rejilla=rej, crit=crit)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", action="store_true")
    ap.add_argument("--sin-figura", action="store_true")
    args = ap.parse_args()
    if args.descargar:
        descargar()
    pd.set_option("display.width", 250, "display.max_columns", 40,
                  "display.max_colwidth", 60)
    print("Racha máx. de días sin reporte (JHU), por trimestre:")
    print(racha_max_ceros(serie_jhu()).to_string())
    for cfg in (DECLARADA, A1):
        r = ejecutar(cfg, not args.sin_figura)
        print(f"\n===== {cfg.nombre}: rho={cfg.rho}, w={cfg.w}, "
              f"lote corregido={cfg.corregir_lote} =====")
        print(r["olas"][["ola", "inicio", "pico", "fin", "duracion_dias",
                         "incidencia_pico", "ola_convencional",
                         "periodos_abarcados"]].to_string(index=False))
        print("\nSensibilidad:")
        cols = [c for c in r["sens"].columns if c not in ("fronteras", "fronteras_nuevas")]
        print(r["sens"][cols].to_string(index=False))
        print("\nRobustez:")
        print(r["rob"].to_string(index=False))
        print("\nrho crítico por pico:")
        print(r["crit"].to_string(index=False))
        print("\nRejilla n_olas (rho × w):")
        print(r["rejilla"].to_string())


if __name__ == "__main__":
    main()
