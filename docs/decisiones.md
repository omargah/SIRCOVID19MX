# Registro de decisiones (F4 · validación sintética)

Fecha de registro: 2026-11-04. Estas decisiones se fijaron **antes** de escribir el
código de `sirmx/` y gobiernan las pruebas de `tests/`. Cualquier cambio posterior
se agrega como entrada nueva con fecha; no se edita lo ya escrito.

> **Nota sobre I2, I3, I4.** La solicitud pedía resolver "los issues abiertos I2, I3, I4
> (abajo)", pero su texto no venía en el mensaje y no existen issues en el repositorio
> GitHub. Abajo se resuelven las tres decisiones abiertas que el plan de análisis
> necesita para poder programarse: (I2) qué se estima y qué se fija, (I3) el periodo
> infeccioso D y la conversión r→R, (I4) los criterios de "recuperado" y la selección
> de puntos de cambio. **Si los I2–I4 originales eran otros, hay que confrontarlos con
> esta lista antes de usar datos reales.**

---

## D0. Convenciones del modelo (no controvertidas)

- SIR determinista en fracciones, `s' = -β(t) s i`, `i' = β(t) s i − γ i`, γ = 1/D.
  Integración RK4 con 4 subpasos por día; β(t) constante por tramos en días enteros.
- Incidencia diaria de infecciones: `inc_t = N·(s(t) − s(t+1))`, t = 0,…,T−1.
- Observación: `casos_t ~ BinNeg(media μ_t, dispersión k)`, `Var = μ + μ²/k`, con
  `μ_t = ρ · inc_t · w_{(t + d0) mod 7}`.
- Efecto de día de semana multiplicativo, `log w_d` con suma cero (media geométrica 1):
  6 parámetros libres. `d0` es el día de la semana del primer dato (conocido).
- **Sin convolución de retraso de reporte.** Un retraso fijo desplaza la serie en el
  tiempo y no altera R_eff(0), r ni ρ. Se documenta como limitación para datos reales,
  porque un retraso con dispersión suaviza el pico.
- N se considera conocida (población).

## I2. Parámetros estimables y parametrización del ajuste

**Hecho matemático (verificado numéricamente en `tests/test_4_perfiles.py`).** Si se
reescalan `x = s/s0` y `j = i/s0`, el sistema queda `x' = −(R0·s0) γ x j`,
`j' = (R0·s0) γ x j − γ j`, con `x(0) = 1`, `j(0) = i0/s0`, y los casos esperados son
`ρ·s0·N·(−Δx)`. Es decir, con solo casos la verosimilitud depende de (R0, s0, ρ, i0)
**únicamente** a través de

- `R_eff(0) = R0·s0`
- `ρ·s0` (escala de reporte efectiva)
- `i0/s0` (fracción inicial de infecciosos relativa a los susceptibles)

**Decisión.** El ajuste por ola (MLE) usa la parametrización identificable
`θ = (log R_eff(0), log(i0/s0), log(ρ·s0), log k, 6 log w_d, log-factores de cambio de β)`.
R0, s0 y ρ por separado **no** se reportan a partir de casos solos. ρ se obtiene solo si
s0 viene de fuera (primera ola: s0 ≈ 1; olas siguientes: seroprevalencia ENSANUT), como
`ρ = (ρ·s0)/s0`, y la incertidumbre de s0 se propaga. Restricciones físicas que acotan
la cresta: `s0 ≤ 1` y `ρ ≤ 1`, de modo que `R0 ∈ [R_eff(0), R_eff(0)/(ρ·s0)]`.

- Ajuste: L-BFGS-B sobre parámetros transformados (sin cotas activas en el interior),
  **8 inicios aleatorios** (generador con semilla). Se toma el mejor y se reporta
  cuántos inicios quedaron a ≤ 0.5 de log-verosimilitud del mejor (diagnóstico de
  multimodalidad).
- Intervalos: Wald al 95 % en escala transformada, con hessiana numérica por
  diferencias centrales. Para R_eff(0), R0 y s0 también hay perfiles de verosimilitud
  (umbral χ²₁: 1.92).

