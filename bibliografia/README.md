# Bibliografía · Proyecto Terminal 1

**Fase F1:** Revisión bibliográfica y referencias.

## Contenido

- **INDICE.csv** — Tabla de 79 referencias (clave | bloque | autor | año | DOI)
- **referencias.bib** — BibTeX generado automáticamente desde INDICE.csv
- **fuentes/** — PDFs organizados por bloque (A/, B/, F/, G/, etc.)
- **fichas/** — Fichas de lectura en markdown (B03.md, F01.md, etc.)
- **TEMPLATE.md** — Template para crear nuevas fichas

## Workflow

1. **Organiza PDFs** en `fuentes/A/`, `fuentes/B/`, etc.
2. **Lee un PDF** → copia `fichas/TEMPLATE.md` a `fichas/CLAVE.md`
3. **Llena la ficha** con: qué afirma, cifra+página, método, limitaciones, dónde la usas
4. **Marca en INDICE.csv**: columna `Estado` = "fichado"
5. **Regenera referencias.bib**: `python3 ../scripts/generar_referencias.py`

## Estructura de bloques

| Bloque | Tema | Uso |
|--------|------|-----|
| A | Sistemas dinámicos | Cap. 2 |
| B | SIR: clásicos y teoría | Caps. 1–2 |
| F | De r a R₀ | Caps. 2–3 |
| G | Parámetros de SARS-CoV-2 | Cap. 3 |
| H | México: olas, variantes | Caps. 1 y 3 |
| I | Serología y subregistro | H3 · S₀ · ρ |
| J | Identificabilidad | H1 · Cap. 3 |
| K | Método de estimación (MLE) | Cap. 3 |
| L | Límites del SIR homogéneo | H2 · H3 · Cap. 5 |
| M | Pronóstico en tiempo real | SP4 · H4 |
| N | Efecto de intervenciones | SP5 · H5 |
| O | México: respuesta y medidas | SP4 · SP5 |
| LIB | Libros (Strogatz, Pawitan, etc.) | Caps. 1–2 |

## Regla fundamental

**Sin PDF leído no hay cita.**

Cada referencia que uses en el escrito debe tener:
- ✓ PDF en `fuentes/BLOQUE/`
- ✓ Ficha en `fichas/CLAVE.md`
- ✓ Estado = "fichado" en INDICE.csv

## Git workflow

```bash
# Clonar
git clone https://github.com/omargah/SIRCOVID19MX.git
cd SIRCOVID19MX

# Después de leer y fichar
git add bibliografia/
git commit -m "F1: Ficha B03 (Diekmann 1990) — Definición de R₀"
git push

# Para regenerar referencias.bib
python3 scripts/generar_referencias.py
git add bibliografia/referencias.bib
git commit -m "F1: Regenerar referencias.bib"
git push
```

## Calendario

| Semana | Bloques | Tareas |
|--------|---------|--------|
| 1 | A, B, D | Strogatz, Kermack-McKendrick, Hethcote (fichas) |
| 2 | C, F, G | Sistemas complejos, generación de r a R₀, parámetros |
| 3 | E, H, I | COVID internacional, olas mexicanas, serología |
| 4 | J, L, K | Identificabilidad, límites del SIR, método MLE |
| 5+ | M, N, O | Pronóstico, intervenciones, respuesta mexicana |

---

**Última actualización:** 2026-10-27  
**Generado por:** Claude (chat 01 · Bibliografía y teoría)
