# Regla declarada para delimitar las olas de COVID-19 en México

> **Estado:** declarada *antes* de aplicarse (ver historial de git: este archivo
> se versiona en un commit anterior a `src/olas.py`).
> **Fase:** F3 — Análisis de datos y olas epidemiológicas.

## 0. Motivación

La versión anterior (`v0-anterior/analisis_montecarlo.py`) delimitaba olas con
`find_peaks(-y, distance=100, prominence=500)` y, en otras iteraciones,
`prominence=2500`. Ese umbral está en **casos/día absolutos** y se afinó a mano
hasta obtener el número de olas esperado. Tiene dos defectos:

1. **No es invariante de escala.** 2500 casos/día es enorme frente a la ola 1
   (pico ≈ 7 000/día) y despreciable frente a la ola 4 (pico ≈ 50 000/día); el
   mismo umbral significa cosas distintas en cada ola.
2. **Es circular.** Si el parámetro se elige para "obtener cinco olas", el
   número de olas deja de ser un resultado.

Esta regla sustituye ese criterio por uno **relativo**, con un único parámetro
fijado por argumento previo, y declara de antemano qué se hace si el resultado
no coincide con las cinco olas convencionales.

## 1. Datos

| Rol | Fuente | Fecha de referencia | Cobertura |
|---|---|---|---|
| **Primaria** | JHU CSSE, `time_series_covid19_confirmed_global.csv`, fila *Mexico* (CC BY 4.0). Recoge el acumulado del comunicado diario de la SSa. | Fecha de **reporte** | 2020-01-22 → 2023-03-09 |
| Contraste (solo sensibilidad, olas 1–3) | Datos abiertos DGE agregados por `mexicovid19/Mexico-datos`, `series_de_tiempo/nuevos/covid19_mex_confirmados.csv` (Libre Uso MX). | `FECHA_INGRESO` a la unidad médica | 2020-02-27 → 2022-02-03 |

La serie preferible en epidemiología sería la de fecha de inicio de síntomas del
portal CONACYT/DGE, pero no es accesible desde el entorno de cómputo de este
análisis. Se usa la serie por fecha de reporte (que abarca toda la ventana hasta
febrero de 2023) y se contrasta con la serie por fecha de ingreso donde existe.
Las fronteras por fecha de reporte llevan un **retraso sistemático** de días a
semanas respecto a inicio de síntomas; esto se cuantifica en la sensibilidad
por fuente.

Transparencia: antes de fijar esta regla se inspeccionaron los máximos mensuales
de la serie JHU únicamente para verificar que la fuente cubre la ventana de
estudio. No se ha evaluado ningún valor del parámetro sobre los datos.

## 2. Ventana de estudio

`2020-02-27` (primer caso confirmado) → `2023-02-28` (cierre de la 5.ª ola según
el planteamiento del proyecto). La ventana se fija por diseño, no por los datos.

## 3. La regla

Sea $C_t$ el acumulado de casos confirmados.

**R1 — Incidencia diaria.** $y_t = \max(C_t - C_{t-1},\,0)$. Las diferencias
negativas (correcciones del acumulado) se ponen a cero.

**R2 — Suavizado.** $\bar y_t$ = media móvil **centrada de $w = 7$ días**
(elimina el ciclo semanal de reporte). No se corrigen manualmente días con
carga atrasada de casos; su efecto se evalúa en la sensibilidad (mediana móvil).

**R3 — Escala logarítmica.** $z_t = \ln(1 + \bar y_t)$. En un SIR la fase de
crecimiento y de caída es aproximadamente exponencial, de modo que la escala
natural de comparación es la logarítmica: una ola es un cambio *multiplicativo*
de la incidencia, no un cambio absoluto.

**R4 — Picos candidatos.** Todo máximo local de $z_t$ (una meseta cuenta como un
solo máximo, en su punto medio).

**R5 — Criterio de aceptación (único parámetro, $\rho$).** Para cada candidato
se calcula su **prominencia topográfica** en $z$:

$$P = z_{\text{pico}} - \max\big(\,\min_{\text{izq}} z,\ \min_{\text{der}} z\,\big),$$

donde cada mínimo se toma desde el pico hasta el primer punto más alto que el
pico (o el borde de la ventana) en esa dirección. Se acepta el pico como **ola**
si

$$P \ \ge\ \ln \rho, \qquad \rho = 2 .$$

En palabras: **una ola es un episodio en que la incidencia suavizada se
duplica, como mínimo, desde el valle que la precede y se reduce, como mínimo, a
la mitad hacia el valle que la sigue** (respecto del valle más alto de los dos).

