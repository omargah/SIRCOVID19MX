# Parámetros y su fuente

Generado por `scripts/listar_supuestos.py` desde `config/parametros.yaml` (validado por `src/datos.py`). No editar a mano.

## Sección `sintetico`

Entradas: 18; supuestos (sin fuente, entran a sensibilidad): 0; con valor pendiente (null): 0.

| parámetro | valor | ¿fuente? | fuente o justificación |
|---|---|---|---|
| `semilla` | 20200228 | sí | regla: Semilla fija para reproducibilidad; cualquier entero sirve. |
| `N` | 10000000.0 | sí | regla: Valor de diseño: población del orden de una zona metropolitana grande. |
| `gamma` | 0.14285714285714285 | sí | regla: Valor de diseño: periodo infeccioso medio de 7 días, gamma = 1/7. Es la verdad conocida del experimento; se usa igual para simular y para ajustar. |
| `R0` | 2.5 | sí | regla: Valor de diseño (verdad conocida para F4). |
| `s0` | 0.6 | sí | regla: Valor de diseño (verdad conocida para F4). s0 < 1 para que la simetría de H1 sea visible. |
| `i0` | 1e-05 | sí | regla: Valor de diseño: 100 infecciosos en N = 1e7. |
| `rho` | 0.1 | sí | regla: Valor de diseño: se reporta 1 de cada 10 infecciones. |
| `k` | 20.0 | sí | regla: Valor de diseño: sobredispersión moderada (Var = mu + mu^2/20). |
| `n_semanas` | 30 | sí | regla: Valor de diseño: cubre crecimiento, pico y descenso con los valores de arriba. |
| `sero` | [[0.0, 182.0, None, 0.007]] | sí | regla: Diseño: ee = sqrt(p(1-p)/n), p = 0.3, n = 5000 -> 0.0065, redondeado a 0.007. delta_obs (null) se simula. |
| `B_bootstrap` | 200 | sí | regla: 200 réplicas: error Monte Carlo de un percentil 2.5% ~ sqrt(0.025*0.975/200) ~ 0.011 en probabilidad; suficiente para validar el método. |
| `malla_R0` | [2.0, 3.0] | sí | regla: Diseño: R0 en {2, 3}. Se corrigió {1.5, 3} porque R0 = 1.5 con s0 = 0.6 da R_eff(0) = 0.9 < 1 (sin ola). Decisión de Omar 2026-11-04. |
| `malla_s0` | [0.6, 1.0] | sí | regla: Diseño: s0 = 0.6 (ola posterior, simetría de H1 visible) y s0 = 1 (ola 1, nadie inmune). Decisión de Omar 2026-11-04. |
| `malla_D` | [4.7, 6.84] | sí | regla: Diseño: los extremos de los D base con fuente (D_ola3 = 4.7, G05; D_ola4 = 6.84, G06). gamma = 1/D en cada escenario. |
| `replicas` | 50 | sí | regla: 50 réplicas por escenario: error Monte Carlo de una cobertura de 0.95 ~ sqrt(0.95*0.05/50) ~ 0.03. Decisión de Omar 2026-11-04. |
| `fin_ola_fraccion_pico` | 0.01 | sí | regla: Cada serie termina en la primera semana después del pico en que la incidencia ESPERADA (sin ruido) baja del 1 % del pico. Decisión de Omar 2026-11-04. |
| `perfil_paso_inicial` | 0.002 | sí | regla: IC95 por perfil buscando los extremos (K02 p. 88): desde la MLE, pasos b = v*exp(+-0.002*2^j) hasta cruzar lmax - 1.92 o llegar al límite. Reemplaza la malla fija de 21 puntos, que no podía ubicar un IC más angosto que su paso (falló en la primera réplica, 2026-11-04). Límites: R0 en [0.8*Reff, 1.5*Reff/(rho*s0)], s0 en [0.7*rho*s0, 1], Reff en [0.5, 2]*Reff (src/recuperacion.py::limites_perfil). |
| `perfil_biseccion` | 8 | sí | regla: 8 bisecciones (en escala log) entre el último punto dentro y el primero fuera del umbral: el extremo queda dentro de 2^-8 del intervalo de cruce. |

## Sección `real`

Entradas: 19; supuestos (sin fuente, entran a sensibilidad): 11; con valor pendiente (null): 12.

