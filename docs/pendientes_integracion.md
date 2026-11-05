# Pendientes de la integración (rama `integracion/pt1-v2`)

Aquí está todo lo que apareció al unir las ramas y que **no se decidió**. Cada
entrada dice dónde está el problema, qué opciones hay y qué se recomienda, en
lenguaje simple. Quien decide es Omar. Las decisiones que sí se aplicaron
están en [`decisiones_integracion.md`](decisiones_integracion.md).

Las entradas 1–13 son las que pidió la tarea. Las 14–20 son hallazgos que
salieron durante la unión.

| # | Tema |
|---|---|
| 1 | Cuál `docs/plan_analisis.md` se queda |
| 2 | Qué hacer con los I2–I4 inventados de F4 |
| 3 | Verosimilitud por día o por semana |
| 4 | Olas con JHU o con DGE |
| 5 | `src/sir.py` y `s0 = 1` (Ola 1) |
| 6 | Lugares con D = 7 fijo |
| 7 | Semillas escritas a mano |
| 8 | Wald + BIC (F4) contra perfil + AIC + Ljung–Box (remake) |
| 9 | ¿La serología entra en la verosimilitud? |
| 10 | N de INEGI o de CONAPO |
| 11 | El rango de Byrne no contiene ningún D base |
| 12 | Valores de literatura en `null` |
| 13 | Los xfail estrictos |
| 14 | `sirmx` no cumple la equivalencia con R0 = 8 |
| 15 | Hay dos reglas de olas en `src/` |
| 16 | Qué se versiona de `data/processed/` |
| 17 | Dos listas de dependencias |
| 18 | Restos menores |
| 19 | Autor de los commits y commits heredados con firma |
| 20 | El `HANDOFF.md` anterior descartaba cosas que esta tarea sí unió |

---

## 1. Cuál `docs/plan_analisis.md` se queda

**Dónde.** `docs/plan_analisis.md` (el de la rama de integración, de
remake/stoic: hipótesis H1–H5) y `docs/plan_analisis_f4.md` (el que escribió
F4, copiado **sin modificar** desde `kind-newton`).

**Qué pasa.** El de F4 dice "CONGELADO" en su primera línea (2026-11-04). Esa
sesión decidió por su cuenta los issues I2, I3 e I4 (ver 2), así que el
"congelado" se apoya en decisiones que nadie confirmó. Además no incluye H3,
H4b ni H5; dice "D fijo: valor base de 7 días" (línea 27) y "N es la población
nacional (CONAPO)" (línea 19). El plan de remake/stoic dice que el plan se
congela al cerrar F4 y que los cambios van a `docs/desviaciones.md`.

**Opciones.** (a) quedarse con el de remake/stoic y dejar el de F4 como
referencia de métodos; (b) quedarse con el de F4; (c) unirlos: H1–H5 del
primero y los métodos del segundo.

**Recomendación.** (c), anotando en `docs/desviaciones.md` todo lo que cambie
del plan de F4. Mientras Omar no decida, **ninguno de los dos está congelado**.

## 2. Qué hacer con los I2–I4 inventados de F4

**Dónde.** `docs/decisiones.md` (de F4), líneas 7–14: admite que el texto de
los issues "no venía en el mensaje y no existen como issues en el
repositorio", y que la sesión definió por su cuenta tres decisiones.

**Qué pasa.** Comparadas con las otras ramas (inventario §2.2 e), unas
coinciden y otras chocan:

- **Coinciden:** γ = 1/D y β = R0·γ; R = 1 + r·D; la binomial negativa;
  "solo se identifican R_eff(0), ρ·s0 e i0/s0"; ρ solo si s0 viene de fuera;
  IC de τ por perfil; WIS contra persistencia.
- **Chocan:** D = 7 para todas las olas (ver 6); RK4 + numba contra LSODA
  (decidido en D-C); efecto de día de la semana con 6 parámetros contra
  semanas sin esos parámetros (ver 3); K de cambios por BIC contra Ljung–Box +
  AIC (ver 8); N de CONAPO contra INEGI (ver 10); sin serología (ver 9).
- **Nuevas, sin choque:** r con ventana fija de 21 días; k fijado de la ola
  completa al estimar r; toda la aleatoriedad con `numpy.random.Generator`.

