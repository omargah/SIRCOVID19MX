# Inventario de ramas y plan de integración — PT1

Fecha de la revisión: 2026-11-04. Repositorio: `omargah/SIRCOVID19MX`.

Este documento es **solo un inventario y una propuesta**. No se unió ninguna
rama. Las pruebas de unión se hicieron en seco (`git merge-tree`, objetos
sueltos sin rama) y las pruebas de código en worktrees temporales que ya se
borraron.

Cómo se corrieron las pruebas: Python 3 con numpy 2.5.4, scipy 1.18.1,
sympy 1.14.0, pandas 3.1.0, pyyaml y pytest, en un entorno virtual aparte
(no se usó `make env`).

---

## 0. Ramas que existen en GitHub

`git fetch --all --prune` y la API de GitHub dan las mismas **6 ramas**. El
clon no es superficial. No hay etiquetas en el remoto.

| Rama | Último commit | Fecha (UTC) | Autor |
|---|---|---|---|
| `main` | `675437f` Agregar contacto de Facultad de Medicina-UNAM | 2026-10-27 | Omar García Hernández |
| `claude/sir-covid-mexico-remake-834hzi` | `f9745f7` sir.py: SIR en personas, β por tramos y pruebas (a)–(g) | 2026-11-04 01:00 | Claude |
| `claude/zealous-heisenberg-d3q5dk` | `fa6cfa1` separar ola 1 y 2 con frontera por mínimo de media móvil | 2026-11-04 01:00 | Claude |
| `claude/compassionate-dijkstra-hoccgu` | `726f3e6` F3: pipeline de datos DGE | 2026-11-04 00:45 | Claude |
| `claude/fervent-dirac-ud7ob4` | `015c40a` F2: verificación SymPy + sir.py de las derivaciones a–k | 2026-11-04 00:43 | Claude |
| `claude/stoic-galileo-qsf1n6` | `302ed4b` F1: parametros.yaml con fuente obligatoria o supuesto | 2026-11-04 00:36 | Claude |

**Ramas que NO están en GitHub:**

- `claude/elegant-pascal-woh4d4`: **no existe** en el remoto. O la sesión no
  hizo nada, o no subió su trabajo. No se puede saber desde aquí.
- **La rama de la validación sintética F4** (paquete `sirmx/`,
  `docs/decisiones.md`, `scripts/validacion_sintetica.py`,
  `sirmx/pronostico.py`): **no está en GitHub.** `git log --all -- sirmx/`,
  `git log --all -- docs/decisiones.md` y
  `git log --all -- scripts/validacion_sintetica.py` no devuelven nada, y la
  búsqueda de commits y de código en GitHub con "sirmx" da 0 resultados.
  Lo más probable es que esa sesión no haya hecho `push`. Quizá sea la misma
  sesión de `elegant-pascal` (no verificado). **Todo lo que este documento
  dice sobre `sirmx/` y `docs/decisiones.md` sale de la descripción de la
  tarea, no del código: queda como "no verificado".**

Nota: el commit `8fc89d6` de `sir-covid-mexico-remake` ya trae una
"validación sintética de H1" (`scripts/correr_sintetico.py`,
`src/verosimilitud.py`, `src/identificabilidad.py`). Esa sí está en GitHub,
pero **no** es el paquete `sirmx/`.

### Árbol de dependencias

```
main 675437f
 ├── sir-covid-mexico-remake:  8fc89d6 (F0) ── e61a3a5 (infra) ── f9745f7 (sir.py nuevo)
 │                                               ├── stoic-galileo:  302ed4b (F1 parámetros)
 │                                               └── fervent-dirac:  015c40a (F2 teoría a–k)
 ├── zealous-heisenberg:  f2ef6ee ─ 86cac48 ─ bd237d1 ─ 2564c37 ─ 550ab3a ─ fa6cfa1 (olas)
 └── compassionate-dijkstra:  726f3e6 (F3 pipeline DGE)
```

`stoic-galileo` y `fervent-dirac` salen de `e61a3a5`, **antes** del último
commit de `sir-covid-mexico-remake` (`f9745f7`), que cambió `src/sir.py`.
`zealous-heisenberg` y `compassionate-dijkstra` salen directo de `main` y no
conocen la infraestructura de F0.

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
  `integrar_sir_tramos` con β por tramos, `R0 = (1 + rD)/s0`). También trae
  verosimilitud binomial negativa + serología y el experimento de
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
  en fracciones: `integrar_sir(R0, gamma, s0, i0, t) -> (s, i)`). Ver §2.1.

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

