# Inventario de versiones históricas del microdato DGE

> Generado por `python scripts/inventario_historicos.py`. **Solo inventario**: el tratamiento de las versiones (análisis por versión, nowcasting, elección de versión de referencia) queda pendiente de decisión.

**Fuente:** Secretaría de Salud, Dirección General de Epidemiología (DGE). Datos Abiertos — Información referente a casos COVID-19 en México (microdatos SISVER/SINAVE). https://www.gob.mx/salud/documentos/datos-abiertos-152127 Directorio de históricos: https://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/historicos/ (patrón `historicos/AAAA/MM/datos_abiertos_covid19_DD.MM.AAAA.zip`; **confirmar** con el primer archivo descargado — si difiere, corregir `URL` en el script).

## Resumen

- Rejilla semanal: martes desde 2020-04-14 hasta 2023-06-27 → **168 versiones esperadas**.
- Presentes en `data/raw/dge/historicos/`: **0**; faltan **168**.
- Versiones locales fuera de la rejilla (otro día): 0.
- Presentes sin registro de procedencia: 0.
- `FECHA_ACTUALIZACION` interna distinta a la fecha del nombre: 0.

Detalle por versión (URL, hash, esquema, etc.): `data/inventario_historicos.csv`.
Lista de URLs faltantes: `python scripts/inventario_historicos.py --urls-faltantes`.

## Cronología de esquemas observada en los archivos locales

Sin archivos locales todavía: la cronología se llena al descargar versiones.

## Cambios de esquema esperados (a contrastar con la cronología observada)

Ver `docs/diccionario_datos.md` §4. En particular: `RESULTADO` → `RESULTADO_LAB` + `CLASIFICACION_FINAL` (otoño 2020) y alta de `TOMA_MUESTRA_ANTIGENO`/`RESULTADO_ANTIGENO` (fines de 2020–inicios de 2021).

## Estado por versión (rejilla semanal)

