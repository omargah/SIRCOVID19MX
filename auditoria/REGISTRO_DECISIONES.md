# Registro de decisiones del PT1

Fecha de corte: 2026-11-05. Construido a partir de las fuentes S01–S11 (ver `AUDITORIA_INTEGRAL_PT1.md` §3). Las conversaciones de claude.ai **no** se pudieron revisar; una decisión tomada solo ahí no aparece aquí.

Regla de este registro: una decisión es **vigente** solo si (a) está escrita, (b) tiene fecha, (c) se atribuye a Omar o a una autoridad académica y (d) no la contradice una fuente posterior o el prompt actual. Una decisión de una sesión de IA sin confirmación de Omar no es vigente.

Estados: Vigente · Vigente condicionada (depende de una confirmación P0) · Histórica/obsoleta · Contradictoria · Requiere confirmación.

---

## 1. Decisiones vigentes

| ID | Fecha | Decisión | Justificación registrada | Evidencia | Consecuencias | Relación con tareas |
|---|---|---|---|---|---|---|
| V-01 | 2026-10-03 | No reutilizar código, parámetros ni resultados de v0 (2025) | Diagnóstico: cifras reproducibles pero metodología no sostenible | S08, S09 bitácora; acta F0 punto 6 | Todo resultado se recalcula | Coincide con el prompt (regla 6) |
| V-02 | 2026-11-03 | Ninguna cifra a mano: el escrito toma cifras de `reports/numeros.tex` generado | Evitar el error de v0 (RMSE escritos a mano) | README v2 regla 1; `scripts/make_numeros.py` | Requiere pipeline reproducible | Arquitectura (Entrega 3) |
| V-03 | 2026-11-03 | Ningún parámetro sin fuente (DOI + página, cifra oficial o regla); lo no respaldado se marca `supuesto: true` con rango | Trazabilidad | README v2 regla 2; `src/parametros.py` lo hace cumplir | 12 parámetros reales siguen en `null` | Bloquea F5 |
| V-04 | 2026-11-03 | Primero datos sintéticos; ningún método toca datos reales antes de recuperar parámetros conocidos | Validación (coincide con el prompt §O) | README v2 regla 3 | F5 bloqueada hasta cerrar F4 | — |
| V-05 | 2026-11-03 | Nada se borra para que una figura se vea bien | Error de v0 | README v2 regla 5 | — | Coincide con el prompt (regla 18) |
| V-06 | 2026-11-03 | D (γ = 1/D) uno solo por ola, el mismo para estimar y simular; nunca incubación | Error de v0 (5.1 d de incubación al simular) | README v2 regla 2; plan nota 4 | Ver C-09 sobre el valor | — |
| V-07 | 2026-11-03 | D por variante = intervalo de generación intrínseco con fuente; sensibilidad = IC95 + rango de Byrne | Fuentes G02, G05, G06, G04 | S06 `INSUMOS_CODIGO.md`, `parametros_D.csv` | Valores NO VERIFICADOS contra PDF por esta auditoría | — |
| V-08 | 2026-11-03 | I1: una medida tiene reducción medible si el IC95 de β_después/β_antes excluye 1; H5 se rechaza si todo el IC95 del punto de cambio queda antes de la fecha del DOF | Fijado antes de ver datos | S06 `INSUMOS_CODIGO.md` | Requiere fecha DOF verificada | H5 |
| V-09 | 2026-11-03 | I2: comparar binomial negativa y Poisson, primero en sintético y luego en Ola 1, con dispersión de Pearson y AIC | — | S06 | Implementado en `src/verosimilitud.py` | F4 |
| V-10 | 2026-11-03 | I3: truncar los últimos N días de cada corte (sin nowcasting); N estimado comparando versiones de la DGE antes de ver ajustes | — | S06 | Requiere versiones históricas (0/168) | H4 |
| V-11 | 2026-11-03 | I4: 1–3 puntos de cambio de β, número elegido por AIC y BIC con sensibilidad a ambos; sin corrección por retraso | — | S06 | No implementado (acta F4) | H5 |
| V-12 | 2026-11-04 | Verosimilitud semanal; semana epidemiológica domingo–sábado | Decisión de Omar | S02 HANDOFF §2 | Choca con `sirmx` diaria (C-07) | — |
| V-13 | 2026-11-04 | Convención s0 = (S0+I0)/N; s0 = 1 ⇒ S0 = N·s0 − I0 | Resolver el caso Ola 1 | S02 HANDOFF §2 | `sirmx` no la sigue (C-08) | — |
| V-14 | 2026-11-04 | Malla sintética R0 ∈ {2, 3}, s0 ∈ {0.6, 1}, D ∈ {4.7, 6.84}, 50 réplicas | Corrección de {1.5, 3} que daba R_eff < 1 | `config/parametros.yaml` | 19/400 réplicas corridas | F4 |
| V-15 | 2026-11-05 | La integración vive en `integracion/pt1-v2`; no tocar otras ramas | Evitar pisar el trabajo de recuperación | S02 `decisiones_integracion.md` D-A | — | Integración |
| V-16 | 2026-11-05 | Ningún commit nuevo lleva firmas de IA en el mensaje | Instrucción del dueño del repo | S02 D-D | Aplica a futuros commits de esta auditoría si se autorizan | Control documental |
| V-17 | 2026-11-05 | La recuperación sintética completa se corre en la computadora de Omar | La nube recicla el contenedor | S02 HANDOFF | Resultados pendientes | F4 |
| V-18 | 2026-11-05 | El PT I se evaluó en 25-P; la reconstrucción es un trabajo personal; el trabajo original fue SIR | Respuesta de Omar a P0-1 | Respuesta de Omar tras la Entrega 1 | Resuelve C-01 y C-02; el plan 25-P (SEIRS-V) pasa a histórico; el asesor es opcional | Planteamiento (Entrega 2) |
| V-19 | 2026-11-05 | Objetivo temporal: terminar lo antes posible; sin fecha institucional | Respuesta de Omar a P0-3 | Ídem | Favorece el escenario conservador; faltan las horas semanales | Cronograma (Entrega 4) |