### 1.6 `main`

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

**En cadena** (`main` → remake → stoic → fervent → zealous → compassionate):
los tres primeros pasos son limpios; zealous da conflicto en `.gitignore`,
`README.md`, `src/olas.py`; compassionate da conflicto en `.gitignore`,
`Makefile`, `README.md`, `data/raw/README.md`, `src/datos.py`.

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
- **`README.md`:** lo modifican las 5 ramas. Conflicto de texto con
  zealous y compassionate; con stoic y fervent git une solo.
- **`Makefile`:** remake lo crea; fervent le agrega `teoria` (une limpio);
  compassionate crea **otro** `Makefile` con objetivos `serie`, `eda`,
  `comparar`, etc. y su propio `test`.
- **`pytest.ini`:** solo lo crea fervent. Sin conflicto de git. Pero
  `--strict-markers` hará fallar cualquier marcador no declarado que traigan
  otras ramas (hoy ninguna usa marcadores; no verificado para `sirmx/`).
- **`environment.yml`:** solo en remake. compassionate trae
  `requirements.txt` (numpy, pandas, matplotlib, pytest). Son dos listas de
  dependencias; remake dice explícitamente que debe haber una sola.
- **`.gitignore`:** tres versiones. Además del conflicto de texto, hay un
  **choque de criterio**: remake ignora todo `data/processed/*`;
  compassionate quiere versionar `data/processed/serie_nacional_sintomas.csv`
  y `manifiesto.json`.
- **`bibliografia/INDICE.csv`:** solo zealous lo toca (agrega `H04`). Sin
  conflicto. stoic valida que las claves de `fuente_candidata` (`G01, G02,
  G05, G06, I01, I03`) existan en este archivo: ya existen en `main`.
- **`src/olas.py`:** remake trae un esqueleto vacío (docstring de 6 líneas);
  zealous trae la implementación. Se resuelve tomando la de zealous.
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

La unión remake + stoic + fervent (sin zealous ni compassionate) da
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

`sirmx/` **no está en GitHub**, así que no se pudo comparar línea por línea.
Lo que sigue es lo que **sí** se verificó de `src/sir.py`, y lo que habría
que revisar en `sirmx/` cuando se suba (**no verificado**):

| Punto | `src/sir.py` (verificado) | `sirmx/` (según la tarea; no verificado) |
|---|---|---|
| Ecuaciones | dS/dt = −βSI/N, dI/dt = βSI/N − γI, dR/dt = γI, en personas | SIR (forma exacta no verificada) |
| Parametrización | β = R0·γ, γ = 1/D (`tasas(R0, D)`) | revisar si usa la misma |
| Integrador | LSODA de scipy en (S, ln I, R), `rtol=1e-10`, `atol` relativa a N | RK4 propio con paso fijo y numba |
| β variable | `integrar_sir_tramos`: reinicia en cada cambio | "puntos de cambio" (implementación no verificada) |
| Incidencia | ρ·[S(t_k) − S(t_{k+1})] por semana, recortada a ≥ 0 | revisar |
| r → R | `R0 = (1 + rD)/s0` | revisar |
| Estado inicial | exige S0 > 0, I0 > 0 y S0 + I0 ≤ N | revisar |

Qué tendría que cambiar en `sirmx/` para usar `src/sir.py` por dentro, sin
perder lo que aporta:

1. Quitar el RK4 propio y llamar a `src.sir.integrar_sir_tramos` (o a
   `integrar_sir` si no hay cambios de β). Los puntos de cambio de `sirmx`
   pasan a ser `t_cambios` y los R0 por tramo a `R0_tramos`.
2. Pasar de lo que use `sirmx` a la firma `(R0, D, S0, I0, N, t)` en
   personas. γ no se pasa: se deriva de D.
3. Calcular la incidencia con `src.sir.incidencia_semanal` (o con la misma
   regla, diferencia de S) para que la verosimilitud de `sirmx` vea los
   mismos μ_k que `src/verosimilitud.py`.
4. Conservar de `sirmx`: la verosimilitud (comparar con
   `src/verosimilitud.py`, que ya tiene binomial negativa + serología, y
   quedarse con una sola), el ajuste multi-inicio, la detección de puntos de
   cambio y `pronostico.py`, pero todos llamando al integrador oficial.
