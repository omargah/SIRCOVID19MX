# Pendientes de la integración (rama `integracion/pt1-v2`)

Aquí está todo lo que apareció al unir las ramas y que **no se decidió**.
Cada entrada dice dónde está el problema, qué opciones hay y qué se
recomienda. Quien decide es Omar. Este archivo se va llenando paso a paso;
la lista completa y ordenada queda al cerrar la integración.

---

## P-A. Hay dos reglas de olas distintas, las dos en `src/`

**Dónde.** Al unir `zealous-heisenberg` chocaron `src/olas.py` y
`tests/test_olas.py`. El inventario decía que el de la rama de partida era un
esqueleto vacío. No es cierto: ya tenía 132 líneas, con otra regla.

| | Regla de la rama de partida | Regla de zealous |
|---|---|---|
| Archivo | `src/olas_provisional.py` (antes `src/olas.py`) | `src/olas.py` |
| Pruebas | `tests/test_olas_provisional.py` (6) | `tests/test_olas.py` (5) |
| Método | media móvil de 7 días centrada; mínimos con prominencia ≥ 10 % del máximo global; separación ≥ 60 días; frontera = domingo de la semana epidemiológica | regla R1–R7 de `docs/regla_olas.md`, enmienda A1 y frontera 1.ª/2.ª ola (2020-10-01) |
| Resultados | ninguno sobre datos reales | `resultados/olas/` (5 olas) |

**Qué se hizo (lo menos destructivo).** Se conservaron las dos. La de zealous
quedó como `src/olas.py` porque es la que documentan `docs/regla_olas.md` y
`docs/olas_resultados.md` y la que produjo `resultados/olas/`. La otra se
movió **sin cambiar su lógica** a `src/olas_provisional.py`; solo cambió la
línea de importación de su prueba. Nadie más la importaba.

**Opciones.** (a) quedarse solo con la de zealous y archivar la otra;
(b) quedarse con la provisional (usa semanas epidemiológicas, que es lo que
pide la verosimilitud semanal); (c) unirlas.

**Recomendación.** (a), pero solo después de comprobar que la regla de zealous
da fronteras en domingo (la verosimilitud es semanal). Es decisión de Omar.

## P-B. Olas con JHU o con DGE

**Dónde.** `src/olas.py` y `resultados/olas/` usan **JHU CSSE**, que cuenta
por **fecha de reporte**. El pipeline de datos (`compassionate-dijkstra`) usa
microdatos **DGE por fecha de inicio de síntomas**. No se decidió cuál manda.

**Opciones.** (a) olas con JHU y dejar el pipeline para el ajuste;
(b) rehacer las olas con la serie DGE y dejar JHU como sensibilidad.

**Recomendación.** (b) cuando existan los microdatos. Las fechas de las olas
podrían moverse unos días porque la fecha de síntomas va antes que la de
reporte. Hasta entonces las olas son provisionales. En este paso no se
cambió ρ, la ventana de suavizado ni la frontera 2020-10-01.

## P-C. Qué se versiona de `data/processed/`

**Dónde.** `.gitignore`. La rama de integración ignoraba todo
`data/processed/*` (salvo su README). `compassionate-dijkstra` quiere
versionar la serie principal, el manifiesto y las series de
hospitalizaciones/defunciones, e ignora solo los intermedios (`cubos/`,
`historicos/`, `eda/`, `comparacion_tablero.csv`).

**Qué se hizo.** Se tomó el criterio de compassionate para `data/processed/`
(si no, el pipeline escribiría archivos que nadie ve que se pierden). Los
crudos siguen ignorados; se versiona solo `data/fuentes.csv` y el README.

**Opciones.** (a) como quedó; (b) versionar solo `serie_nacional_sintomas.csv`
y `manifiesto.json`; (c) no versionar nada derivado (todo regenerable).

**Recomendación.** (b): lo más corto que permite reproducir el análisis sin
meter archivos grandes. Decide Omar.

## P-D. Dos listas de dependencias

**Dónde.** `environment.yml` (rama de partida, lo usa `make env`) y
`requirements.txt` (compassionate: pandas, matplotlib…). No se unieron.
El pipeline DGE (`src/datos.py`, `src/eda.py`) necesita pandas y matplotlib;
`make env` instala lo de `environment.yml`.