## 2. Decisiones históricas u obsoletas

| ID | Fecha | Decisión | Por qué es obsoleta |
|---|---|---|---|
| H-01 | 2025-05-21 | Proyecto SEIRS-V con vacunación e inmunidad declinante (plan 25-P) | Abandonada de hecho desde jun 2025; **formalmente puede seguir siendo el registro vigente** → ver P0-1 |
| H-02 | 2025-07/08 | 6 olas (prominence 500) / 5 olas (prominence 2500) por "valle a valle" | Sustituida por regla declarada (v2) |
| H-03 | 2025-08 | FD 0.024/0.050/0.059 y 0.032/0.054/0.072; S0/N fijos; D 10/11/9/7/6 y 5.1/3.0 | Errores (matriz DAT-06, MAT-05) |
| H-04 | 2025-08 | Monte Carlo triangular ±20 % como incertidumbre | Error (EST-01) |
| H-05 | 2025-08 | Parámetro de evasión ε | No identificado (EST-05) |
| H-06 | 2025-08 | Sistema de alerta temprana | Error (EST-08) |
| H-07 | 2026-10-03 | Plan de ocho fases de 20–27 semanas a 6–8 h/sem (diagnóstico) | Reemplazado por los cronogramas del 16 oct y del Hito de enero |
| H-08 | 2026-10-16 | Plan L–S 6:00–7:30, 68 sesiones, hito 17 ene 2027 | Contradicho por el Hito de enero (C-11) |
| H-09 | 2026-10-27 | README de `main` con fases F0–F7 y F0 "Completada" | Superado por v2; estado sin evidencia |
| H-10 | 2026-11-04 | Integrar solo remake + stoic; descartar zealous (JHU, frontera 2020-10-01) y D = 7 de kind-newton | La integración del 5 nov los incorporó (C-06) |

## 3. Decisiones contradictorias

| ID | Tema | Posición A | Posición B | Fuentes | Recomendación de la auditoría |
|---|---|---|---|---|---|
| C-01 | Modelo | SEIRS-V (registro 25-P) | Solo SIR (bitácora 3 oct; acta F0) | S06 / S09, S02 | **Resuelta (V-18):** el 25-P es histórico; el modelo de referencia es el SIR. |
| C-02 | Asesor | Dr. Escobar Ruiz (carta, README oct, cronograma con controles) | "Sin asesor" (acta F0 3 nov) | S06, S01, S10 / S02 | **Resuelta (V-18):** trabajo personal; la revisión del asesor es opcional. |
| C-03 | Marco rector | Física matemática y sistemas dinámicos al centro (prompt actual) | Se descarta el encuadre de espacio de fases (acta F0) | prompt / S02 | El prompt es la instrucción más reciente; confirmar (P0-2) |
| C-04 | Inferencia bayesiana | "Nada bayesiano" (acta F0) | Evaluar MCO, MV y bayesiano (prompt) | S02 / prompt | Decidir nivel (indispensable/importante/exploratorio) |
| C-05 | Unidad de análisis | Por ola desde el inicio (v2) | Serie completa primero (prompt) | S02 / prompt | Seguir el prompt salvo objeción fundada |
| C-06 | Datos para olas | JHU + frontera 2020-10-01 (integrados) | Descartados (HANDOFF previo, INSUMOS) | S02 / S06 | Rehacer con serie DGE por síntomas; JHU como sensibilidad |
| C-07 | Resolución temporal | Semanal (V-12) | Diaria con día de semana (F4) | S02 | Semanal principal; diaria como sensibilidad |
| C-08 | Convención s0 | (S0+I0)/N (`src/sir.py`) | S0/N (`sirmx`) | S02 | Unificar a V-13 |
| C-09 | D base | D por variante con fuente (V-07) | D = 7 fijo (F4, `sirmx`) | S02 | D por variante; {5, 7, 10} solo sensibilidad |
| C-10 | Decisiones I2–I4 | Las de Omar (V-09 a V-11) | Las inventadas por la sesión F4 (`docs/decisiones.md`) | S06 / S02 | Vigentes las de Omar; las de F4 son provisionales |
| C-11 | Cronograma | Hito 9 ene, diario, F7 14 mar | Hito 17 ene, L–S, fin de marzo | S10 / S09 | Rehacer en la Entrega 4 |
| C-12 | Plan de análisis | Borrador hasta cerrar F4 | "CONGELADO" 2026-11-04 | S02 | Ningún plan está congelado válidamente |
| C-13 | Población N | INEGI 2020 | CONAPO | S02 | INEGI base, CONAPO sensibilidad, tras verificar |
| C-14 | Incubación (H5) | Mediana G01 (Lauer) | Media 6.4 d G03 (Backer) | S02, S06 | Decidir estadístico y fuente con ficha |
| C-15 | Gestor bibliográfico | Zotero + Better BibTeX (cronograma) | "Sin Zotero": CSV + script (main) | S10 / S01 | Decidir; el `.bib` actual es inutilizable en ambos casos |
| C-16 | Criterio de H2 | Ljung–Box + AIC | ΔBIC + Pearson; Wald | S02 | Fijar uno antes de datos |
| C-17 | Estado de F0 | Completada / Cerrada v0.0 | En curso | S01, S02 / S09 | En ejecución (no hay etiqueta ni control del asesor) |