5. Leer D de `config/parametros.yaml` (`D_olaN`), no de una constante.
6. Quitar numba del camino del integrador (scipy no se compila con numba).

**Velocidad (medido con `src/sir.py`):** una llamada a `incidencia_semanal`
tarda **~2 ms** (30 semanas, R0 = 2.5), **~4 ms** (60 semanas o R0 = 15);
`integrar_sir_tramos` con 3 tramos y 43 semanas, **~3 ms**. Un ajuste
multi-inicio de, digamos, 20 inicios × 500 evaluaciones son ~10 000
llamadas ≈ **20–40 s por ola**. Con bootstrap de 200 réplicas eso sube a
**1–2 h por ola**. Lo que puede ser lento: bootstrap, perfiles de
verosimilitud, búsqueda de puntos de cambio (muchas combinaciones de `τ`) y
el pronóstico por simulación. RK4 con numba suele ser 10–100 veces más
rápido (estimación, no medido). Si hace falta velocidad: paralelizar los
inicios y las réplicas, o aflojar `rtol` solo en la exploración y refinar
el mejor punto con la tolerancia oficial.

#### d) D por ola

**Decisión ya tomada: D por ola con fuente (`D_olaN` en `parametros.yaml`).
D = 5, 7 y 10 solo como sensibilidad.**

Dónde choca con lo que hay en GitHub (verificado):

| Lugar | Qué dice | ¿Choca? |
|---|---|---|
| `stoic-galileo: config/parametros.yaml` | `D_ola1`…`D_ola5` con `intervalo_generacion`, valores en `null`, `sensibilidad` 4–7 (olas 1–3) y 3–7 (olas 4–5) | **Coincide** con la decisión. **Choca** en el rango: 10 queda fuera de todos los rangos. |
| `remake: config/parametros.yaml` (sección `real`) | un solo `gamma` para todas las olas | **Choca.** stoic lo reemplaza; al unir stoic se arregla. |
| `remake: docs/plan_analisis.md` | "γ fijo… Fijos con fuente: γ, N" | Choca en redacción; stoic ya lo cambia a "γ = 1/D por ola". |
| `remake` y `stoic`: sección `sintetico` | `gamma = 1/7` | No choca: es la "verdad" del experimento sintético, no un valor de México. |
| `remake: tests/test_sir.py` (f) | D = 7 para BA.1 | No choca: reproduce el error del código viejo. |
| `fervent: tests/teoria/` | γ = 1/7 y 1/5 en ejemplos | No choca: son pruebas de teoría. |
| `zealous`, `compassionate` | no usan D | — |
| `sirmx/` y `docs/decisiones.md` | D = 7 en todas las olas (según la tarea) | **Choca** (no verificado línea por línea: el código no está en GitHub). Revisar al subirlo: toda constante `D = 7`, `gamma = 1/7` o equivalente en `sirmx/`, `scripts/validacion_sintetica.py` y `pronostico.py`. |

#### e) I2, I3 e I4 inventados (`docs/decisiones.md`)

`docs/decisiones.md` **no está en GitHub**: no se pudo leer. Por lo tanto
**no se puede clasificar** cada decisión (D0, I2, I3, I4). Estado de las
cuatro: **no verificado**.

Lo único que sí se puede decir con lo que diste en la tarea:

| Decisión | Clasificación | Con qué rama y en qué |
|---|---|---|
| D0 (D = 7 para todas las olas) | **(b) choca** — basado solo en tu descripción | stoic-galileo (`D_olaN` por ola, con fuente) y la decisión ya tomada |
| I2 | no verificado | — |
| I3 | no verificado | — |
| I4 | no verificado | — |

Cuando se suba el archivo, compararlo contra: `docs/actas/F0-alcance.md` y
`docs/plan_analisis.md` (remake), `config/parametros.yaml` (stoic),
`docs/regla_olas.md` (zealous) y `docs/diccionario_datos.md`
(compassionate).

#### f) Relación r → R

Verificado con `git grep` en las 5 ramas (sin `v0-anterior/`):

- **Ninguna rama usa `exp(rD)` como fórmula.** Solo aparece en comentarios
  y en pruebas que muestran que es incorrecta.
