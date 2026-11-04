# Validación sintética (F4)

Generado por `scripts/validacion_sintetica.py` con semilla 20261104. Solo datos simulados; ningún dato real se leyó.

## Paso 3 · Valor real vs estimado (IC 95 % de Wald)

τ se toma como conocido (la detección de τ es el paso 6).

### ola_simple

Inicios: 8; a ≤ 0.5 de log-verosimilitud del mejor: 8. log-verosimilitud = -1447.90.

| parámetro | real | estimado | IC 95 % | ¿cubre? | error rel. |
|---|---|---|---|---|---|
| R_eff(0) | 2 | 2.01 | [1.995, 2.024] | sí | +0.5 % |
| i0/s0 | 1e-05 | 8.894e-06 | [7.769e-06, 1.018e-05] | sí | -11.1 % |
| rho*s0 | 0.5 | 0.5233 | [0.4964, 0.5517] | sí | +4.7 % |
| k | 20 | 18.72 | [15.06, 23.28] | sí | -6.4 % |
| w_0 | 1.191 | 1.163 | [1.07, 1.264] | sí | -2.4 % |
| w_1 | 1.14 | 1.091 | [1.003, 1.187] | sí | -4.3 % |
| w_2 | 1.088 | 1.104 | [1.016, 1.2] | sí | +1.5 % |
| w_3 | 1.088 | 1.046 | [0.9627, 1.137] | sí | -3.8 % |
| w_4 | 1.036 | 1.107 | [1.018, 1.204] | sí | +6.9 % |
| w_5 | 0.8288 | 0.8464 | [0.7778, 0.9211] | sí | +2.1 % |
| rho (s0 conocido) | 0.5 | 0.5233 | [0.4964, 0.5517] | sí | +4.7 % |
| R0 (s0 conocido) | 2 | 2.01 | [1.995, 2.024] | sí | +0.5 % |

### subregistro

Inicios: 8; a ≤ 0.5 de log-verosimilitud del mejor: 8. log-verosimilitud = -1186.78.

| parámetro | real | estimado | IC 95 % | ¿cubre? | error rel. |
|---|---|---|---|---|---|
| R_eff(0) | 2 | 2.003 | [1.986, 2.02] | sí | +0.1 % |
| i0/s0 | 2.5e-05 | 2.348e-05 | [2.023e-05, 2.726e-05] | sí | -6.1 % |
| rho*s0 | 0.12 | 0.1242 | [0.1175, 0.1314] | sí | +3.5 % |
| k | 20 | 17.19 | [13.57, 21.77] | sí | -14.1 % |
| w_0 | 1.191 | 1.169 | [1.065, 1.283] | sí | -1.9 % |
| w_1 | 1.14 | 1.058 | [0.9636, 1.161] | sí | -7.2 % |
| w_2 | 1.088 | 1.118 | [1.019, 1.227] | sí | +2.8 % |
| w_3 | 1.088 | 1.062 | [0.968, 1.165] | sí | -2.3 % |
| w_4 | 1.036 | 1.124 | [1.024, 1.234] | sí | +8.5 % |
| w_5 | 0.8288 | 0.8254 | [0.7509, 0.9072] | sí | -0.4 % |
| rho (s0 conocido) | 0.15 | 0.1553 | [0.1468, 0.1642] | sí | +3.5 % |
| R0 (s0 conocido) | 2.5 | 2.504 | [2.482, 2.526] | sí | +0.1 % |

### cambio_beta

Inicios: 8; a ≤ 0.5 de log-verosimilitud del mejor: 8. log-verosimilitud = -1448.05.

