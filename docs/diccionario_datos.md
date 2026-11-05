# Diccionario de datos — microdato COVID-19 de la DGE

Proyecto Terminal · Fase F3 (datos y olas). Documento mantenido a mano.
Complementa `docs/nota_diferencias.md` (generado), `docs/eda.md` (generado) y
`docs/inventario_historicos.md` (generado).

## 1. Fuentes (citar siempre los dos niveles)

| Nivel | Fuente | Uso en el proyecto |
|---|---|---|
| **1 · Primaria** | Secretaría de Salud, Dirección General de Epidemiología (DGE). *Datos Abiertos — Información referente a casos COVID-19 en México* (microdatos del sistema de vigilancia SISVER/SINAVE) y su *Diccionario de datos* y *Catálogos* oficiales (`diccionario_datos_covid19.zip`, mismo portal). <https://www.gob.mx/salud/documentos/datos-abiertos-152127>; históricos en <https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/historicos/> | Fuente de todas las series (`src/datos.py`). |
| **2 · Secundaria** | CONAHCYT (antes CONACYT). *COVID-19 Tablero México*, «Descarga de datos», archivo `Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv`. <https://datos.covid-19.conacyt.mx/>. Declara como fuente a la DGE. | Solo para comparar contra el PT1 original (`src/comparar_tablero.py`). |

Forma de cita sugerida en el manuscrito:

> Elaboración propia con microdatos de la DGE, Secretaría de Salud (Datos Abiertos COVID-19, versión con
> `FECHA_ACTUALIZACION` = AAAA-MM-DD, descargada el AAAA-MM-DD, SHA-256 `…`). En el PT1 se usó la serie
> derivada publicada por el tablero CONAHCYT (archivo del 25-jun-2023), que a su vez procesa los datos de la DGE.

La procedencia exacta (URL, fecha de descarga, SHA-256) de cada archivo está en
`data/fuentes.csv` (`scripts/registrar_fuente.py`) y se copia al
`data/processed/manifiesto.json` de cada corrida.

> **Verificación pendiente.** El entorno donde se escribió este documento no tenía acceso a gob.mx.
> Los catálogos de la §3 corresponden a la estructura publicada de la base; las fechas de la §4 deben
> contrastarse con los documentos oficiales (columna «Verificado»), en especial con el diccionario y los
> catálogos que vienen en el zip de la DGE descargado por Omar. Cualquier discrepancia: corregir aquí y,
> si afecta códigos, en `src/datos.py`.

## 2. Variables usadas

Una fila del microdato = una persona registrada en el sistema de vigilancia
(caso sospechoso estudiado), no una prueba. Solo se leen estas columnas:

| Variable | Tipo | Uso en el pipeline | Notas |
|---|---|---|---|
| `FECHA_ACTUALIZACION` | fecha | corte de la versión; cota superior de fechas válidas | igual en todas las filas de una versión |
| `ID_REGISTRO` | texto | detección de duplicados entre archivos (hash de 64 bits) | estable entre versiones (supuesto a verificar con históricos) |
| `ORIGEN` | cat. | % USMER en EDA | 1 USMER (unidad monitora), 2 fuera de USMER, 99 NE |
| `ENTIDAD_RES` | cat. | ámbito nacional: residentes en 1–32 | 1–32 entidades; 36 EUM, 97 NA, 98 SI, 99 NE |
| `ENTIDAD_UM` | cat. | variante alternativa (entidad de la unidad médica) | idem |
| `TIPO_PACIENTE` | cat. | hospitalizaciones | 1 ambulatorio, 2 hospitalizado, 99 NE |
| `FECHA_SINTOMAS` | fecha | **fecha de referencia de la serie principal** | declarada por el paciente |
| `FECHA_INGRESO` | fecha | hospitalizaciones; volumen de pruebas; retrasos | fecha de ingreso a la unidad (registro) |
| `FECHA_DEF` | fecha | defunciones | `9999-99-99` = no falleció |
| `UCI` | cat. (Sí/No) | ingresos a UCI | 1 sí, 2 no, 97 no aplica (ambulatorio) |
| `CLASIFICACION_FINAL` | cat. | **definición de caso** | ver §3 (desde otoño 2020) |
| `RESULTADO_LAB` | cat. | homologación de versiones intermedias | 1 positivo, 2 no positivo, 3 pendiente, 4 no adecuado, 97 no aplica |
| `RESULTADO` | cat. | homologación de versiones 2020 | 1 positivo, 2 no positivo, 3 pendiente |
| `TOMA_MUESTRA_LAB` | cat. (Sí/No) | volumen de pruebas | 1 sí, 2 no |
| `TOMA_MUESTRA_ANTIGENO` | cat. (Sí/No) | volumen de pruebas de antígeno | 1 sí, 2 no |
| `RESULTADO_ANTIGENO` | cat. | (leída, no usada aún) | 1 positivo, 2 negativo, 97 no aplica |