- `remake`: `R0_desde_tasa_crecimiento = (1 + r*D)/s0` y la prueba (f).
- `fervent`: prueba (g) a favor de `1 + rD`.
- `stoic`: lo dice en el comentario del YAML (`R0 = 1 + r*Tg`).
- `zealous` y `compassionate`: no calculan R.
- **Discrepancia entre ramas sobre el código viejo:** remake dice que el PT1
  viejo usaba `exp(rD)` (BA.1: 4.28 vs ~2.94, tomado de una captura en PDF);
  fervent dice que el código viejo (`v0-anterior/analisis_montecarlo.py`)
  usa `1 + rD`. El `.py` de `main` efectivamente dice
  `R0 = (1 + growth * D) / S0`. Lo de la captura en PDF **no se verificó**.
  Puede que ambas tengan razón (el PDF y el `.py` serían versiones
  distintas). Hay que aclararlo en el texto del Cap. 2.

#### g) Las olas

- Las fechas de zealous (`resultados/olas/A1_frontera/olas.csv`) son las 5
  de la tarea: 2020-02-27, 2020-10-01, 2021-05-16, 2021-12-10, 2022-04-25;
  fin 2023-02-28.
- Ninguna otra rama en GitHub fija fechas de olas. `stoic` solo nombra
  ola1…ola5 por variante y dice que la delimitación la da `src/olas.py`.
  `compassionate` solo usa el rango del tablero (2020-02-26 a 2023-06-24) y
  el pico del PT1 viejo (2022-01-15), no fechas de olas.
- F4 (`sirmx/`): **no verificado** (no está en GitHub).
- Ojo: la frontera 2020-10-01 está marcada por zealous como "criterio
  externo… tomado después de ver el resultado de la regla principal". Es una
  decisión posterior y hay que declararla así en el escrito.

#### h) Fuente de casos (pendiente)

- Olas: **JHU CSSE por fecha de reporte** (contraste con DGE por fecha de
  ingreso, que solo llega a 2022-01-20).
- Pipeline: **DGE por fecha de inicio de síntomas**.
- Las fechas de las olas pueden moverse días o semanas al cambiar de fuente.
  **Pendiente:** volver a correr `src/olas.py` con la serie de
  `compassionate` cuando existan los microdatos, y decidir cuál manda.

#### i) Otros hallazgos

1. **`s0_ola1 = 1.0` no se puede simular.** `stoic` fija `s0_ola1 = 1.0`
   ("S0 = N"), pero `src/sir.py` exige `S0 + I0 ≤ N` y truena con s0 = 1.
   Peor: con `s0 = 1 − i0` también truena por redondeo
   (`s0*N + i0*N` queda un poco arriba de N). Arreglo: definir S0 = N − I0
   dentro de `sir.py` o tolerar un error de redondeo relativo.
2. **`tests/__init__.py`** (compassionate) junto con `tests/conftest.py`
   (remake) cambia cómo pytest importa los módulos de prueba. Hoy no hay
   nombres repetidos, pero hay que correr toda la suite tras unir.
3. **pandas 4:** `src/eda.py` usa `Series.dt.weekday`, que se va a quitar.
4. **`docs/plan_analisis.md` (remake)** todavía dice "Estado: s, i (r por
   conservación)", que ya no es cierto con el `sir.py` nuevo.

---

## 3. Plan de integración (propuesta, NO ejecutada)

### 3.1 Tabla resumen