**Opciones.** (a) borrarlos y esperar el texto real de los issues;
(b) dejarlos marcados "PROVISIONAL — no viene del issue real", aceptar los que
coinciden, corregir los que chocan y revisar los nuevos; (c) aceptarlos tal
cual.

**Recomendación.** (b). No se pierde trabajo y queda claro qué tiene respaldo.
Lo mínimo a corregir: D = 7 → D por ola; N de CONAPO → INEGI. **No se
modificó `docs/decisiones.md`.** Solo Omar puede conseguir el texto real de los
issues.

## 3. Verosimilitud por día o por semana

**Dónde.** `src/verosimilitud.py` (semanal, de remake) contra
`sirmx/verosimilitud.py` (diaria con efecto de día de la semana, F4). El
pipeline DGE (`src/datos.py`) entrega una serie diaria.

**Qué pasa.** El `HANDOFF.md` anterior registra una decisión de Omar del
2026-11-04: "Verosimilitud SEMANAL, sin sensibilidad diaria". F4 hizo lo
contrario: diaria, con 6 parámetros extra para el ciclo semanal. Las dos
conviven hoy, cada una con su propia verosimilitud.

**Opciones.** (a) semanal como principal (decisión registrada), diaria solo
para el r de 21 días; (b) diaria como principal y semanal como sensibilidad;
(c) las dos como análisis separados.

**Recomendación.** (a): respeta la decisión ya registrada. El ciclo semanal de
los datos por **fecha de inicio de síntomas** puede ser distinto del de fecha
de reporte; eso **no está verificado** (no hay microdatos en el repo).

## 4. Olas con JHU o con DGE

**Dónde.** `src/olas.py` y `resultados/olas/` usan **JHU CSSE por fecha de
reporte**. El pipeline de datos usa **microdatos DGE por fecha de inicio de
síntomas**.

**Opciones.** (a) olas con JHU y el pipeline para el ajuste; (b) rehacer las
olas con la serie DGE y dejar JHU como sensibilidad.

**Recomendación.** (b), cuando existan los microdatos. Las fechas pueden
moverse unos días porque la fecha de síntomas va antes que la de reporte. Hasta
entonces las olas son provisionales. No se cambió ρ, la ventana de suavizado
ni la frontera 2020-10-01. (La frontera se tomó después de ver el resultado de
la regla; zealous lo marca así y hay que declararlo en el escrito.)

## 5. `src/sir.py` y `s0 = 1` (el caso de la Ola 1)

**Dónde.** `src/sir.py` (`integrar_sir`, `estado_inicial`,
`incidencia_semanal`) y `config/parametros.yaml` (`s0_ola1 = 1.0`).

**Qué se encontró (probado, sin cambiar `sir.py`).**

| Llamada | Resultado |
|---|---|
| `integrar_sir(R0, D, S0=N, I0=N·i0, N, t)` | **ValueError**: `S0 + I0 > N` |
| `integrar_sir(R0, D, S0=N−I0, I0, N, t)` | funciona |
| `estado_inicial(1.0, 1e-5, N)` | funciona (S0 = N − I0, con guarda de redondeo) |
| `incidencia_semanal(…, s0=1.0, …)` | funciona |

Entonces el problema que se esperaba existe **solo** si se llama a
`integrar_sir` con `S0 = N` e `I0 > 0`. Con el modelo de observación
(`estado_inicial`) `s0 = 1` ya se acepta, por la convención de Omar del
2026-11-04 (`s0 = (S0 + I0)/N`).

**Lo que sí queda abierto: dos convenciones de `s0`.** `sirmx` usa `s0` =
fracción susceptible e `i0` = fracción infecciosa, sin exigir `s0 + i0 ≤ 1`
(sus escenarios usan `s0 = 1.0` con `i0 = 1e-5`). `src/sir.py` usa
`s0 = (S0 + I0)/N`. Con `s0 = 1.0` arrancan de estados que difieren en `i0`
(~1e-5). Por eso `sirmx` no se puede pasar tal cual a `src/sir.py`, y por eso
el test de equivalencia usa `s0 = 0.999` (como se pidió) y llama a
`integrar_sir` con `S0 = N·s0`. En `tests/teoria/` se tuvieron que cambiar a
`s0 = 1 − i0` ocho casos (en siete pruebas) que usaban `s0 = 1.0` con `i0 > 0`.

