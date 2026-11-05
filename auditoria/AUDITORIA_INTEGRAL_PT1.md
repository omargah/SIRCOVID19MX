# Auditoría integral del Proyecto Terminal I (SIR · COVID-19 en México)

**Fase:** F0 — Auditoría y diagnóstico (Entrega 1)
**Fecha de corte de la auditoría:** 2026-11-05
**Rama de trabajo de la sesión:** `claude/cool-einstein-qwqjvj` (sin commits; esta carpeta no está versionada todavía)
**Alcance de escritura:** solo se crearon archivos nuevos en `auditoria/`. No se modificó ningún archivo existente, no se hicieron commits ni push y no se escribió en GitHub, Drive ni en ningún Artifact.

Documentos que acompañan a este informe:

| Archivo | Contenido |
|---|---|
| `MATRIZ_AUDITORIA_PT1.csv` | 71 hallazgos (18 críticos, 25 altos, 23 medios, 5 bajos) con evidencia, fuente, gravedad, consecuencia, acción y prioridad (P0–P4) |
| `REGISTRO_DECISIONES.md` | Decisiones vigentes, históricas, contradictorias y por confirmar |
| `REGISTRO_RIESGOS.md` | 16 riesgos con probabilidad, impacto, mitigación y condición de cierre |
| `INVENTARIO_RECURSOS.md` | Datos, documentos, código, bibliografía y herramientas realmente disponibles |

Convención de este informe: **NO VERIFICADO** marca toda afirmación que no pude comprobar con una fuente primaria o con una ejecución propia. "v0", "v1" y "v2" son etiquetas de esta auditoría (definidas en §5), no nombres oficiales.

---

## 1. Resumen ejecutivo

1. **El proyecto no tiene un estado único.** Existen al menos cinco "verdades" simultáneas que se contradicen: (a) el plan registrado ante la coordinación (trimestre 25-P: modelo **SEIRS-V** con vacunación e inmunidad declinante, asesor Dr. Adrián Mauricio Escobar Ruiz); (b) el trabajo entregado en agosto de 2025 (SIR, Monte Carlo, "espacio de fases"); (c) el plan de reconstrucción de octubre de 2026 (SIR, con controles del asesor, tablero con 2 de 101 pasos hechos); (d) la rama `main` de GitHub (solo archivo histórico + un índice bibliográfico); (e) once ramas sin fusionar de noviembre de 2026 (SIR, "sin asesor", código extenso, ninguna con datos reales).

2. **Hallazgo institucional crítico.** El título y objetivo registrados del PT I (`Plan de trabajo trimestral 25-P`, 21 may 2025) son *"Modelado físico de la dinámica del COVID-19 en México: impacto de la inmunidad declinante y la vacunación de refuerzo"* con un modelo SEIRS-V. La reconstrucción actual declara "solo modelo SIR" y "trabajo personal, sin asesor" (acta F0, 2026-11-03), mientras que el cronograma de octubre (Artifact *Hito de enero*) prevé controles con el Dr. Escobar Ruiz, y la bitácora del tablero dice "rehacer desde cero como mejora personal, sin fecha límite". **No se sabe si este trabajo es una entrega académica evaluable, una re-entrega o un proyecto personal.** Esa respuesta cambia el alcance, el formato, la fecha y quién aprueba. Es la primera pregunta que debe responderse.

3. **El trabajo de 2025 (v0) no es científicamente defendible y no debe heredarse.** Mi revisión independiente de los PDF confirma los hallazgos del diagnóstico previo (Artifact del 2026-10-03): ecuaciones con errores conceptuales (equilibrio endémico y bifurcación transcrítica en un SIR cerrado; "caos determinista" en un sistema plano integrable), periodo de incubación usado como periodo infeccioso al simular, mezcla de las relaciones R = 1 + rD y R = e^{rD}, incertidumbre asignada (±20 % triangular) presentada como intervalo de confianza, parámetro de evasión inmune ajustado y "validado" con los mismos datos, comparación de prevalencia simulada contra incidencia observada, etiquetas de variante desalineadas con las fechas (una "ola Ómicron" con pico el 10 ago 2021), cuatro o más conjuntos incompatibles de R0 por ola con los mismos datos, métricas escritas a mano, un capítulo de "alerta temprana" evaluado sobre curvas simuladas y un rastro de conversación con IA en el texto ("Como bien reflexionas…").

4. **La reconstrucción de noviembre de 2026 (v2) tiene una base técnica aprovechable, pero no es todavía un proyecto de física ni está integrada.** Verifiqué por ejecución propia que la suite rápida de `integracion/pt1-v2` da **218 pruebas aprobadas y 5 fallos esperados documentados** (coincide con lo declarado). Lo valioso: registro de parámetros con fuente obligatoria, verificación simbólica-numérica de 11 derivaciones del SIR (integral primera, ausencia de equilibrio endémico, tamaño final con W de Lambert, relación r–R), demostración de la simetría de escala que hace estructuralmente no identificables R0, s0 y ρ con casos solos, y una regla de olas declarada con un resultado negativo honesto (ninguna prominencia reproduce las cinco olas convencionales). Lo que falta: **cero análisis con datos reales, cero fichas bibliográficas, cero capítulos escritos** (salvo un borrador de una sección), recuperación sintética al 4.75 % (19 de 400 réplicas), y doce parámetros de literatura en `null`.

5. **Inversión del orden científico.** El cronograma de octubre ponía bibliografía y teoría (F1–F2) antes del código (F4, diciembre). En la práctica se escribieron ~7 500 líneas de código y pruebas en tres días (3–5 nov), casi todas con autor "Claude" (39 de 47 commits de la rama de integración), antes de leer y fichar una sola fuente. Esto genera un **riesgo alto de defensa académica**: la regla 6 del propio proyecto ("cada línea debe poder explicarse") no tiene evidencia de cumplimiento.

6. **Contradicción con las prioridades del prompt actual.** El prompt de reconstrucción pone en el centro la física matemática y los sistemas dinámicos. El acta F0 (2026-11-03) **descartó explícitamente** el encuadre de "espacio de fases / atractores / bifurcaciones", y el plan v2 está orientado a inferencia, identificabilidad y pronóstico (H1–H5). También choca la decisión "nada bayesiano" con el pedido de comparar métodos de estimación, y el análisis "por ola" con el pedido de estudiar primero la serie completa sin dividir en olas.

7. **Gobernanza fragmentada.** Seis "chats" del proyecto, sesiones paralelas de Claude Code que produjeron decisiones incompatibles (por ejemplo, una sesión *inventó* las decisiones I2–I4 y declaró "CONGELADO" un plan que contradice las I1–I4 que Omar sí había fijado el 2026-11-03), dos cronogramas con hitos distintos (9 ene vs 17 ene 2027), un tablero sin actualizar desde el 2026-10-16, tres PR abiertos y ninguno fusionado.