| Rama | Base | Commits propios | Archivos | Pruebas | Aporte | ¿Se une? |
|---|---|---|---|---|---|---|
| `sir-covid-mexico-remake-834hzi` | `main` 675437f | 3 | 36 | 30 ✔ / 0 ✘ / 0 xfail | Infraestructura, `src/sir.py` oficial, verosimilitud, H1 sintético | **sí** |
| `stoic-galileo-qsf1n6` | `e61a3a5` (remake) | 1 | 5 | 45 ✔ / 0 ✘ / 0 xfail | `parametros.yaml` con fuente obligatoria, `D_olaN`, cargador | **sí con cambios** (rango de D incluye 10; `s0_ola1`) |
| `fervent-dirac-ud7ob4` | `e61a3a5` (remake) | 1 | 16 | 110 ✔ / 0 ✘ / 2 xfail (en su rama); 47 ✔ / 40 ✘ / 2 xfail contra `sir.py` actual | Teoría a–k verificada con SymPy | **sí con cambios** (adaptar a la nueva firma) |
| `zealous-heisenberg-d3q5dk` | `main` 675437f | 6 | 31 | 5 ✔ / 0 ✘ / 0 xfail | Regla de olas, A1, frontera 2020-10-01, 5 olas | **sí con cambios** (resolver 3 conflictos) |
| `compassionate-dijkstra-hoccgu` | `main` 675437f | 1 | 25 | 8 ✔ / 0 ✘ / 0 xfail | Pipeline DGE por inicio de síntomas, comparación con tablero, EDA | **sí con cambios** (renombrar su `src/datos.py`, unir `Makefile`) |
| `elegant-pascal-woh4d4` | — | — | — | — | No existe en GitHub | **no** (nada que unir) |
| Rama F4 (`sirmx/`) | no verificado | no verificado | no verificado | no verificado | Validación sintética, pronóstico (según la tarea) | **no por ahora** (no está en GitHub); después, **sí con cambios** |

### 3.2 Orden recomendado hacia `integracion/pt1`

1. **`sir-covid-mexico-remake`.** Las demás dependen de ella (stoic y
   fervent salen de su commit `e61a3a5`). Trae `src/sir.py` oficial,
   `Makefile`, `environment.yml` y `.gitignore`. Une limpio con `main`.
   Revisar: 30 pruebas pasan.
2. **`stoic-galileo`.** Une limpio. Reemplaza el `parametros.yaml` y el
   `src/datos.py` de remake por las versiones con validación y `D_olaN`.
   Debe ir **antes** de compassionate, para que `src/datos.py` ya sea "el
   cargador" cuando llegue el otro. En el mismo paso (commit aparte):
   agregar D = 5, 7, 10 a la sensibilidad y resolver `s0_ola1 = 1.0`.
   Revisar: 52 pruebas pasan.
3. **`fervent-dirac`.** Une limpio en git, pero hay que **adaptar
   `tests/teoria/`** a `integrar_sir(R0, D, S0, I0, N, t) -> (S, I, R)` en un
   commit aparte, y agregar `raises=AssertionError` a los dos xfail para que
   no "pasen" por un `TypeError`. Actualizar `docs/teoria_verificacion.md`
   (discrepancia 3 resuelta; 1 y 2 siguen, con 1.5e-9 y 3.2 %).
   Revisar: 0 fallas, 2 xfail.
4. **`zealous-heisenberg`.** Conflictos: `src/olas.py` → tomar el de
   zealous; `.gitignore` → unir líneas; `README.md` → a mano.
   Revisar: `tests/test_olas.py` pasa y `resultados/olas/` no cambia.
5. **`compassionate-dijkstra`.** El paso más delicado. Antes de unir (o en
   el commit de unión): renombrar su `src/datos.py` (ver decisión 3),
   cambiar `from src.datos import` en `src/series_historicas.py`,
   `tests/test_pipeline.py` y `python -m src.datos` en `Makefile`,
   docstrings y mensajes. Unir los dos `Makefile` en uno. Pasar
   `requirements.txt` a `environment.yml`. Resolver el criterio de
   `.gitignore` para `data/processed/`. Unir `data/raw/README.md`.
   Revisar: toda la suite pasa.
6. **F4 (`sirmx/`)**, cuando esté en GitHub. Primero leer
   `docs/decisiones.md` y clasificar D0–I4; luego hacer que `sirmx/` use
   `src/sir.py` y `D_olaN` (ver §2.2 c y d).

Recomendación de forma: usar `git merge --no-ff` por rama (no rebase), para
conservar la historia de cada sesión, y poner los ajustes en commits
separados después de cada unión.

### 3.3 Cada conflicto: opciones y recomendación