| parámetro | real | estimado | IC 95 % | ¿cubre? | error rel. |
|---|---|---|---|---|---|
| R_eff(0) | 2.5 | 2.494 | [2.45, 2.538] | sí | -0.3 % |
| i0/s0 | 1e-05 | 9.654e-06 | [7.877e-06, 1.183e-05] | sí | -3.5 % |
| rho*s0 | 0.3 | 0.3044 | [0.2899, 0.3196] | sí | +1.5 % |
| k | 20 | 17.65 | [14.28, 21.83] | sí | -11.7 % |
| factor beta tau=40 | 0.6 | 0.6088 | [0.5917, 0.6264] | sí | +1.5 % |
| w_0 | 1.191 | 1.137 | [1.045, 1.236] | sí | -4.6 % |
| w_1 | 1.14 | 1.113 | [1.023, 1.212] | sí | -2.3 % |
| w_2 | 1.088 | 1.087 | [0.9993, 1.182] | sí | -0.1 % |
| w_3 | 1.088 | 1.06 | [0.9746, 1.153] | sí | -2.5 % |
| w_4 | 1.036 | 1.112 | [1.022, 1.21] | sí | +7.3 % |
| w_5 | 0.8288 | 0.8557 | [0.7858, 0.9318] | sí | +3.2 % |
| rho (s0 conocido) | 0.3 | 0.3044 | [0.2899, 0.3196] | sí | +1.5 % |
| R0 (s0 conocido) | 2.5 | 2.494 | [2.45, 2.538] | sí | -0.3 % |

**Veredicto paso 3:** recuperado (criterios 1–3 de I4).

Cobertura empírica del IC 95 % (40 réplicas por escenario, criterio 4):

| escenario | R_eff(0) | ρ·s0 | i0/s0 | k |
|---|---|---|---|---|
| ola_simple | 0.95 | 0.90 | 0.93 | 0.95 |
| subregistro | 1.00 | 0.90 | 1.00 | 0.97 |
| cambio_beta | 0.95 | 0.88 | 0.97 | 0.90 |

## Paso 4 · Perfiles de verosimilitud (escenario subregistro)

Valores reales: R0 = 2.5, s0 = 0.8, ρ = 0.15 → R_eff(0) = 2.0, ρ·s0 = 0.12. ℓ̂ = -1186.783 (natural: -1186.783).

| R0 | 1.6 | 1.8 | 1.9 | 2 | 2.1 | 2.5 | 3 | 4 | 6 | 8 | 11 | 14 | 15.5 | 16.5 | 18 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ℓ̂ − ℓ_p | 4.09e+03 | 503 | 56.8 | 0.0703 | 1.36e-06 | -1.21e-07 | 6.48e-08 | 9.5e-08 | -1.46e-07 | 3.32e-07 | 4.32e-07 | -3.53e-08 | 9.82e-07 | 0.417 | 9.2 | 31.5 |

| s0 | 0.08 | 0.1 | 0.11 | 0.12 | 0.13 | 0.2 | 0.3 | 0.5 | 0.7 | 0.9 | 0.99 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ℓ̂ − ℓ_p | 81.5 | 26.4 | 9.01 | 0.747 | 3.81e-07 | 1.02e-06 | -1.77e-08 | 1.48e-06 | 4.71e-07 | 9.8e-11 | 1.05e-07 |

- IC de perfil 95 % de R_eff(0): [1.9857, 2.0206] (real 2.0); Wald: [1.9857, 2.0204].
- "IC" de perfil de R0: [2.00, 16.76]; de s0: [0.119, 0.990]. Sus extremos los fijan las restricciones s0 ≤ 1 y ρ ≤ 1, no los datos.
- **Sí aparece la cresta plana de H1**: ℓ_p(R0) y ℓ_p(s0) son constantes (diferencias ≲ 10⁻⁵, error numérico) en toda la región compatible con R0·s0 = R_eff(0); R_eff(0) tiene un perfil cuadrático y estrecho. Con casos solos, H1 se cumple de forma **estructural** (exacta), no solo práctica.

## Paso 5 · r con ventana fija (21 días), perfil, bootstrap (B = 200) y R(D)

| escenario | ventana | r real | r̂ | IC perfil | IC bootstrap | R(D=5) | R(D=7) | R(D=10) | R_eff(0) real |
|---|---|---|---|---|---|---|---|---|---|
| ola_simple | (0, 21) | 0.1428 | 0.1467 | [0.1261, 0.1676] | [0.1281, 0.1670] | 1.73 [1.63, 1.84] | 2.03 [1.88, 2.17] | 2.47 [2.26, 2.68] | 2.0 |
| subregistro | (3, 24) | 0.1427 | 0.1384 | [0.1166, 0.1606] | [0.1183, 0.1630] | 1.69 [1.58, 1.80] | 1.97 [1.82, 2.12] | 2.38 [2.17, 2.61] | 2.0 |
| cambio_beta | (0, 21) | 0.2142 | 0.2206 | [0.1998, 0.2418] | [0.1997, 0.2393] | 2.10 [2.00, 2.21] | 2.54 [2.40, 2.69] | 3.21 [3.00, 3.42] | 2.5 |

