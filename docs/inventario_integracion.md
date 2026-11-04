# Inventario de ramas y plan de integración — PT1

Fecha de la revisión: 2026-11-04. Repositorio: `omargah/SIRCOVID19MX`.

Este documento es **solo un inventario y una propuesta**. No se unió ninguna
rama. Las pruebas de unión se hicieron en seco (`git merge-tree`, objetos
sueltos sin rama) y las pruebas de código en worktrees temporales que ya se
borraron.

Cómo se corrieron las pruebas: Python 3 con numpy 2.5.4, scipy 1.18.1,
sympy 1.14.0, pandas 3.1.0, pyyaml, pytest, numba 0.68.1 y pytest-xdist, en
un entorno virtual aparte (no se usó `make env`).

---

## 0. Ramas que existen en GitHub

Hay **7 ramas** (más `integracion/pt1`, que es esta). El clon no es
superficial. No hay etiquetas en el remoto.

| Rama | Último commit | Fecha (UTC) | Autor |
|---|---|---|---|
| `main` | `675437f` Agregar contacto de Facultad de Medicina-UNAM | 2026-10-27 | Omar García Hernández |
| `claude/kind-newton-2qjan7` | `ce9cf8e` F4: validación sintética del SIR por ola y plan de análisis congelado | 2026-11-04 01:30 | Claude |
| `claude/sir-covid-mexico-remake-834hzi` | `f9745f7` sir.py: SIR en personas, β por tramos y pruebas (a)–(g) | 2026-11-04 01:00 | Claude |
| `claude/zealous-heisenberg-d3q5dk` | `fa6cfa1` separar ola 1 y 2 con frontera por mínimo de media móvil | 2026-11-04 01:00 | Claude |
| `claude/compassionate-dijkstra-hoccgu` | `726f3e6` F3: pipeline de datos DGE | 2026-11-04 00:45 | Claude |
| `claude/fervent-dirac-ud7ob4` | `015c40a` F2: verificación SymPy + sir.py de las derivaciones a–k | 2026-11-04 00:43 | Claude |
| `claude/stoic-galileo-qsf1n6` | `302ed4b` F1: parametros.yaml con fuente obligatoria o supuesto | 2026-11-04 00:36 | Claude |

- **La rama de la validación sintética F4 es `claude/kind-newton-2qjan7`.**
  Tiene `sirmx/`, `docs/decisiones.md`, `scripts/validacion_sintetica.py` y
  `sirmx/pronostico.py`. Ojo: **apareció en GitHub durante esta revisión**
  (no estaba en el primer `git fetch`; se subió a las 01:30 UTC).
- `claude/elegant-pascal-woh4d4`: **no existe** en el remoto. O la sesión no
  hizo nada, o no subió su trabajo. No se puede saber desde aquí.
- El commit `8fc89d6` de `sir-covid-mexico-remake` también trae una
  "validación sintética de H1" (`scripts/correr_sintetico.py`,
  `src/verosimilitud.py`, `src/identificabilidad.py`). Es **otra** validación,
  distinta de `sirmx/`. Hay dos.

### Árbol de dependencias

```
main 675437f
 ├── sir-covid-mexico-remake:  8fc89d6 (F0) ── e61a3a5 (infra) ── f9745f7 (sir.py nuevo)
 │                                               ├── stoic-galileo:  302ed4b (F1 parámetros)
 │                                               └── fervent-dirac:  015c40a (F2 teoría a–k)
 ├── zealous-heisenberg:  f2ef6ee ─ 86cac48 ─ bd237d1 ─ 2564c37 ─ 550ab3a ─ fa6cfa1 (olas)
 ├── compassionate-dijkstra:  726f3e6 (F3 pipeline DGE)
 └── kind-newton:  ce9cf8e (F4 sirmx)
```

`stoic-galileo` y `fervent-dirac` salen de `e61a3a5`, **antes** del último
commit de `sir-covid-mexico-remake` (`f9745f7`), que cambió `src/sir.py`.
`zealous-heisenberg`, `compassionate-dijkstra` y `kind-newton` salen directo
de `main` y no conocen la infraestructura de F0 (ni `src/sir.py`).

---

## 1. Inventario por rama

### 1.1 `claude/sir-covid-mexico-remake-834hzi` (F0 + infraestructura + sir.py)

- **Base:** `main` (`675437f`).
- **Commits propios (3):** `8fc89d6` F0 alcance, reglas, estructura y
  validación sintética de H1 · `e61a3a5` Infra: make env/test/figuras,
  environment.yml · `f9745f7` sir.py en personas, β por tramos, pruebas (a)–(g).
- **Archivos (36; +2940 / −93):** borra `.DS_Store`; agrega `.gitignore`,
  `Makefile`, `environment.yml`, `config/parametros.yaml`, `src/{sir,
  verosimilitud, identificabilidad, datos, olas}.py` (`olas.py` es un
  esqueleto de 6 líneas), `scripts/{correr_sintetico, make_figuras,
  make_numeros, make_tablas, deps_pip}.py`, `tests/{conftest, test_sir,
  test_identificabilidad, test_infra, test_parametros}.py`,
  `docs/{actas/F0-alcance, plan_analisis, desviaciones}.md`, `escrito/`
  (LaTeX), `reports/` (figuras, tablas, JSON sintético); modifica `README.md`.
- **Pruebas:** **30 pasan, 0 fallan, 0 xfail.**
- **Aporte:** la base de todo: estructura, `make`, entorno y el simulador
  oficial `src/sir.py` (S, ln I, R con LSODA, `rtol=1e-10`,
  `integrar_sir_tramos` con β por tramos, `R0 = (1 + rD)/s0`). Trae
  verosimilitud binomial negativa semanal + serología y el experimento de
  identificabilidad H1.

### 1.2 `claude/stoic-galileo-qsf1n6` (F1: parámetros con fuente)

- **Base:** `e61a3a5` (de `sir-covid-mexico-remake`, sin `f9745f7`).
- **Commits propios (1):** `302ed4b`.
- **Archivos (5; +577 / −87), todos modificados:** `config/parametros.yaml`,
  `src/datos.py` (cargador con validación de fuentes), `tests/test_parametros.py`,
  `docs/plan_analisis.md`, `README.md`.
- **Pruebas:** **45 pasan, 0 fallan, 0 xfail.**
- **Aporte:** esquema obligatorio de fuente (`doi` / `institucional` /
  `regla`) o `supuesto: true` con rango de sensibilidad; `D_ola1`…`D_ola5`
  con `definicion: intervalo_generacion` (nunca incubación), `gamma = 1/D`
  derivado; `N = 126 014 024` (INEGI 2020); seroprevalencias, `s0` y `rho`
  por ola. Casi todos los valores reales están en `null` (pendientes de la
  hoja "Parámetros" del xlsx).