**Opciones.** (a) `sirmx` adopta la convención de `sir.py`; (b) `sir.py`
acepta `S0 + I0 ≤ N(1+ε)`; (c) se deja y se traduce en la frontera entre
módulos.

**Recomendación.** (a), porque `parametros.yaml` ya usa la convención de
`sir.py`. Después hay que repetir la validación sintética de F4 (**no
verificado** cuánto cambian sus tablas).

## 6. Lugares con D = 7 fijo

Decisión ya tomada: D por ola con fuente (`D_olaN` de `parametros.yaml`), y
5/7/10 solo como sensibilidad. **No se cambió nada.** Nota: en esta rama los
`D_olaN` **sí tienen valor** (5.20, 5.20, 4.7, 6.84, 6.84; D_ola1 y D_ola5 son
`supuesto: true`), no son `null`.

**Código (`sirmx/`)**

| Archivo:línea | Qué es |
|---|---|
| `sirmx/modelo.py:89` | `ParamsOla.D = 7.0` por omisión |
| `sirmx/verosimilitud.py:102` | `ajustar_ola(y, D=7.0, …)` |
| `sirmx/cambios.py:88` | `detectar_cambios(y, D=7.0, …)` |
| `sirmx/escenarios.py:15, 19, 22, 25, 30` | `D=7.0` en los 5 escenarios sintéticos (es la "verdad" del experimento: ahí 7 es válido) |
| `sirmx/crecimiento.py:13` | `D_ESCENARIOS = (5.0, 7.0, 10.0)` (sensibilidad; coincide con la decisión) |

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
| `tests/test_equivalencia_simuladores.py:45` | `D = 7.0` (nuevo en esta integración; valor de diseño del test) |

**Documentos de F4**

| Archivo:línea | Qué dice |
|---|---|
| `docs/decisiones.md:62` | "base D = 7 días; escenarios D ∈ {5, 7, 10}" |
| `docs/plan_analisis_f4.md:27, 40` | "D fijo: valor base de 7 días; D ∈ {5, 7, 10}" |

**No son D** (ventanas de 7 días): `sirmx/cambios.py:23`,
`sirmx/crecimiento.py:21` (`np.ones(7)/7`), `sirmx/pronostico.py:44, 77, 129`
(semanas) y `d0` / `% 7` (día de la semana).

**Recomendación.** Aplicarlo en otra tarea: `ParamsOla`, `ajustar_ola` y
`detectar_cambios` reciben D de `parametros.yaml` sin valor por omisión; la
sensibilidad {5, 7, 10} más el rango por variante. Los números de F4 van a
cambiar y hay que regenerar `docs/validacion_sintetica.md`.

## 7. Semillas escritas a mano

No se unificaron. `SEMILLA = 20261104` es la de F4; `config/parametros.yaml`
(sección sintético) usa `semilla: 20200228`.

| Archivo:línea | Semilla |
|---|---|
| `sirmx/escenarios.py:8` | `SEMILLA = 20261104` |
| `sirmx/cambios.py:89` | `default_rng(0)` si no se pasa `rng` |
| `sirmx/verosimilitud.py:110` | `default_rng(0)` si no se pasa `rng` |
| `sirmx/validacion.py:22` | `default_rng(SEMILLA)` |
| `sirmx/validacion.py:80, 83` | `semilla_base=SEMILLA`; réplicas `SEMILLA + 1 + i` |
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

Los tests de la rama de partida (`tests/test_*.py` de remake) y
`scripts/recuperacion_sintetica.py` también tienen semillas; no se listan
porque la tarea pidió `sirmx/`, `scripts/` y `tests/` de F4. **No verificado**
que la lista cubra todas las de esos archivos: se buscó con `grep` por
`seed|semilla|default_rng|RandomState`.

**Recomendación.** Un solo lugar (`config/parametros.yaml`) para la semilla
base y semillas derivadas por réplica (`SeedSequence.spawn`), en otra tarea,
después de aplicar el punto 6. Cambiar semillas cambia todas las tablas.

## 8. Wald + BIC (F4) contra perfil + AIC + Ljung–Box (remake)

**Dónde.** `docs/plan_analisis.md`, fila H2: "sistemático si Ljung–Box rechaza
al 5 % **y** el modelo por tramos mejora el AIC". `docs/decisiones.md` (F4):
IC de Wald para los parámetros, K de cambios elegido por **BIC** (cada cambio
cuenta 2 parámetros), H2 con ΔBIC y residuos de Pearson.