| parámetro | valor | ¿fuente? | fuente o justificación |
|---|---|---|---|
| `N` | 126014024 | sí | INEGI, Censo de Población y Vivienda 2020 (2020), Población total, fecha de referencia 15 de marzo de 2020 (tabulados del cuestionario básico) |
| `N_conapo_2021` | pendiente | **supuesto** | Alternativa a N para olas 2021-2022: proyección de población a mitad de año de CONAPO. Copiar cifra y cuadro de la hoja Parámetros. (candidata: CONAPO) |
| `D_ola1` | 5.2 | **supuesto** | No hay GI intrínseco del linaje ancestral en la bibliografía con PDF. G02 (Ganyani 2020) estima 5.20 d en Singapur con aislamiento y cuarentena vigentes (p. 1) y sin corregir el acortamiento por agotamiento de susceptibles (p. 6): no es intrínseco. Decisión de Omar 2026-11-04: se usa como supuesto con sensibilidad. (candidata: G02) |
| `D_ola2` | 5.2 | **supuesto** | Linaje ancestral; B.1.1.519 no tiene GI propio en la bibliografía. Regla: D_ola2 = D_ola1 (hereda que G02 no es intrínseco). Alpha (G05) no dominó ninguna ola en México: entra solo a la sensibilidad. Decisión de Omar 2026-11-04. (candidata: G02) |
| `D_ola3` | 4.7 | sí | G05, p. 603 (Summary); p. 606 (Results) |
| `D_ola4` | 6.84 | sí | G06, p. 1 (Summary, Findings); Tabla 2 |
| `D_ola5` | 6.84 | **supuesto** | Sin GI intrínseco de BA.2/BA.5 en la bibliografía. Regla: D_ola5 = D_ola4 (valor de BA.1, G06). Decisión de Omar 2026-11-04. (candidata: G06) |
| `incubacion_mediana` | pendiente | **supuesto** | Retraso infección->síntomas para correr la fecha de cambio tau de H5. Copiar valor y página de G01 (Lauer et al. 2020). No se usa en el SIR. (candidata: G01) |
| `sero_ensanut2020` | pendiente | **supuesto** | Seroprevalencia nacional anti-SARS-CoV-2, ENSANUT 2020 Covid-19. Copiar estimación puntual, IC 95% y página de I03 (Basto-Abreu et al. 2022). (candidata: I03) |
| `sero_ensanut2020_ee` | pendiente | sí | regla: ee = (lim_sup - lim_inf) / (2*1.96) con el IC 95% publicado de sero_ensanut2020. |
| `sero_ensanut2022` | pendiente | **supuesto** | Seroprevalencia ENSANUT 2022 (distinguir anti-N de anti-S por la vacunación). Copiar cifra, anticuerpo y página de I01 (Carnalla et al. 2023). (candidata: I01) |
| `sero_ensanut2022_ee` | pendiente | sí | regla: ee = (lim_sup - lim_inf) / (2*1.96) con el IC 95% publicado de sero_ensanut2022. |
| `s0_ola1` | 1.0 | sí | regla: Virus nuevo en 2020: sin inmunidad previa, S0 = N. Además rompe la simetría de escala de H1 (plan_analisis.md, nota 1). |
| `s0_ola2` | pendiente | sí | regla: s0 = 1 - sero_ensanut2020 (fracción no infectada al inicio de la ola 2; ENSANUT 2020 se levantó entre olas 1 y 2). |
| `s0_ola3` | pendiente | **supuesto** | Tras la vacunación (2021) S0 depende de infección + vacuna; no hay encuesta nacional justo antes de la ola 3. Se estima o se barre. |
| `s0_ola4` | pendiente | **supuesto** | Ómicron escapa parcialmente a la inmunidad previa; S0 efectivo no observable directamente. Se estima o se barre. |
| `s0_ola5` | pendiente | **supuesto** | Posterior a ENSANUT 2022 / BA.1; S0 efectivo para BA.5 sin medición directa. Se estima o se barre. |
| `rho_ola1` | pendiente | sí | regla: rho = casos confirmados acumulados (SSA) desde el inicio de la ola 1 hasta la fecha media de ENSANUT 2020 / (sero_ensanut2020 * N). Casos: data/raw (F3). |
| `rho_ola2_5` | pendiente | **supuesto** | Sin encuesta serológica que acote cada ola posterior por separado y con cambios en la política de pruebas; rho se estima libre en cada ola y se barre en este rango. |