### 1.3 `claude/fervent-dirac-ud7ob4` (F2: teoría a–k)

- **Base:** `e61a3a5`.
- **Commits propios (1):** `015c40a`.
- **Archivos (16; +1221 / −1):** agrega `tests/teoria/` (11 pruebas a–k +
  README), `docs/teoria_verificacion.md`, `pytest.ini` (marcador `teoria`,
  `--strict-markers`); modifica `Makefile` (objetivo `teoria`) y `README.md`.
- **Pruebas (en su propia rama):** **110 pasan, 0 fallan, 2 xfail estrictos.**
- **Aporte:** cada derivación del Cap. 2 se comprueba en SymPy y contra
  `src/sir.py`. Documenta 8 discrepancias, entre ellas los 2 xfail.
- **Ojo:** probó la versión **anterior** de `src/sir.py` (la de `e61a3a5`,
  en fracciones: `integrar_sir(R0, gamma, s0, i0, t) -> (s, i)`). Ver §2.2 a.

### 1.4 `claude/zealous-heisenberg-d3q5dk` (F3: regla de olas)

- **Base:** `main` (`675437f`).
- **Commits propios (6):** `f2ef6ee` declarar regla · `86cac48` registrar
  resultado y enmienda A1 antes de ejecutarla · `bd237d1` implementar regla,
  A1 y sensibilidad · `2564c37` ignorar `__pycache__` · `550ab3a` declarar
  frontera 1.ª/2.ª ola · `fa6cfa1` separar ola 1 y 2 (decisión posterior).
- **Archivos (31; +3339 / −1):** `src/olas.py` (494 líneas),
  `tests/test_olas.py`, `docs/{regla_olas, olas_resultados}.md`,
  `data/{README.md, jhu_mexico_confirmados_acumulados.csv,
  dge_mexico_confirmados_por_ingreso.csv}`, `resultados/olas/{declarada, A1,
  A1_frontera}/…`, `.gitignore` (nuevo, 2 líneas), `README.md`,
  `bibliografia/INDICE.csv` y `referencias.bib` (agrega `H04` Taboada et al.
  2021, `por_verificar`).
- **Pruebas:** **5 pasan, 0 fallan, 0 xfail.**
- **Aporte:** regla de olas declarada antes de aplicarse; con A1 + frontera
  del 2020-10-01 da las 5 olas: **2020-02-27, 2020-10-01, 2021-05-16,
  2021-12-10, 2022-04-25; fin 2023-02-28** (coinciden con las de la tarea).
  La frontera 1.ª/2.ª ola se tomó **después** de ver el resultado (está
  marcado así en el CSV). Fuente: JHU por fecha de reporte.

### 1.5 `claude/compassionate-dijkstra-hoccgu` (F3: pipeline DGE)

- **Base:** `main` (`675437f`).
- **Commits propios (1):** `726f3e6`.
- **Archivos (25; +2792 / −1):** `src/{datos, comparar_tablero, eda, fuentes,
  series_historicas, __init__}.py`, `scripts/{registrar_fuente,
  inventario_historicos}.py`, `tests/{__init__, sintetico, test_pipeline}.py`,
  `docs/{diccionario_datos, inventario_historicos, nota_diferencias}.md`,
  `data/{fuentes.csv, inventario_historicos.csv, raw/README.md, …/.gitkeep}`,
  `Makefile`, `.gitignore`, `requirements.txt`, `README.md`.
- **Pruebas:** **8 pasan, 0 fallan, 0 xfail** (34 avisos de pandas por
  `Series.dt.weekday`, que pandas 4 va a quitar).
- **Aporte:** serie nacional diaria por **fecha de inicio de síntomas**
  desde microdatos DGE, determinista byte a byte, con registro de procedencia
  (hash), comparación con el tablero CONAHCYT y EDA de artefactos. No trae
  datos crudos (hay que bajarlos a mano).

### 1.6 `claude/kind-newton-2qjan7` (F4: validación sintética, `sirmx/`)

- **Base:** `main` (`675437f`).
- **Commits propios (1):** `ce9cf8e`.
- **Archivos (27; +1992 / −2):** `sirmx/{__init__, modelo, verosimilitud,
  identificabilidad, crecimiento, cambios, pronostico, escenarios,
  validacion}.py`, `scripts/validacion_sintetica.py`,
  `docs/{decisiones, plan_analisis, validacion_sintetica}.md`,
  `tests/{__init__, conftest, test_1_observacion … test_8_reproducibilidad}.py`,
  `pytest.ini`, `requirements.txt`, `.gitignore`; modifica `README.md`.
- **Pruebas:** **40 pasan, 0 fallan, 0 xfail** (con numba y `-n 4`:
  **6 min 30 s**).
- **Aporte:** SIR por ola con observación diaria (BinNeg + efecto de día de
  la semana), ajuste en la parametrización identificable
  (R_eff(0), i0/s0, ρ·s0) con 8 inicios, perfiles, r con ventana fija y
  R = 1 + rD para D ∈ {5, 7, 10}, puntos de cambio de β por BIC, pronóstico
  con WIS contra persistencia y reproducibilidad bit a bit. Congela un
  `docs/plan_analisis.md` propio. Fija **D = 7** para todo.

### 1.7 `main`

- 0 pruebas (no hay `tests/`). Contiene `bibliografia/`, `v0-anterior/` y
  `README.md`.

---

## 2. Conflictos

### 2.1 Conflictos de git (unión en seco con `git merge-tree`)

**Por pares:**

| Par | Resultado | Archivos en conflicto |
|---|---|---|
| remake + stoic | limpio | — |
| remake + fervent | limpio | — |
| stoic + fervent | limpio | — |
| remake / stoic / fervent + zealous | conflicto | `.gitignore` (add/add), `README.md`, `src/olas.py` (add/add) |
| remake / stoic / fervent + compassionate | conflicto | `.gitignore`, `Makefile`, `README.md`, `data/raw/README.md` (add/add), `src/datos.py` (add/add) |
| zealous + compassionate | conflicto | `.gitignore` (add/add) |
| kind-newton + remake / stoic | conflicto | `.gitignore`, `README.md`, `docs/plan_analisis.md` (add/add), `tests/conftest.py` (add/add) |
| kind-newton + fervent | conflicto | lo anterior + `pytest.ini` (add/add) |
| kind-newton + zealous | conflicto | `.gitignore`, `README.md` |
| kind-newton + compassionate | conflicto | `.gitignore`, `README.md`, `requirements.txt` (add/add) |