## 4. Decisiones que requieren confirmación (preguntas concretas)

| ID | Pregunta | Quién puede responder | Bloquea |
|---|---|---|---|
| P0-1 | ~~Estatus administrativo del PT I~~ | — | **Resuelta (V-18)** |
| P0-2 | ¿El marco rector es el del prompt actual (física matemática al centro)? | Omar | Entrega 2. Recomendación de la auditoría en la sección 5 (R-01). |
| P0-3 | ~~Fecha de entrega~~ Lo antes posible, sin fecha institucional | — | **Resuelta en parte (V-19):** falta P0-4 |
| P0-4 | Horas semanales reales disponibles (los dos cronogramas suponen 9 y 10.5 h/sem) | Omar | Entrega 4 |
| P1-1 | ¿Se conservan SP4/H4 (pronóstico) y SP5/H5 (medidas) o pasan a exploratorio? | Omar (+ asesor) | Alcance |
| P1-2 | ¿Se acepta lo bayesiano y en qué nivel? | Omar | Metodología |
| P1-3 | ¿Qué código de v2 se conserva tras el plan de apropiación? | Omar | Arquitectura |
| P1-4 | ¿Se comprometen descargas locales de la DGE (microdatos y versiones)? | Omar | F3, H4 |
| P1-5 | Valor de ENSANUT 2021 (57.9 % vs 59.2 %) y universo | Omar con los PDF | H3 |

## 5. Recomendaciones de la auditoría pendientes de decisión

### R-01 · Marco rector (P0-2)

**Recomendación: un marco intermedio con dos núcleos indispensables y lo demás condicionado.**

1. **Núcleo físico-matemático (indispensable).** Un capítulo de teoría del SIR escrito a partir de las 11 derivaciones ya verificadas: construcción del modelo, espacio de fases, integral primera, continuo de equilibrios y su estabilidad, umbral, tamaño final general, relación r–R según el intervalo de generación, y la simetría de escala que gobierna la identificabilidad. Es lo que pide el prompt, y casi todo el trabajo matemático ya existe como pruebas. Falta redactarlo y respaldarlo con bibliografía fichada.
2. **Núcleo de aplicación (indispensable).** Primero la serie nacional completa, sin dividir en olas. Después, estimación por máxima verosimilitud con modelo de observación binomial negativo y perfiles de verosimilitud. El eje es qué parámetros son identificables con casos solos y cuáles con serología (ENSANUT). Solo se toman olas cuyos datos lo permitan; la primera ola con s0 = 1 es la candidata natural.
3. **Importante (si el tiempo da):** comparar el estimador de mínimos cuadrados con el de verosimilitud, H3 acotada a la primera ola y sensibilidad local y global.
4. **Exploratorio:** pronóstico en tiempo real (H4, exige 168 versiones históricas de la DGE), puntos de cambio frente a las medidas (H5) y estimación bayesiana.

**Por qué.** Respeta la prioridad física del prompt sin tirar lo que ya funciona. Es el camino más corto a un trabajo defendible, que es la meta de terminar lo antes posible. Saca del camino crítico lo que depende de datos que hoy no tienes (las versiones históricas y el DOF).

**Qué se pierde.** La pregunta "¿le habría alcanzado un SIR a una pandemia nueva?" (SP4) y el análisis de las medidas (SP5) dejan de ser obligatorios.