## I3. Periodo infeccioso D y conversión r → R

- **D no se estima**: se fija. Con casos y ρ desconocido, la información sobre γ
  viene solo de la curvatura de la caída y se confunde con cambios de β (H2). Valor
  base D = 7 días; escenarios de sensibilidad **D ∈ {5, 7, 10}** días.
- Conversión SIR (periodo infeccioso exponencial, Wallinga–Lipsitch):
  `R = 1 + r·D`. Se reporta la tabla R(D) para los tres valores de D.
- **r con ventana fija**: 21 días a partir del primer día en que el promedio móvil
  de 7 días alcanza 20 casos. Modelo: BinNeg con `log μ_t = a + r·t + log w_{dow}`.
  Intervalos: (a) perfil de verosimilitud de r; (b) bootstrap paramétrico, B = 200,
  percentiles 2.5–97.5. La longitud y el umbral **no** se ajustan después de ver datos.
- El r "verdadero" contra el que se compara es el promedio en la ventana de
  `γ(R0·s(t) − 1)`, la tasa instantánea de crecimiento de la incidencia en el SIR.

## I4. Criterios de recuperación, puntos de cambio y pronóstico

**Recuperación (paso 3, condición para avanzar).** En cada escenario, con la semilla
fijada de antemano (20261104):

1. el valor real de R_eff(0), ρ·s0, i0/s0, k y de cada factor de cambio de β cae dentro
   de su IC 95 %;
2. el error relativo en R_eff(0), ρ·s0 y en el factor de cambio es < 10 %;
3. cada log w_d tiene un error absoluto < 0.1;
4. estudio de cobertura (`scripts/validacion_sintetica.py`, 40 réplicas por
   escenario): la cobertura del IC 95 % de R_eff(0) y ρ·s0 está entre 0.85 y 1.00.

Si alguno falla, se corrige el método y **no** se pasa a los pasos 4–7.

**Puntos de cambio de β (paso 6).**
- β(t) constante por tramos con K ∈ {0, 1, 2} cambios en días enteros τ_j, con
  factores multiplicativos exp(δ_j).
- Búsqueda de τ: rejilla cada 2 días con arranque en caliente, refinamiento ±2 días.
  Para K = 2: descenso coordenado alternando τ1 y τ2 (separación mínima: 5 días).
- Selección de K por **BIC**, contando cada cambio como 2 parámetros (τ y δ).
- IC de τ: conjunto de días con `2·(ℓ̂ − ℓ(τ)) ≤ 3.84` (perfil). IC de δ: Wald en τ̂.
- Éxito: |τ̂ − τ| ≤ 3 días, el factor real está en su IC, y BIC elige el K correcto,
  incluido K = 0 en un escenario sin cambio y K = 2 con cambios separados 10 días.

**Pronóstico en tiempo simulado (paso 7).**
- Orígenes semanales; en cada uno el modelo se ajusta **solo** con datos hasta ese día.
- Objetivo: casos semanales a 1, 2, 3 y 4 semanas.
- Distribución predictiva: 300 trayectorias con parámetros muestreados de la normal
  de Wald más ruido BinNeg diario, agregadas por semana; 23 cuantiles estándar
  (0.01, 0.025, 0.05, 0.10, …, 0.95, 0.975, 0.99).
- Métricas: WIS (Bracher et al. 2021), cobertura empírica del 50 % y del 95 %, y
  error del pico (fecha en días y altura relativa) usando la proyección completa.
- Referencia: persistencia (mediana = último valor semanal, cuantiles a partir de las
  diferencias semanales pasadas simetrizadas, sumadas h veces, al estilo del baseline
  del COVID-19 Forecast Hub). Pico por persistencia: la semana actual y su valor.
- Éxito en el escenario de ola simple: WIS medio del modelo < WIS de persistencia,
  cobertura del 95 % ≥ 0.80 y error medio absoluto de la fecha del pico menor que el de
  persistencia.

**Reproducibilidad (paso 8).** Toda aleatoriedad pasa por `numpy.random.Generator`
creado con semilla explícita; no se usa estado global. Prueba: dos corridas con la
misma semilla dan resultados idénticos bit a bit, y una semilla distinta da otro
resultado.