R(D) con IC de perfil. R(D) = 1 + r·D (SIR, periodo infeccioso exponencial).

Cobertura del IC 95 % de r (160 réplicas, escenario subregistro):

| k | perfil | bootstrap |
|---|---|---|
| tomado del ajuste de la ola (decisión C4) | 0.956 | 0.931 |
| estimado en la ventana (versión original) | 0.881 | 0.856 |

## Paso 6 · Puntos de cambio de β (selección de K por BIC)

| escenario | τ real | factor real | K elegido | BIC (K=0, 1, 2) | τ̂ [IC] | factor [IC 95 %] | τ del mejor K=2 |
|---|---|---|---|---|---|---|---|
| ola_simple | — | — | 0 | 2948.8, 2956.3, 2965.8 | — | — | [45, 89] |
| cambio_beta | [40] | [0.6] | 1 | 3342.7, 2959.7, 2968.5 | 40 [40, 40] | 0.609 [0.592, 0.626] | [32, 40] |
| dos_cambios | [35, 45] | [0.7, 0.7] | 1 | 3534.7, 3099.1, 3100.0 | 40 [39, 40] | 0.519 [0.501, 0.537] | [35, 44] |
| dos_cambios_sep15 | [35, 50] | [0.7, 0.7] | 2 | 3424.1, 3028.8, 3011.0 | 35 [35, 38]; 50 [50, 50] | 0.722 [0.677, 0.770]; 0.698 [0.644, 0.757] | [35, 50] |
| dos_cambios_sep20 | [35, 55] | [0.7, 0.7] | 2 | 3291.4, 2954.2, 2913.5 | 35 [35, 35]; 55 [55, 55] | 0.729 [0.693, 0.766]; 0.680 [0.620, 0.745] | [35, 55] |
| dos_cambios_sep30 | [35, 65] | [0.7, 0.7] | 2 | 3008.3, 2764.0, 2744.8 | 35 [35, 35]; 64 [62, 65] | 0.727 [0.703, 0.751]; 0.714 [0.615, 0.828] | [35, 64] |

IC de τ: perfil a resolución diaria (condicional al otro τ cuando K = 2).

## Paso 7 · Pronóstico en tiempo simulado (orígenes semanales desde el día 21)

| escenario | métrica | modelo SIR | persistencia |
|---|---|---|---|
| ola_simple | WIS medio h=1 sem | 14163 | 62455 |
| ola_simple | WIS medio h=2 sem | 18982 | 123350 |
| ola_simple | WIS medio h=3 sem | 39100 | 177742 |
| ola_simple | WIS medio h=4 sem | 66729 | 214581 |
| ola_simple | WIS relativo (modelo/persistencia) | 0.24 | 1 |
| ola_simple | cobertura 50 % | 0.50 | 0.47 |
| ola_simple | cobertura 95 % | 0.91 | 0.61 |
| ola_simple | EAM fecha del pico (días) | 7.0 | 31.5 |
| ola_simple | EAM altura del pico (relativo) | 0.58 | 0.80 |
| cambio_beta | WIS medio h=1 sem | 35095 | 21618 |
| cambio_beta | WIS medio h=2 sem | 62836 | 38606 |
| cambio_beta | WIS medio h=3 sem | 94390 | 54589 |
| cambio_beta | WIS medio h=4 sem | 137389 | 62186 |
| cambio_beta | WIS relativo (modelo/persistencia) | 1.86 | 1 |
| cambio_beta | cobertura 50 % | 0.01 | 0.58 |
| cambio_beta | cobertura 95 % | 0.16 | 0.86 |
| cambio_beta | EAM fecha del pico (días) | 7.0 | 21.0 |
| cambio_beta | EAM altura del pico (relativo) | 3.13 | 0.62 |

## Paso 8 · Reproducibilidad

Huella SHA-256 de dos corridas con semilla 123: `66ea2de2bce33e4f…` y `66ea2de2bce33e4f…` → idénticas.