**En cadena** (`main` → remake → stoic → fervent → zealous → compassionate →
kind-newton): los tres primeros pasos son limpios; zealous da conflicto en
`.gitignore`, `README.md`, `src/olas.py`; compassionate en `.gitignore`,
`Makefile`, `README.md`, `data/raw/README.md`, `src/datos.py`; kind-newton en
`.gitignore`, `README.md`, `docs/plan_analisis.md`, `pytest.ini`,
`requirements.txt`, `tests/conftest.py`.

Puntos que pediste revisar:

- **`src/datos.py`: sí, son dos módulos distintos con el mismo nombre.**
  - stoic-galileo: cargador de `config/parametros.yaml` con validación de
    fuentes (`cargar_parametros`, `rangos_sensibilidad`, `gamma_ola`,
    `RAIZ`). Lo usan `scripts/correr_sintetico.py`, `make_figuras.py`,
    `make_numeros.py` y `tests/test_parametros.py`.
  - compassionate-dijkstra: pipeline DGE (`construir`, `armar_series`,
    `verificar_determinismo`, `python -m src.datos`). Lo usan
    `src/series_historicas.py`, `tests/test_pipeline.py`, el `Makefile` y
    textos de `src/eda.py` y `src/comparar_tablero.py`.
  - No comparten ni una función. No se pueden "mezclar": hay que renombrar uno.
- **`README.md`:** lo modifican las 6 ramas. Conflicto de texto con
  zealous, compassionate y kind-newton; con stoic y fervent git une solo.
- **`Makefile`:** remake lo crea; fervent le agrega `teoria` (une limpio);
  compassionate crea **otro** `Makefile` con objetivos `serie`, `eda`,
  `comparar`, etc. y su propio `test`. kind-newton no tiene `Makefile`.
- **`pytest.ini`:** fervent (`--strict-markers`, marcador `teoria`) y
  kind-newton (`pythonpath = .`, `testpaths = tests`, `addopts = -ra`).
  Se pueden sumar sin choque de fondo. Con `--strict-markers`, cualquier
  marcador no declarado truena (hoy kind-newton no usa marcadores).
- **`tests/conftest.py`:** remake (agrega la raíz a `sys.path`) y
  kind-newton (1 hilo de BLAS y la "puerta" `paso3_aprobado`). Se suman.
- **`environment.yml` / `requirements.txt`:** remake trae
  `environment.yml`; compassionate y kind-newton traen **dos**
  `requirements.txt` distintos (pandas/matplotlib contra scipy/numba/xdist).
  Son tres listas; remake dice que debe haber una sola.
- **`.gitignore`:** cuatro versiones. Además del conflicto de texto, hay un
  **choque de criterio**: remake ignora todo `data/processed/*`;
  compassionate quiere versionar `data/processed/serie_nacional_sintomas.csv`
  y `manifiesto.json`.
- **`bibliografia/INDICE.csv`:** solo zealous lo toca (agrega `H04`). Sin
  conflicto. stoic valida que las claves de `fuente_candidata` (`G01, G02,
  G05, G06, I01, I03`) existan en este archivo: ya existen en `main`.
- **`src/olas.py`:** remake trae un esqueleto vacío (docstring de 6 líneas);
  zealous trae la implementación. Se resuelve tomando la de zealous.
- **`docs/plan_analisis.md`:** dos planes distintos con el mismo nombre
  (ver §2.2 e).
- **`src/sir.py`: sí, fervent probó una versión anterior.** fervent parte
  de `e61a3a5`. Ahí `integrar_sir(R0, gamma, s0, i0, t)` trabajaba en
  fracciones y devolvía `(s, i)`. En `f9745f7` cambió a
  `integrar_sir(R0, D, S0, I0, N, t)` en personas y devuelve `(S, I, R)`.
  Git une limpio, pero las pruebas se rompen (ver abajo).

### 2.2 Conflictos de contenido

#### a) `tests/teoria/` contra el `sir.py` actual

Se copiaron `tests/teoria/` y `pytest.ini` de fervent sobre
`sir-covid-mexico-remake` (`f9745f7`) en un worktree temporal:

**40 fallan, 47 pasan, 2 xfail.** Las 40 fallas son todas
`TypeError: integrar_sir() missing 1 required positional argument: 't'` (o
derivadas de eso): es el **cambio de firma**, no un error matemático. Hay
que adaptar las llamadas (`gamma → D = 1/gamma`, fracciones → personas con
`N`, desempacar 3 salidas).

La unión remake + stoic + fervent (sin las demás) da
**99 pasan, 40 fallan, 2 xfail**; sin `tests/teoria/`, **52 pasan**.

#### b) Los 2 xfail de fervent: ¿siguen fallando con el `sir.py` actual?

Ojo: un xfail sin `raises=` también "pasa" si la prueba truena por
`TypeError`, así que el "2 xfailed" de arriba no dice nada. Se revisaron a
mano:

1. **Error de LSODA en ola explosiva** (R0 = 15, γ = 1/5, s0 = 0.99,
   i0 = 1e-9, umbral 1e-9). Con un adaptador a la nueva firma, el error
   máximo en s contra DOP853 (`rtol=1e-13`) es **1.5e-9** (N = 1 o 1e7) y
   **1.7e-9** (N = 126 014 024). Antes era ~1e-8. **Mejoró ~6 veces pero
   sigue fallando** (sigue arriba de 1e-9). En el caso típico (R0 = 2.5) es
   3.5e-10: pasa.
2. **Incidencia semanal con i0 = 1e-10.** `incidencia_semanal` conserva su
   firma, así que esta prueba sí corrió tal cual (con `--runxfail`): error
   relativo máximo **3.2 %** (antes ~5 %), umbral 1e-5. **Sigue fallando.**
   La causa no cambió: se calcula como diferencia de S.

Conclusión: los dos xfail **siguen siendo reales** con el `sir.py` actual.
La discrepancia 3 de fervent ("sir.py no implementa β(t)") **ya quedó
resuelta** con `integrar_sir_tramos`.

#### c) Dos simuladores SIR: `src/sir.py` contra `sirmx/`

**Decisión ya tomada: `src/sir.py` es el oficial.**

