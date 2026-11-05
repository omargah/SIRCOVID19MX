# Inventario de recursos del PT1

Fecha de corte: 2026-11-05. Solo se listan recursos cuya existencia comprobé. "Revisado" indica hasta dónde lo leí; "Verificado" indica si su contenido fue comprobado contra una fuente primaria o una ejecución.

## 1. Datos

| Recurso | Ubicación | Periodo / contenido | Procedencia registrada | Revisado | Verificado | Uso posible |
|---|---|---|---|---|---|---|
| JHU CSSE, confirmados acumulados México | `data/jhu_mexico_confirmados_acumulados.csv` (rama `integracion/pt1-v2`) | 2020-01-22 → 2023-03-09, diario, por fecha de reporte | URL + SHA-256 del CSV global (descarga 2026-11-04) | Cabecera y extremos | No | Sensibilidad; no como serie primaria |
| DGE agregada por mexicovid19 | `data/dge_mexico_confirmados_por_ingreso.csv` (v2) | 2020-02-27 → 2022-02-03, por FECHA_INGRESO; el último día está truncado | URL + SHA-256 | Cabecera y extremos | No | Contraste |
| Tablero CONAHCYT (datos de v0) | Drive, carpeta *SIR S2 final* (`Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv`, 145 869 B) | 2020-02-26 → 2023-06-24 según S08 | Sin registro | No descargado | No | Comparación con el PT1 anterior |
| Seroprevalencia ENSANUT transcrita | Drive, `v.2 2026/insumos_codigo/serologia.csv` | 2020: 24.9 % (22.2–26.7) anti-N; 2021: 57.9 % / 59.2 % adultos; 2022: 94.4 % (93.2–95.3); ρ indicativos 0.038 (2020) y 0.054 (2021) | Clave + página | Completo | **No** (PDF no abiertos) | Parámetros s0/ρ y H3, tras verificar |
| Olas y variantes (literatura) | Drive, `olas_variantes.csv` | 5 olas con periodo, variante, fuente, página, D | Clave + página | Completo | No | Etiquetado de olas |
| Parámetros D | Drive, `parametros_D.csv`; `config/parametros.yaml` (v2) | GI 5.20, 3.95, 5.5, 4.7, 6.84 d con IC95; usos prohibidos (3.59, 13.4, 6.4 d) | Clave + página | Completo | No | Parámetro γ |
| Inventario de versiones DGE | `data/inventario_historicos.csv` (v2) | 168 versiones esperadas (mar 2020 – jun 2023), 0 presentes | Generado por script | Completo | — | Plan de descarga para H4 |
| Medidas | `config/medidas.yaml` (v2) | Fechas candidatas "sin citar" | Ninguna verificada | Parcial | No | H5, tras verificar DOF |
| Resultados de olas | `resultados/olas/{declarada,A1,A1_frontera}` (v2) | Fronteras y sensibilidad con JHU | Generado por `src/olas.py` | Resumen | No reejecutado | Provisional |
| Resultados sintéticos | `reports/resultados/sintetico_h1.json`, `reports/resultados/recuperacion/casos.jsonl` (19 réplicas) | Experimentos con parámetros conocidos | Manifiesto con commit | Resumen | Pruebas pasan | Validación (incompleta) |
| **Ausentes** | — | Microdatos DGE, 168 versiones históricas, ENSANUT en crudo, DOF, movilidad, OxCGRT, CONAPO | — | — | — | Bloquean F5 |

## 2. Documentos

| Recurso | Ubicación | Fecha | Revisado | Valor para la reconstrucción |
|---|---|---|---|---|
| Plan de trabajo trimestral 25-P (SEIRS-V) | Drive `v.1` | 2025-05-21 | Completo | Registro institucional: **clave para P0-1** |
| Carta de aceptación PT I | Drive `v.1` | archivo 2025-05-23 (texto: 21 dic 2025) | Completo | Ídem |
| Notebooks v0 (PDF impresos) | `v0-anterior/` (4 PDF; 2 duplicados de texto) | jul–ago 2025 | Búsqueda dirigida | Antecedente / catálogo de errores |
| Escrito v0 (52 y 56 págs.) | `v0-anterior/` (capturas) | 2025-08-09 | Completo | Antecedente |
| Presentación v0 | `v0-anterior/PTI (2).pdf` | 2025-08-13 | Búsqueda dirigida | Antecedente |
| Diagnóstico y plan (Claude Doc) | Artifact `AJzYRKY2fm7QJGX9dPTs3Q` | 2026-10-03 | ~65 % de la pestaña 1 | Diagnóstico de v0 coincidente; propuesta de pregunta |
| Tablero de fases | Artifact `BkZGXpVxh6rKmeWG6x8qqq` (base de datos) | 2026-10-08/16 | Completo | Lista de 101 pasos reutilizable como insumo, no como estado |
| Cronograma Hito de enero | Artifact `KTeFUa6xLXKNwXdWNH4HpM` | 2026-11-05 | Completo | Calendario personal (feriados, exámenes FacMed, Variable Compleja) útil para la Entrega 4 |
| Fuentes del PT1 | Artifact `PnMDJHa4u4V4LRTwjCoxpX` | 2026-10-25 | **No revisado** | Posible inventario bibliográfico |
| INSUMOS_CODIGO.md | Drive `v.2 2026/insumos_codigo` | 2026-11-04 | Completo | Decisiones I1–I4 de Omar; recortes previstos |
| Documentación v2 | `integracion/pt1-v2:docs/` (actas F0 y F4, dos planes, decisiones, 20 pendientes, regla de olas, teoría, diccionario de datos) | 2026-11-03/05 | Completo | Base del registro de decisiones |
| Borrador de identificabilidad | `escrito/capitulos/identificabilidad.tex` (v2) | 2026-11 | Completo | Rescatable tras revisión de originalidad |
| Ayuda Proyecto Terminal COVID-19 | Drive (otra cuenta) | 2025-06-30 | ~4 % | No es fuente académica |