**Opciones.** (a) criterio de remake para decidir H2; (b) el de F4; (c) el de
remake para H2 y el BIC de F4 solo para elegir K.

**Recomendación.** (c), porque el plan de remake se escribió antes. Los IC por
perfil (remake) se reportan siempre; los de Wald (F4) solo como comparación.

## 9. ¿La serología entra en la verosimilitud o `s0` viene de fuera?

**Dónde.** `src/verosimilitud.py` (`logvero_sero`) usa serología en la
verosimilitud; `sirmx/verosimilitud.py` no la usa y toma `s0` de fuera (ola 1:
~1; olas siguientes: ENSANUT). `config/parametros.yaml` tiene `s0_ola2..5`,
`sero_ensanut2020/2022` en `null`.

**Qué pasa.** Con casos solos solo se identifican R_eff(0), ρ·s0 e i0/s0
(H1). La serología rompe esa cresta pero hace falta H3 (tamaño final contra
ENSANUT) y los valores de ENSANUT no están cargados (ver 12).

**Opciones.** (a) serología dentro de la verosimilitud (remake); (b) `s0` fijo
de fuera con su incertidumbre propagada (F4); (c) las dos y comparar.

**Recomendación.** (c) mientras no haya valores de ENSANUT. Si hay que
elegir una, (a): es la que permite H3.

## 10. N de INEGI (126 014 024, sin verificar) o de CONAPO

**Dónde.** `config/parametros.yaml`: `N = 126014024` (INEGI, Censo 2020; la
ubicación exacta en el tabulado **no está verificada**) y `N_conapo_2021 =
null`. `docs/plan_analisis_f4.md` línea 19 dice "N es la población nacional
(CONAPO)". `sirmx` usa `N = 1e7` por omisión (valor de diseño sintético).

**Opciones.** (a) INEGI en todas las olas; (b) CONAPO por año; (c) INEGI como
base y CONAPO como sensibilidad.

**Recomendación.** (c), que es como lo deja el YAML. Antes hay que verificar
la cifra y anotar la ubicación (solo Omar, con el tabulado del Censo).

## 11. El rango de Byrne no contiene ningún D base

**Dónde.** `config/parametros.yaml` (líneas ~203–204 y los bloques
`D_ola1…D_ola5`): el rango de Byrne 2020 (G04), 6.5–9.5 d, y los D base
(4.7–6.84 d). El propio YAML lo dice: "la sensibilidad es asimétrica".

**Qué pasa.** La sensibilidad de D solo mira hacia D **más largos** que el
base; nunca hacia más cortos por esa fuente. Además el rango de Byrne es el
periodo infeccioso de asintomáticos en un solo estudio, no un intervalo de
generación.

**Opciones.** (a) dejarlo y declararlo en el escrito; (b) agregar a todas las
olas el barrido simétrico {5, 7, 10} de F4; (c) quitar el rango de Byrne.

**Recomendación.** (b): cubre los dos lados y coincide con la decisión de usar
5/7/10 como sensibilidad. Dejar el de Byrne marcado como asimétrico.

## 12. Los valores de literatura de `parametros.yaml` siguen en `null`

**Dónde.** `config/parametros.yaml`, 12 entradas con `valor: null`:
`N_conapo_2021`, `incubacion_mediana`, `sero_ensanut2020` y su error estándar,
`sero_ensanut2022` y su error estándar, `s0_ola2`…`s0_ola5`, `rho_ola1` y
`rho_ola2_5`. El propio archivo dice que se transcriben de la hoja "Parámetros"
de `PT1_bibliografia_v2.xlsx`, **que no está en ninguna rama**.

**Qué pasa.** Mientras estén en `null`, `cargar_parametros("real")` truena a
propósito (regla 2: ningún parámetro sin fuente), y no puede correrse nada con
datos reales.

**Recomendación.** Omar sube `PT1_bibliografia_v2.xlsx` (o copia valor +
página de cada ficha). No se escribió ninguna cifra de memoria.

## 13. Los xfail estrictos

Hay **5 xfail estrictos** en la suite (todos con `raises=AssertionError`):