| Punto | `src/sir.py` (remake `f9745f7`) | `sirmx/modelo.py` (kind-newton) |
|---|---|---|
| Ecuaciones | dS/dt = −βSI/N, dI/dt = βSI/N − γI, dR/dt = γI, **en personas** | s' = −βsi, i' = βsi − γi, **en fracciones**; R no se integra |
| Parametrización | β = R0·γ, γ = 1/D (`tasas(R0, D)`) | β = R0·γ, γ = 1/D (`ParamsOla.gamma`). **Igual.** |
| Integrador | LSODA (scipy) en (S, ln I, R), `rtol=1e-10`, `atol` relativa a N; I > 0 por construcción | **RK4 propio**, paso fijo de 1/4 de día, en (s, i); compilado con numba si está |
| β variable | `integrar_sir_tramos`: τ en cualquier tiempo real, reinicia la integración en cada cambio | `beta_por_tramos`: β constante **por día**, τ en días enteros, sin reiniciar |
| Incidencia | ρ·[S(t_k) − S(t_{k+1})] **por semana**, recortada a ≥ 0 | N·[s(t) − s(t+1)] **por día**, recortada a ≥ 0, × ρ × efecto de día de la semana |
| Observación | BinNeg semanal + serología (Normal) | BinNeg diaria + efecto de día de la semana; **sin** serología |
| Estado inicial | exige S0 > 0, I0 > 0 y S0 + I0 ≤ N | no valida |
| r → R | `R0 = (1 + rD)/s0` | `R = 1 + rD` |

Concuerdan en lo numérico: con R0 = 2.5, D = 7, s0 = 0.6, i0 = 1e-5 y 200
días, **la diferencia máxima en s entre el RK4 de `sirmx` y LSODA de
`src/sir.py` es 3.0e-10.** La diferencia es de diseño, no de resultado.

Qué tendría que cambiar en `sirmx/` para usar `src/sir.py` por dentro, sin
perder lo que aporta:

1. `sirmx/modelo.py::sir_incidencia` y `_sir_rk4`: reemplazar por una
   llamada a `src.sir.integrar_sir_tramos` con `t = 0, 1, …, T` (días) y
   `N`, y sacar la incidencia diaria como `−diff(S)/N`.
2. `beta_por_tramos`: traducir `cambios` (τ) y `log_factores` (δ) a
   `t_cambios` y `R0_tramos = R0·exp(Σ δ)`. Ojo: `integrar_sir_tramos` exige
   τ estrictamente dentro de (t[0], t[−1]) y crecientes.
3. `ParamsOla`, `ajustar_ola`, `detectar_cambios`, `pronostico_sir`,
   `identificabilidad.py`: dejar de tener `D = 7.0` por omisión y recibir D
   de `config/parametros.yaml` (`D_olaN`) — ver §2.2 d.
4. Conservar intactos: la verosimilitud con efecto de día de la semana, la
   parametrización identificable, el multi-inicio, los perfiles,
   `crecimiento.py`, la búsqueda de cambios por BIC, `pronostico.py` (WIS,
   persistencia) y la prueba de reproducibilidad.
5. Hay **dos verosimilitudes** (`src/verosimilitud.py`: semanal + serología,
   parámetros naturales; `sirmx/verosimilitud.py`: diaria, día de la semana,
   parámetros identificables). Hay que decidir si se quedan las dos o se
   unen en una (ver decisión 2 en §3.4).
6. La prueba de reproducibilidad "bit a bit" debería seguir pasando con
   LSODA (es determinista), pero **no verificado**.
7. La comparación numba = Python de `sirmx` deja de tener sentido y se borra.

**Velocidad (medido):**

| Llamada (200 días o 30–60 semanas) | Tiempo |
|---|---|
| `sirmx` RK4 con numba | **0.024 ms** |
| `sirmx` RK4 en Python puro | 0.37 ms |
| `src/sir.py` LSODA, 200 días | **2.8 ms** |
| `src/sir.py` `incidencia_semanal`, 30 semanas | ~2 ms |
| `src/sir.py` `integrar_sir_tramos`, 3 tramos | ~3 ms |