---

## Correcciones durante la implementación (2026-11-04)

- **C1 (I2).** La primera versión de I2 reescalaba solo `x = s/s0` y afirmaba que i0 era
  identificable. Es falso: la reescala correcta también divide i (`j = i/s0`), y lo
  identificable es `i0/s0`. Se detectó en el paso 3: en el escenario de subregistro
  (s0 = 0.8), log i0 salía sesgado en +0.215 ≈ log(1/0.8). Se corrigieron el texto de
  arriba y el código; la decisión de fondo (ajustar solo combinaciones identificables)
  no cambia.
- **C2 (escenarios).** En el escenario de ola simple se cambió ρ = 1 por ρ = 0.5. Con
  ρ = 1 y s0 = 1, el valor real ρ·s0 = 1 queda en la cota ρ ≤ 1, donde el IC de Wald no
  es válido (caso no regular). No es un ajuste a conveniencia: el criterio del paso 3
  presupone parámetros interiores.
- **C3 (I4, puntos de cambio).** Resultado contra el criterio preregistrado: **falla** la
  parte "BIC elige K = 2 con cambios separados 10 días". Con dos factores de 0.7 en los
  días 35 y 45, el par real solo mejora ℓ en 3.3 sobre un cambio único de ≈0.49, y la
  penalización BIC de 2 parámetros es log(200) ≈ 10.6; la diferencia de BIC queda en 0.9.
  Es un límite de información, no de búsqueda (el mejor ajuste K = 2 sí está en (35, 44)).
  Con 15, 20 y 30 días de separación, BIC elige K = 2 y |τ̂ − τ| ≤ 1. El límite de
  resolución, en estas condiciones (k = 20, ~10⁴–10⁵ casos/día), está entre 10 y 15 días.
  Cambios al método hechos **después** de ver la primera corrida, y por eso registrados:
  (a) en K = 2, además del arranque codicioso, se prueban arranques que parten τ̂(K=1) en
  (τ̂ − s, τ̂ + s) con s ∈ {3, 5, 8, 12} (antes, la búsqueda acababa en (39, 88)); (b) la
  rejilla de τ se limita a los días con media móvil ≥ 5 % del máximo (fuera de ahí β no es
  informable). La prueba del caso de 10 días documenta el límite; no lo presenta como
  éxito.
- **C4 (I3, r).** En una ventana de 21 días con conteos bajos, el MLE de k está muy
  sesgado hacia arriba (mediana 59 cuando el real es 20). Por eso los IC de r salían
  cortos: cobertura 0.88 (perfil) y 0.86 (bootstrap). Agrandar la ventana a 28 días o
  usar el umbral F(1, n−p) no lo resolvía (≤ 0.90). **Decisión:** en la estimación de r,
  k se fija en el valor del ajuste de la ola completa (paso 2), donde está bien estimado.
  Cobertura resultante: 0.956 (perfil) y 0.931 (bootstrap). La ventana se mantiene en 21
  días, como se preregistró.
- **C5 (I4, pronóstico).** El criterio preregistrado (ola simple) se cumple. En el
  escenario con cambio de β, el pronóstico con β constante **es peor que la persistencia**
  (WIS relativo 1.86, cobertura del 95 % de 0.16): queda sobreconfiado y sesgado después
  del cambio. Esto no era un criterio de paso, pero es evidencia directa del riesgo de H2
  para pronosticar. **Consecuencia para el plan:** en datos reales, el pronóstico debe usar
  el modelo con los cambios detectados hasta el origen (paso 6 en tiempo real); queda como
  tarea pendiente y debe validarse en sintéticos antes de usarse.
- **C6 (implementación).** El bucle RK4 se compila con numba (opcional; es bit a bit
  idéntico a la versión en Python, ver prueba). Se usa 1 hilo de BLAS por proceso, porque
  con 4 hilos L-BFGS-B es ~4× más lento. El paralelismo usa `multiprocessing` con `spawn`.
- **C7 (paso 3).** En el paso 3, τ se trata como conocido; la estimación de τ se valida
  aparte en el paso 6.
