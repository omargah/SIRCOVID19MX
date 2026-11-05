"""Corrida completa de la recuperación sintética (F4, decisiones del 2026-11-04).

Uso:
    python scripts/recuperacion_sintetica.py --datos casos
    python scripts/recuperacion_sintetica.py --datos casos_sero

Diseño (config/parametros.yaml, sección `sintetico`):
    escenarios = malla_R0 x malla_s0 x malla_D  (2 x 2 x 2 = 8)
    réplicas por escenario = replicas (50)
    por réplica: ruido NB y Poisson x verosimilitud NB y Poisson (4 ajustes),
    cada uno con perfiles de R0, s0 y R_eff(0).

Salida: reports/resultados/recuperacion/<datos>.jsonl, una línea por
réplica, escrita en cuanto termina (si la corrida se interrumpe, al volver a
lanzarla se saltan las réplicas ya hechas). Junto a ella,
<datos>_manifiesto.json con el commit de git y el diseño usado.

Semillas: cada réplica usa SeedSequence([semilla, escenario, réplica,
con_sero]); el resultado no depende del orden en que terminan los procesos.
"""

from __future__ import annotations

import os

# Un hilo de BLAS por proceso: los procesos ya usan todos los núcleos.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import itertools
import json
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import parametros, recuperacion as R  # noqa: E402

SALIDA = RAIZ / "reports" / "resultados" / "recuperacion"


def escenarios(P):
    return [
        {"id": i, "R0": R0, "s0": s0, "D": D}
        for i, (R0, s0, D) in enumerate(itertools.product(P["malla_R0"], P["malla_s0"], P["malla_D"]))
    ]


def _a_json(x):
    if isinstance(x, dict):
        return {k: _a_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_a_json(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    return x


def leer_hechas(archivo):
    """{(escenario_id, réplica)} ya guardadas en el .jsonl.

    Si la corrida se cortó a media escritura (p. ej. la computadora se
    suspendió), la última línea puede quedar incompleta: se descarta (esa
    réplica se vuelve a calcular, con la misma semilla), se reescribe el
    archivo sin ella y se avisa.
    """
    hechas = set()
    if not archivo.exists():
        return hechas
    buenas, malas = [], 0
    for linea in archivo.read_text().splitlines():
        try:
            d = json.loads(linea)
        except json.JSONDecodeError:
            malas += 1
            continue
        buenas.append(linea)
        hechas.add((d["escenario_id"], d["replica"]))
    if malas:
        archivo.write_text("".join(l + "\n" for l in buenas))
        print(f"Aviso: se descartaron {malas} línea(s) incompletas de {archivo.name}", flush=True)
    return hechas


def _tarea(args):
    esc, rep, con_sero, P = args
    semilla = np.random.SeedSequence([P["semilla"], esc["id"], rep, int(con_sero)])
    t0 = time.time()
    esc_modelo = {k: esc[k] for k in ("R0", "s0", "D")}
    try:
        r = R.replica(esc_modelo, P, semilla, con_sero)
        r["error"] = None
    except Exception as e:  # se registra; no se descarta en silencio
        r = {"escenario": esc_modelo, "error": f"{type(e).__name__}: {e}"}
    r.update({"escenario_id": esc["id"], "replica": rep, "segundos": time.time() - t0})
    return _a_json(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", choices=["casos", "casos_sero"], required=True)
    ap.add_argument("--procesos", type=int, default=os.cpu_count())
    ap.add_argument("--replicas", type=int, default=None, help="por omisión, la del YAML")
    a = ap.parse_args()

    P = parametros.cargar_parametros("sintetico")
    con_sero = a.datos == "casos_sero"
    n_rep = a.replicas or P["replicas"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    archivo = SALIDA / f"{a.datos}.jsonl"

    hechas = leer_hechas(archivo)
    escs = escenarios(P)
    # Orden réplica-mayor: si se corta, todos los escenarios tienen réplicas.
    tareas = [(e, r, con_sero, P) for r in range(n_rep) for e in escs if (e["id"], r) not in hechas]

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    sucio = bool(subprocess.run(["git", "status", "--porcelain", "src", "config", "scripts"],
                                cwd=RAIZ, capture_output=True, text=True).stdout.strip())
    (SALIDA / f"{a.datos}_manifiesto.json").write_text(json.dumps(_a_json({
        "commit": commit, "arbol_con_cambios_sin_commit": sucio, "datos": a.datos,
        "escenarios": escs, "replicas": n_rep, "semilla": P["semilla"],
        "verdad_fija": {k: P[k] for k in ("N", "i0", "rho", "k")},
        "sero": P["sero"] if con_sero else None, "perfil_paso_inicial": P["perfil_paso_inicial"],
        "perfil_biseccion": P["perfil_biseccion"], "perfil_pulir": P["perfil_pulir"],
        "fin_ola_fraccion_pico": P["fin_ola_fraccion_pico"],
    }), indent=1))

    print(f"{len(hechas)} réplicas ya hechas; faltan {len(tareas)}", flush=True)
    t0 = time.time()
    with Pool(a.procesos) as pool, open(archivo, "a") as f:
        for i, res in enumerate(pool.imap_unordered(_tarea, tareas), 1):
            f.write(json.dumps(res) + "\n")
            f.flush()
            print(f"[{i}/{len(tareas)}] esc {res['escenario_id']} rep {res['replica']} "
                  f"{res['segundos']:.0f}s  error={res['error']}  total {time.time() - t0:.0f}s",
                  flush=True)


if __name__ == "__main__":
    main()