LSODA es **~115 veces más lento** que el RK4 con numba. Las 40 pruebas de
`sirmx` tardan **6 min 30 s** con numba en 4 procesos; si el integrador
domina el tiempo, con LSODA podrían tardar **horas** (estimación, no
medida). Lo más lento: el estudio de cobertura (40 réplicas × 3 escenarios
× 8 inicios), el bootstrap de r (B = 200), la búsqueda de τ en rejilla
para K = 2 y el pronóstico (un ajuste por origen + 300 trayectorias).
Opciones: correr esas partes en paralelo, marcar esas pruebas como lentas
(`@pytest.mark.lento`) y no correrlas en `make test`, o usar un RK4 solo
para explorar y LSODA para el punto final (pero eso vuelve a ser "dos
simuladores").

#### d) D por ola

**Decisión ya tomada: D por ola con fuente (`D_olaN`, de `parametros.yaml`).
D = 5, 7 y 10 solo como sensibilidad.**

Cada lugar donde choca:

| Lugar | Qué dice | ¿Choca? |
|---|---|---|
| `kind-newton: docs/decisiones.md`, I3 | "D no se estima: se fija. Valor base D = 7 días; escenarios D ∈ {5, 7, 10}" | **Choca** en el valor base. La sensibilidad {5, 7, 10} **coincide**. |
| `kind-newton: docs/plan_analisis.md` §2 y §8 | "D fijo: valor base de 7 días" (y está **congelado**) | **Choca.** Hay que enmendarlo. |
| `kind-newton: sirmx/modelo.py:89` | `ParamsOla.D = 7.0` por omisión | **Choca.** |
| `kind-newton: sirmx/verosimilitud.py:102` | `ajustar_ola(y, D=7.0, …)` | **Choca.** |
| `kind-newton: sirmx/cambios.py:88` | `detectar_cambios(y, D=7.0, …)` | **Choca.** |
| `kind-newton: sirmx/escenarios.py` | `D=7.0` en los escenarios sintéticos | No choca: es la "verdad" del experimento. |
| `kind-newton: sirmx/crecimiento.py:13` | `D_ESCENARIOS = (5.0, 7.0, 10.0)` | **Coincide** (sensibilidad). |
| `stoic-galileo: config/parametros.yaml` | `D_ola1`…`D_ola5`, `intervalo_generacion`, en `null`; `sensibilidad` 4–7 (olas 1–3) y 3–7 (olas 4–5) | **Coincide** con la decisión. **Choca** en el rango: 10 queda fuera. |
| `remake: config/parametros.yaml` (sección `real`) | un solo `gamma` para todas las olas | **Choca.** stoic lo reemplaza al unir. |
| `remake: docs/plan_analisis.md` | "Fijos con fuente: γ, N" | Choca en redacción; stoic ya lo cambia a "γ = 1/D por ola". |
| `remake`/`stoic`: sección `sintetico` | `gamma = 1/7` | No choca: valor de diseño sintético. |
| `remake: tests/test_sir.py` (f) | D = 7 para BA.1 | No choca: reproduce el error del código viejo. |
| `fervent: tests/teoria/` | γ = 1/7 y 1/5 en ejemplos | No choca. |
| `zealous`, `compassionate` | no usan D | — |

#### e) `docs/decisiones.md` de F4: D0, I2, I3, I4 (y C1–C7)

El propio archivo dice que **I2–I4 no venían en la solicitud y no existen
como issues en GitHub**; la sesión los definió por su cuenta. Clasificación
de cada decisión: **(a)** coincide con otra rama, **(b)** choca con otra
rama, **(c)** es nueva y nada la contradice.

**D0. Convenciones del modelo**

| Decisión | Clase | Con qué y en qué |
|---|---|---|
| SIR en fracciones, RK4 con 4 subpasos/día | **(b)** | remake `src/sir.py`: personas, LSODA. Y la decisión ya tomada. |
| β constante por tramos en días enteros | **(b)** parcial | remake `integrar_sir_tramos`: τ continuo y reinicio en cada cambio. Misma idea, otra implementación. |
| γ = 1/D, β = R0·γ | **(a)** | remake, stoic, fervent. |
| Incidencia = N·(s(t) − s(t+1)) | **(a)** en la regla / **(b)** en la escala | La regla (diferencia de S) es la de remake; pero F4 es **diaria** y remake/stoic (`plan_analisis.md`) son **semanales**. |
| BinNeg, Var = μ + μ²/k | **(a)** | remake `src/verosimilitud.py`, `plan_analisis.md`. |
| Efecto multiplicativo de día de la semana (6 parámetros) | **(b)** | remake `src/sir.py` decidió "semanas y no días" justamente para quitar el ciclo semanal sin agregar parámetros. |
| Sin convolución de retraso de reporte | **(a)** | Coincide con la limitación que anotan fervent (discrepancia 6) y el plan de stoic (nota 5). Ojo: el plan de stoic pide restar la incubación para H5. |
| N conocida | **(a)** | stoic (`N` con fuente). |

**I2. Qué se estima y cómo**

| Decisión | Clase | Con qué y en qué |
|---|---|---|
| Con casos solos solo se identifican R_eff(0) = R0·s0, ρ·s0 e i0/s0 | **(a)** | remake H1 (`src/identificabilidad.py`, `plan_analisis.md`: "solo R_eff(0) = R0·s0"). F4 lo extiende a i0/s0 (corrección C1). |
| Ajustar en esa parametrización identificable | **(b)** parcial | remake `src/verosimilitud.py` ajusta (R0, s0, i0, ρ, k) **con serología**, que rompe la cresta. F4 no usa serología. No es error, pero son dos estrategias. |
| ρ solo si s0 viene de fuera: s0 = 1 en la ola 1, ENSANUT en las demás | **(a)** | stoic (`s0_ola1 = 1.0`, `s0_ola2 = 1 − sero_ensanut2020`) y plan de stoic (nota crítica 1). |
| L-BFGS-B, 8 inicios aleatorios con semilla | **(a)** parcial | remake también usa L-BFGS-B (más pulido con Nelder-Mead). El número de inicios es nuevo. |
| IC de Wald (hessiana numérica) + perfiles con umbral 1.92 | **(a)** parcial | remake: perfiles (umbral 1.92) y bootstrap paramétrico. Wald es nuevo; el plan de stoic dice que el bootstrap solo se reporta para combinaciones identificables. |

**I3. D y r → R**

| Decisión | Clase | Con qué y en qué |
|---|---|---|
| D no se estima, se fija | **(a)** | remake y stoic también lo fijan. |
| Valor base D = 7 para todas las olas | **(b)** | stoic (`D_olaN` por ola, con fuente) y la decisión ya tomada. |
| Sensibilidad D ∈ {5, 7, 10} | **(a)** con tu decisión / **(b)** con stoic | stoic usa rangos 4–7 y 3–7. |
| R = 1 + r·D | **(a)** | remake, fervent, stoic. |
| r con ventana fija de 21 días desde media móvil ≥ 20 casos | **(c)** | Nueva. |
| k fijado del ajuste de la ola completa al estimar r (C4) | **(c)** | Nueva. |
| r "verdadero" = promedio de γ(R0·s(t) − 1) | **(c)** | Nueva. |

**I4. Recuperación, puntos de cambio, pronóstico, reproducibilidad**

| Decisión | Clase | Con qué y en qué |
|---|---|---|
| Criterios de recuperación (IC 95 %, error < 10 %, cobertura 0.85–1.00) | **(a)** | El plan de stoic/remake pide que F4 estime la cobertura real de los IC (nota 9). Los umbrales concretos son nuevos. |
| K ∈ {0, 1, 2} cambios elegidos por **BIC** | **(b)** | Plan de remake/stoic, H2: "Ljung–Box al 5 % **y** el modelo por tramos mejora el **AIC**". |
| H2 evaluada con ΔBIC + residuos de Pearson | **(b)** | Mismo plan: residuos cuantil-aleatorizados, Ljung–Box y rachas. |
| IC de τ por perfil | **(a)** | Plan, H5: "τ estimada por perfil". |
| Pronóstico: WIS contra persistencia, coberturas, error del pico | **(a)** | Plan, H4a y H4b (WIS de Bracher et al. 2021). |
| Horizontes de 1 a 4 semanas | **(b)** parcial | H4a habla de 1–2 semanas. |
| Semilla 20261104 | **(b)** menor | `parametros.yaml` (remake/stoic) usa `semilla: 20200228` para lo sintético. |
| Toda la aleatoriedad por `numpy.random.Generator` con semilla | **(c)** | Nueva; nadie la contradice. |

**Correcciones C1–C7:** son ajustes internos de F4. Las que importan para la
integración: **C3** (con cambios a menos de ~10–15 días BIC no los separa:
límite de resolución), **C5** (el pronóstico con β constante es peor que la
persistencia si hay cambio de β) y **C6** (numba, 1 hilo de BLAS,
`multiprocessing` con `spawn`), que choca con usar LSODA (§2.2 c).

**Además, choque de procedimiento:** `docs/plan_analisis.md` de kind-newton
dice "**CONGELADO** el 2026-11-04" con enmiendas al final del archivo. El
plan de remake/stoic dice "se congela al cerrar F4" y que los cambios van a
`docs/desviaciones.md`. Y el plan de F4 **no incluye H3** (tamaño final
contra ENSANUT), **H4b** (estabilidad del pico) **ni H5** (JNSD), ni la
serología en el ajuste, que sí están en el plan de remake/stoic. También
dice "N es la población nacional (**CONAPO**)", mientras que stoic usa INEGI
2020 y deja CONAPO como alternativa.

#### f) Relación r → R

Verificado con `git grep` en las 6 ramas (sin `v0-anterior/`):

- **Ninguna rama usa `exp(rD)` como fórmula.** Solo aparece en comentarios
  y en pruebas que muestran que es incorrecta.
- `remake`: `R0_desde_tasa_crecimiento = (1 + r*D)/s0` y la prueba (f).
- `fervent`: prueba (g) a favor de `1 + rD`.
- `stoic`: lo dice en el comentario del YAML (`R0 = 1 + r*Tg`).
- `kind-newton`: `sirmx/crecimiento.py::R_de_D` → `1 + r·D`.
- `zealous` y `compassionate`: no calculan R.
- Diferencia menor: remake divide entre s0 (`R0 = (1 + rD)/s0`); `sirmx` da
  `R = 1 + rD`, que es R_eff(0). Son la misma relación; solo hay que
  rotular bien cuál de los dos se reporta.
- **Discrepancia sobre el código viejo:** remake dice que el PT1 viejo usaba
  `exp(rD)` (BA.1: 4.28 vs ~2.94, tomado de una captura en PDF); fervent dice
  que el código viejo usa `1 + rD`. El `.py` de `main`
  (`v0-anterior/analisis_montecarlo.py`) efectivamente dice
  `R0 = (1 + growth * D) / S0`. Lo de la captura en PDF **no se verificó**.

#### g) Las olas

- Las fechas de zealous (`resultados/olas/A1_frontera/olas.csv`) son las 5
  de la tarea: 2020-02-27, 2020-10-01, 2021-05-16, 2021-12-10, 2022-04-25;
  fin 2023-02-28.
- **Ninguna otra rama fija fechas de olas.** stoic solo nombra ola1…ola5 por
  variante. compassionate solo usa el rango del tablero (2020-02-26 a
  2023-06-24) y el pico del PT1 viejo (2022-01-15). kind-newton (F4) usa solo
  datos sintéticos y dice que las fechas "se registrarán como enmienda A1
  antes de F5". Ojo: zealous **ya usó el nombre "A1"** para otra cosa (su
  enmienda de preprocesamiento). Conviene renombrar para no confundir.
