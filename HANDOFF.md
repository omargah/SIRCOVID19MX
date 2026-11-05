# HANDOFF · PT1 (SIR, COVID-19 en México) · rama de integración

Repo `omargah/SIRCOVID19MX`. Última actualización: 2026-11-05.

## 1. Estado actual

**La rama buena es `integracion/pt1-v2`.** Nace de la punta de
`claude/adoring-goodall-jf3lyb` (`cd1b32f`) y le suma, con `git merge --no-ff`
y un commit por paso, las cuatro ramas que faltaban:

| Paso | Rama que entró | Qué aportó |
|---|---|---|
| 1 | `fervent-dirac` | `tests/teoria/` (derivaciones a–k), adaptado a la firma actual de `integrar_sir` |
| 2 | `zealous-heisenberg` | regla de olas, enmienda A1, frontera 1.ª/2.ª ola, `resultados/olas/` |
| 3 | `compassionate-dijkstra` | pipeline de microdatos DGE (`src/datos.py`), EDA, comparación con el tablero |
| 4 | `kind-newton` (F4) | `sirmx/`: validación sintética por ola, puntos de cambio, pronóstico |

Antes del paso 3, el cargador de parámetros se renombró a `src/parametros.py`.

**No tocar:** `claude/adoring-goodall-jf3lyb` (Omar sube ahí `reports/` de la
recuperación sintética), `main`, `integracion/pt1` ni ninguna otra `claude/*`.

**Lo que NO está decidido** está en
[`docs/pendientes_integracion.md`](docs/pendientes_integracion.md) (20 puntos).
Lo que sí, en [`docs/decisiones_integracion.md`](docs/decisiones_integracion.md).
Los más importantes:

1. Hay dos `plan_analisis.md` (`docs/plan_analisis.md` y `docs/plan_analisis_f4.md`);
   el "CONGELADO" de F4 se apoya en issues I2–I4 que esa sesión inventó.
2. `sirmx` no cumple la equivalencia con `src/sir.py` para R0 = 8 (error ~5e-5
   contra tolerancia 1e-6).
3. Olas con JHU (reporte) y pipeline con DGE (síntomas): no se eligió.
4. D = 7 y semillas siguen escritas a mano en `sirmx/`, `scripts/` y `tests/`.
5. Casi todos los valores de literatura de `config/parametros.yaml` siguen en
   `null`: falta `PT1_bibliografia_v2.xlsx`.

## 2. Qué hace cada módulo

| Archivo | Qué hace |
|---|---|
| `config/parametros.yaml` | Parámetros con fuente obligatoria o `supuesto: true` + sensibilidad; D por ola; diseño de la recuperación sintética. |
| `src/parametros.py` | Cargador del YAML que hace cumplir la regla de fuentes. (Antes `src/datos.py`.) |
| `src/sir.py` | **Simulador oficial.** SIR en personas (LSODA en S, ln I, R), β por tramos, modelo de observación. Convención `s0 = (S0+I0)/N`. |
| `src/verosimilitud.py`, `src/identificabilidad.py`, `src/recuperacion.py` | Verosimilitud semanal (+ serología), perfiles, H1, una réplica de recuperación sintética. |
| `src/semanas.py`, `src/truncar.py` | Semana epidemiológica domingo–sábado; truncado a semanas completas. |
| `src/olas.py` | Regla de olas de zealous (R1–R7 + A1 + frontera). Produce `resultados/olas/`. Fuente: JHU. |
| `src/olas_provisional.py` | La otra regla de olas (la que ya estaba en la rama de partida). Ver pendiente 15. |
| `src/datos.py` | Pipeline de microdatos DGE por fecha de inicio de síntomas (`python -m src.datos`). |
| `src/comparar_tablero.py`, `src/eda.py`, `src/series_historicas.py`, `src/fuentes.py` | Comparación con el tablero CONAHCYT, EDA de artefactos, versiones históricas, registro de fuentes. |
| `sirmx/` | F4: SIR por ola con RK4 + numba, verosimilitud diaria con día de la semana, perfiles, r con ventana fija, puntos de cambio, pronóstico. Motor propio; **no** llama a `src/sir.py`. |
| `scripts/` | `correr_sintetico.py`, `recuperacion_sintetica.py`, `resumen_recuperacion.py`, `make_*.py`, `validacion_sintetica.py` (F4), `registrar_fuente.py`, `inventario_historicos.py`. |
| `tests/test_equivalencia_simuladores.py` | Garantiza que `sirmx` y `src/sir.py` coinciden (tolerancia 1e-6; R0 = 8 es xfail). |
| `tests/teoria/` | Derivaciones a–k del Cap. 2 (SymPy + `src/sir.py`). `firma_sir.py` es el adaptador a la firma actual. |