**Conclusión de la auditoría.** El proyecto está **en preparación**, no en ejecución: no hay ningún resultado científico sobre datos reales que pueda considerarse validado. Lo aprovechable es infraestructura (código probado, registro de parámetros, verificación de derivaciones, inventario bibliográfico con PDFs en Drive, serología transcrita con página) y aprendizaje metodológico. Antes de reconstruir el planteamiento hay que resolver cuatro decisiones bloqueantes (§19, prioridad 0).

---

## 2. Alcance de la auditoría

Se auditaron: planteamiento científico, matemáticas, estadística, código, bibliografía, datos y gestión, del periodo mayo 2025 – 5 nov 2026. No se ejecutó código de v0 (solo existe como PDF impreso de notebooks). Sí se ejecutó la suite de pruebas de v2 en una copia en el directorio temporal de la sesión. No se descargaron datos nuevos ni se corrigió nada.

## 3. Fuentes consultadas

| ID | Fuente | Qué se revisó | Grado de revisión |
|---|---|---|---|
| S01 | Repositorio `omargah/SIRCOVID19MX`, rama `main` (8 commits, feb–oct 2026) | Todos los archivos de texto, historia de commits, versiones previas del README | Completa |
| S02 | 11 ramas remotas (traídas con `git fetch`, solo lectura); contenido completo de `integracion/pt1-v2` extraído a un directorio temporal | README, HANDOFF, `docs/` (actas F0 y F4, planes, decisiones, pendientes, teoría, olas), `config/parametros.yaml`, `data/`, `reports/`, estructura de `src/`, `sirmx/`, `tests/` | Documentación completa; código revisado por estructura, pruebas y fragmentos, no línea por línea |
| S03 | Pull requests #1, #2, #3 (abiertos) | Metadatos (rama, fecha, estado) | Parcial: no se leyeron sus descripciones |
| S04 | Issues de GitHub | Listado | Completa: **no existe ningún issue** |
| S05 | `v0-anterior/`: 6 PDF (5 únicos: `Proyecto_Terminal_1 (3).pdf` y la "Captura 2025-07-22" tienen el mismo texto) y `analisis_montecarlo.py` | Texto extraído completo; lectura de código, salidas y prosa | Completa para escrito y presentación; notebooks por búsqueda dirigida de celdas, parámetros y salidas |
| S06 | Google Drive (carpeta *Proyecto Terminal 1*, v.1 y v.2 2026) | `Plan de trabajo trimestral 25-P.PDF`, `Carta Aceptación PT I`, `INSUMOS_CODIGO.md`, `serologia.csv`, `olas_variantes.csv`, `parametros_D.csv`, `INDICE.csv` (versión Drive), `MAPEO_fuentes.csv`, listados de carpetas | Completa para esos archivos |
| S07 | Drive: documento *Ayuda Proyecto Terminal COVID-19* (jun 2025, otra cuenta) | Primeros ~3 500 de 80 000 caracteres | Parcial |
| S08 | Artifact *Diagnóstico y plan para rehacer el Proyecto Terminal* (Claude Docs, 2026-10-03) | Pestaña 1, ~24 000 de 37 000 caracteres | Parcial; pestaña "Organización del trabajo" no leída |
| S09 | Artifact *Reconstrucción del PT1* (tablero de fases) | Base de datos: 8 fases, 101 pasos, 9 entradas de bitácora, estado | Completa |
| S10 | Artifact *Hito de enero del PT1* | Cronograma de 77 sesiones, controles, calendario, fases posteriores | Completa en sus datos |
| S11 | Ejecución propia de pruebas de `integracion/pt1-v2` (Python 3.13, numpy 2.5, scipy 1.18, sympy 1.14, numba 0.68) | Suite rápida (teoría + `src/`) y suite lenta F4 (`sirmx/`) | Suite rápida: completa. Suite F4: ver §9.3 |

## 4. Fuentes no disponibles o no revisadas

| Fuente | Estado | Consecuencia |
|---|---|---|
| Las 12 conversaciones de los proyectos de claude.ai (*Proyecto Terminal 1 - Code*: 5; *Proyecto Terminal 1 · SIR COVID*: 7) | **No accesibles desde esta sesión.** No existe herramienta para leer conversaciones de claude.ai. No se simula su revisión. | Las decisiones tomadas solo en esos chats no están auditadas. Solo las conozco indirectamente por lo que quedó escrito en `INSUMOS_CODIGO.md`, el HANDOFF, el tablero y la bitácora. |
| Documentos citados pero ausentes: "planteamiento 2026-10-24", "bitácora de decisiones", "protocolo de trabajo", `PT1_bibliografia_v2.xlsx`, matriz de bibliografía, página de planteamiento enviada al asesor | No encontrados en repo ni en Drive (búsqueda por título) | No se puede verificar si el control 1 con el asesor ocurrió ni qué respondió. |
| Artifact *Fuentes del PT1* (2026-10-25) | Existe; no se leyó | Posible inventario bibliográfico adicional no contrastado. |
| Drive v.1: carpetas *Semana 1*, *Semana 2*, *Otros*; `SIR S2 final.tex`; `Semana 2 SIR Mex.ipynb` (jun 2025) | No revisados | La transición SEIRS-V → SIR en junio de 2025 queda sin documentar. |
| PDFs de la bibliografía en Drive (~70 con clave) | Existen; no se abrieron | **No puedo verificar** las cifras y páginas citadas en `config/parametros.yaml` (G02, G05, G06, G04, G03) ni en `serologia.csv`. Quedan NO VERIFICADAS por esta auditoría. |
| CSV de datos de v0 (`Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv`) | Existe en Drive (carpeta *SIR S2 final*, 145 869 bytes, jun 2025); no se descargó | No reproduje cifras de v0; me apoyo en la reproducción declarada por S08. |
| Microdatos DGE, versiones históricas, ENSANUT en crudo, DOF | No existen en repo ni en Drive; la nube no alcanza `gob.mx` (según HANDOFF; no reprobado aquí) | Ningún análisis real es posible hoy. |
| Notion, otros conectores | No consultados | — |

---

## 5. Cronología histórica

Etiquetas: **v0** = trabajo de 2025 (notebooks, escrito, presentación) y su subida a GitHub en feb 2026; **v1** = reconstrucción planificada en oct 2026 (diagnóstico, tablero, cronograma, índice bibliográfico); **v2** = ramas de código de nov 2026.