- La frontera 2020-10-01 está marcada por zealous como "criterio externo…
  tomado después de ver el resultado de la regla principal". Es una decisión
  posterior y hay que declararla así en el escrito.

#### h) Fuente de casos (pendiente)

- Olas: **JHU CSSE por fecha de reporte** (contraste con DGE por fecha de
  ingreso, que solo llega a 2022-01-20).
- Pipeline: **DGE por fecha de inicio de síntomas**.
- F4 modela un efecto de día de la semana pensado para fechas de reporte;
  con fecha de síntomas ese efecto es otro (no verificado).
- **Pendiente:** volver a correr `src/olas.py` con la serie de
  compassionate cuando existan los microdatos, y decidir cuál manda.

#### i) Otros hallazgos

1. **`s0_ola1 = 1.0` no se puede simular con `src/sir.py`.** stoic fija
   `s0_ola1 = 1.0` ("S0 = N"), pero `src/sir.py` exige `S0 + I0 ≤ N` y truena
   con s0 = 1. Con `s0 = 1 − i0` también truena por redondeo. `sirmx` sí
   acepta s0 = 1 (sus escenarios lo usan). Al pasar `sirmx` a `src/sir.py`
   esto **va a romper** los escenarios. Arreglo: que `sir.py` use
   S0 = N − I0 cuando s0 = 1, o tolere un error de redondeo.
2. **`tests/__init__.py`** (compassionate y kind-newton, ambos vacíos) junto
   con `tests/conftest.py` cambia cómo pytest importa. Hay que correr toda
   la suite tras unir.
3. **pandas 4:** `src/eda.py` usa `Series.dt.weekday`, que se va a quitar.
4. **`docs/plan_analisis.md` (remake)** todavía dice "Estado: s, i (r por
   conservación)", que ya no es cierto con el `sir.py` nuevo.
5. **Dos validaciones sintéticas de H1:** `scripts/correr_sintetico.py`
   (remake) y `scripts/validacion_sintetica.py` (kind-newton). Dicen lo
   mismo sobre la cresta, con métodos distintos.

---

## 3. Plan de integración (propuesta, NO ejecutada)

### 3.1 Tabla resumen

| Rama | Base | Commits propios | Archivos | Pruebas | Aporte | ¿Se une? |
|---|---|---|---|---|---|---|
| `sir-covid-mexico-remake-834hzi` | `main` 675437f | 3 | 36 | 30 ✔ / 0 ✘ / 0 xfail | Infraestructura, `src/sir.py` oficial, verosimilitud, H1 sintético | **sí** |
| `stoic-galileo-qsf1n6` | `e61a3a5` (remake) | 1 | 5 | 45 ✔ / 0 ✘ / 0 xfail | `parametros.yaml` con fuente, `D_olaN`, cargador | **sí con cambios** (rango de D con 10; `s0_ola1`) |
| `fervent-dirac-ud7ob4` | `e61a3a5` (remake) | 1 | 16 | 110 ✔ / 0 ✘ / 2 xfail (en su rama); 47 ✔ / 40 ✘ / 2 xfail contra `sir.py` actual | Teoría a–k verificada | **sí con cambios** (adaptar a la nueva firma) |
| `zealous-heisenberg-d3q5dk` | `main` 675437f | 6 | 31 | 5 ✔ / 0 ✘ / 0 xfail | Regla de olas, 5 olas | **sí con cambios** (3 conflictos) |
| `compassionate-dijkstra-hoccgu` | `main` 675437f | 1 | 25 | 8 ✔ / 0 ✘ / 0 xfail | Pipeline DGE por inicio de síntomas | **sí con cambios** (renombrar su `src/datos.py`) |
| `kind-newton-2qjan7` | `main` 675437f | 1 | 27 | 40 ✔ / 0 ✘ / 0 xfail (6 min 30 s) | F4: `sirmx/`, decisiones, pronóstico | **sí con cambios** (usar `src/sir.py`, `D_olaN`, unir planes) |
| `elegant-pascal-woh4d4` | — | — | — | — | No existe en GitHub | **no** |

### 3.2 Orden recomendado hacia `integracion/pt1`

1. **`sir-covid-mexico-remake`.** Las demás dependen de ella (stoic y
   fervent salen de `e61a3a5`). Trae `src/sir.py`, `Makefile`,
   `environment.yml`, `.gitignore`. Une limpio. Revisar: 30 pruebas pasan.
