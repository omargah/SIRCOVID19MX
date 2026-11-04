# Nota de diferencias: serie propia (microdato DGE) vs. tablero CONAHCYT

> **Estado: PENDIENTE DE CORRIDA CON DATOS REALES.** Este archivo se reemplaza
> automáticamente al ejecutar `make serie comparar` (o `python -m src.comparar_tablero`)
> una vez que el microdato de la DGE y el CSV del tablero estén en `data/raw/` y
> registrados en `data/fuentes.csv`. Hasta entonces solo describe qué se va a medir y
> qué causas se esperan; **ninguna cifra de este archivo proviene de datos reales**.

## Fuentes (dos niveles)

1. **Primaria — DGE.** Secretaría de Salud, Dirección General de Epidemiología (DGE).
   Datos Abiertos — Información referente a casos COVID-19 en México (microdatos SISVER/SINAVE).
   <https://www.gob.mx/salud/documentos/datos-abiertos-152127>. Versión, fecha de descarga y SHA-256:
   *pendiente* (`data/fuentes.csv`).
2. **Secundaria — tablero.** CONAHCYT (antes CONACYT), COVID-19 Tablero México, «Descarga de datos»,
   `Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv`, <https://datos.covid-19.conacyt.mx/>
   (fuente declarada: DGE). Es el archivo que usó el PT1 (`v0-anterior/Proyecto_Terminal_1 (3).pdf`).

## Qué se compara

Fila «Nacional» del CSV del tablero contra la columna `confirmados` de
`data/processed/serie_nacional_sintomas.csv` (CLASIFICACION_FINAL 1–3, residencia 1–32, por fecha de inicio
de síntomas), día por día. Diferencia = DGE − tablero.

## Pruebas diagnósticas y causa esperada de cada diferencia

| ID | Prueba (automática) | Causa que diagnostica | Expectativa a priori |
|---|---|---|---|
| D1 | Fechas presentes en una sola fuente | Cobertura temporal | El tablero empieza el 2020-02-26 y termina el 2023-06-24/25; la serie DGE empieza con el primer inicio de síntomas registrado y termina en el corte del microdato. |
| D2 | Diferencia en los últimos 14/30/90 días antes del corte del tablero | Versión distinta → rezago de notificación / truncamiento | Si el microdato es posterior a jun-2023, la DGE tendrá **más** casos en las semanas previas al 25-jun-2023. |
| D3 | Desfase (−7…+7 d) que minimiza la discrepancia L1 | Fecha de referencia distinta o encabezado corrido | 0 d (ambas por inicio de síntomas). |
| D4 | Variante de la serie propia más cercana al tablero | Definición de caso / ámbito geográfico | «confirmados» (1–3, residencia). Si gana `confirmados_lab_antigeno` o `…_por_entidad_um`, el tablero usó otra definición. |
| D5 | Diferencia neta lejos del corte (≥ 90 d), por año | Reclasificación retroactiva entre versiones | Pequeña pero ≠ 0: pendientes resueltos, dictaminaciones tardías, depuración de duplicados y correcciones de fecha/entidad posteriores a jun-2023. |
| D6 | Nacional vs. suma de las 32 entidades del tablero | Consistencia interna del tablero | 0. |
| D7 | Total 2020-02-26…2023-06-24 y pico suavizado del tablero vs. cifras del PT1 | Que el CSV sea el mismo del PT1 | Total **7,633,355**; pico de la media móvil centrada de 7 d **62,299** el **2022-01-15** (PT1, Tabla 2). |

## Pendientes para cerrar esta nota

- [ ] Descargar el microdato DGE y el CSV del tablero; registrarlos (`data/raw/README.md`).
- [ ] `make serie comparar` → este archivo se regenera con cifras reales.
- [ ] Si D7 falla, localizar el CSV original del PT1 antes de interpretar el resto.
- [ ] Llevar las causas confirmadas a `docs/diccionario_datos.md` §5 si implican reglas nuevas.