| Fecha | Evento | Tipo | Fuente |
|---|---|---|---|
| 2025-05-21 | Plan de trabajo trimestral 25-P: **SEIRS-V** con vacunación e inmunidad declinante; asesor Dr. Escobar Ruiz; reuniones L-M-V 2 h | Decisión institucional (vigente hasta prueba en contrario) | S06 |
| 2025-05-23 | Carta de aceptación (archivo creado ese día; el texto dice "21 de diciembre de 2025": **fecha inconsistente**) | Documento institucional | S06 |
| 2025-06-10/11 | Carpetas "Semana 1/2" con `SIR S2 final.tex` y notebook "SIR Mex": el modelo ya es SIR | Cambio de alcance no documentado | S06 (solo títulos) |
| 2025-06-30 | Documento *Ayuda Proyecto Terminal COVID-19* (otra cuenta, estilo de reporte generado) | Material de apoyo, no fuente | S07 |
| 2025-07-22 | Notebook exportado (129 págs.): 6 olas (prominence 500), NLS, MLE Poisson, Monte Carlo; R0 por ola en tres versiones | Trabajo ejecutado (v0) | S05 |
| 2025-08-07 | Notebook "versión congelada": 5 olas (prominence 2500), FD 0.032/0.054/0.072, D = 5.1/3.0, ε = 0.50, alerta temprana | Trabajo ejecutado (v0) | S05 |
| 2025-08-09 | Escrito "Proyecto Terminal I" (52 y 56 págs.): R0 = 2.12, 1.50, 3.37, 4.28, 3.37 | Entregable (v0) | S05 |
| 2025-08-13 | Presentación Beamer (34 diapositivas) | Entregable (v0); **si fue evaluada: NO VERIFICADO** | S05 |
| 2026-02-15 | Repositorio creado; README: "Status: Finalizado", "caos determinista", "R0 ≈ 4.28" | Publicación (v0) | S01 |
| 2026-10-03 | Diagnóstico externo de v0 (reproduce cifras, las declara no sostenibles); decisión: "rehacer desde cero como mejora personal, sin fecha límite y solo con el modelo SIR" | Decisión (v1) | S08, S09 |
| 2026-10-08 | Tablero de fases F0–F7 (101 pasos, cuatro controles con el asesor) | Gestión (v1) | S09 |
| 2026-10-11 | Se agregan SP4 (pronóstico) y SP5 (medidas de la SSA) | Cambio de alcance (v1) | S09 |
| 2026-10-16 | Plan semanal: L–S 6:00–7:30, 68 sesiones, hito 17 ene 2027; última actualización del tablero | Gestión (v1) | S09 |
| 2026-10-19 → 2027-01-10 | Cronograma *Hito de enero*: diario 6:00–7:30, 77 sesiones, hito 9 ene 2027, F7 hasta 14 mar 2027 (**contradice** el anterior) | Gestión (v1) | S10 |
| 2026-10-27 | `main`: sistema bibliográfico "sin Zotero" (el cronograma pedía Zotero), 79 referencias "descargado", v0 a `v0-anterior/`, README con asesor | Ejecutado (v1) | S01 |
| 2026-11-03 | Acta F0 "cerrada" en rama (no en `main`): solo SIR, H1–H5, MLE sin bayesiano, "**sin asesor**", descarta el encuadre de espacio de fases. Decisiones I1–I4 de Omar (en Drive) | Decisión (v2) | S02, S06 |
| 2026-11-04 | Seis sesiones paralelas: parámetros (stoic), teoría a–k (fervent), olas (zealous), pipeline DGE (compassionate), F4 `sirmx` con plan "CONGELADO" e I2–I4 **inventadas** (kind-newton), recuperación sintética (adoring-goodall). PR #1 y #2 | Ejecutado (v2) | S02, S03 |
| 2026-11-05 | `integracion/pt1-v2` une todo; HANDOFF con 20 pendientes; recuperación pasa a la computadora de Omar; PR #3 | Ejecutado (v2) | S02 |
| 2026-11-05 | Esta auditoría | — | — |

---

## 6. Estado científico

### 6.1 Planteamientos sucesivos

| Versión | Pregunta / objetivo | Evaluación |
|---|---|---|
| Registro 25-P | Desarrollar y analizar un SEIRS-V (inmunidad declinante, refuerzos), R0, Rt, equilibrios ELE y EE, estabilidad, sensibilidad, escenarios | Coherente como proyecto teórico de modelación, pero **no es el que se ejecutó**. |
| v0 (ago 2025) | "¿En qué medida un SIR canónico… puede reconstruir las trayectorias de las cinco olas en el espacio de fases?"; hipótesis central de que el SIR "cuantifica" parámetros de control y que sus desviaciones "revelan" física faltante | **No falsable**: toda discrepancia se declara hallazgo (coincido con S08). Atribuciones causales (intervenciones, conducta adaptativa) sin diseño que las permita. |
| v1 (oct 2026) | Qué parte de cada ola es consistente con un SIR de parámetros constantes y qué parámetros son identificables con casos + serología; SP4 pronóstico; SP5 medidas | Pregunta respondible; alcance creció de 3 a 5 hipótesis en ocho días. |
| v2 (nov 2026) | Igual que v1, con H1–H5 y criterios de rechazo explícitos | Mejor formulado. Problemas en §6.2. |

### 6.2 Evaluación de las hipótesis vigentes (v2)

| H | Enunciado | Problema detectado | Gravedad |
|---|---|---|---|
| H1 | R0 y S0 no identificables por separado; solo R_eff(0) = R0·S0/N | Con casos solos, ρ desconocido y γ fijo, la no identificabilidad es un **teorema** (simetría de escala exacta demostrada en `escrito/capitulos/identificabilidad.tex` y verificada en pruebas). Un teorema no se "contrasta" con datos. La parte empírica legítima es: (a) si la serología rompe la cresta en la práctica y con qué precisión, y (b) si las restricciones s0 ≤ 1, ρ ≤ 1 acotan algo útil. Además, el criterio de rechazo no tiene umbral numérico fijado. | Alta |
| H2 | β constante por ola deja residuos sistemáticos | Contrastable. Se confunde con ρ variable (cambios de política de pruebas) y con el retraso de notificación. Dos criterios incompatibles en dos planes (Ljung–Box + AIC vs ΔBIC + Pearson). | Media |
| H3 | El tamaño final sobrestima el aumento de seroprevalencia (ENSANUT) | Depende de H1 (el tamaño final en fracción también se escala). Seroprevalencia ≠ incidencia acumulada: serorreversión, reinfecciones, y anticuerpos anti-N también inducidos por vacunas inactivadas (CoronaVac se usó en México; `serologia.csv` lo anota). ENSANUT 2020 se levantó del 17 ago al 20 nov 2020, que se traslapa con el inicio de la segunda ola. | Alta |
| H4a/b | SIR vs persistencia (WIS); estabilización de la fecha del pico | Exige reconstruir lo disponible en cada fecha: 168 versiones históricas de la DGE, **0 descargadas**. Sin ellas solo es una cota optimista. | Alta |
| H5 | La transmisión bajó después de la JNSD, no antes | Riesgo de lectura causal; la fecha de la medida no está verificada en el DOF; τ se estima en fecha de síntomas y hay que restar la incubación (valor y fuente sin decidir). | Alta |

