# Pendientes de la integración (rama `integracion/pt1-v2`)

Aquí está todo lo que apareció al unir las ramas y que **no se decidió**.
Cada entrada dice dónde está el problema, qué opciones hay y qué se
recomienda. Quien decide es Omar. Este archivo se va llenando paso a paso;
la lista completa y ordenada queda al cerrar la integración.

---

## P-A. Hay dos reglas de olas distintas, las dos en `src/`

**Dónde.** Al unir `zealous-heisenberg` chocaron `src/olas.py` y
`tests/test_olas.py`. El inventario decía que el de la rama de partida era un
esqueleto vacío. No es cierto: ya tenía 132 líneas, con otra regla.

| | Regla de la rama de partida | Regla de zealous |
|---|---|---|
| Archivo | `src/olas_provisional.py` (antes `src/olas.py`) | `src/olas.py` |
| Pruebas | `tests/test_olas_provisional.py` (6) | `tests/test_olas.py` (5) |
| Método | media móvil de 7 días centrada; mínimos con prominencia ≥ 10 % del máximo global; separación ≥ 60 días; frontera = domingo de la semana epidemiológica | regla R1–R7 de `docs/regla_olas.md`, enmienda A1 y frontera 1.ª/2.ª ola (2020-10-01) |
| Resultados | ninguno sobre datos reales | `resultados/olas/` (5 olas) |

**Qué se hizo (lo menos destructivo).** Se conservaron las dos. La de zealous
quedó como `src/olas.py` porque es la que documentan `docs/regla_olas.md` y
`docs/olas_resultados.md` y la que produjo `resultados/olas/`. La otra se
movió **sin cambiar su lógica** a `src/olas_provisional.py`; solo cambió la
línea de importación de su prueba. Nadie más la importaba.

**Opciones.** (a) quedarse solo con la de zealous y archivar la otra;
(b) quedarse con la provisional (usa semanas epidemiológicas, que es lo que
pide la verosimilitud semanal); (c) unirlas.

**Recomendación.** (a), pero solo después de comprobar que la regla de zealous
da fronteras en domingo (la verosimilitud es semanal). Es decisión de Omar.

## P-B. Olas con JHU o con DGE

**Dónde.** `src/olas.py` y `resultados/olas/` usan **JHU CSSE**, que cuenta
por **fecha de reporte**. El pipeline de datos (`compassionate-dijkstra`) usa
microdatos **DGE por fecha de inicio de síntomas**. No se decidió cuál manda.

**Opciones.** (a) olas con JHU y dejar el pipeline para el ajuste;
(b) rehacer las olas con la serie DGE y dejar JHU como sensibilidad.

**Recomendación.** (b) cuando existan los microdatos. Las fechas de las olas
podrían moverse unos días porque la fecha de síntomas va antes que la de
reporte. Hasta entonces las olas son provisionales. En este paso no se
cambió ρ, la ventana de suavizado ni la frontera 2020-10-01.

## P-C. Qué se versiona de `data/processed/`

**Dónde.** `.gitignore`. La rama de integración ignoraba todo
`data/processed/*` (salvo su README). `compassionate-dijkstra` quiere
versionar la serie principal, el manifiesto y las series de
hospitalizaciones/defunciones, e ignora solo los intermedios (`cubos/`,
`historicos/`, `eda/`, `comparacion_tablero.csv`).

**Qué se hizo.** Se tomó el criterio de compassionate para `data/processed/`
(si no, el pipeline escribiría archivos que nadie ve que se pierden). Los
crudos siguen ignorados; se versiona solo `data/fuentes.csv` y el README.

**Opciones.** (a) como quedó; (b) versionar solo `serie_nacional_sintomas.csv`
y `manifiesto.json`; (c) no versionar nada derivado (todo regenerable).

**Recomendación.** (b): lo más corto que permite reproducir el análisis sin
meter archivos grandes. Decide Omar.

## P-D. Dos listas de dependencias

**Dónde.** `environment.yml` (rama de partida, lo usa `make env`) y
`requirements.txt` (compassionate: pandas, matplotlib…). No se unieron.
El pipeline DGE (`src/datos.py`, `src/eda.py`) necesita pandas y matplotlib;
`make env` instala lo de `environment.yml`.

**Recomendación.** Una sola lista (`environment.yml`) y borrar
`requirements.txt`, comprobando antes que `environment.yml` trae todo lo que
usa `src/eda.py` y `src/comparar_tablero.py` (**no verificado**: esos
módulos solo se probaron con datos sintéticos).

## P-E. Otros restos de este paso

- `src/datos.py:230` y `tests/sintetico.py:51` siguen usando `weekday`
  (en un índice/`dt`). Solo se pidió cambiar `src/eda.py`. Con pandas 3.0.5
  `weekday` y `dayofweek` funcionan y no dan aviso: que `weekday` desaparezca
  en pandas 4 es afirmación del inventario, **no verificada**.
- `data/processed/README.md` (rama de partida) dice que todo se regenera con
  código de `src/datos.py`: ahora sí es el pipeline DGE.
- `docs/actas/F0-alcance.md` sigue mencionando `src/datos.py::cargar_parametros`
  (acta histórica; no se reescribió).
- `reports/parametros_fuentes.md` dice "validado por `src/datos.py`" hasta que
  Omar lo regenere con `make resumen`.