## 3. Cómo correr las pruebas

```bash
pip install -r requirements.txt
```

```bash
python -m pytest -q
```

La suite de F4 es la lenta. Medido: **7 min 45 s con 4 procesos** y un solo hilo
de BLAS por proceso (sin `-n` no se midió):

```bash
OPENBLAS_NUM_THREADS=1 python -m pytest -n 4 -q
```

Solo la teoría (segundos), y después todo menos F4 (218 pasan, 5 xfail, ~1 min):

```bash
make teoria
```

```bash
python -m pytest -q --ignore=tests/test_1_observacion.py --ignore=tests/test_2_verosimilitud.py --ignore=tests/test_3_escenarios.py --ignore=tests/test_4_perfiles.py --ignore=tests/test_5_crecimiento.py --ignore=tests/test_6_cambios.py --ignore=tests/test_7_pronostico.py --ignore=tests/test_8_reproducibilidad.py
```

**Estado de la suite al cerrar la integración: 258 pasan, 0 fallan, 5 xfail
estrictos** (263 pruebas recolectadas). Los 5 xfail son errores reales
documentados (pendiente 13). Un `make` completo del pipeline de datos
(`make todo`) necesita los microdatos de la DGE en `data/raw/`, que no están en
el repo.

`numba` es opcional pero sin él `sirmx` es ~15× más lento (`requirements.txt`
lo incluye; `environment.yml` todavía no, ver pendiente 17).

## 4. Siguientes pasos

1. **Omar decide los 20 pendientes**, empezando por el plan de análisis (1), los
   I2–I4 de F4 (2) y la fuente de las olas (4).
2. Omar corre `make recuperacion` y `make resumen` y hace push de `reports/` en
   `claude/adoring-goodall-jf3lyb`; luego traer eso a esta rama.
3. Subir `PT1_bibliografia_v2.xlsx` y llenar los `null` de `parametros.yaml`.
4. Aplicar D por ola (`D_olaN`) en `sirmx/` y unificar las semillas
   (pendientes 6 y 7); regenerar `docs/validacion_sintetica.md`.
5. Resolver la convención de `s0` entre `sirmx` y `src/sir.py` (pendiente 5) y
   decidir qué hacer con R0 ≥ 8 (pendiente 14).
6. Con red: bajar los microdatos de la DGE a `data/raw/dge/`, registrarlos
   (`scripts/registrar_fuente.py`) y rehacer las olas con la serie de síntomas.
7. Limpiar aparte las firmas de IA en los 9 commits heredados y decidir el
   autor de los commits (pendiente 19).

---

# Anexo · HANDOFF anterior (rama `claude/adoring-goodall-jf3lyb`, 2026-11-05)

> Se conserva tal cual para no perder las decisiones y bloqueos de Omar. **Lo que
> quedó desactualizado:** la sección "1. Qué hay" dice que `zealous`,
> `kind-newton`, `fervent-dirac` y `compassionate-dijkstra` no se unieron y que
> se descartaban los datos JHU, la frontera 2020-10-01 y el D = 7: esta
> integración las unió todas (ver pendiente 20). `src/olas.py` ya no es la regla
> provisional (ahora es `src/olas_provisional.py`).