Catálogo Sí/No común: 1 sí, 2 no, 97 no aplica, 98 se ignora, 99 no especificado.
Formato de fecha: `AAAA-MM-DD` (el lector acepta también `DD/MM/AAAA`).

## 3. Definición operativa de caso confirmado

### 3.1 Catálogo `CLASIFICACION_FINAL`

| Código | Descripción (catálogo DGE) | ¿Confirmado? |
|---|---|---|
| 1 | Caso de COVID-19 confirmado por asociación clínica epidemiológica | sí |
| 2 | Caso de COVID-19 confirmado por comité de dictaminación | sí |
| 3 | Caso de SARS-CoV-2 confirmado (laboratorio o prueba de antígeno) | sí |
| 4 | Inválido por laboratorio | no |
| 5 | No realizado por laboratorio | no |
| 6 | Caso sospechoso (sin resultado definitivo) | no |
| 7 | Negativo a SARS-CoV-2 | no |

### 3.2 Definición usada (serie `confirmados`)

> **Caso confirmado** = registro con `CLASIFICACION_FINAL ∈ {1, 2, 3}` y `ENTIDAD_RES ∈ {1,…,32}`,
> contado en su `FECHA_SINTOMAS` (válida, ≥ 2020-01-01 y ≤ `FECHA_ACTUALIZACION`).

Es la definición que aplica la DGE en sus comunicados desde que existe `CLASIFICACION_FINAL`. Que sea
también la del tablero se comprueba empíricamente en `docs/nota_diferencias.md` (prueba D4: variante de la
serie propia más cercana al tablero).
Las variantes se guardan como columnas para análisis de sensibilidad:

| Columna | Definición |
|---|---|
| `confirmados_lab_antigeno` | solo código 3 (excluye asociación y dictaminación) |
| `confirmados_asoc_clin_epi`, `confirmados_dictaminacion` | códigos 1 y 2 por separado |
| `confirmados_todas_entidades` | 1–3 sin filtrar residencia |
| `confirmados_por_entidad_um` | 1–3 por entidad de la unidad médica |
| `sospechosos`, `negativos` | códigos 6 y 7 |

Segunda serie (`serie_nacional_hosp_def.csv`): `hospitalizados_confirmados` (confirmados con
`TIPO_PACIENTE=2`, por `FECHA_INGRESO`), `uci_confirmados`, `defunciones_confirmadas` (confirmados con
`FECHA_DEF` válida, por `FECHA_DEF`) y `defunciones_conf_por_fecha_sintomas`.

### 3.3 Homologación de versiones antiguas

Las versiones de 2020 previas a `CLASIFICACION_FINAL` solo traen `RESULTADO` (o `RESULTADO_LAB`). Para
que el pipeline lea cualquier versión, se mapea (`src/datos.py`, `MAPA_RESULTADO*`):

| Antiguo | → `CLASIFICACION_FINAL` equivalente |
|---|---|
| `RESULTADO`=1 positivo | 3 |
| `RESULTADO`=2 no positivo | 7 |
| `RESULTADO`=3 pendiente | 6 |
| `RESULTADO_LAB`=4 no adecuado | 4 |
| `RESULTADO_LAB`=97 no aplica (sin muestra) | 6 |

**Advertencia:** en esas versiones no existían las categorías 1 y 2, de modo que «confirmado» equivale a
«confirmado por laboratorio». Una serie construida con una versión de 2020 *no* es comparable con una
posterior sin tomar en cuenta la reclasificación retroactiva (§4).

## 4. Cambios de criterio y de estructura 2020–2022

Efecto esperado = cómo se ve el cambio en una serie por fecha de inicio de síntomas. «Verificado» se
marca al contrastar con el documento oficial citado (lineamiento o diccionario de la DGE) y con la
cronología observada en `docs/inventario_historicos.md`.

