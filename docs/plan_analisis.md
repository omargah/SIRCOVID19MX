# Plan de análisis — BORRADOR

> **Estado:** borrador. Se congela al cerrar F4 (regla 4). Después de congelarlo,
> todo cambio va a `docs/desviaciones.md` con fecha, qué cambió y por qué.
> Antes de congelarlo se puede editar libremente, pero cada cambio queda en
> el historial de git.

## Pregunta

¿Qué parte de la dinámica de COVID-19 en México 2020–2023 es consistente con
un SIR de parámetros constantes? ¿Qué parámetros son identificables con
casos + serología? ¿Qué tan útil habría sido el SIR en tiempo real? ¿Cuándo
cambió la transmisión respecto a las medidas de la SSA?

## Modelo común

SIR determinista por ola, en fracciones de población (`src/sir.py`):

- Estado: s, i (r por conservación). β = R0·γ.
- Observación: casos semanales confirmados por fecha de inicio de síntomas,
  `y_k ~ BinNeg(media ρ·N·[s(t_k) − s(t_{k+1})], tamaño k)`.
- Serología: aumento de seroprevalencia entre dos encuestas,
  `Δ_obs ~ Normal(s(t_a) − s(t_b), ee²)`.
- Parámetros estimados por ola: R0, s0, i0, ρ, k. Fijos con fuente: γ, N.
- Estimación: máxima verosimilitud (`src/verosimilitud.py`); intervalos por
  perfil (Wilks, umbral 1.92) y por bootstrap paramétrico (percentiles).
  Nada bayesiano.

## Hipótesis, estimando y criterio

| H | Afirmación | Estimando / prueba | Criterio de decisión | Validación sintética (F4) |
|---|---|---|---|---|
| H1 | R0 y S0 no identificables por separado; solo R_eff(0)=R0·s0 | Perfil de R0 con casos solos y con casos + serología | No identificable si el perfil es plano (caída < 0.1 en log-verosimilitud) en un intervalo cuyos extremos coinciden con las cotas impuestas por s0 ≤ 1 y ρ ≤ 1, y no por los datos. ("IC abierto" no sirve: las cotas lo cierran — ver acta F0) | **Hecho (adelantado):** simetría exacta verificada; perfil plano en [R0·s0, R0/ρ]; con serología el IC se cierra |
| H2 | β constante por ola deja residuos sistemáticos | Residuos cuantil-aleatorizados de la BinNeg; autocorrelación (Ljung–Box) y prueba de rachas; comparación con β por tramos (razón de verosimilitudes / AIC) | Sistemático si Ljung–Box rechaza al 5 % **y** el modelo por tramos mejora el AIC | Pendiente: tasa de rechazo ≈ 5 % con β constante verdadero; potencia con un cambio de β conocido |
| H3 | El tamaño final sobrestima el aumento de seroprevalencia (ENSANUT) | Tamaño final predicho vs Δ seroprevalencia ENSANUT | Sobrestima si el IC del cociente predicho/observado está por encima de 1 | Pendiente. **Ver nota crítica abajo** |
| H4a | El SIR supera a la persistencia a 1–2 semanas | WIS (Bracher et al. 2021, M02) promedio con origen móvil, SIR vs persistencia | Supera si el cociente de WIS < 1 con IC (bootstrap por bloques de semanas) por debajo de 1 | Pendiente |
| H4b | El SIR no estabiliza la fecha del pico antes de que ocurra | Fecha de pico predicha en cada origen | "Estabiliza" = a partir de cierto origen, todas las predicciones quedan a ±1 semana del pico observado. H4b se sostiene si ese origen es posterior al pico | Pendiente |
| H5 | La transmisión bajó después de la JNSD, no antes | β por tramos en la ola 1 con fecha de cambio τ estimada por perfil | Se sostiene si el IC de perfil de τ (corrido a fecha de infección) queda después del inicio de la JNSD | Pendiente: recuperar τ conocido |

## Notas críticas que el plan debe resolver antes de congelarse

1. **H3 depende de H1.** Bajo la simetría de escala, el tamaño final en
   *fracción de población* también se divide entre c, así que con casos
   solos **no está identificado**. H3 solo es comprobable (a) fijando s0 = 1
   en la ola 1 (población sin inmunidad previa), lo que rompe la simetría, o
   (b) usando la serología en el ajuste — pero entonces no es una prueba
   independiente. Decisión pendiente; propuesta: (a) para la ola 1 y
   reportar las demás olas como condicionales a s0.
2. **Vacunación (2021+).** La seroprevalencia anti-S mezcla infección y
   vacuna. Para olas posteriores hay que usar anti-N o ajustar; si no hay
   cómo, H3 se limita a la ola 1.
3. **Tiempo real (H4) exige versiones históricas de los datos.** Los datos
   abiertos de la SSA se revisan con retraso; usar la base final como si
   fuera la disponible en ese momento sobrestima el desempeño. F3 debe
   conseguir versiones fechadas o modelar el retraso; si no, H4 se reporta
   como cota optimista.
4. **γ fijo.** Todos los resultados son condicionales a γ. Plan: análisis de
   sensibilidad con el rango de γ de la literatura (fuente en
   `config/parametros.yaml`).
5. **Fecha de síntomas vs fecha de infección (H5).** τ se estima en tiempo
   de síntomas; para compararlo con la JNSD hay que restar el periodo de
   incubación (parámetro con fuente, pendiente: G01 Lauer et al. 2020).
6. **ρ constante dentro de la ola.** Cambios en la política de pruebas
   alteran ρ y pueden confundirse con cambios de β (H2, H5). Se discutirá;
   la positividad de pruebas puede servir de diagnóstico en F3.
7. **Bootstrap paramétrico supone el modelo correcto.** Si H2 se confirma
   (residuos sistemáticos), los intervalos del modelo de β constante son
   demasiado angostos. Se reportará junto con H2. Además, en direcciones no
   identificables el bootstrap da intervalos falsamente angostos (ver acta
   F0): solo se reporta para combinaciones identificables.
9. **Cobertura.** F4 debe estimar la cobertura real de los IC de perfil y
   bootstrap con muchas réplicas sintéticas (no una sola), al menos para
   R_eff(0), y con γ mal especificado para ver la sensibilidad.
8. **Definición de olas.** La regla para delimitar olas (`src/olas.py`) se
   fija en F3 antes de cualquier ajuste y no se cambia según el ajuste.