**Estado tras unir F4.** `requirements.txt` quedó como unión de las dos
(numpy≥2.0, scipy, pandas, matplotlib, numba, pytest, pytest-xdist). **No se
agregaron `numba` ni `pytest-xdist` a `environment.yml`**: el test
`tests/test_infra.py::test_deps_pip_sale_de_environment_yml` fija esa lista
exacta (sin numba, `sirmx` cae a Python puro, ~15× más lento: 0.37 ms contra
0.024 ms por llamada según el inventario; la suite de F4 con `-n 4` tardó 8 min
con numba). Decidir si numba entra al entorno oficial.

**Recomendación.** Una sola lista (`environment.yml`) y borrar
`requirements.txt`, comprobando antes que `environment.yml` trae todo lo que
usa `src/eda.py` y `src/comparar_tablero.py` (**no verificado**: esos
módulos solo se probaron con datos sintéticos).

## P-E. Otros restos de este paso

- `src/datos.py:230` y `tests/sintetico.py:51` siguen usando `weekday`
  (en un índice/`dt`). Solo se pidió cambiar `src/eda.py`. Con pandas 3.0.5
  `weekday` y `dayofweek` funcionan y no dan aviso: que `weekday` desaparezca
  en pandas 4 es afirmación del inventario, **no verificada**.
- `data/processed/README.md` (rama de partida) dice que todo se regenera con
  código de `src/datos.py`: ahora sí es el pipeline DGE.
- `docs/actas/F0-alcance.md` sigue mencionando `src/datos.py::cargar_parametros`
  (acta histórica; no se reescribió).
- `reports/parametros_fuentes.md` dice "validado por `src/datos.py`" hasta que
  Omar lo regenere con `make resumen`.

---

# Pendientes que salen de unir F4 (`kind-newton`, `sirmx/`)

## P-F. Hay dos `plan_analisis.md` y no se eligió

**Dónde.** `docs/plan_analisis.md` (el de la rama de integración, que viene de
remake/stoic, con H1–H5) y `docs/plan_analisis_f4.md` (el que escribió F4,
copiado **sin modificar** desde `kind-newton`).

**Qué pasa.** El de F4 dice en su primera línea "CONGELADO" (2026-11-04). Esa
sesión decidió por su cuenta los issues I2, I3 e I4: el propio
`docs/decisiones.md` (líneas 7–14) admite que "no venían en el mensaje y no
existen como issues en el repositorio". Así que el "congelado" se apoya en
decisiones que nadie confirmó. Además el plan de F4 no incluye H3, H4b ni H5,
dice "D fijo: 7 días" (línea 27) y "N es la población nacional (CONAPO)"
(línea 19). El plan de remake/stoic dice que el plan se congela al cerrar F4
y que los cambios van a `docs/desviaciones.md`.

**Opciones.** (a) quedarse con el de remake/stoic y dejar el de F4 como
referencia de métodos; (b) quedarse con el de F4; (c) unirlos: H1–H5 del
primero y los métodos del segundo.

**Recomendación.** (c), registrando en `docs/desviaciones.md` todo lo que
cambie del plan de F4. Mientras Omar no decida, **ninguno de los dos está
congelado**. Decide Omar.

## P-G. `src/sir.py` y `s0 = 1` (Ola 1): lo que realmente pasa hoy

**Dónde.** `src/sir.py` (`integrar_sir`, `estado_inicial`, `incidencia_semanal`)
y `config/parametros.yaml` (`s0_ola1 = 1.0`).

**Qué se encontró (probado al integrar, sin cambiar `sir.py`).**

| Llamada | Resultado |
|---|---|
| `integrar_sir(R0, D, S0=N, I0=N·i0, N, t)` | **ValueError**: `S0 + I0 > N` |
| `integrar_sir(R0, D, S0=N−I0, I0, N, t)` | funciona |
| `estado_inicial(1.0, 1e-5, N)` | funciona (S0 = N − I0, con guarda de redondeo) |
| `incidencia_semanal(…, s0=1.0, …)` | funciona |

O sea: el problema que describía el inventario existe **solo** si se llama a
`integrar_sir` con `S0 = N` e `I0 > 0`. Con el modelo de observación
(`estado_inicial`) `s0 = 1` ya se acepta, por la convención del 2026-11-04
(`s0 = (S0 + I0)/N`).