*Por qué $\rho = 2$:* (i) la duplicación es la unidad natural del crecimiento
exponencial y la que se reporta para el tiempo de duplicación; (ii) tras el
promedio de 7 días, los artefactos de reporte residuales (festivos, cargas
atrasadas) son de orden ±20–30 %, muy por debajo de un factor 2; (iii) es el
valor redondo más simple que no depende de ningún ajuste a esta serie. El valor
se fija aquí y no se modifica tras ver el resultado.

**R6 — Fronteras.** Entre dos picos aceptados consecutivos, la frontera es el
día de **mínimo** de $\bar y_t$ en el intervalo abierto entre ambos. La ola $k$
abarca $[\,v_{k-1},\, v_k)$, con $v_0$ = inicio de ventana y la última ola
terminando en el fin de ventana. Se reportan inicio, pico, fin, duración,
incidencia en el pico y casos acumulados en la ola.

**R7 — Regla de no reajuste.** El número de olas es un **resultado**. Si la regla
con $\rho = 2$ no produce cinco olas, se reporta tal cual y la discrepancia se
discute; **no** se cambia $\rho$, $w$ ni la ventana para forzar cinco. La
correspondencia con la numeración convencional (1.ª–5.ª) se hace por la fecha
del pico frente a los periodos de dominancia de variantes de la §5.

## 4. Análisis de sensibilidad (declarado)

Se repite la regla variando **un factor a la vez** alrededor del caso base
($\rho = 2$, $w = 7$, media, JHU):

| Factor | Valores |
|---|---|
| $\rho$ (parámetro de la regla) | 1.25, 1.5, 1.75, **2**, 2.5, 3, 4 |
| $w$ (ventana de suavizado) | **7**, 14, 21 días |
| Suavizador | **media**, mediana |
| Fuente (solo hasta 2022-01-19) | **JHU (reporte)**, DGE (ingreso) |

Para cada variante se reporta: número de olas, fechas de frontera y
**desplazamiento en días** de cada frontera respecto del caso base
(emparejando por cercanía; una frontera sin pareja se marca como
aparecida/desaparecida). Criterio de robustez: una frontera es *robusta* si se
desplaza ≤ 14 días en todas las variantes de $w$ y suavizador y existe para
$\rho \in [1.5, 3]$.

Para la fuente DGE se descartan los últimos 14 días del archivo (registro
incompleto por retraso de captura) y la comparación se limita a las fronteras
anteriores a 2022-01-19.

## 5. Etiquetado por variante y estatus en el análisis

| Ola | Variante dominante | Fuente | Estatus |
|---|---|---|---|
| 1.ª | Linajes ancestrales (B.1, B.1.1, B.1.1.222; con D614G) | Taboada et al. 2021 | **Primario** |
| 2.ª | **B.1.1.519** (no Alpha ni Gamma: Alpha no logró dominar en México) | Zárate et al. 2022 (doi:10.1128/spectrum.02240-21); Taboada et al. 2021 | **Primario** |
| 3.ª | Delta (B.1.617.2, sublinajes AY.*) | Taboada et al. 2022 *(por verificar)*; CoViGen-Mex | **Primario** |
| 4.ª | Ómicron BA.1 / BA.1.1 | CoViGen-Mex / InDRE, informes de vigilancia genómica *(por verificar)* | Secundario, supuestos violados marcados |
| 5.ª | Ómicron BA.4/BA.5; en dic 2022–feb 2023, BQ.1 y XBB.1.5 | CoViGen-Mex / InDRE *(por verificar)* | Secundario, supuestos violados marcados |

Las referencias marcadas *por verificar* no pudieron cotejarse en línea desde el
entorno de cómputo y deben confirmarse antes de citarse en el manuscrito.

### Supuestos del SIR de parámetros constantes violados en las olas 4–5

| Supuesto | Ola 4 | Ola 5 |
|---|---|---|
| Población inicialmente susceptible y homogénea (sin **vacunación**) | Violado: cobertura amplia con esquema completo antes de dic 2021 | Violado: además, refuerzos |
| Inmunidad tras infección permanente (sin **escape inmune**) | Violado: Ómicron reinfecta a recuperados y vacunados | Violado: BA.5, BQ.1, XBB con escape adicional |
| Casos confirmados ∝ infecciones con fracción de detección constante (sin **pruebas caseras**) | Violado: auge de autopruebas no notificadas | Violado con más fuerza |

Por ello las olas 4–5 se delimitan con la misma regla y se incluyen en las
tablas, pero no forman parte del análisis primario de identificabilidad.

## 6. Productos

- `src/olas.py` — implementación de R1–R7 y de la sensibilidad.
- `resultados/olas/olas_base.csv` — fechas de cada ola (caso base).
- `resultados/olas/sensibilidad.csv` — tabla de sensibilidad.
- `resultados/olas/olas.png` — figura de control.
- `docs/olas_resultados.md` — resultados y discusión.
