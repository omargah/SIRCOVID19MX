# Acta F4 · Recuperación sintética, olas y truncado (chat de código)

Fechas: 2026-11-03 a 2026-11-05. Rama `claude/adoring-goodall-jf3lyb`
(`omargah/SIRCOVID19MX`). Regla de cifras: este acta no escribe cifras de
resultados a mano. Los resultados están en los archivos generados que se
citan; los valores de diseño vienen de `config/parametros.yaml`.

## 1. Qué se hizo

1. Paso 0: unión de `sir-covid-mexico-remake` y `stoic-galileo` con `--no-ff`.
   Las pruebas previas siguen pasando.
2. D por ola con fuente verificada en los PDF (G02, G05, G06, G04, G03) y
   sensibilidad en lista con fuente (CrI95 + Byrne). Validador ampliado.
3. Bug de `sir.py` con s0 = 1 resuelto con la convención s0 = (S0+I0)/N.
4. Semana epidemiológica domingo-sábado (`src/semanas.py`).
5. `truncar_corte(serie, N)` y `semanas_desde_dias` (`src/truncar.py`). N no
   se ha estimado (I3, bloqueado por red).
6. Verosimilitud Poisson junto a la NB; residuos y dispersión de Pearson;
   AIC; BIC; perfil de R_eff(0); IC95 por perfil buscando los extremos.
7. Recuperación sintética: código, script reanudable y resumen. Corrida
   parcial en la nube; la corrida completa pasa a la computadora de Omar
   (`docs/correr_recuperacion.md`).
8. Etiquetado de olas con la regla provisional y su sensibilidad ±5 pts,
   probado solo en series sintéticas.
9. Fechas candidatas de la medida registradas sin citar (`config/medidas.yaml`).

## 2. Entregables

| Entregable | Ruta |
|---|---|
| Código | `src/{sir,datos,semanas,truncar,verosimilitud,identificabilidad,recuperacion,olas}.py` |
| Pruebas | `tests/` (conteo: salida de `python -m pytest -q`; en el último commit de esta acta pasaron todas) |
| Parámetros con fuente | `config/parametros.yaml`; cruce generado: `reports/parametros_fuentes.md` |
| Medida (H5) | `config/medidas.yaml` |
| Recuperación sintética (parcial) | `reports/recuperacion_sintetica_casos.md` (generado; dice cuántas réplicas tiene cada celda) |
| Datos crudos de la recuperación | `reports/resultados/recuperacion/casos.jsonl` + manifiesto |
| Instrucciones de la corrida completa | `docs/correr_recuperacion.md` |
| Estado y siguientes pasos | `HANDOFF.md` |

## 3. Decisiones y por qué

De Omar (con fecha en `HANDOFF.md` §2): base remake + stoic; verosimilitud
semanal; semana epidemiológica; s0 = 1 → S0 = N·s0 − I0; D_ola1 supuesto
(Ganyani no es intrínseco); D_ola2 = original; D_ola5 = supuesto; malla
sintética (R0 corregida a {2, 3} porque {1.5, 3} con s0 = 0.6 daba
R_eff(0) < 1); serie hasta el 1 % del pico; frontera de ola en el domingo de
la semana del mínimo; "pico del periodo" = máximo global; sensibilidad de D
en lista con fuente; correr la recuperación completa en su computadora.

Numéricas (mías; registradas en el YAML o en el código, con su medición):
- IC95 por perfil como ceros de lp − l* (Venzon y Moolgavkar 1988, K02 p. 88)
  en lugar de malla fija: la malla no podía ubicar un IC más angosto que su
  paso y la primera réplica falló.
- Arranque de cada punto del perfil sobre la cresta de H1 (simetría de
  escala): el optimizador se quedaba varado lejos de la cresta.
- Puntos del perfil sin pulido Nelder-Mead (la MLE sí se pule): extremos del
  IC idénticos en las dos pruebas registradas en `parametros.yaml`
  (`perfil_pulir`), con menos evaluaciones.
- Tope numérico K_MAX para k de la NB: con datos Poisson la MLE de k tiende a
  infinito y el ajuste se desbordaba.

## 4. Cifras clave

Pendientes de la corrida completa. Con la corrida parcial,
`reports/recuperacion_sintetica_casos.md` ya muestra el patrón cualitativo
(R_eff(0) acotado, perfiles de R0 y s0 abiertos o cubriendo el rango no
identificable analítico, sobredispersión de Pearson alta cuando se ajusta
Poisson a datos NB), pero con pocas réplicas por celda: no es concluyente y
no se resume aquí. Al terminar la corrida completa, este apartado se llena
copiando las tablas generadas por `make resumen`.

## 5. Pendientes y riesgos

1. Corrida completa (Omar, en su computadora) y `make resumen`.
2. Umbral de "comparable" del criterio de rechazo de H1 (cociente de
   amplitudes relativas IC(R0)/IC(R_eff(0))): sin fijar. Debe fijarse antes de
   datos reales.
3. Red bloqueada (DOF, gob.mx, datos abiertos de la DGE): sin fecha
   verificada de la medida, sin N del truncado, sin olas reales ni Ola 1.
4. Fuentes con página sin verificar: BIC (sin fuente), Pearson y AIC (Pawitan,
   copia incompleta).
5. `INDICE.csv` del repo sin M07, J06, M23, M24, N08.
6. `incubacion_mediana` sigue en G01; la corrección de Omar (6.4 d es Backer,
   G03, media) no se aplicó porque solo afecta a H5 y falta decidir mediana o
   media.
7. Puntos de cambio de β (H5) no implementados.
8. Procedencia mixta posible en `casos.jsonl` (réplicas de la nube y de la
   computadora de Omar, mismo código y semillas); resultados de punto
   flotante pueden no ser idénticos entre máquinas. Se puede evitar borrando
   el archivo antes de la corrida completa.

## 6. Qué necesita la siguiente fase

- Resultados completos de la recuperación para decidir si NB o Poisson en la
  Ola 1 (I2) y para congelar el plan de análisis al cerrar F4.
- Red habilitada para DGE y DOF.

## 7. Para registrar en el chat 00 (bitácora y tablero)

1. Decisiones del 2026-11-04 y 2026-11-05 listadas en `HANDOFF.md` §2.
2. Desviación de calendario: la recuperación sintética completa no corrió en la
   nube (el contenedor se recicla al quedar inactivo); pasa a la computadora de
   Omar.
3. Corrección de diseño: malla R0 {1.5, 3} → {2, 3}.
4. Cambio del método numérico de los IC por perfil (malla → búsqueda de
   extremos) y del arranque de los perfiles; no cambian el criterio (umbral
   1.92) ni el plan.
5. Bloqueos abiertos: red (DOF, DGE), fuentes faltantes (BIC; Pawitan
   incompleto; claves M07, J06, M23, M24, N08 fuera de `INDICE.csv`), umbral de
   H1 sin fijar.
6. Estado: código y pruebas de F4 listos; Ola 1 real no iniciada (regla 3: no
   se toca hasta tener la recuperación sintética completa y la red).
