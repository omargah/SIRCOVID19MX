# Olas de COVID-19 en México: resultados de la regla declarada

Regla: [`docs/regla_olas.md`](regla_olas.md) · Código: [`src/olas.py`](../src/olas.py) ·
Salidas: `resultados/olas/{declarada,A1}/` · Reproducir: `python3 src/olas.py`

Fuente primaria: JHU CSSE, casos confirmados en México por fecha de reporte.
Contraste: DGE por fecha de ingreso, disponible hasta 2022-01-20.
Ventana de estudio: 2020-02-27 → 2023-02-28.

## 1. Resumen

| | Regla declarada (ρ = 2, w = 7) | Enmienda A1 (ρ = 2, w = 28, lote corregido) |
|---|---|---|
| Número de olas | **15** | **4** |
| ¿Coincide con las 5 convencionales? | No: el reporte por lotes de 2022 fragmenta la serie | No: la 1.ª y la 2.ª olas no se separan |
| Fronteras robustas (§4) | 2 de 14 | 2 de 3 |

**Hallazgo principal.** Con la regla aplicada sin reajustes, **ningún valor de
ρ reproduce las cinco olas convencionales.** El valle de septiembre de 2020
entre la 1.ª y la 2.ª olas es menos profundo que el rebote de dic 2022–ene 2023
dentro de la 5.ª ola: ρ\* ≈ 1.46 frente a ρ\* ≈ 1.91 (tabla 3). Por eso
cualquier ρ que separe la 1.ª ola también separa ese rebote. La serie DGE por
fecha de ingreso confirma que la 1.ª ola es poco prominente (ρ\* = 1.48 a 28 d;
1.77 a 7 d), así que no es un artefacto de la fuente JHU.

## 2. Fechas de cada ola: enmienda A1, ρ = 2 (resultado de referencia)

`resultados/olas/A1/olas.csv`

| Ola (regla) | Inicio | Pico | Fin | Días | Pico (casos/d, 28 d) | Casos | Ola convencional | Variante dominante en el pico | Fuente | Estatus |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2020-02-27 | 2021-01-18 | 2021-05-15 | 444 | 14 839 | 2 357 403 | **1.ª + 2.ª (fusionadas)** | B.1.1.519 en el pico; ancestrales hasta nov 2020 | Zárate et al. 2022; Taboada et al. 2021 | Primario |
| 2 | 2021-05-16 | 2021-08-07 | 2021-12-09 | 208 | 17 406 | 1 531 024 | 3.ª | Delta (B.1.617.2, AY.\*) | Taboada et al. 2022 *(por verificar)* | Primario |
| 3 | 2021-12-10 | 2022-01-25 | 2022-04-24 | 136 | 36 978 | 1 822 071 | 4.ª | Ómicron BA.1/BA.1.1 | CoViGen-Mex/InDRE *(por verificar)* | ⚠ Secundario: vacunación, escape inmune, pruebas caseras |
| 4 | 2022-04-25 | 2022-07-14 | 2023-02-28 | 310 | 25 001 | 1 718 792 | 5.ª (incluye el rebote de dic 2022–feb 2023) | BA.4/BA.5; después BQ.1, XBB.1.5 | CoViGen-Mex/InDRE *(por verificar)* | ⚠ Secundario: vacunación con refuerzos, escape inmune, pruebas caseras |

La 4.ª ola de la regla equivale a la 5.ª convencional y, como plantea el
proyecto, llega hasta febrero de 2023.

**Delimitación condicional de la 1.ª ola (no se adopta como base).** La frontera
entre la 1.ª y la 2.ª olas aparece solo si ρ ≤ 1.455 (con w = 28). En ese caso
el valle cae el **2020-10-01** (tabla 3). Si el análisis primario necesita
ajustar la 1.ª y la 2.ª olas por separado, esa decisión debe declararse aparte
(por ejemplo, fijar la frontera por el cambio de variante dominante en lugar de
por el valle de incidencia) y no puede presentarse como un resultado de esta
regla.