### 6.3 Alcance frente a las prioridades del prompt actual

El prompt pide: núcleo físico-matemático (construcción del modelo, espacio de fases, invariantes, equilibrios, estabilidad, umbrales, escalas, bifurcaciones solo si proceden), luego aplicación a México con inferencia, identificabilidad, incertidumbre, sensibilidad y evaluación predictiva; estudiar primero la serie completa sin olas; comparar métodos de estimación (mínimos cuadrados, verosimilitud, bayesiano). El plan v2 cubre bien identificabilidad y pronóstico, pero: no tiene capítulo de física escrito, descartó el espacio de fases, excluye lo bayesiano, analiza por olas desde el inicio y no tiene análisis de sensibilidad global. **Hay que decidir explícitamente cuál de los dos marcos manda** (ver REGISTRO_DECISIONES, C-01 a C-04).

### 6.4 Contribuciones: qué es reproducción y qué podría ser propio

| Elemento | Clasificación | Comentario |
|---|---|---|
| Integral primera, tamaño final (W de Lambert), ausencia de equilibrio endémico, R = 1 + rD, Euler–Lotka con intervalo gamma | Reproducción de resultados conocidos | Deben citarse como tales (Kermack y McKendrick 1927; Ma y Earn 2006; Wallinga y Lipsitch 2007; etc.). |
| Simetría de escala (R0, s0, i0, ρ) → (cR0, s0/c, i0/c, cρ) | Presentada en el acta F0 como "resultado analítico nuevo" | **Originalidad NO VERIFICADA**; es muy probable que exista en la literatura de identificabilidad de modelos epidémicos con fracción de reporte (p. ej., candidatos a revisar: Tuncer y Le 2018, Math. Biosci.; Roosa y Chowell 2019, J03, ya en el índice). No debe presentarse como aportación propia hasta revisarlo. |
| Estructura de Poisson del SIR (prueba k2: campo = J∇H con J antisimétrica dependiente del estado) | Matemáticamente correcta (verificada por la prueba) | Es una estructura **no canónica**; no es un sistema hamiltoniano canónico. Hay literatura previa sobre estructura hamiltoniana/bi-hamiltoniana del modelo de Kermack–McKendrick (candidatos: Nutku 1990, J. Phys. A; Ballesteros et al. 2020, citado en el cronograma). **NO VERIFICADO.** |
| Umbral como "transición de fase" (prueba k3: z = 2ε − (8/3)ε², misma ecuación que la componente gigante de Erdős–Rényi) | La expansión es correcta (la comprobé a mano) | Es una analogía con fundamento matemático para el **tamaño final**, no para los equilibrios de la EDO. Debe redactarse con esa precisión. |
| Aplicación a México con regla de olas declarada, identificabilidad con serología, evaluación predictiva honesta | Posible aportación empírica y metodológica | Aún no existe. |

---

## 7. Estado matemático

### 7.1 Errores en v0 (verificados en los PDF)

| # | Afirmación en v0 | Diagnóstico | Gravedad |
|---|---|---|---|
| M1 | "Equilibrio endémico que existe solo si R0 > 1"; "el DFE transfiere su estabilidad al EE" (Cap. 2.3–2.4; Fig. 2.3B) | Falso para el SIR cerrado: ds/dt = 0 exige s = 0 o i = 0, así que los equilibrios son la recta {(s, 0)}, un continuo no aislado; no hay equilibrio con i* > 0. La figura dibuja la rama "endémica" escalada a mano (`i_endemico * 0.3`). | Crítica |
| M2 | Bifurcación transcrítica en R0 = 1 "análoga a una transición de fase de segundo orden" con i* como parámetro de orden | Sin fundamento para esta EDO. Lo correcto: cada equilibrio (s*, 0) tiene autovalores {0, γ(R0 s* − 1)}; el umbral vive en el tamaño final. | Crítica |
| M3 | "Caos determinista… sensibilidad a condiciones iniciales" (README feb 2026) | Imposible: sistema autónomo efectivamente bidimensional (Poincaré–Bendixson) y además integrable (tiene integral primera). | Crítica |
| M4 | R0 = (1 + rD)/s0 en el texto; `modelo_exponencial` usa e^{rD}; el resultado final es un promedio ponderado por R² de ambos | Dos supuestos incompatibles sobre el intervalo de generación (exponencial vs fijo). | Alta |
| M5 | D = 10, 11, 9, 7, 6 d para estimar; D = 5.1 y 3.0 d para simular (`D_PRE_OMICRON`, `D_OMICRON`) | 5.1 d coincide con la mediana de incubación de Lauer et al. 2020 (el propio plan v2, nota 4, lo reconoce). Confunde incubación con periodo infeccioso. | Crítica |
| M6 | Ajuste de ε: RMSE entre I(t) simulada (prevalencia) y casos/FD diarios (incidencia); I0 = incidencia del primer día | Confunde incidencia con prevalencia. | Crítica |
| M7 | Tamaño final r_f = 1 − e^{−R0 r_f} presentado como general | Solo vale para s0 ≈ 1, i0 → 0; las olas 2–5 tenían s0 entre 0.3 y 0.8 en el propio trabajo. | Media |
| M8 | Presentación: "los modelos epidémicos son sistemas disipativos que evolucionan a atractores" | Impreciso: el SIR conserva H; los puntos finales forman un continuo que depende de la condición inicial. | Baja |

### 7.2 Estado en v2

Verificado por ejecución propia: las 11 derivaciones (a–k) tienen igualdad simbólica en SymPy y comprobación numérica; 87 pruebas de teoría pasan y 3 quedan como fallos esperados por precisión numérica documentada (error global de LSODA ~1.5e-9 en olas explosivas R0 = 15; cancelación en la incidencia con i0 = 1e-10; escala en N al nivel de 1e-8). Ninguna derivación resultó falsa.