## HANDOFF · código del PT1 (SIR, COVID-19 en México)

Rama: `claude/adoring-goodall-jf3lyb` (repo `omargah/SIRCOVID19MX`). Chat de
código (chat 02). Lo de bibliografía y teoría va en el chat 01; bitácora y
tablero, en el chat 00.

Última actualización: 2026-11-05. Acta: `docs/actas/F4-sintetico.md`.

### 1. Qué hay

Base: `claude/sir-covid-mexico-remake-834hzi` + `claude/stoic-galileo-qsf1n6`
unidas con `--no-ff` (decisión de Omar 2026-11-04). Las demás ramas
(`zealous-heisenberg`, `kind-newton`, `fervent-dirac`, `compassionate-dijkstra`)
NO se unieron; solo son referencia (`integracion/pt1:docs/inventario_integracion.md`).
Se descartan explícitamente de `zealous` los datos JHU y la frontera 2020-10-01
(decidida viendo los datos), y de `kind-newton` el D = 7.

| Archivo | Qué hace |
|---|---|
| `config/parametros.yaml` | Parámetros con fuente obligatoria o `supuesto: true` + sensibilidad. D por ola con CrI95 y rango de Byrne. Diseño de la recuperación sintética. |
| `config/medidas.yaml` | Fechas candidatas de la medida para H5 (sin citar hasta ver el DOF). |
| `src/parametros.py` | Cargador que hace cumplir la regla de fuentes. Sensibilidad en lista con fuente; `estimador` de D obligatorio. |
| `src/sir.py` | SIR en personas (LSODA en S, ln I, R). Convención s0 = (S0+I0)/N. BinNeg y Poisson. |
| `src/semanas.py` | Semana epidemiológica domingo-sábado (una sola definición). |
| `src/truncar.py` | `truncar_corte(serie, N)` en semanas completas; `semanas_desde_dias`. |
| `src/verosimilitud.py` | Verosimilitud semanal NB y Poisson (+ serología), MLE, perfiles, IC por búsqueda de extremos, Pearson, AIC, BIC. |
| `src/identificabilidad.py` | Simetría de escala de H1, clasificación de perfiles (Raue 2009). |
| `src/recuperacion.py` | Una réplica de recuperación sintética (ruido NB/Poisson × verosimilitud NB/Poisson). |
| `src/olas.py` | Regla provisional de olas y su sensibilidad ±5 pts. |
| `scripts/recuperacion_sintetica.py` | Corrida completa en paralelo, reanudable, a `reports/resultados/recuperacion/*.jsonl`. |
| `scripts/resumen_recuperacion.py` | Sesgo, cobertura, perfiles, NB vs Poisson → `reports/recuperacion_sintetica_<datos>.md`. |
| `scripts/listar_supuestos.py` | Cruce parámetro–fuente → `reports/parametros_fuentes.md`. |

Pruebas: `python -m pytest -q` (con `OMP_NUM_THREADS=1`). El conteo de pruebas
que pasan está en el acta (`docs/actas/F4-sintetico.md`), sacado de pytest.

### 2. Decisiones (todas de Omar; fecha)

- 2026-11-03 · I1, I2, I3, I4, reglas de olas, D por variante (ver acta F4).
- 2026-11-04 · Base remake + stoic. Verosimilitud SEMANAL, sin sensibilidad diaria.
  Semana epidemiológica domingo-sábado. τ con resolución de una semana.
- 2026-11-04 · s0 = 1 → `S0 = N·s0 − I0`. D_ola1 (Ganyani, no intrínseco) = supuesto
  con sensibilidad. D_ola2 = original, D_ola5 = supuesto (valor BA.1).