## 3. Sensibilidad al parámetro de la regla y a los demás factores

### Tabla 1. Enmienda A1: número de olas y desplazamiento de fronteras (días respecto de la base)

Fronteras base: v1 = 2021-05-16 (3.ª), v2 = 2021-12-10 (3.ª→4.ª), v3 = 2022-04-25 (4.ª→5.ª).

| Factor | Valor | n olas | Δv1 | Δv2 | Δv3 | Fronteras nuevas |
|---|---|---|---|---|---|---|
| ρ | 1.25 | 10 | 0 | 0 | 0 | 2020-10-01, 2022-03-23, 2022-05-09, 2022-05-15, 2022-11-07, 2022-11-17 |
| ρ | 1.5 | 5 | 0 | 0 | 0 | 2022-11-07 |
| ρ | 1.75 | 5 | 0 | 0 | 0 | 2022-11-07 |
| **ρ** | **2** | **4** | 0 | 0 | 0 | — |
| ρ | 2.5 | 4 | 0 | 0 | 0 | — |
| ρ | 3 | 4 | 0 | 0 | 0 | — |
| ρ | 4 | 4 | 0 | 0 | 0 | — |
| w | 21 | 5 | 0 | +2 | +10 | 2022-11-10 |
| w | 35 | 4 | +3 | +3 | +3 | — |
| suavizador | mediana | 25 | +7 | −19 | +7 | 21 fronteras en 2022–23 |
| fuente | DGE (ingreso), hasta 2022-01-19 | 2 | +3 | n/a\* | — | — |

\* La serie DGE termina el 2022-01-20, antes del pico de Ómicron, por lo que la
frontera v2 no puede evaluarse con esa fuente. No es una desaparición real.

**Lectura.** Las tres fronteras son estables frente a ρ en todo el rango
[1.25, 4], con desplazamiento de 0 días. ρ solo cambia **cuántas** olas hay:

- de 4 olas para ρ ≥ 1.92,
- a 5 para 1.46 < ρ ≤ 1.91 (el rebote de dic 2022–ene 2023 se separa, frontera 2022-11-07),
- a 6 o más para ρ ≤ 1.455 (aparece la frontera 1.ª/2.ª, 2020-10-01).

Frente a la ventana de suavizado, las fronteras se mueven ≤ 10 días. La mediana
móvil no sirve en el régimen de reporte por lotes: con 40–60 % de días en cero,
la mediana colapsa y fragmenta la serie. Por eso v2 no supera el criterio de
robustez (−19 días), aunque sí es estable frente a w y ρ.

### Tabla 2. Rejilla exploratoria ρ × w: número de olas (A1, lote corregido)

`resultados/olas/A1/rejilla_rho_w.csv`

| ρ \ w | 7 | 14 | 21 | 28 | 35 | 42 |
|---|---|---|---|---|---|---|
| 1.25 | 53 | 28 | 13 | 10 | 7 | 6 |
| 1.5 | 30 | 11 | 6 | 5 | 5 | 5 |
| 1.75 | 20 | 8 | 5 | 5 | 4 | 4 |
| **2** | 14 | 6 | 5 | **4** | 4 | 4 |
| 2.5 | 10 | 4 | 4 | 4 | 4 | 4 |
| 3 | 10 | 4 | 4 | 4 | 4 | 4 |
| 4 | 6 | 4 | 4 | 4 | 4 | 4 |

Para w ≥ 14 y ρ ≥ 2.5 el resultado se estabiliza en 4 olas. Las 5 olas que
aparecen en algunas casillas son siempre las 4 anteriores más el rebote de
dic 2022, **nunca** la 1.ª ola convencional.

### Tabla 3. ρ crítico por pico (A1, w = 28)