| # | Fecha aprox. | Cambio | Efecto esperado en la serie | Documento a consultar | Verificado |
|---|---|---|---|---|---|
| C1 | ene–mar 2020 | Definición operacional inicial de caso sospechoso ligada a antecedente de viaje/contacto; confirmación solo por laboratorio de la red InDRE. | Muy pocas pruebas; confirmados = laboratorio. | Avisos epidemiológicos CONAVE (ene–mar 2020) | ☐ |
| C2 | 24-mar-2020 (fase 2) | Se elimina el requisito de viaje: sospechoso = ≥ 2 de tos, fiebre, cefalea + ≥ 1 síntoma acompañante. Estrategia de muestreo centinela: en USMER se muestrea ~10 % de ambulatorios y 100 % de graves; fuera de USMER, solo graves. | Subregistro grande y variable de leves; sesgo hacia hospitalizados (`ORIGEN` importa). | *Lineamiento estandarizado para la vigilancia epidemiológica y por laboratorio de COVID-19* (mar/abr 2020) | ☐ |
| C3 | 12–14-abr-2020 | Inicio de la publicación diaria del microdato en Datos Abiertos. Primera versión histórica disponible. | Inicio del inventario (§ inventario). | Portal Datos Abiertos DGE | ☐ |
| C4 | ago-2020 | Actualización del lineamiento: sospechoso = ≥ 1 de tos, fiebre, disnea o cefalea + ≥ 1 acompañante (incluye anosmia/disgeusia). Se formalizan la **confirmación por asociación clínica-epidemiológica** (contacto de un confirmado, sin muestra) y por **comité de dictaminación** (defunciones sin muestra válida). | Aumento de confirmados sin prueba (códigos 1 y 2), sobre todo en defunciones. | *Lineamiento estandarizado…* (actualización ago-2020) | ☐ |
| C5 | oct-2020 | **Cambio de estructura de la base:** `RESULTADO` se reemplaza por `RESULTADO_LAB` y se agrega `CLASIFICACION_FINAL` (1–7). La nueva clasificación se aplica **retroactivamente** a todos los registros desde 2020. | Salto en el acumulado de confirmados (más casos en fechas pasadas) entre versiones antes/después del cambio. | Diccionario de datos DGE (versión oct-2020); comunicado técnico diario | ☐ |
| C6 | fines 2020–inicios 2021 | Incorporación de **pruebas rápidas de antígeno**: columnas `TOMA_MUESTRA_ANTIGENO`, `RESULTADO_ANTIGENO`; un positivo por antígeno se clasifica como 3. | Aumento del volumen de pruebas y del número de confirmados; cambio en la positividad. Ver EDA §4 (primera semana con antígeno). | Diccionario de datos DGE; lineamiento con uso de antígeno | ☐ |
| C7 | 2021 | Revisiones del lineamiento (definición de caso sospechoso de enfermedad respiratoria viral, ERV) que integran COVID-19 a la vigilancia de virus respiratorios. | Cambios en qué se registra como sospechoso → denominador de positividad. | *Lineamiento estandarizado para la vigilancia epidemiológica y por laboratorio de la enfermedad respiratoria viral* (2021) | ☐ |
| C8 | ene-2022 (ómicron) | Saturación de la capacidad diagnóstica; positividad máxima; aumento relativo de confirmaciones por asociación clínica-epidemiológica; recomendaciones de aislamiento sin prueba para casos leves. | Subregistro creciente en la ola de ómicron: el pico de confirmados subestima más la incidencia real que en olas previas. | Lineamiento ERV actualizado (ene-2022); comunicados técnicos | ☐ |
| C9 | 2022–2023 | Bases anuales «cerradas» por año de registro (p. ej. `COVID19MEXICO2020.zip`, `…2021.zip`) además de la base vigente; periodicidad de actualización menor. | Si se combinan varias bases, revisar solapamiento de `ID_REGISTRO` (el pipeline descarta duplicados conservando la versión más reciente). | Portal Datos Abiertos DGE | ☐ |

Notas:

- Las fechas de C1–C9 son aproximadas y se escriben con la confianza que permite la memoria del autor del
  código; **no** usarlas en el manuscrito sin la marca ☑ y la cita del documento.
- C5 y C6 deben aparecer como cambios de columnas en la cronología de esquemas del inventario; si la
  cronología observada difiere, corregir esta tabla.

## 5. Consecuencias para la serie y reglas del pipeline

1. **Retroactividad:** cada versión de la DGE reescribe el pasado (resultados pendientes que se resuelven,
   dictaminaciones, depuración). La serie depende de la versión: se documenta su `FECHA_ACTUALIZACION` y
   su hash en el manifiesto.
2. **Truncamiento por la derecha:** los últimos días antes del corte están incompletos (ver `docs/eda.md` §3).
3. **Duplicados:** `ID_REGISTRO` repetido → se conserva el de la versión con `FECHA_ACTUALIZACION` más
   reciente (desempate por nombre de archivo). Contador en el manifiesto.
4. **Fechas inválidas:** fuera de [2020-01-01, `FECHA_ACTUALIZACION`] o mal formateadas se excluyen de la
   serie correspondiente y se cuentan en el manifiesto.
5. **Determinismo:** sin semillas ni marcas de tiempo; salidas ordenadas; `python -m src.datos
   --verificar-determinismo` compara byte a byte dos corridas.