| Versión | Local | Registrado | Esquema | Procesado |
|---|---|---|---|---|
| 2020-04-14 | no | — | — | no |
| 2020-04-21 | no | — | — | no |
| 2020-04-28 | no | — | — | no |
| 2020-05-05 | no | — | — | no |
| 2020-05-12 | no | — | — | no |
| 2020-05-19 | no | — | — | no |
| 2020-05-26 | no | — | — | no |
| 2020-06-02 | no | — | — | no |
| 2020-06-09 | no | — | — | no |
| 2020-06-16 | no | — | — | no |
| 2020-06-23 | no | — | — | no |
| 2020-06-30 | no | — | — | no |
| 2020-07-07 | no | — | — | no |
| 2020-07-14 | no | — | — | no |
| 2020-07-21 | no | — | — | no |
| 2020-07-28 | no | — | — | no |
| 2020-08-04 | no | — | — | no |
| 2020-08-11 | no | — | — | no |
| 2020-08-18 | no | — | — | no |
| 2020-08-25 | no | — | — | no |
| 2020-09-01 | no | — | — | no |
| 2020-09-08 | no | — | — | no |
| 2020-09-15 | no | — | — | no |
| 2020-09-22 | no | — | — | no |
| 2020-09-29 | no | — | — | no |
| 2020-10-06 | no | — | — | no |
| 2020-10-13 | no | — | — | no |
| 2020-10-20 | no | — | — | no |
| 2020-10-27 | no | — | — | no |
| 2020-11-03 | no | — | — | no |
| 2020-11-10 | no | — | — | no |
| 2020-11-17 | no | — | — | no |
| 2020-11-24 | no | — | — | no |
| 2020-12-01 | no | — | — | no |
| 2020-12-08 | no | — | — | no |
| 2020-12-15 | no | — | — | no |
| 2020-12-22 | no | — | — | no |
| 2020-12-29 | no | — | — | no |
| 2021-01-05 | no | — | — | no |
| 2021-01-12 | no | — | — | no |
| 2021-01-19 | no | — | — | no |
| 2021-01-26 | no | — | — | no |
| 2021-02-02 | no | — | — | no |
| 2021-02-09 | no | — | — | no |
| 2021-02-16 | no | — | — | no |
| 2021-02-23 | no | — | — | no |
| 2021-03-02 | no | — | — | no |
| 2021-03-09 | no | — | — | no |
| 2021-03-16 | no | — | — | no |
| 2021-03-23 | no | — | — | no |
| 2021-03-30 | no | — | — | no |
| 2021-04-06 | no | — | — | no |
| 2021-04-13 | no | — | — | no |
| 2021-04-20 | no | — | — | no |
| 2021-04-27 | no | — | — | no |
| 2021-05-04 | no | — | — | no |
| 2021-05-11 | no | — | — | no |
| 2021-05-18 | no | — | — | no |
| 2021-05-25 | no | — | — | no |
| 2021-06-01 | no | — | — | no |
| 2021-06-08 | no | — | — | no |
| 2021-06-15 | no | — | — | no |
| 2021-06-22 | no | — | — | no |
| 2021-06-29 | no | — | — | no |
| 2021-07-06 | no | — | — | no |
| 2021-07-13 | no | — | — | no |
| 2021-07-20 | no | — | — | no |
| 2021-07-27 | no | — | — | no |
| 2021-08-03 | no | — | — | no |
| 2021-08-10 | no | — | — | no |
| 2021-08-17 | no | — | — | no |
| 2021-08-24 | no | — | — | no |
| 2021-08-31 | no | — | — | no |
| 2021-09-07 | no | — | — | no |
| 2021-09-14 | no | — | — | no |
| 2021-09-21 | no | — | — | no |
| 2021-09-28 | no | — | — | no |
| 2021-10-05 | no | — | — | no |
| 2021-10-12 | no | — | — | no |
| 2021-10-19 | no | — | — | no |
| 2021-10-26 | no | — | — | no |
| 2021-11-02 | no | — | — | no |
| 2021-11-09 | no | — | — | no |
| 2021-11-16 | no | — | — | no |
| 2021-11-23 | no | — | — | no |
| 2021-11-30 | no | — | — | no |
| 2021-12-07 | no | — | — | no |
| 2021-12-14 | no | — | — | no |
| 2021-12-21 | no | — | — | no |
| 2021-12-28 | no | — | — | no |
| 2022-01-04 | no | — | — | no |
| 2022-01-11 | no | — | — | no |
| 2022-01-18 | no | — | — | no |
| 2022-01-25 | no | — | — | no |
| 2022-02-01 | no | — | — | no |
| 2022-02-08 | no | — | — | no |
| 2022-02-15 | no | — | — | no |
| 2022-02-22 | no | — | — | no |
| 2022-03-01 | no | — | — | no |
| 2022-03-08 | no | — | — | no |
| 2022-03-15 | no | — | — | no |
| 2022-03-22 | no | — | — | no |
| 2022-03-29 | no | — | — | no |
| 2022-04-05 | no | — | — | no |
| 2022-04-12 | no | — | — | no |
| 2022-04-19 | no | — | — | no |
| 2022-04-26 | no | — | — | no |
| 2022-05-03 | no | — | — | no |
| 2022-05-10 | no | — | — | no |
| 2022-05-17 | no | — | — | no |
| 2022-05-24 | no | — | — | no |
| 2022-05-31 | no | — | — | no |
| 2022-06-07 | no | — | — | no |
| 2022-06-14 | no | — | — | no |
| 2022-06-21 | no | — | — | no |
| 2022-06-28 | no | — | — | no |
| 2022-07-05 | no | — | — | no |
| 2022-07-12 | no | — | — | no |
| 2022-07-19 | no | — | — | no |
| 2022-07-26 | no | — | — | no |
| 2022-08-02 | no | — | — | no |
| 2022-08-09 | no | — | — | no |
| 2022-08-16 | no | — | — | no |
| 2022-08-23 | no | — | — | no |
| 2022-08-30 | no | — | — | no |
| 2022-09-06 | no | — | — | no |
| 2022-09-13 | no | — | — | no |
| 2022-09-20 | no | — | — | no |
| 2022-09-27 | no | — | — | no |
| 2022-10-04 | no | — | — | no |
| 2022-10-11 | no | — | — | no |
| 2022-10-18 | no | — | — | no |
| 2022-10-25 | no | — | — | no |
| 2022-11-01 | no | — | — | no |
| 2022-11-08 | no | — | — | no |
| 2022-11-15 | no | — | — | no |
| 2022-11-22 | no | — | — | no |
| 2022-11-29 | no | — | — | no |
| 2022-12-06 | no | — | — | no |
| 2022-12-13 | no | — | — | no |
| 2022-12-20 | no | — | — | no |
| 2022-12-27 | no | — | — | no |
| 2023-01-03 | no | — | — | no |
| 2023-01-10 | no | — | — | no |
| 2023-01-17 | no | — | — | no |
| 2023-01-24 | no | — | — | no |
| 2023-01-31 | no | — | — | no |
| 2023-02-07 | no | — | — | no |
| 2023-02-14 | no | — | — | no |
| 2023-02-21 | no | — | — | no |
| 2023-02-28 | no | — | — | no |
| 2023-03-07 | no | — | — | no |
| 2023-03-14 | no | — | — | no |
| 2023-03-21 | no | — | — | no |
| 2023-03-28 | no | — | — | no |
| 2023-04-04 | no | — | — | no |
| 2023-04-11 | no | — | — | no |
| 2023-04-18 | no | — | — | no |
| 2023-04-25 | no | — | — | no |
| 2023-05-02 | no | — | — | no |
| 2023-05-09 | no | — | — | no |
| 2023-05-16 | no | — | — | no |
| 2023-05-23 | no | — | — | no |
| 2023-05-30 | no | — | — | no |
| 2023-06-06 | no | — | — | no |
| 2023-06-13 | no | — | — | no |
| 2023-06-20 | no | — | — | no |
| 2023-06-27 | no | — | — | no |
