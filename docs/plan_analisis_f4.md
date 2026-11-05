# Plan de análisis (F5 · datos reales) — CONGELADO

**Congelado el 2026-11-04**, en el commit que introduce este archivo (rama
`claude/kind-newton-2qjan7`). Las decisiones y sus justificaciones están en
`docs/decisiones.md` (D0, I2–I4, C1–C7); la evidencia sintética, en
`docs/validacion_sintetica.md`. Todo cambio posterior se registra como enmienda fechada al
final de este archivo, **antes** de mirar el resultado afectado.

Condición de congelamiento: las 40 pruebas de `tests/` pasan
(`OPENBLAS_NUM_THREADS=1 python3 -m pytest -n 4`), sin haber leído ningún dato real.

> Pendiente de confirmar: el texto original de los issues I2, I3, I4 no llegó con la
> solicitud. Si difiere de lo resuelto en `docs/decisiones.md`, se enmienda este plan
> antes de abrir los datos.

## 1. Unidad de análisis
Cada ola por separado. Las fechas de inicio y fin de cada ola se fijan **antes** del
ajuste, a partir de un criterio sobre la serie suavizada (fuera del alcance de F4; se
registrará como enmienda A1 antes de F5). N es la población nacional (CONAPO).

## 2. Modelo y observación (pasos 1–2)
- SIR de una cepa por ola, `μ_t = ρ · inc_t · w_{dow(t)}`, `casos_t ~ BinNeg(μ_t, k)`,
  con un efecto multiplicativo por día de la semana (suma cero en escala log).
- MLE en la parametrización identificable `(R_eff(0), i0/s0, ρ·s0, k, w, δ)`, con 8 inicios
  aleatorios e IC de Wald al 95 %. Diagnósticos obligatorios: número de inicios que llegan
  al mejor óptimo y parámetros en cota.
- D fijo: valor base de 7 días; sensibilidad con D ∈ {5, 7, 10}.

## 3. Qué se reporta y qué no (paso 4, H1)
- Se reportan R_eff(0), ρ·s0, i0/s0 y k con su IC.
- **No** se reportan R0, s0 ni ρ por separado a partir de casos solos: su perfil es
  exactamente plano (cresta de H1, demostrada en sintéticos). Solo se reportan si s0 viene
  de fuera: primera ola s0 = 1; en las siguientes, seroprevalencia ENSANUT, propagando su
  incertidumbre. Para cada ola se presentan los perfiles de R0 y s0 que muestran la cresta.

## 4. Crecimiento temprano (paso 5)
- r en una ventana fija de 21 días desde el primer día con media móvil de 7 días ≥ 20
  casos. BinNeg log-lineal con día de la semana y k fijado del ajuste de la ola (C4).
- IC por perfil y por bootstrap paramétrico (B = 200). Tabla R(D) = 1 + r·D para
  D ∈ {5, 7, 10}. No se modifican la ventana ni el umbral después de ver los datos.

## 5. Cambios de β (paso 6, H2)
- K ∈ {0, 1, 2} cambios, elegidos por BIC; τ en la rejilla de días activos (paso 2 +
  refinamiento diario) y la búsqueda de K = 2 descrita en C3.
- Se reportan τ̂ con su IC de perfil y el factor exp(δ) con su IC de Wald.
- **Límite de interpretación:** dos cambios separados por menos de ~15 días pueden
  aparecer como uno solo, con un factor ≈ el producto de ambos. No se interpreta un
  cambio único como "una sola medida".
- H2 se evalúa con: (a) ΔBIC entre K = 0 y el K elegido; (b) residuos de Pearson del
  modelo con K = 0 (autocorrelación y rachas).

## 6. Pronóstico retrospectivo (paso 7)
- Orígenes semanales y datos solo hasta el origen. Horizontes de 1 a 4 semanas; 23
  cuantiles; WIS, coberturas del 50 % y 95 % y error del pico, contra la persistencia.
- Por C5, el modelo con β constante **no** es aceptable si hay cambios de β; antes de F5
  debe validarse en sintéticos el pronóstico con cambios detectados en tiempo real
  (enmienda A2). Mientras tanto, los pronósticos del SIR con β constante se reportan
  como lo que son: una referencia que se sabe frágil.

## 7. Reproducibilidad (paso 8)
- Toda la aleatoriedad pasa por `numpy.random.default_rng(semilla)`; la semilla global del
  proyecto es 20261104. La misma semilla da resultados idénticos bit a bit, también entre
  procesos (lo verifica una prueba).
- Versiones: Python 3.13, numpy 2.5, scipy 1.18, numba 0.68 (`requirements.txt`).

## 8. Limitaciones conocidas (aceptadas)
- Sin retraso de reporte modelado (solo desplazamiento temporal); sin heterogeneidad ni
  cambios de ρ dentro de una ola. Un cambio de ρ dentro de una ola sería indistinguible de
  un cambio de β en la escala de los casos.
- D no se estima.

## Enmiendas
_(ninguna)_