Puntos abiertos:
- **No existe el Capítulo 2 escrito.** Las derivaciones viven solo como docstrings de pruebas. `escrito/` tiene `main.tex`, `introduccion.tex` (91 bytes), `modelo.tex` (695 bytes) e `identificabilidad.tex` (borrador).
- **D = media del intervalo de generación usada como 1/γ.** Es coherente dentro del SIR (sin latencia, el intervalo de generación es exponencial con media 1/γ), pero el intervalo real de SARS-CoV-2 no es exponencial; esto cambia la relación r–R (la prueba h lo cuantifica). Es incertidumbre **estructural** que debe declararse.
- Dos convenciones de s0 entre simuladores (`sirmx`: s0 = S0/N; `src/sir.py`: s0 = (S0+I0)/N).
- `sirmx` (RK4, 4 subpasos) no cumple la tolerancia 1e-6 frente a `src/sir.py` con R0 = 8 (error ~5e-5); dentro de tolerancia con R0 ≤ 2.5.
- Unidades: el YAML guarda γ en d⁻¹ y D en días con fuente; N con fuente pero ubicación en el tabulado NO VERIFICADA.

---

## 8. Estado estadístico

### 8.1 v0

| Elemento | Qué se hizo | Diagnóstico |
|---|---|---|
| Parámetros estimados | Solo r (pendiente del crecimiento) en una ventana de 21 días por ola; R0 = R_eff/s0 con s0 y D fijados a mano | El resto (S0/N, D, FD, ε) se fijó o se "calibró" sin procedimiento estadístico reproducible. |
| Datos | Casos confirmados nacionales del tablero CONAHCYT (corte 25 jun 2023), suavizados 7 días, divididos por FD | La FD no cambia la pendiente r (invariancia de escala), pero se "propagó" como incertidumbre. |
| Función objetivo | Mínimos cuadrados (`curve_fit`) y verosimilitud de Poisson (Nelder-Mead) sobre conteos **suavizados e inflados** por 1/FD y redondeados | La verosimilitud de Poisson no es válida sobre conteos suavizados ni escalados; subestima la varianza. |
| Selección de ventana | Ventana de 21 días que maximiza R² | Sesgo de selección; R0 de BA.1 cambia de 4.68 a 3.27 entre ventanas de 14 y 35 días (según S08). |
| Incertidumbre | Monte Carlo con triangulares ±20 % en D, FD y S0/N, reportado como "IC 95 %" | **Incertidumbre asignada, no inferida.** El error estándar de r se ignora. |
| ε (evasión) | Barrido 0–1 minimizando RMSE contra los mismos datos que luego "validan" | Circular; curva plana entre 0.35 y 0.54 (S08); texto 0.444 vs código 0.50. |
| Residuos, identificabilidad, pruebas sintéticas | No se hicieron (salvo una mención en limitaciones) | — |
| Reproducibilidad | Mismo código de Monte Carlo produce dos tablas distintas (olas 3–6: 1.83/1.22/1.44/2.12 vs 2.84/1.82/5.41/4.82); RMSE escritos a mano (`RMSE_FINALES`) que no coinciden con la Tabla 4.1; `DETECTION_FACTORS` = 0.091, 0.111, 0.143, 0.167 (son 1/D, error de copia) | No reproducible como resultado científico. |
| Alerta temprana (Cap. 6) | Velocidad y aceleración calculadas **sobre la trayectoria SIR simulada**, umbrales por percentiles de la misma ola; tabla de "adelanto" (45, 38, 50, 40, 48 días) sin código que la genere en los notebooks revisados | No es evaluación predictiva; los adelantos son NO VERIFICADOS y probablemente no reproducibles. |

### 8.2 v2

| Elemento | Estado | Evidencia |
|---|---|---|
| Modelo de observación | Binomial negativa y Poisson sobre incidencia semanal (`src/`) o diaria con efecto de día de semana (`sirmx/`) | Dos verosimilitudes conviven; la decisión registrada de Omar fue "semanal". |
| Estimación | Máxima verosimilitud; perfiles con búsqueda de extremos (Venzon y Moolgavkar 1988); bootstrap paramétrico; Wald en `sirmx` | Implementado y probado en sintéticos. |
| Identificabilidad | Simetría estructural demostrada; perfiles planos reproducidos; el bootstrap da intervalos falsamente estrechos en direcciones no identificables (documentado honestamente en el acta F0) | `tests/test_identificabilidad.py`, `reports/resultados/sintetico_h1.json` |
| Recuperación sintética | Diseño 8 escenarios × 50 réplicas × 4 combinaciones de ruido/verosimilitud; **19 de 400 réplicas** corridas (4.75 %); celdas con n = 1–3 | `reports/recuperacion_sintetica_casos.md`; no concluyente. |
| Datos reales | Ninguno ajustado (correcto por la regla 3, pero F5 está bloqueada) | — |
| Plan de análisis | Dos planes: `plan_analisis.md` (borrador) y `plan_analisis_f4.md` ("CONGELADO" sobre decisiones I2–I4 inventadas por una sesión, que chocan con las I1–I4 que Omar fijó el 2026-11-03: I2 = BinNeg vs Poisson; I3 = truncado sin nowcasting; I4 = 1–3 puntos de cambio por AIC y BIC) | `docs/decisiones.md` líneas 7–14 lo admite; S06 `INSUMOS_CODIGO.md`. |
| Sensibilidad | Solo barrido de parámetros marcados como supuesto; sin sensibilidad global; rango de Byrne asimétrico | `config/parametros.yaml` |

---

## 9. Estado computacional

### 9.1 v0
Código disponible solo como impresión PDF de notebooks y un script (`analisis_montecarlo.py`) que **no reproduce el análisis**: genera R0 a partir de una normal centrada en valores objetivo escritos a mano (`target_R0`) y descarta las muestras de D y S0/N que calcula. Celdas dependientes de variables en memoria. Sin entorno, sin pruebas. 125 MB de PDF (capturas impresas) y `.DS_Store` en la historia de git.

### 9.2 v2 (rama `integracion/pt1-v2`)
- Estructura: `config/`, `data/{raw,processed}`, `src/` (14 módulos), `sirmx/` (9), `scripts/` (13), `tests/` (32 archivos + `teoria/`), `docs/`, `reports/`, `escrito/`, `Makefile`, `environment.yml`, `requirements.txt`. ~4 460 líneas de código y ~3 035 de pruebas.
- Reglas en código: el cargador rechaza parámetros sin fuente; los números del escrito salen de `reports/numeros.tex`.
- Duplicaciones sin resolver: dos simuladores, dos reglas de olas, dos verosimilitudes, dos planes, dos listas de dependencias (`environment.yml` sin numba ni xdist), D = 7 y semillas escritas a mano en `sirmx/`, `scripts/` y `tests/`.
- Integración: `main` sigue en el estado de octubre; 11 ramas; PR #1–#3 abiertos; la rama "buena" no tiene PR.
- El acta F0 declara una etiqueta `v0.0` que **no existe** en el remoto (`git ls-remote --tags` vacío).
- Autoría: 39 de 47 commits de la rama de integración tienen autor "Claude".