| Conflicto | Opciones | Recomendación |
|---|---|---|
| `src/datos.py` (stoic vs compassionate) | (a) renombrar el de compassionate; (b) renombrar el de stoic a `src/parametros.py`; (c) hacer un paquete `src/datos/` con dos módulos | **(a)**: renombrar el de compassionate a `src/serie_dge.py`. El de stoic ya lo usan 3 scripts y las pruebas de F0; el de compassionate tiene menos usuarios. |
| `src/olas.py` (remake vs zealous) | tomar uno | Tomar el de **zealous** (el de remake está vacío). |
| `.gitignore` (3 versiones) | unir todo | Unir todas las líneas. Para `data/processed/`: ignorar todo **menos** `serie_nacional_sintomas.csv`, `manifiesto.json` y `README.md`. |
| `Makefile` (remake+fervent vs compassionate) | uno solo o dos | Uno solo: el de remake + `teoria` + los objetivos de compassionate (`serie`, `determinismo`, `comparar`, `eda`, `inventario`, `fuentes`) con `python -m src.serie_dge`. Un solo `test`. |
| `README.md` (5 ramas) | a mano | Partir del de remake y agregar una línea por fase (F1, F2, F3 olas, F3 datos). |
| `data/raw/README.md` (remake vs compassionate) | a mano | Tomar el de compassionate (más completo) y agregar lo de hashes de remake. |
| `environment.yml` vs `requirements.txt` | dos listas o una | Una: **`environment.yml`**; borrar `requirements.txt`. |
| `sir.py` vs `sirmx/` | dos simuladores o uno | **Uno: `src/sir.py`** (decisión tomada). `sirmx/` lo llama por dentro. |
| D = 7 fijo vs `D_olaN` | — | **`D_olaN` con fuente** (decisión tomada); 5, 7, 10 como sensibilidad. |
| `tests/teoria/` vs `sir.py` nuevo | adaptar pruebas o volver a la API vieja | Adaptar las pruebas (las 40 que fallan). |
| `s0_ola1 = 1.0` vs `S0 + I0 ≤ N` | cambiar el YAML o `sir.py` | Que `sir.py` acepte s0 = 1 usando S0 = N − I0. |

### 3.4 Decisiones que necesitas tomar tú

1. **Qué hacer con I2, I3 e I4 inventados.**
   - (a) Borrarlos y esperar el texto real de los issues.
   - (b) Dejarlos en `docs/decisiones.md` marcados "PROVISIONAL — no viene
     del issue real" y revisarlos cuando tengas el texto.
   - (c) Aceptarlos como decisiones propias.
   - **Recomendación: (b).** No se pierde el trabajo, pero queda claro que
     no tienen respaldo. Antes, sube la rama para poder revisarlos.
2. **Si `sirmx/` se queda como paquete aparte o se pasa a `src/`.**
   - (a) Paquete aparte que importa `src.sir`.
   - (b) Pasar sus módulos a `src/` (`src/ajuste.py`, `src/pronostico.py`,
     `src/puntos_cambio.py`).
   - **Recomendación: (b).** Un solo paquete evita dos formas de importar y
     dos lugares donde buscar. Además ya existe `src/verosimilitud.py`: hay
     que quedarse con una sola verosimilitud.
3. **Cómo resolver los dos `src/datos.py`.**
   - (a) El de compassionate pasa a `src/serie_dge.py`.
   - (b) El de stoic pasa a `src/parametros.py`.
   - (c) Paquete `src/datos/` con `parametros.py` y `dge.py`.
   - **Recomendación: (a).** Es el cambio más chico.
4. **Rango de sensibilidad de D.** stoic usa 4–7 / 3–7; tú quieres 5, 7, 10.
   - (a) Cambiar a `{valores: [5, 7, 10]}` para todas las olas.
   - (b) Dejar los rangos por variante y agregar 5, 7, 10 como escenarios
     extra.
   - **Recomendación: (b).** Los rangos por variante tienen sentido
     biológico; 5/7/10 permite comparar con el PT1 viejo.
5. **Fuente de casos para las olas: JHU (reporte) o DGE (síntomas).**
   - (a) Quedarse con JHU para las olas y DGE para el ajuste.
   - (b) Rehacer las olas con DGE cuando haya microdatos.
   - **Recomendación: (b),** con JHU como sensibilidad. La regla está
     declarada, así que se puede volver a aplicar sin cambiarla.
6. **La frontera 2020-10-01 (decisión posterior).** ¿Se acepta como olas 1
   y 2 separadas o se reporta la ola 1+2 unida como análisis principal?
   **Recomendación:** separadas como principal (es lo convencional) y unidas
   como sensibilidad, declarando en el escrito que la frontera se fijó
   después.
7. **Los 2 xfail.** ¿Se corrigen o se aceptan?
   **Recomendación:** corregir el de incidencia (integrar la incidencia
   acumulada como cuarta variable) porque afecta la verosimilitud si i0 es
   muy chico; aceptar el de LSODA (no afecta con los valores del proyecto,
   3.5e-10 con R0 = 2.5) y documentarlo.
