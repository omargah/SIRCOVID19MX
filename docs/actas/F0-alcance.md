# Acta F0 — Alcance

- **Fecha de cierre:** 2026-11-03
- **Etiqueta:** `v0.0`
- **Responsable:** Omar (trabajo personal, sin asesor)

## Qué se decidió

1. **Alcance:** rehacer el Proyecto Terminal 1 usando **solo el modelo SIR**,
   COVID-19 en México 2020–2023. Se descartan el encuadre de "espacio de
   fases / atractores / bifurcaciones" y el Monte Carlo con distribuciones
   triangulares de la versión anterior.
2. **Pregunta e hipótesis H1–H5:** como en el `README.md`. Estimandos y
   criterios de decisión en `docs/plan_analisis.md` (borrador).
3. **Método:** máxima verosimilitud con perfiles; bootstrap paramétrico;
   nada bayesiano. β constante por ola (H2) y por tramos (H5).
4. **Reglas 1–6** del `README.md`. Las reglas 1 y 2 se hacen cumplir en
   código: `scripts/make_numeros.py` genera todas las cifras del escrito y
   `src/datos.py::cargar_parametros` se niega a entregar un parámetro sin
   fuente o "pendiente" (probado en `tests/test_parametros.py`).
5. **Estructura del repositorio** fijada (ver `README.md`). Se agregaron,
   respecto a la lista original: `scripts/correr_sintetico.py` (separa el
   cálculo lento de la presentación), `Makefile`, `docs/plan_analisis.md` y
   `docs/desviaciones.md`.
6. **Código anterior:** `v0-anterior/` se conserva como archivo histórico
   (regla 5) pero no se reutiliza. Nada del código nuevo viene de ahí.
7. **Asesor:** el README anterior nombraba un asesor; se corrige a
   "trabajo personal, sin asesor".

## Qué se adelantó (no cierra ninguna fase)

Para comprobar que el método propuesto para H1 es viable antes de invertir
en datos, se escribió el núcleo numérico y se probó **solo con datos
sintéticos** (regla 3):

- `src/sir.py`, `src/verosimilitud.py`, `src/identificabilidad.py`.
- Tests contra resultados exactos: ecuación de tamaño final de
  Kermack–McKendrick, crecimiento exponencial inicial, media y varianza de la
  binomial negativa, conservación de la incidencia.
- Experimento sintético de H1 (ver sección siguiente).

Esto es trabajo de F2 (derivación) y F4 (validación). Esas fases siguen
abiertas.

## Resultado del experimento sintético de H1

Las cifras están en `reports/numeros.tex` (generado); aquí solo se
describen, para no copiar números a mano.

- **Resultado analítico nuevo para el plan:** con subregistro ρ desconocido,
  el SIR tiene una simetría de escala exacta
  `(R0, s0, i0, ρ) → (c·R0, s0/c, i0/c, c·ρ)` que deja idénticos los casos
  esperados. H1 es entonces una no identificabilidad **estructural**, no solo
  práctica, y el rango indistinguible de R0 es `[R0·s0, R0/ρ]`. Demostración en
  `src/identificabilidad.py` y `escrito/capitulos/identificabilidad.tex`;
  verificación numérica en `tests/test_identificabilidad.py`.
- **Casos solos:** R_eff(0) se recupera; el perfil de R0 es plano en todo el
  rango predicho y cae justo en sus bordes (`reports/figuras/perfil_R0_sintetico.pdf`).
- **Casos + una encuesta serológica:** la simetría se rompe; el intervalo de
  perfil de R0 se cierra y contiene el valor verdadero.

## Revisión crítica

1. **El criterio original de H1 estaba mal.** El borrador decía "no
   identificable si el IC de perfil es abierto". En el experimento el IC de
   R0 con casos solos sale *finito*, porque lo cierran las restricciones
   s0 ≤ 1 y ρ ≤ 1. Se corrigió el criterio en `docs/plan_analisis.md` (aún no
   congelado, así que no es desviación).
2. **El bootstrap paramétrico engaña en direcciones no identificables.** Con
   casos solos, el intervalo bootstrap de R0 salió angostísimo y sin la
   verdad: las réplicas arrancan en la MLE y el optimizador no se mueve sobre
   una cresta plana. No se borró el número (regla 5); se reporta en el escrito
   como modo de falla. Regla adoptada: bootstrap solo para combinaciones
   identificables, y siempre después del perfil.
3. **H3 depende de H1.** El tamaño final en fracción de población también se
   escala por 1/c, así que con casos solos no está identificado. H3 solo se
   puede probar fijando s0 = 1 en la ola 1 o usando la serología en el ajuste
   (y entonces no es prueba independiente). Decisión pendiente en el plan.
4. **Una sola realización sintética no valida un método.** Falta estimar
   cobertura con muchas réplicas (F4).
5. **Riesgos de datos** que el plan anota y F3 debe atender: versiones
   históricas de la base SSA para H4 (si no, el desempeño "en tiempo real" es
   optimista); vacunación y anticuerpos anti-S para H3 en olas 2021+; ρ que
   cambia con la política de pruebas (confunde H2 y H5); fecha de síntomas vs
   fecha de infección para H5.
6. **Parámetros reales pendientes.** γ y N de México están `pendiente` en
   `config/parametros.yaml` porque sus fuentes aún no están fichadas
   (regla de bibliografía: sin PDF leído no hay cita). El código se niega a
   correr con ellos hasta que se llenen.
7. **Regla 6.** El núcleo tiene ~400 líneas comentadas. Omar debe leerlas y
   poder explicar cada una antes de cerrar F2; cualquier línea que no pueda
   defender se reescribe o se quita.

## Pendientes que pasan a la siguiente fase

- F1: fichar G01, G04, G08 (γ, incubación), I01, I03 (ENSANUT), M02 (WIS).
- F2: revisar la derivación de la simetría; buscar en J01/J03 si ya está
  publicada y citarla.
- F3: descarga registrada (URL, fecha, SHA-256), regla de olas fijada antes de ajustar.
- F4: validación sintética de H2–H5 y estudio de cobertura; congelar el plan.

## Verificación

- `make test`: todas las pruebas pasan.
- `make`: regenera `reports/numeros.tex`, figuras y tablas desde
  `reports/resultados/sintetico_h1.json`.