2. **`stoic-galileo`.** Une limpio. Reemplaza `parametros.yaml` y
   `src/datos.py` por las versiones con validación y `D_olaN`. Debe ir
   **antes** de compassionate (para que `src/datos.py` ya sea "el cargador")
   y antes de kind-newton (para que `D_olaN` exista). Commit aparte después:
   agregar 5, 7, 10 a la sensibilidad de D y resolver `s0_ola1 = 1.0`.
   Revisar: 52 pruebas pasan.
3. **`fervent-dirac`.** Une limpio en git, pero hay que **adaptar
   `tests/teoria/`** a la nueva firma en un commit aparte, y agregar
   `raises=AssertionError` a los dos xfail. Actualizar
   `docs/teoria_verificacion.md` (discrepancia 3 resuelta; 1 y 2 siguen).
   Revisar: 0 fallas, 2 xfail.
4. **`zealous-heisenberg`.** `src/olas.py` → el de zealous; `.gitignore` →
   unir líneas; `README.md` → a mano. Revisar: `tests/test_olas.py` pasa.
5. **`compassionate-dijkstra`.** Renombrar su `src/datos.py` (decisión 3),
   cambiar `from src.datos import` en `src/series_historicas.py` y
   `tests/test_pipeline.py`, y `python -m src.datos` en `Makefile`,
   docstrings y mensajes. Unir los dos `Makefile`. Pasar `requirements.txt`
   a `environment.yml`. Resolver `.gitignore` para `data/processed/`.
   Revisar: toda la suite pasa.
6. **`kind-newton` (F4).** El paso más grande. Al unir: sumar `pytest.ini`
   y `tests/conftest.py`; pasar `requirements.txt` (numba, pytest-xdist) a
   `environment.yml`; **no** dejar dos `docs/plan_analisis.md` (decisión 4).
   Después, en commits aparte: (a) `sirmx` llama a `src/sir.py` (§2.2 c);
   (b) D sale de `D_olaN` (§2.2 d); (c) marcar las pruebas lentas;
   (d) volver a correr `scripts/validacion_sintetica.py` y comparar con
   `docs/validacion_sintetica.md`. Revisar: 40 pruebas de F4 + el resto.

Se une **al final** porque es la que más depende de decisiones tuyas
(§3.4) y la que más se mueve al cambiar el integrador y D.

Forma: `git merge --no-ff` por rama (no rebase), para conservar la historia
de cada sesión, y los ajustes en commits separados después de cada unión.

### 3.3 Cada conflicto: opciones y recomendación

| Conflicto | Opciones | Recomendación |
|---|---|---|
| `src/datos.py` (stoic vs compassionate) | (a) renombrar el de compassionate; (b) renombrar el de stoic a `src/parametros.py`; (c) paquete `src/datos/` | **(a)**: el de compassionate pasa a `src/serie_dge.py`. El de stoic ya lo usan 3 scripts y las pruebas de F0. |
| `src/olas.py` (remake vs zealous) | tomar uno | El de **zealous** (el de remake está vacío). |
| `docs/plan_analisis.md` (remake/stoic vs kind-newton) | (a) quedarse con uno; (b) unir: el de stoic como plan general (H1–H5) y el de F4 como su sección de métodos | **(b)**. El de F4 no cubre H3, H4b ni H5; el de stoic no tiene el detalle de F4. Lo que cambie del plan "congelado" de F4 se registra en `docs/desviaciones.md`. |
| `.gitignore` (4 versiones) | unir todo | Unir todas las líneas. `data/processed/`: ignorar todo **menos** `serie_nacional_sintomas.csv`, `manifiesto.json` y `README.md`. |
| `Makefile` (remake+fervent vs compassionate) | uno o dos | Uno: el de remake + `teoria` + los objetivos de compassionate con `python -m src.serie_dge` + uno para F4 (`validacion`). Un solo `test`. |
| `pytest.ini` (fervent vs kind-newton) | sumar | Un archivo con `pythonpath = .`, `testpaths = tests`, `addopts = -ra --strict-markers`, marcadores `teoria` y `lento`. |
| `tests/conftest.py` (remake vs kind-newton) | sumar | Ambos bloques en un archivo. |
| `README.md` (6 ramas) | a mano | Partir del de remake y agregar una línea por fase. |
| `data/raw/README.md` (remake vs compassionate) | a mano | El de compassionate + lo de hashes de remake. |
| `environment.yml` vs 2 `requirements.txt` | una lista | **`environment.yml`** con todo (incluidos numba y pytest-xdist si se quedan); borrar los `requirements.txt`. |
| `sir.py` vs `sirmx/modelo.py` | dos simuladores o uno | **Uno: `src/sir.py`** (decisión tomada). |
| D = 7 fijo vs `D_olaN` | — | **`D_olaN` con fuente** (decisión tomada); 5, 7, 10 como sensibilidad. |
| Semanal (remake) vs diario + día de la semana (F4) | elegir una | Ver decisión 5 en §3.4. |
| BIC (F4) vs Ljung–Box + AIC (plan) para H2 | elegir uno | Ver decisión 6 en §3.4. |
| `tests/teoria/` vs `sir.py` nuevo | adaptar o volver atrás | Adaptar las pruebas (las 40 que fallan). |
| `s0_ola1 = 1.0` vs `S0 + I0 ≤ N` | cambiar YAML o `sir.py` | Que `sir.py` acepte s0 = 1 con S0 = N − I0. |

### 3.4 Decisiones que necesitas tomar tú

1. **Qué hacer con I2, I3 e I4 inventados.**
   - (a) Borrarlos y esperar el texto real de los issues.
   - (b) Dejarlos en `docs/decisiones.md` marcados "PROVISIONAL — no viene
     del issue real", aceptar las que coinciden (§2.2 e, clase a), corregir
     las que chocan (clase b) y revisar las nuevas (clase c).
   - (c) Aceptarlos tal cual.
   - **Recomendación: (b).** No se pierde el trabajo y queda claro qué tiene
     respaldo. Lo mínimo a corregir: D = 7 → `D_olaN`; N de CONAPO → INEGI.
2. **Si `sirmx/` se queda como paquete aparte o se pasa a `src/`.**
   - (a) Paquete aparte que importa `src.sir`.
   - (b) Pasar sus módulos a `src/` (`src/ajuste.py`, `src/crecimiento.py`,
     `src/cambios.py`, `src/pronostico.py`) y unir las dos verosimilitudes.
   - **Recomendación: (a) por ahora, (b) después.** Primero que `sirmx` use
     `src/sir.py` y pasen sus 40 pruebas; mover archivos al mismo tiempo
     hace difícil saber qué rompió qué.
