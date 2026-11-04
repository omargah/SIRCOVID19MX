# Datos

| Archivo | Origen | Licencia | Notas |
|---|---|---|---|
| `jhu_mexico_confirmados_acumulados.csv` | JHU CSSE, `time_series_covid19_confirmed_global.csv`, fila *Mexico* ([URL](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv)) | CC BY 4.0 | Acumulado por fecha de reporte, 2020-01-22 → 2023-03-09. sha256 del CSV global descargado el 2026-11-04: `e6234a59eec4359d2577358b5220e1a7e3da74c162913cdb7d882db1413f98c2` |
| `dge_mexico_confirmados_por_ingreso.csv` | Datos abiertos DGE (SSa), agregados por [mexicovid19/Mexico-datos](https://github.com/mexicovid19/Mexico-datos), `datos_abiertos/series_de_tiempo/nuevos/covid19_mex_confirmados.csv`, columna *Nacional* | Libre Uso MX | Casos nuevos por `FECHA_INGRESO`, 2020-02-27 → 2022-02-03. sha256 del CSV original: `3b089248e35ba9de5cf44356b629c71c86a26199069f77be52aa00eb7c5146db` |

Regenerar: `python3 src/olas.py --descargar`.