### 9.3 Pruebas ejecutadas en esta auditoría
| Suite | Resultado | Comentario |
|---|---|---|
| Rápida (teoría + `src/`; 223 pruebas) | **218 aprobadas, 5 fallos esperados (xfail estrictos), 35 avisos de obsolescencia de pandas**; 89 s con 4 procesos | Coincide exactamente con el HANDOFF. Los 5 xfail son discrepancias numéricas reales y documentadas. |
| Lenta F4 (`tests/test_1…8`, `sirmx/`; 40 pruebas) | **40 aprobadas**, 536 s con 4 procesos | Coincide con lo declarado. En total: 258 aprobadas + 5 xfail = 263, igual que el HANDOFF. |

Que el código pase sus pruebas **no** lo hace científicamente correcto: las pruebas verifican consistencia interna y recuperación sintética, no la adecuación del modelo a México.

---

## 10. Estado bibliográfico

| Indicador | `main` (repo) | Drive (v.2 2026) |
|---|---|---|
| Referencias en el índice | 79 | 84 (incluye J06, M07, M23, M24, N08 ausentes del repo) |
| Estado declarado | Las 79 "descargado" | 79 "descargado", 5 "pendiente_pdf" (B03, B08, C02, LIB01, LIB13) |
| PDFs | Ninguno en el repo (`fuentes/` no existe) | ~70 mapeados a clave, ~15 sin clave, 1 duplicado (`MAPEO_fuentes.csv`) |
| Fichas de lectura | 0 (solo `TEMPLATE.md`, que además viene llena con B03 como ejemplo) | 0 |
| Referencias con DOI en el índice | 23 de 79 | 30 de 84 |
| `referencias.bib` | Inutilizable: todas las entradas `@article` (incluidos libros), sin título ni revista, autores tipo "Diekmann et al." y "&" sin escapar | Igual |

Problemas específicos:
- **Ninguna referencia cumple la regla del propio proyecto** ("sin PDF leído no hay cita": PDF + ficha + estado "fichado").
- Probable error de metadatos: el índice asigna a I01 (Carnalla et al. 2023, *Salud Pública de México* según el nombre del PDF) el DOI 10.1002/jmv.29038, que por la revista parece corresponder a Basto-Abreu et al. 2023, *J. Med. Virol.* (archivo "sin clave" en Drive). NO VERIFICADO.
- El escrito v0 final no tiene bibliografía; la versión previa tiene 4 referencias, una con DOI que S08 reporta inexistente (NO VERIFICADO por mí). Las fuentes de D de la Tabla 3.1 de v0 (Gries 2021, Rodríguez-Morales 2021, Singh 2021, Lee 2022, Iwata 2023, Rosen 2023) no aparecen en ningún índice.
- `bibliografia/README.md` lista bloques A–O pero su tabla omite C, D y E, y refiere SP4/SP5/H4/H5 sin definirlos.
- Huecos para el núcleo físico-matemático que pide el prompt: hay Strogatz, Perko, Murray, Hethcote, Brauer, Ma y Earn; falta literatura específica sobre soluciones analíticas y estructura geométrica del SIR en el índice (Kröger y Schlickeiser 2020 está en Drive "sin clave"), sobre identificabilidad del SIR con fracción de reporte y sobre sensibilidad global.
- El cronograma de octubre pedía Zotero; `main` instaló un sistema "sin Zotero". Decisión no registrada.

---

## 11. Estado de los datos

| Conjunto | Dónde | Estado |
|---|---|---|
| JHU CSSE, confirmados acumulados México por fecha de reporte, 2020-01-22 → 2023-03-09 | `data/` en v2 (versionado, SHA-256 del CSV global) | Disponible. Fecha de **reporte**, no de síntomas; con reporte por lotes en 2022 (40–60 % de días en cero según `olas_resultados.md`). |
| DGE agregada por terceros (mexicovid19), nuevos por FECHA_INGRESO, 2020-02-27 → 2022-02-03 | `data/` en v2 | Disponible; fuente secundaria; termina antes del pico de Ómicron; el último día (10 casos) es truncamiento por retraso. |
| Tablero CONAHCYT, `Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv` (v0) | Drive (jun 2025) | Existe; no versionado; tipo de fecha no verificado. |
| Microdatos DGE (fuente primaria declarada) y 168 versiones históricas | — | **No existen.** Inventario generado: 0 de 168 presentes. `data/fuentes.csv` vacío. |
| ENSANUT (seroprevalencia) | Drive `serologia.csv` (transcrito con página) | 2020: 24.9 % (22.2–26.7) anti-N, todas las edades (I03). 2021: 57.9 % vs 59.2 % adultos (discrepancia abierta). 2022: 94.4 % anti-N. **No cargados** en `config/parametros.yaml` (valores en `null`). Cifras NO VERIFICADAS por esta auditoría contra los PDF. |
| Población N | YAML v2: 126 014 024 (INEGI 2020) | Ubicación en el tabulado NO VERIFICADA; v0 usó cuatro N distintos. |
| Medidas (DOF), movilidad, OxCGRT | `config/medidas.yaml` con fechas candidatas "sin citar" | No verificadas. |

Otros hallazgos: (a) las olas de v2 se definieron con JHU por fecha de reporte, mientras el ajuste previsto usa fecha de síntomas; (b) la frontera 1.ª/2.ª ola (2020-10-01) se fijó después de ver el resultado de la regla (zealous lo declara); (c) en v0 las etiquetas de variante están desalineadas: la "Ola 3 (Delta)" de jul 2025 va del 23 dic 2020 al 13 may 2021 y la "Ola 4 (Ómicron)" tiene pico el 10 ago 2021, antes de que Ómicron existiera; además, el algoritmo partió la ola de invierno 2020–21 en dos con un valle el 23 dic 2020 (picos el 18 dic y el 10 ene), compatible con el bache de reporte navideño; (d) "Alpha" nunca dominó en México según Zárate et al. 2022 (citado por S08 y por `olas_variantes.csv`; NO VERIFICADO por mí).

---

## 12. Estado de gestión