3. **Cómo resolver los dos `src/datos.py`.**
   - (a) El de compassionate pasa a `src/serie_dge.py`.
   - (b) El de stoic pasa a `src/parametros.py`.
   - (c) Paquete `src/datos/` con `parametros.py` y `dge.py`.
   - **Recomendación: (a).** Es el cambio más chico.
4. **Qué `plan_analisis.md` manda.** (a) El de F4 (congelado); (b) el de
   remake/stoic; (c) unirlos. **Recomendación: (c),** con H1–H5 del de
   stoic y los métodos de F4.
5. **Datos diarios con efecto de día de la semana (F4) o semanales (remake).**
   - (a) Diarios: más datos, 6 parámetros más, necesario para el r de 21 días.
   - (b) Semanales: más simple, quita el ciclo sin parámetros.
   - **Recomendación: (a)** para el ajuste principal (F4 ya lo validó) y
     (b) como sensibilidad. Con fecha de síntomas (DGE) revisar si el ciclo
     semanal sigue presente.
6. **Criterio para H2:** BIC + residuos de Pearson (F4) o Ljung–Box + AIC
   (plan). **Recomendación:** usar el del plan como criterio de decisión de
   H2 y el BIC de F4 solo para elegir K, porque el plan se escribió antes.
7. **Serología en el ajuste.** remake la usa; F4 no. **Recomendación:**
   mantenerla como en el plan (es lo que permite H3 y cerrar la cresta en
   la ola 1).
8. **Rango de sensibilidad de D.** stoic 4–7 / 3–7; F4 y tú {5, 7, 10}.
   **Recomendación:** {5, 7, 10} en todas las olas, más el rango por
   variante de stoic.
9. **Fuente de casos para las olas:** JHU (reporte) o DGE (síntomas).
   **Recomendación:** rehacer las olas con DGE cuando haya microdatos; JHU
   como sensibilidad.
10. **La frontera 2020-10-01 (decisión posterior).** **Recomendación:**
    olas 1 y 2 separadas como principal, unidas como sensibilidad, y
    declararlo en el escrito.
11. **Los 2 xfail.** **Recomendación:** corregir el de incidencia
    (integrar la incidencia acumulada como variable extra) porque afecta la
    verosimilitud si i0 es muy chico; aceptar y documentar el de LSODA.
12. **Velocidad.** ¿Se acepta que las pruebas de F4 tarden mucho más con
    LSODA? **Recomendación:** sí, marcándolas como `lento` y corriéndolas
    aparte (`make test-lento`).
13. **`exp(rD)` en el PT1 viejo.** ¿Qué fórmula se usó en la Tabla 4.1? Solo
    tú puedes confirmarlo con el PDF/código original.

### 3.5 Lo que solo tú puedes hacer

1. **Etiquetas `v0.0` (commit `8fc89d6`) y `v0.0-infra` (commit
   `e61a3a5`).** Los commits existen en GitHub (en `sir-covid-mexico-remake`,
   `stoic-galileo` y `fervent-dirac`), pero no hay ninguna etiqueta en el
   remoto. Desde tu clon:

   ```bash
   git tag -a v0.0 8fc89d6 -m "F0: alcance, reglas, estructura"
   git tag -a v0.0-infra e61a3a5 -m "Infraestructura"
   git push origin v0.0 v0.0-infra
   ```
2. **Subir `PT1_bibliografia_v2.xlsx`.** stoic lo cita como origen de
   `parametros.yaml`, pero no está en ninguna rama. Sin él, casi todos los
   valores reales (incluidos los `D_olaN`) quedan en `null`.
3. **Bajar los microdatos de la DGE** a `data/raw/dge/` y registrarlos con
   `scripts/registrar_fuente.py` (rama compassionate). Pesan GB.
4. **Verificar N = 126 014 024** en el tabulado del Censo 2020 de INEGI y
   anotar la ubicación exacta.
5. Conseguir el **texto real de los issues I2, I3 e I4** y compararlo con
   `docs/decisiones.md`.
6. Confirmar si `elegant-pascal-woh4d4` tenía trabajo y subirlo si existe.

### 3.6 Riesgos por paso

| Paso | Qué se puede romper |
|---|---|
| 1. remake | Poco. Borra `.DS_Store`. Cambia el `README.md` de portafolio. |
| 2. stoic | Su `src/datos.py` es más estricto: un parámetro sin fuente hace tronar `correr_sintetico.py` (a propósito). Conviene regenerar `reports/` y ver que no cambie. |
| 3. fervent | 40 pruebas fallan hasta adaptar la firma. Si se adaptan mal, se pierde lo que verifican. Los xfail sin `raises=` esconden errores. |
| 4. zealous | Tomar el `src/olas.py` equivocado deja las olas sin código. Trae datos en `data/` y resultados en `resultados/` (otra carpeta además de `reports/`). `olas.py --descargar` necesita red. |
| 5. compassionate | Renombrar `src/datos.py` rompe `series_historicas.py`, `test_pipeline.py`, el `Makefile` y el manifiesto (guarda `"src/datos.py"` en `codigo_sha256`): cambian los hashes. Un `.gitignore` mal escrito puede meter GB de crudos. |
| 6. kind-newton | Cambiar RK4 + numba por LSODA hace todo ~100 veces más lento: `make test` puede pasar de minutos a horas. Los escenarios con s0 = 1 truenan en `src/sir.py`. Cambiar D = 7 por `D_olaN` cambia los números de F4 (y `D_olaN` hoy está en `null`, así que nada corre con datos reales hasta tener el xlsx). Unir los dos planes puede "descongelar" el de F4: registrar todo en `desviaciones.md`. `--strict-markers` + marcadores nuevos. `multiprocessing` con `spawn` + `conftest.py` que toca variables de entorno. |

---

## Anexo: comandos usados (todos de solo lectura o temporales)

- `git fetch --all --prune`; `git ls-remote --heads --tags origin`; API de
  GitHub `list_branches`. Segundo `git ls-remote` al final: apareció
  `claude/kind-newton-2qjan7`.
- `git log --all -- sirmx/` (antes de que apareciera kind-newton: vacío).
- `git merge-base`, `git log base..rama`, `git diff --stat base rama`.
- `git merge-tree --write-tree` por pares y en cadena (objetos sueltos, sin
  ramas ni refs).
- `git worktree add --detach /tmp/wt-<rama>` + `pytest -q` (kind-newton:
  `OPENBLAS_NUM_THREADS=1 pytest -n 4`); después `git worktree remove`.
- `tests/teoria/` de fervent copiado sobre remake en un worktree temporal;
  los 2 xfail con `--runxfail` y con un adaptador a la nueva firma.
- Tiempos y diferencia RK4 vs LSODA medidos con un script temporal fuera
  del repositorio.