## 3. Código

| Componente | Ubicación | Estado verificado | Recomendación |
|---|---|---|---|
| `src/sir.py` (SIR en personas, β por tramos, observación) | v2 | Validado contra soluciones exactas y DOP853 (tolerancias documentadas) | Conservar como referencia, tras apropiación |
| `src/parametros.py` + `config/parametros.yaml` | v2 | Implementado; rechaza parámetros sin fuente | Conservar |
| `src/verosimilitud.py`, `src/identificabilidad.py`, `src/recuperacion.py` | v2 | Implementado y probado en sintéticos | Conservar; completar recuperación |
| `tests/teoria/` (11 derivaciones, SymPy + numérico) | v2 | 87 pasan, 3 xfail documentados | Conservar; base del capítulo físico-matemático |
| `src/datos.py`, `src/eda.py`, `src/comparar_tablero.py`, `src/series_historicas.py`, `src/fuentes.py` | v2 | Probado solo con datos sintéticos | Conservar si se consiguen microdatos |
| `src/olas.py` (regla declarada) y `src/olas_provisional.py` | v2 | Dos reglas; resultados solo con JHU | Elegir una |
| `sirmx/` (RK4 + numba, verosimilitud diaria, cambios, pronóstico) | v2 | 40 pruebas pasan; no equivalente a `src/sir.py` con R0 = 8; D = 7 escrito a mano | Decidir si se conserva (útil para puntos de cambio y pronóstico por velocidad) |
| `scripts/` (make_numeros, make_figuras, make_tablas, recuperación, inventario) | v2 | Implementado | Conservar los que respalden la regla 1 |
| `scripts/generar_referencias.py` | `main` | Funciona pero produce un `.bib` inutilizable | Reemplazar |
| `v0-anterior/analisis_montecarlo.py` | `main` | Genera R0 ficticios | Archivo histórico; no reutilizar |

Suite completa ejecutada en esta auditoría: **258 aprobadas, 5 xfail, 0 fallos** (Python 3.13.18, numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, numba 0.68.1, pandas 3.0.5).

## 4. Bibliografía

| Recurso | Ubicación | Cantidad | Estado |
|---|---|---|---|
| Índice | `bibliografia/INDICE.csv` (`main`) | 79 | Estados no confiables (todos "descargado") |
| Índice ampliado | Drive `v.2 2026/insumos_codigo/INDICE.csv` | 84 | 5 sin PDF |
| PDFs con clave | Drive `v.2 2026/Bibliografía/.../bibliografia/fuentes/{A…O,LIB}` | ~70 (según `MAPEO_fuentes.csv`) | No abiertos por esta auditoría |
| PDFs sin clave | Drive `fuentes/_sin_clave` | ~15 (Acuña-Zegarra 2022, Alcocer 2023, Basto-Abreu 2023, DOF 15.05.2020, Gostic 2020, Kröger y Schlickeiser 2020, Lessler y Cummings 2016, Mossong 2008, Park 2020, Reich 2019, Roda 2020, Viboud 2018, Wood 2010) | Por indexar |
| Duplicados | Drive `fuentes/_duplicados` | 1 (Kermack y McKendrick 1927) | — |
| Fichas | repo y Drive | 0 | No iniciado |
| `referencias.bib` | `main` | 79 entradas | Inutilizable |

Fuentes candidatas mencionadas en esta auditoría y **no verificadas** (no se deben citar sin comprobar): Tuncer y Le 2018 (identificabilidad de modelos de brote); Nutku 1990 (estructura hamiltoniana del modelo de Kermack–McKendrick); Ballesteros et al. 2020 (citado en el cronograma de octubre).

## 5. Herramientas y entorno

| Herramienta | Estado |
|---|---|
| Repositorio GitHub `omargah/SIRCOVID19MX` | Accesible (lectura; esta sesión puede escribir solo en `claude/cool-einstein-qwqjvj`) |
| Google Drive (carpeta *Proyecto Terminal 1*) | Accesible en lectura desde esta sesión |
| Artifacts de claude.ai (tablero, cronograma, diagnóstico) | Accesibles en lectura |
| Conversaciones de claude.ai | **No accesibles** |
| Entorno Python reproducible | `environment.yml` (sin numba/xdist) y `requirements.txt` (con ellos); `make env`, `make test` |
| Red desde la nube hacia `gob.mx`/DOF | Bloqueada según HANDOFF (no reprobado aquí) |
| LaTeX | `escrito/main.tex`; compilación no probada en esta auditoría |