8. **`exp(rD)` en el PT1 viejo.** ¿Cuál fue la fórmula que se usó para la
   Tabla 4.1? Solo tú puedes confirmarlo con el PDF/código original.

### 3.5 Lo que solo tú puedes hacer

1. **Etiquetas `v0.0` (commit `8fc89d6`) y `v0.0-infra` (commit
   `e61a3a5`).** Los commits existen en GitHub (están en
   `sir-covid-mexico-remake`, `stoic-galileo` y `fervent-dirac`), pero
   las etiquetas no se subieron: no hay ninguna etiqueta en el remoto. Desde
   tu clon:

   ```bash
   git tag -a v0.0 8fc89d6 -m "F0: alcance, reglas, estructura"
   git tag -a v0.0-infra e61a3a5 -m "Infraestructura"
   git push origin v0.0 v0.0-infra
   ```
2. **Subir `PT1_bibliografia_v2.xlsx`.** stoic lo cita como origen de
   `parametros.yaml`, pero no está en ninguna rama. Sin él, casi todos los
   valores reales quedan en `null`.
3. **Bajar los microdatos de la DGE** a `data/raw/dge/` y registrarlos con
   `scripts/registrar_fuente.py` (rama compassionate). Pesan GB.
4. **Verificar N = 126 014 024** en el tabulado del Censo 2020 de INEGI y
   anotar la ubicación exacta (stoic ya lo marca como fuente institucional,
   pero nadie lo comprobó contra el tabulado).
5. **Subir la rama de F4 (`sirmx/`)** y, si existe, la de `elegant-pascal`,
   desde la sesión o máquina donde se hicieron.
6. Conseguir el **texto real de los issues I2, I3 e I4**.

### 3.6 Riesgos por paso

| Paso | Qué se puede romper |
|---|---|
| 1. remake | Poco. Borra `.DS_Store` de `main`. Cambia el `README.md` de portafolio. |
| 2. stoic | Su `src/datos.py` es más estricto: si alguien agrega un parámetro sin fuente, `correr_sintetico.py` truena (es a propósito). Los resultados sintéticos (`reports/`) se generaron con el `sir.py` nuevo en remake; stoic no los cambia, pero conviene regenerarlos y ver que no se muevan. |
| 3. fervent | 40 pruebas fallan hasta adaptar la firma. Si se adaptan mal, se pierde lo que verifican. `--strict-markers` puede romper pruebas futuras con marcadores no declarados. Los xfail sin `raises=` esconden errores. |
| 4. zealous | Tomar el `src/olas.py` equivocado deja las olas sin código. Trae datos (`data/*.csv`) y resultados en la raíz de `data/` y en `resultados/` (otra carpeta además de `reports/`): estructura duplicada. `olas.py --descargar` necesita red. |
| 5. compassionate | Renombrar `src/datos.py` rompe `series_historicas.py`, `test_pipeline.py`, el `Makefile` y el manifiesto (guarda `"src/datos.py"` como nombre en `codigo_sha256`): los hashes de salida cambian. `tests/__init__.py` cambia cómo pytest importa. El `.gitignore` puede dejar fuera la serie que se quería versionar, o meter GB de crudos si se escribe mal. |
| 6. F4 / sirmx | Cambiar RK4 + numba por LSODA puede hacer el ajuste 10–100 veces más lento (estimación). Cambiar D = 7 por `D_olaN` cambia todos los números de F4. I2–I4 pueden contradecir decisiones de otras ramas. |

---

## Anexo: comandos usados (todos de solo lectura o temporales)

- `git fetch --all --prune`; `git ls-remote --heads --tags origin`; API de
  GitHub `list_branches`.
- `git log --all -- sirmx/` (y los demás archivos de F4): sin resultados.
- `git merge-base`, `git log base..rama`, `git diff --stat base rama`.
- `git merge-tree --write-tree` por pares y en cadena (objetos sueltos, sin
  ramas ni refs).
- `git worktree add --detach /tmp/wt-<rama>` + `pytest -q`; después
  `git worktree remove`.
- `tests/teoria/` de fervent copiado sobre remake en un worktree temporal;
  los 2 xfail con `--runxfail` y con un adaptador a la nueva firma.
