# HANDOFF · código del PT1 (SIR, COVID-19 en México)

Rama: `claude/adoring-goodall-jf3lyb` (repo `omargah/SIRCOVID19MX`). Chat de
código (chat 02). Lo de bibliografía y teoría va en el chat 01; bitácora y
tablero, en el chat 00.

Última actualización: 2026-11-05. Acta: `docs/actas/F4-sintetico.md`.

## 1. Qué hay

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

## 2. Decisiones (todas de Omar; fecha)

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

## 3. Bloqueos

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

## 4. Qué sigue

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