**Lo que sí queda abierto: dos convenciones de `s0`.**
`sirmx` usa `s0` = fracción susceptible e `i0` = fracción infecciosa, sin
exigir `s0 + i0 ≤ 1` (sus escenarios usan `s0 = 1.0` con `i0 = 1e-5`).
`src/sir.py` usa `s0 = (S0 + I0)/N`. Con `s0 = 1.0` los dos arrancan de
estados que difieren en `i0` (≈ 1e-5). Por eso `sirmx` no se puede pasar tal
cual a `src/sir.py`, y por eso el test de equivalencia usa `s0 = 0.999`
(como se pidió) y llama a `integrar_sir` con `S0 = N·s0`.

**Opciones.** (a) `sirmx` adopta la convención de `sir.py`; (b) `sir.py`
acepta `S0 + I0 ≤ N(1+ε)`; (c) se deja y se traduce en la frontera entre
módulos.

**Recomendación.** (a), porque `parametros.yaml` ya usa la convención de
`sir.py`. Hay que repetir la validación sintética después (**no verificado**
cuánto cambian sus tablas). Decide Omar.

## P-H. `sirmx` no cumple la tolerancia de equivalencia con R0 = 8

**Dónde.** `tests/test_equivalencia_simuladores.py`, `sirmx/modelo.py:11`
(`NSUB = 4`).

**Resultado.** Tolerancia declarada: 1e-6 absoluta (cota que el inventario
midió para `sirmx`). Con `s0 = 0.999`, D = 7, 200 días:

| R0 | i0 | error en s | en i | en r | en incidencia | ¿cumple? |
|---|---|---|---|---|---|---|
| 1.5 | 1e-5 | 7.8e-10 | 1.3e-10 | 7.6e-10 | 2.7e-11 | sí |
| 1.5 | 2.5e-5 | 6.7e-10 | 1.2e-10 | 6.4e-10 | 1.9e-11 | sí |
| 2.5 | 1e-5 | 1.1e-7 | 4.3e-8 | 8.5e-8 | 8.6e-9 | sí |
| 2.5 | 2.5e-5 | 9.3e-8 | 3.8e-8 | 7.5e-8 | 7.7e-9 | sí |
| 8 | 1e-5 | **5.5e-5** | 4.4e-5 | 2.1e-5 | 2.0e-5 | **no** |
| 8 | 2.5e-5 | **4.9e-5** | 3.9e-5 | 1.9e-5 | 1.8e-5 | **no** |

Contra una referencia de alta precisión (DOP853, rtol = 1e-13) `src/sir.py`
queda a ≤ 3e-10; el desvío es del RK4 de `sirmx` con 4 subpasos por día. Baja
con el orden 4 esperado: con 16 subpasos, R0 = 8 daría ~2.5e-7 (medido, no
aplicado). Los dos escenarios R0 = 8 quedan `xfail(strict=True)` con esta
explicación. **No se aflojó la tolerancia ni se cambió `NSUB`.**

**Opciones.** (a) subir `NSUB` (más lento: 16 subpasos son 4× más pasos; tiempo **no medido**); (b) dejar `NSUB = 4`
y declarar que `sirmx` solo vale para R_eff ≲ 3 (con R0 = 2.5 el error es
~1e-7, dentro de la cota; **no verificado** qué R_eff(0) tienen las olas
reales, porque nada se ha ajustado a datos reales); (c) usar `src/sir.py` en la estimación final.
**Recomendación.** (b) por ahora, y escribirlo en `docs/decisiones.md`;
revisar con (a) si algún ajuste real da R_eff(0) > 3. Decide Omar.

## P-I. Lugares con D = 7 fijo (para aplicar "D por ola con fuente" después)

Decisión ya tomada: D por ola (`D_olaN` de `parametros.yaml`), y 5/7/10 solo
como sensibilidad. **No se cambió nada.** Los valores `null` de `D_olaN`
hacen que hoy no se pueda aplicar (ver pendiente 12).

**Código (`sirmx/`)**

| Archivo:línea | Qué es |
|---|---|
| `sirmx/modelo.py:89` | `ParamsOla.D = 7.0` por omisión |
| `sirmx/verosimilitud.py:102` | `ajustar_ola(y, D=7.0, …)` |
| `sirmx/cambios.py:88` | `detectar_cambios(y, D=7.0, …)` |
| `sirmx/escenarios.py:15, 19, 22, 25, 30` | `D=7.0` en los 5 escenarios sintéticos (es la "verdad" del experimento: ahí 7 es válido) |
| `sirmx/crecimiento.py:13` | `D_ESCENARIOS = (5.0, 7.0, 10.0)` (sensibilidad: coincide con la decisión) |