- 2026-11-04 · Malla sintética R0 ∈ {2, 3} (corregida desde {1.5, 3}), s0 ∈ {0.6, 1},
  D ∈ {4.7, 6.84}, 50 réplicas, solo casos y casos + serología, dos noches.
  Serie hasta 1 % del pico. Frontera de ola = domingo de la semana del mínimo.
  "Pico del periodo" = máximo global. Sensibilidad de D en lista con fuente.
- 2026-11-04 · Hart 2022 se cita como Lancet Infect Dis 22(5):603–610. Todos los
  intervalos de G02, G05, G06 son CrI95.
- 2026-11-05 · La recuperación sintética completa se corre en la computadora de
  Omar (`docs/correr_recuperacion.md`): la sesión en la nube no sostiene
  cálculos largos sin vigilancia.

Decisiones numéricas mías (no de diseño del análisis; registradas en el YAML o
el docstring): IC por perfil buscando los extremos (K02 p. 88) en vez de malla
fija, porque la malla no ubicaba IC más angostos que su paso; arranque de cada
punto del perfil sobre la cresta de H1; puntos del perfil sin pulido
Nelder-Mead (extremos idénticos, medido); tope K_MAX de k; reajuste si un perfil
supera a la MLE.

### 3. Bloqueos

0. **Cómputo.** El contenedor de la sesión se recicla minutos después de quedar
   inactivo y mata los procesos en segundo plano. La recuperación completa se
   corre fuera (`docs/correr_recuperacion.md`); van las réplicas que tenga
   `reports/resultados/recuperacion/casos.jsonl`.
1. **Red.** La sesión no alcanza `www.dof.gob.mx`, `www.gob.mx` ni
   `datosabiertos.salud.gob.mx` (403 / no resuelve). Sin eso: no hay texto del
   acuerdo del DOF (fecha de la medida), no hay bases históricas de la DGE
   (estimación de N del truncado, I3) ni serie real (Ola 1, olas reales).
2. **Fuentes sin página verificada para fórmulas implementadas:**
   - BIC: ninguna fuente con PDF en la bibliografía.
   - Dispersión de Pearson y AIC: Pawitan 2001 (LIB03) según su índice (§4.5
     p. 84, §13.5 p. 375), pero la copia en Drive solo trae ~55 páginas.
3. **INDICE.csv del repo** no tiene M07, J06, M23, M24 ni N08 (Gostic, Roda,
   Bastos, McGough, Goolsbee). El validador de `src/parametros.py` rechaza claves que no
   estén ahí: mientras el chat 01 no actualice el índice, esas fuentes solo se
   citan en comentarios, no en `parametros.yaml`.
4. `incubacion_mediana` sigue apuntando a G01 (Lauer). Omar corrigió que 6.4 d es
   Backer 2020 (G03, media, no mediana). No se tocó: solo se usa en H5 y falta
   decidir mediana o media y qué fuente.
5. `N = 126 014 024` (INEGI 2020): falta verificar la ubicación en el tabulado.

### 4. Qué sigue

1. Omar corre `make recuperacion` y `make resumen` en su computadora y hace push;
   luego se llenan las cifras del acta F4 con las tablas generadas.
2. Fijar, ANTES de datos reales, el umbral de "comparable" del criterio de
   rechazo de H1 (amplitud relativa de IC(R0) contra IC(R_eff(0))): hoy se reporta
   el cociente sin umbral.
3. Con red: bajar las bases históricas de la DGE, escribir el procedimiento y el
   umbral de "estabilizado" para N (I3) ANTES de calcularlo, estimar N.
4. Con red: leer el acuerdo del DOF, llenar `config/medidas.yaml`.
5. Olas reales con la regla y su sensibilidad; luego Ola 1 (s0 = 1, D_ola1).
6. Puntos de cambio de β (H5, 1–3 libres, AIC y BIC): falta implementarlos.