| Instrumento | Estado | Problema |
|---|---|---|
| Tablero de fases (Artifact) | F0 y F1 "en curso"; 2 de 101 pasos hechos; última actualización 2026-10-16 | Desincronizado: el repo declara F0 cerrada y tiene código de F2–F4. |
| Cronograma *Hito de enero* | 77 sesiones diarias de 1.5 h (115.5 h para F0–F4), hito 9 ene 2027; F5–F7 hasta 14 mar 2027 | Contradice el plan del tablero (L–S, 68 sesiones, hito 17 ene). Avance calculado "por fecha del calendario", no por evidencia. |
| Cronograma real ejecutado | F4 (planeada 18 dic–8 ene) se ejecutó el 3–5 nov; F1 (planeada con 4 fichas al 5 nov) tiene 0 fichas | Orden científico invertido. |
| Issues de GitHub | 0 | Las "issues I1–I4" referidas por las sesiones no existen como issues. |
| Actas | F0 (rama), F4 (rama, sin cifras) | El acta F0 cita una etiqueta inexistente; ningún acta en `main`. |
| Controles con el asesor | Control 1 programado para el 24 oct 2026 | Sin evidencia de envío ni respuesta; el acta F0 posterior dice "sin asesor". |
| Fechas institucionales | Ninguna registrada | Fecha de entrega, trimestre, formato y política de IA: desconocidos (el paso f0-07 "consultar a la coordinación" está pendiente). |

---

### 12.1 Estado de ejecución verificado (requisito 4.6)

Escala: No iniciado · En preparación · En ejecución · Implementado · Validado · Documentado · Cerrado. "Declarado" es lo que dicen las fuentes; "Verificado" es lo que esta auditoría puede sostener con evidencia.

| Elemento | Declarado | Verificado | Evidencia |
|---|---|---|---|
| F0 Alcance y decisiones | "Completada" / "Cerrada v0.0" / "en curso" | **En ejecución** | Acta en rama sin etiqueta; control con el asesor sin evidencia; decisiones institucionales sin confirmar |
| F1 Bibliografía | "En curso" | **En preparación** | Índice y PDFs existen; 0 fichas; `.bib` inutilizable |
| F2 Teoría (derivaciones a–k) | "En curso" | **Implementado** (como pruebas); capítulo **No iniciado** | 87 pruebas de teoría pasan; sin texto |
| F3 Datos | "En curso" | **En preparación** | Pipeline DGE implementado y probado con datos sintéticos; 0 datos primarios; olas calculadas con JHU (provisional) |
| F3 Regla de olas | — | **Implementado**, documentado; no validado con la serie primaria | `docs/regla_olas.md`, `resultados/olas/` |
| F4 Validación sintética | "En curso" | **En ejecución** | 19/400 réplicas; plan no congelado válidamente |
| Simulador SIR (`src/sir.py`) | Referencia oficial | **Validado** (contra soluciones exactas y DOP853, dentro de tolerancias documentadas) | Suite de pruebas |
| Identificabilidad H1 (sintética) | "Hecho" | **Implementado** y documentado; cobertura no estimada | `sintetico_h1.json`; una realización + 19 réplicas |
| F5 Análisis real | Bloqueada | **No iniciado** | — |
| F6 Escrito | Pendiente | **No iniciado** (salvo un borrador de sección) | `escrito/` |
| F7 Presentación | Pendiente | **No iniciado** | — |
| v0 (2025) | "Finalizado" (README feb 2026) | **Cerrado como antecedente; no válido como resultado** | §7–§9 |

## 13. Contradicciones

| ID | Contradicción | Fuentes |
|---|---|---|
| X01 | Modelo registrado SEIRS-V vs "solo SIR" | S06 plan 25-P / acta F0, README v2 |
| X02 | Asesor Dr. Escobar Ruiz (carta, README de oct, cronograma con controles) vs "trabajo personal, sin asesor" (acta F0, README v2) | S06, S01, S10 / S02 |
| X03 | "Mejora personal, sin fecha límite" (bitácora) vs cronograma con hito y fecha de tesis (mar 2027) vs prompt que lo trata como PT I evaluable | S09, S10 |
| X04 | Hito 9 ene 2027 (diario) vs 17 ene 2027 (L–S); F7 14 mar vs "fines de marzo" | S10 / S09 |
| X05 | Prioridad físico-matemática del prompt vs descarte del encuadre de espacio de fases (acta F0) | Prompt / S02 |
| X06 | "Nada bayesiano" (acta F0) vs comparación de métodos incluyendo bayesiano (prompt) | S02 / prompt |
| X07 | Análisis por olas desde el inicio (v2) vs "primero la serie completa sin dividir en olas" (prompt) | S02 / prompt |
| X08 | I2–I4 de F4 (inventadas) vs I1–I4 de Omar del 2026-11-03 | S02 `docs/decisiones.md` / S06 `INSUMOS_CODIGO.md` |
| X09 | Plan "CONGELADO" (F4) vs plan "BORRADOR, se congela al cerrar F4" | S02 |
| X10 | HANDOFF previo descarta JHU, frontera 2020-10-01 y D = 7 vs integración los incorpora | S02 |
| X11 | Verosimilitud semanal (decisión de Omar) vs diaria con día de semana (F4) | S02 |
| X12 | N de INEGI vs CONAPO; incubación mediana (G01) vs media 6.4 d (G03) | S02, S06 |
| X13 | Estado F0: "Completada" (README main), "Cerrada v0.0" (acta), "en curso" (tablero) | S01, S02, S09 |
| X14 | Bibliografía: 79 "descargado" (repo) vs 84 con 5 sin PDF (Drive); "sin Zotero" vs Zotero en el cronograma | S01, S06, S10 |
| X15 | v0: cinco o más conjuntos de R0 por ola con los mismos datos; ε 0.444 vs 0.50; RMSE de figuras vs tabla; prominence 500/1000/2500 | S05 |
| X16 | Carta de aceptación fechada "21 de diciembre de 2025" para el trimestre 25-P, con archivo creado el 23 may 2025 | S06 |

## 14. Errores (resumen; detalle en la matriz)

Críticos: M1, M2, M3, M5, M6 (§7.1); incertidumbre asignada como IC (§8.1); circularidad de ε; irreproducibilidad de v0; alerta temprana sobre curvas simuladas; etiquetas de variante desalineadas; rastro de conversación con IA en el escrito; datos editados por estética (truncado de la Ola 5 y borrado de puntos con S/N < 0, según S08, NO VERIFICADO por mí). En v2 no encontré errores matemáticos; sí errores de gobernanza (plan congelado sobre decisiones inventadas) y de metadatos (etiqueta inexistente, bibliografía).

## 15. Riesgos (resumen; detalle en `REGISTRO_RIESGOS.md`)

Los cinco con mayor exposición: (R01) desalineación con el registro institucional; (R02) calendario y fecha de entrega desconocidos; (R05) incapacidad de defender código y texto no escritos por el autor; (R04) datos primarios inaccesibles desde la nube; (R03) alcance excesivo para un PT I.

## 16. Recursos aprovechables

