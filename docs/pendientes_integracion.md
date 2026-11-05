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