Un pico es ola si y solo si ρ ≤ ρ\* = exp(prominencia en escala log). Esta tabla
resume la sensibilidad completa al parámetro. Ver `resultados/olas/A1/rho_critico.csv`.

| Rango | Pico | ρ\* | Casos/d | Valle izq. | Valle der. | Ola convencional |
|---|---|---|---|---|---|---|
| 1 | 2022-01-25 | 83.3 | 36 978 | — | 2022-11-07 | 4.ª |
| 2 | 2022-07-14 | 40.8 | 25 001 | 2022-04-25 | 2022-11-07 | 5.ª |
| 3 | 2021-08-07 | 7.61 | 17 406 | — | 2021-12-10 | 3.ª |
| 4 | 2021-01-18 | 6.52 | 14 839 | — | 2021-05-16 | 2.ª |
| 5 | 2023-01-07 | 1.91 | 5 022 | 2022-11-07 | 2023-02-05 | 5.ª (rebote BQ.1/XBB) |
| 6 | 2020-07-20 | 1.46 | 6 507 | — | 2020-10-01 | 1.ª |
| 7 | 2022-11-09 | 1.35 | 636 | 2022-11-07 | 2022-11-17 | ruido de reporte |
| 8 | 2022-03-26 | 1.34 | 4 570 | 2022-03-23 | 2022-04-25 | BA.2 / ruido |

Hay un salto claro entre el 4.º pico (6.5) y el 5.º (1.9). Las cuatro olas de
la regla están separadas del resto por un factor > 3 en ρ\*. En la serie DGE
(w = 28): Delta 7.57, 2.ª ola 6.91, 1.ª ola 1.48.

### Tabla 4. Regla declarada sin enmienda (ρ = 2, w = 7): por qué se enmendó

`resultados/olas/declarada/`

| Factor | Valor | n olas | Comentario |
|---|---|---|---|
| ρ | 1.25 / 1.5 / 1.75 / **2** / 2.5 / 3 / 4 | 54 / 31 / 20 / **15** / 10 / 10 / 6 | Fragmentación en 2022–23 por reporte por lotes |
| w | **7** / 14 / 21 | **15** / 6 / 5 | |
| suavizador | media / mediana | 15 / 39 | |
| fuente (hasta 2022-01-19) | JHU / DGE | 3 / 2 | Con JHU, la "1.ª ola" tiene su pico el 2020-10-06, que es el lote retroactivo |

Las fronteras de 2020–2021 (2021-05-22 y 2021-12-19) se desplazan ≤ 12 días
entre variantes. Las de 2022–23 aparecen y desaparecen. Solo 2 de 14 fronteras
superan el criterio de robustez.

## 4. Supuestos y limitaciones

- **Fecha de reporte, no de inicio de síntomas.** Las fronteras JHU van algunos
  días por detrás de las DGE (2.ª/3.ª: 2021-05-16 frente a 2021-05-19, 3 días).
  La serie por inicio de síntomas (portal CONACYT/DGE) no fue accesible desde el
  entorno de cómputo. Repetir con ella es el siguiente paso natural.
- **La enmienda A1 es post hoc.** Se declaró antes de ejecutarla, pero después de
  ver que w = 21 producía 5 olas (§7 de la regla). Los artefactos que la motivan
  se identificaron con criterios independientes del número de olas (lote de un
  día de +28 115 casos; rachas de hasta 8 días sin reporte).
- **Olas 4–5:** delimitadas con la misma regla, pero violan los supuestos del SIR
  de parámetros constantes: vacunación (susceptibles no homogéneos), escape
  inmune (reinfección) y pruebas caseras (fracción de detección decreciente). Se
  incluyen solo como análisis secundario.
- **Etiquetas de variante:** los periodos de dominancia son aproximados. Las
  fuentes de las olas 3–5 están marcadas *por verificar* y deben confirmarse con
  CoViGen-Mex/InDRE antes de citarse.