1. **Código v2 probado** como infraestructura: `src/sir.py` (referencia), `src/parametros.py` (regla de fuentes), `tests/teoria/` (11 derivaciones verificadas), `src/identificabilidad.py`, `src/verosimilitud.py`, pipeline DGE (`src/datos.py`, sin datos aún), regla de olas declarada con resultado negativo documentado.
2. **Borrador de la sección de identificabilidad** (`escrito/capitulos/identificabilidad.tex`), tras revisar la originalidad.
3. **Serología transcrita con página** (`serologia.csv`) y **parámetros D con fuente** (`parametros_D.csv`), pendientes de verificación contra PDF.
4. **Bibliografía**: ~70 PDF con clave en Drive, índice de 84 entradas.
5. **Diagnóstico previo** (S08): coincide con esta auditoría y ya propone una pregunta respondible.
6. **Lecciones de v0** como material de discusión (qué no hacer), no como resultados.

## 17. Trabajo que debe descartarse

| Elemento | Motivo |
|---|---|
| Todos los valores numéricos de v0 (R0 por ola, FD, S0/N, ε, RMSE, adelantos de alerta) | No reproducibles o mal definidos |
| Capítulos 2.3–2.4 de v0 (equilibrio endémico, bifurcación), afirmación de caos | Matemáticamente falsos |
| Monte Carlo triangular como cuantificación de incertidumbre | Incertidumbre asignada |
| Parámetro ε y "falsación de la inmunidad permanente" | No identificado y circular |
| Capítulo 6 de v0 (alerta temprana) | Evaluado sobre el propio modelo |
| Etiquetas de variante de v0 | Desalineadas |
| `analisis_montecarlo.py` | Genera resultados ficticios |
| `referencias.bib` actual | Inutilizable; regenerar desde metadatos verificados |
| `docs/plan_analisis_f4.md` como plan "congelado" | Basado en decisiones inventadas (conservar solo como referencia de métodos) |
| README de `main` como descripción del estado | Declara fases completadas sin evidencia |

## 18. Conclusiones

1. El estado real es **"En preparación"**: hay infraestructura, no resultados. Ninguna hipótesis ha sido evaluada con datos reales.
2. El trabajo de 2025 no es base científica; sirve como antecedente y como catálogo de errores a evitar.
3. La reconstrucción de noviembre aporta método y disciplina (fuentes obligatorias, pruebas, declaración previa de reglas), pero está fragmentada, sin integrar, desordenada respecto al orden científico y desalineada con la prioridad física que hoy se pide.
4. La incertidumbre más grande no es técnica sino **institucional**: qué proyecto está registrado, quién lo asesora, cuándo se entrega y si el cambio de SEIRS-V a SIR está autorizado.

## 19. Recomendaciones priorizadas

**Prioridad 0 — bloqueantes (antes de la Entrega 2):**
1. Confirmar con la coordinación y con el Dr. Escobar Ruiz el estatus del PT I: ¿se evaluó en 25-P?, ¿es una re-entrega, un PT II o un trabajo personal?, ¿se autoriza cambiar de SEIRS-V a SIR?, ¿quién asesora?, fecha de entrega, formato y política de uso de IA.
2. Decidir el marco rector: el del prompt actual (física matemática al centro) o el del acta F0. Registrar la decisión con fecha.
3. Fijar la disponibilidad real (horas por semana) y una fecha de entrega verificable.
4. Declarar una única fuente de verdad del estado del proyecto (propuesta: repositorio + un registro de decisiones), y congelar las demás (tablero viejo, cronogramas duplicados).

**Prioridad 1 — integridad:**
5. No fusionar nada a `main` hasta resolver P0; después, una sola integración con revisión del autor.
6. Plan de apropiación del código: el autor lee, explica y documenta cada módulo que se conserve; lo que no pueda defender se retira.
7. Retirar del discurso del proyecto toda cifra de v0.

**Prioridad 2 — base científica:**
8. Escribir primero el capítulo físico-matemático (con las derivaciones ya verificadas) y fichar las 15–20 fuentes núcleo antes de cualquier análisis real.
9. Revisar la originalidad de la simetría de escala y de la estructura de Poisson antes de reclamarlas.
10. Reformular H1 como resultado estructural + pregunta práctica sobre la serología.

**Prioridad 3 — datos y método:**
11. Conseguir (desde una computadora local) los microdatos DGE y, si H4 se conserva, las versiones históricas; registrar procedencia y hash.
12. Verificar ENSANUT contra los PDF y resolver la discrepancia de 2021; decidir cómo tratar serorreversión y anti-N por vacunas inactivadas.
13. Terminar la recuperación sintética completa antes de tocar datos reales.

**Prioridad 4 — gestión:**
14. Convertir las decisiones I1–I4 y los 20 pendientes de integración en issues con criterio de aceptación.
15. Rehacer `referencias.bib` desde DOI verificados; corregir estados del índice.

---

## 20. Resoluciones de Omar tras la Entrega 1 (2026-11-05)

| Pregunta | Respuesta | Efecto en la auditoría |
|---|---|---|
| P0-1 Estatus institucional | El PT I se evaluó en el trimestre 25-P. La reconstrucción es un **trabajo personal**. El trabajo original (el que está en el repo, `v0-anterior/`) se hizo con **SIR**, no con SEIRS-V. | Se cierran GOB-01, GOB-02 y GOB-03 y el riesgo R01. El plan 25-P (SEIRS-V) queda como documento histórico: fue la propuesta, no lo que se ejecutó ni se evaluó. El asesor ya no es requisito; su revisión es opcional. No hay formato ni política institucional que cumplir, aunque se mantiene el estándar académico que pide el prompt. |
| P0-2 Marco rector | "No lo sé, hay que decidir". | Sigue abierta. La auditoría da una recomendación en `REGISTRO_DECISIONES.md` (R-01). Se resuelve en la Entrega 2. |
| P0-3 Fecha de entrega | "Terminar lo antes posible"; sin fecha institucional. | La prioridad es el plazo más corto, y eso favorece el escenario conservador. Faltan las horas semanales para fijar fechas (Entrega 4). |
| Commit de la auditoría | "Como tú lo veas". | Se versiona `auditoria/` en la rama `claude/cool-einstein-qwqjvj`. |

Con esto, el hallazgo crítico de §1.2 deja de ser bloqueante. Las contradicciones X01–X03 quedan explicadas: el registro 25-P es histórico y la reconstrucción es voluntaria, sin fecha límite externa.

### Nota sobre la verificación de pruebas

La suite completa de `integracion/pt1-v2` se ejecutó en esta auditoría (copia en directorio temporal, entorno virtual propio): 258 aprobadas y 5 xfail estrictos, sin fallos. Esto verifica la **consistencia interna** del código, no la validez del modelo para México.