**Scripts**

| Archivo:línea | Qué es |
|---|---|
| `scripts/validacion_sintetica.py:146` | encabezado de tabla "R(D=5) \| R(D=7) \| R(D=10)" |
| `scripts/validacion_sintetica.py:154` | `for D in (5.0, 7.0, 10.0)` |

**Pruebas**

| Archivo:línea | Qué es |
|---|---|
| `tests/test_1_observacion.py:34` | `np.full(T, R0 / 7)` y `1 / 7` (γ con D = 7) |
| `tests/test_1_observacion.py:42, 43` | `1 / 7` como γ |
| `tests/test_5_crecimiento.py:59` | `set(tabla) == set(D_ESCENARIOS)` |
| `tests/test_5_crecimiento.py:64, 66` | `tabla[7.0]`, `tabla[5.0]`, `tabla[10.0]` |
| `tests/test_equivalencia_simuladores.py:45` | `D = 7.0` (nuevo en esta integración; es un valor de diseño del test) |

**Documentos de F4**

| Archivo:línea | Qué dice |
|---|---|
| `docs/decisiones.md:62` | "base D = 7 días; escenarios D ∈ {5, 7, 10}" |
| `docs/plan_analisis_f4.md:27, 40` | "D fijo: valor base de 7 días; D ∈ {5, 7, 10}" |

**No son D** (ventanas de 7 días): `sirmx/cambios.py:23`,
`sirmx/crecimiento.py:21` (`np.ones(7)/7`), `sirmx/pronostico.py:44, 77, 129`
(semanas) y `d0` / `% 7` (día de la semana).

## P-J. Semillas escritas a mano

No se unificaron. `SEMILLA = 20261104` es la de F4 (`sirmx/escenarios.py:8`);
`config/parametros.yaml` (sección sintético) usa `semilla: 20200228`.

| Archivo:línea | Semilla |
|---|---|
| `sirmx/escenarios.py:8` | `SEMILLA = 20261104` |
| `sirmx/cambios.py:89` | `default_rng(0)` si no se pasa `rng` |
| `sirmx/verosimilitud.py:110` | `default_rng(0)` si no se pasa `rng` |
| `sirmx/validacion.py:22` | `default_rng(SEMILLA)` |
| `sirmx/validacion.py:83` | `semilla_base=SEMILLA`, réplicas `SEMILLA + 1 + i` |
| `scripts/validacion_sintetica.py:37, 50, 113, 149` | `default_rng(SEMILLA)` |
| `scripts/validacion_sintetica.py:57` | `default_rng(1000 + s)` |
| `scripts/validacion_sintetica.py:62` | `default_rng(s)` |
| `scripts/validacion_sintetica.py:196, 199` | `_corrida(123)` y texto "semilla 123" |
| `tests/test_1_observacion.py:19` | `default_rng(1)` |
| `tests/test_2_verosimilitud.py:21, 41` | `default_rng(SEMILLA)` |
| `tests/test_2_verosimilitud.py:34` | `default_rng(3)` |
| `tests/test_4_perfiles.py:16` | `default_rng(SEMILLA)` |
| `tests/test_5_crecimiento.py:19, 29, 55` | `default_rng(SEMILLA)` |
| `tests/test_5_crecimiento.py:41` | `default_rng(1000 + s)` |
| `tests/test_6_cambios.py:12` | `default_rng(SEMILLA)` |
| `tests/test_7_pronostico.py:10` | `default_rng(0)` |
| `tests/test_7_pronostico.py:26` | `default_rng(1)` |
| `tests/test_7_pronostico.py:38` | `default_rng(SEMILLA)` |
| `tests/test_8_reproducibilidad.py:31, 37` | `_corrida(123)`, `_corrida(124)` |
| `tests/test_8_reproducibilidad.py:45` | `_corrida(7)` |

(Los tests de la rama de partida —`tests/test_*.py` de remake— y
`scripts/recuperacion_sintetica.py` también tienen semillas; no se listan
porque la tarea pidió `sirmx/`, `scripts/` y `tests/` de F4. **No verificado**
que la lista cubra todas las de esos archivos: se buscó con `grep` por
`seed|semilla|default_rng|RandomState`.)