| Prueba | Por qué falla | ¿Real? |
|---|---|---|
| `teoria/test_b…::test_sir_py_cumple_su_tolerancia_documentada_en_ola_explosiva` | LSODA acumula error global 1.5e-9 > 1e-9 en s con R0 = 15 | sí (sigue con el `sir.py` actual; antes ~1e-8) |
| `teoria/test_i…::test_incidencia_precisa_con_i0_diminuto` | `incidencia_semanal` resta dos números O(1): error relativo 3.2 % > 1e-5 con i0 = 1e-10 | sí (antes ~5 %) |
| `teoria/test_a…::test_sir_py_N_y_rho_solo_escalan` | **nuevo**: con `sir.py` en personas, el error de LSODA depende de N (~9e-9 relativo); la escala exacta rtol = 1e-12 ya no se cumple | sí; hay una prueba compañera a rtol = 1e-7 |
| `test_equivalencia…[R0=8.0-i0=1e-05]` y `[R0=8.0-i0=2.5e-05]` | RK4 de `sirmx` con 4 subpasos (ver 14) | sí |

Los dos primeros son los 2 xfail originales de fervent-dirac; ninguno pasó, así
que siguen siendo errores reales. El tercero apareció al adaptar las pruebas a
la firma actual y **no estaba en el inventario**.

**Opciones y recomendación** (del inventario): corregir el de incidencia
integrando la incidencia acumulada como variable extra, porque afecta la
verosimilitud si i0 es muy chico; aceptar y documentar el de LSODA; para el de
N, decidir si el `atol` relativo a N debe escalar distinto.

## 14. `sirmx` no cumple la equivalencia con R0 = 8

**Dónde.** `tests/test_equivalencia_simuladores.py`, `sirmx/modelo.py:12`
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

Contra una referencia de alta precisión (DOP853, rtol = 1e-13), `src/sir.py`
queda a ≤ 3e-10; el desvío es del RK4 de `sirmx`. Baja con el orden 4
esperado: con 16 subpasos, R0 = 8 daría ~2.5e-7 (medido, no aplicado). No se
aflojó la tolerancia ni se cambió `NSUB`.

**Opciones.** (a) subir `NSUB` (16 subpasos son 4× más pasos; tiempo **no
medido**); (b) dejar `NSUB = 4` y declarar que `sirmx` solo vale para
R_eff ≲ 3 (con R0 = 2.5 el error es ~1e-7, dentro de la cota; **no
verificado** qué R_eff(0) tienen las olas reales, porque nada se ha ajustado
a datos reales); (c) usar `src/sir.py` en la estimación final.

**Recomendación.** (b) por ahora, escrito en `docs/decisiones.md`; revisar
con (a) si algún ajuste real da R_eff(0) > 3.

## 15. Hay dos reglas de olas en `src/`

**Dónde.** Al unir zealous chocaron `src/olas.py` y `tests/test_olas.py`. El
inventario decía que el de la rama de partida era un esqueleto vacío; no es
cierto: tenía 132 líneas con otra regla.

| | Regla de la rama de partida | Regla de zealous |
|---|---|---|
| Archivo | `src/olas_provisional.py` (antes `src/olas.py`) | `src/olas.py` |
| Pruebas | `tests/test_olas_provisional.py` (6) | `tests/test_olas.py` (5) |
| Método | media móvil de 7 días centrada; mínimos con prominencia ≥ 10 % del máximo global; separación ≥ 60 días; frontera = domingo de la semana epidemiológica | regla R1–R7 de `docs/regla_olas.md`, enmienda A1 y frontera 1.ª/2.ª ola (2020-10-01) |
| Resultados | ninguno sobre datos reales | `resultados/olas/` (5 olas) |

**Qué se hizo (lo menos destructivo).** Se conservaron las dos: la de zealous
quedó como `src/olas.py` (es la que documentan `docs/regla_olas.md` y
`docs/olas_resultados.md`); la otra se movió **sin cambiar su lógica** a
`src/olas_provisional.py`, y solo cambió la línea de importación de su prueba.

**Opciones.** (a) quedarse con la de zealous y archivar la otra; (b) con la
provisional (usa semanas epidemiológicas, que es lo que pide la verosimilitud
semanal); (c) unirlas.

**Recomendación.** (a), después de comprobar que la regla de zealous da
fronteras en domingo (la verosimilitud es semanal).

## 16. Qué se versiona de `data/processed/`

