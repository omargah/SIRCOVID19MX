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

- `src/olas.py` — implementación de R1–R7, de la enmienda A1 (§7) y de la sensibilidad.
- `resultados/olas/{declarada,A1}/olas.csv` — fechas de cada ola.
- `resultados/olas/{declarada,A1}/sensibilidad.csv`, `robustez_fronteras.csv`,
  `rho_critico.csv`, `rejilla_rho_w.csv` — sensibilidad.
- `resultados/olas/{declarada,A1}/olas.png` — figura de control.
- `docs/olas_resultados.md` — resultados y discusión.

---

## 7. Enmienda A1 (posterior a la primera aplicación; declarada antes de ejecutarla)

> Esta sección se añadió **después** de aplicar R1–R7 y **antes** de ejecutar
> la enmienda (ver historial de git). No es confirmatoria: al redactarla ya se
> conocía la tabla de sensibilidad de §4, que incluye $w = 21$.

**Resultado de la regla declarada.** Con $\rho = 2$, $w = 7$ y la fuente JHU,
la regla produce **15 episodios**, no 5 (`resultados/olas/declarada/`). Por R7
se reporta tal cual. El diagnóstico muestra que el exceso se debe a dos
artefactos de reporte, que se identifican con criterios que **no dependen del
número de olas**:

1. **Carga retroactiva del 2020-10-05:** +28 115 casos en un día (los días
   vecinos registran ≈ 5 000). La media de 7 días convierte ese lote en un pico
   espurio (2020-10-06) que pasa a ser el "pico" de la 1.ª ola.
2. **Reporte por lotes desde 2022:** la fracción de días con cero casos
   reportados pasa de < 5 % (2020–sep 2021) a 20–60 % (oct 2021–2023), con
   rachas de hasta **$g = 8$ días** consecutivos sin reporte (oct–dic 2022).
   Con $w = 7$, que un lote quede dentro o fuera de la ventana cambia
   $\bar y_t$ en más de un factor 2, el umbral de R5.

**A1.a — Lote retroactivo.** El valor del 2020-10-05 se sustituye por la
mediana de los 7 días centrados en esa fecha. Es la única corrección puntual.

**A1.b — Ventana de suavizado ligada al régimen de reporte.** Para que la
entrada o salida de un solo lote no altere $\bar y_t$ en un factor comparable
a $\rho$, la ventana debe contener al menos 3 ciclos de reporte completos:
$w \ge 3\,(g + 1) = 27$. Redondeando a semanas completas, **$w = 28$ días**, que
se aplica a toda la serie.

**Sin cambios:** $\rho = 2$, R3–R7 y la ventana de estudio.

**Sensibilidad de A1:** la misma de §4, con $w \in \{21, 28, 35\}$ en lugar de
$\{7, 14, 21\}$. Además se calcula, como análisis **exploratorio**, la rejilla
completa $\rho \times w$ con el número de olas.

**Etiquetado (precisión de R7).** Cada ola detectada se etiqueta por el periodo
de dominancia que contiene la fecha de su **pico** y se listan todos los
periodos que su intervalo abarca. Periodos aproximados, *por verificar con
CoViGen-Mex/InDRE*:

| Periodo | Variante dominante | Ola convencional |
|---|---|---|
| 2020-02-27 – 2020-11-30 | Ancestrales (B.1, B.1.1, B.1.1.222) | 1.ª |
| 2020-12-01 – 2021-05-31 | B.1.1.519 | 2.ª |
| 2021-06-01 – 2021-12-14 | Delta (B.1.617.2, AY.*) | 3.ª |
| 2021-12-15 – 2022-04-30 | Ómicron BA.1/BA.1.1 (BA.2 al final) | 4.ª |
| 2022-05-01 – 2022-10-31 | Ómicron BA.4/BA.5 | 5.ª |
| 2022-11-01 – 2023-02-28 | Ómicron BQ.1, XBB.1.5 | 5.ª (extensión a feb 2023) |

---

## 8. Frontera aparte 1.ª/2.ª ola (decisión POSTERIOR; criterio externo a la regla de la curva)

> **Estatus:** esta sección se añadió **después** de ver el resultado de la
> regla principal con la enmienda A1 (4 olas; la 1.ª y la 2.ª convencionales
> quedan fusionadas en un solo episodio con pico 2021-01-18) y **antes** de
> implementarla en `src/olas.py` (ver historial de git). **No es un resultado
> de la regla R1–R7 + A1**, sino una decisión de modelado tomada a la vista de
> ese resultado. Se declara aparte para que no pueda confundirse con él.

**Motivo (externo a la curva de incidencia).** La 1.ª y la 2.ª olas
convencionales corresponden a poblaciones virales distintas: linajes
ancestrales (B.1, B.1.1, B.1.1.222) hasta ≈ nov 2020 y B.1.1.519 después
(Zárate et al. 2022, doi:10.1128/spectrum.02240-21; Taboada et al. 2021), con
el reemplazo durante el hueco de incidencia de sep–nov 2020. El SIR de
parámetros constantes no debe ajustar ambos episodios con un solo juego de
parámetros. La regla de la curva (R5, ρ = 2) no los separa porque el valle es
somero (ρ\* ≈ 1.46 con w = 28); la separación se justifica, por tanto, por la
literatura de variantes y **no** por la prominencia.

**Lo que NO cambia.** ρ = 2, w = 28, la corrección del lote 2020-10-05, R1–R7,
la ventana de estudio y la salida de A1 (`resultados/olas/A1/`) quedan
intactos. No se introduce ningún parámetro nuevo.

**F1 — Picos que delimitan.** Dentro de la ola 1 de A1 (episodio fusionado):

- *pico de la 2.ª ola*: el pico aceptado por A1 (2021-01-18);
- *pico de la 1.ª ola*: el máximo local de $z_t$ (R3–R4, misma serie suavizada
  de A1) con **mayor prominencia** (R5) entre los candidatos anteriores al pico
  de la 2.ª ola. Se usa la misma prominencia de R5, sin umbral.

**F2 — Frontera.** La frontera 1.ª/2.ª es el día de **mínimo de $\bar y_t$**
(media móvil centrada de 28 días, A1) en el intervalo abierto entre ambos
picos, es decir, el mismo criterio de R6 aplicado a ese par de picos. La 1.ª
ola abarca $[\,$2020-02-27$,\ v)$ y la 2.ª, $[\,v,\ $fin de la ola 1 de A1$\,]$.
El resto de las olas de A1 no se modifica: el total es 5 = 4 (A1) + 1 (separación).

**F3 — Expectativa declarada y verificación.** Por la tabla de ρ\* de A1 se
espera que la frontera caiga cerca del **2020-10-01**. Se verifica que cae
entre 2020-09-01 y 2020-11-30 (dentro del hueco de sep–nov 2020); si no
cayera ahí, se reporta tal cual y no se ajusta nada.

**F4 — Sensibilidad.** Se repite F1–F2 con las ventanas de sensibilidad de A1,
$w \in \{21, 28, 35\}$ (además de 7 y 14 como exploración), y se reporta el
desplazamiento en días de la frontera respecto de $w = 28$. Se señala si supera
10 días.

**Productos.** `resultados/olas/A1_frontera/` (`olas.csv`, `frontera_1_2.csv`,
`sensibilidad_frontera.csv`, `olas.png`). Toda tabla o texto que use 5 olas debe
indicar que la separación 1.ª/2.ª es un **criterio externo a la regla de la
curva, tomado después de ver el resultado de la regla principal**.