**Dónde.** `.gitignore`. La rama de integración ignoraba todo
`data/processed/*`; compassionate versiona la serie principal, el manifiesto y
las series de hospitalizaciones/defunciones, e ignora solo `cubos/`,
`historicos/`, `eda/` y `comparacion_tablero.csv`. Se tomó el criterio de
compassionate (si no, el pipeline escribiría archivos que se pierden en
silencio).

**Opciones.** (a) como quedó; (b) versionar solo
`serie_nacional_sintomas.csv` y `manifiesto.json`; (c) no versionar nada
derivado.

**Recomendación.** (b): lo más corto que permite reproducir sin meter archivos
grandes.

## 17. Dos listas de dependencias

**Dónde.** `environment.yml` (lo usa `make env`) y `requirements.txt` (unión de
las listas de compassionate y F4: numpy≥2.0, scipy, pandas, matplotlib, numba,
pytest, pytest-xdist).

**Qué pasa.** `environment.yml` dice ser la "única lista de dependencias".
**No se agregaron `numba` ni `pytest-xdist`** porque
`tests/test_infra.py::test_deps_pip_sale_de_environment_yml` fija esa lista
exacta (mi primer intento la cambió y esa prueba falló; se revirtió). Sin
numba, `sirmx` cae a Python puro (0.37 ms contra 0.024 ms por llamada según el
inventario).

**Recomendación.** Una sola lista (`environment.yml`), con numba y xdist si
`sirmx` se queda con el RK4, actualizando a la vez esa prueba (es cambiar el
valor esperado, no aflojarla), y borrar `requirements.txt`. **No verificado**
que `environment.yml` traiga todo lo que usan `src/eda.py` y
`src/comparar_tablero.py` (solo se probaron con datos sintéticos).

## 18. Restos menores

- `src/datos.py:230` y `tests/sintetico.py:51` siguen usando `weekday`. Solo se
  pidió cambiarlo en `src/eda.py`. Con pandas 3.0.5 `weekday` y `dayofweek`
  funcionan y no dan aviso; que `weekday` desaparezca en pandas 4 es
  afirmación del inventario, **no verificada**.
- `docs/actas/F0-alcance.md` sigue mencionando `src/datos.py::cargar_parametros`
  (acta histórica; no se reescribió).
- `reports/parametros_fuentes.md` dice "validado por `src/datos.py`" hasta que
  Omar lo regenere con `make resumen`.
- `docs/teoria_verificacion.md`, discrepancia 3: ya está resuelta (existe
  `integrar_sir_tramos`), pero falta una prueba de (j) contra
  `integrar_sir_tramos` directamente.
- `tests/teoria/firma_sir.py` es un adaptador de las pruebas de teoría; si
  `integrar_sir` vuelve a cambiar de firma, es el único lugar a tocar.
- La suite de F4 tarda ~8 min con `pytest -n 4` (medido). No se marcó nada
  como `lento`: la tarea no lo pidió.

## 19. Autor de los commits y commits heredados con firma

- Los commits nuevos de esta integración no llevan firma en el mensaje, pero
  su **autor** es el configurado en la sesión (`Claude <noreply@anthropic.com>`).
  Si el dueño no quiere ese nombre, hay que reescribir el autor (afecta a
  todos los commits de esta rama; no se hizo sin pedirlo).
- Nueve commits heredados de otras ramas llevan firma en el mensaje y entraron
  por los merges: `ce9cf8e`, `fa6cfa1`, `550ab3a`, `726f3e6`, `015c40a`,
  `2564c37`, `bd237d1`, `86cac48`, `f2ef6ee`. Se limpian aparte.

## 20. El `HANDOFF.md` anterior descartaba cosas que esta tarea sí unió

El `HANDOFF.md` de la rama de partida decía que de `zealous` se descartaban
"los datos JHU y la frontera 2020-10-01 (decidida viendo los datos)" y de
`kind-newton` "el D = 7", y que las ramas `zealous`, `kind-newton`,
`fervent-dirac` y `compassionate-dijkstra` "NO se unieron". Esta tarea las unió
todas, **incluidos** los datos JHU, la frontera 2020-10-01 y el `D = 7` de
`sirmx` (sin cambiarlos). El nuevo `HANDOFF.md` reemplaza esa sección. Omar
debe confirmar si la frontera 2020-10-01 y los datos JHU se quedan (ver 4) o
si se descartan como decía el HANDOFF anterior.
