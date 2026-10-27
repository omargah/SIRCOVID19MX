# Proyecto Terminal I: SIR COVID-19 en México

> **Licenciatura en Física** | **Universidad Autónoma Metropolitana (UAM-I)**  
> *Autor:* Ángel Omar García Hernández  
> *Asesor:* Dr. Adrian Mauricio Escobar Ruiz

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status](https://img.shields.io/badge/Status-En%20desarrollo-yellow)
![Phase](https://img.shields.io/badge/Fase-F1%20Bibliografía-orange)

---

## 📍 Estructura del Repositorio

```
SIRCOVID19MX/
├── v0-anterior/          ← Archivos de versión anterior (2025)
│   ├── Capturas de pantalla
│   ├── PTI (2).pdf       (presentación antigua)
│   ├── Proyecto_Terminal_1 (3).pdf
│   └── analisis_montecarlo.py
│
├── bibliografia/         ← NUEVO: Fase F1 (Revisión bibliográfica)
│   ├── INDICE.csv        (79 referencias mapeadas)
│   ├── referencias.bib   (BibTeX generado automáticamente)
│   ├── fichas/           (fichas de lectura en markdown)
│   ├── fuentes/          (PDFs organizados por bloque A-O)
│   └── README.md         (guía de F1)
│
├── scripts/              ← Utilidades
│   └── generar_referencias.py  (regenera referencias.bib desde INDICE.csv)
│
└── README.md             (este archivo)
```

---

## 🎯 Proyecto

**Análisis de la dinámica de transmisión del COVID-19 en México (2020–2023) bajo un enfoque de sistemas dinámicos no lineales.**

### Pregunta central
¿Qué tanto de cada ola (2020–2022) es consistente con un **modelo SIR de parámetros constantes**, y cuáles parámetros son **identificables con casos confirmados + serología ENSANUT**?

### Hipótesis principales
- **H1:** R₀ y S₀ no son identificables por separado; R_eff(0) sí.
- **H2:** β constante deja residuos sistemáticos en olas con intervenciones.
- **H3:** El tamaño final predicho sobrestima el aumento de seroprevalencia.

---

## 📚 Fases (F0–F7)

| Fase | Tema | Estado |
|------|------|--------|
| F0 | Decisiones y alcance | ✅ Cerrada |
| **F1** | **Revisión bibliográfica** | 🔄 **En curso** |
| F2 | Teoría del SIR | ⏳ Pendiente |
| F3 | Datos y olas | ⏳ Pendiente |
| F4 | Método (datos sintéticos) | ⏳ Pendiente |
| F5 | Análisis (datos reales) | ⏳ Pendiente |
| F6 | Escritura integrada | ⏳ Pendiente |
| F7 | Presentación | ⏳ Pendiente |

---

## 🔍 Fase F1: Revisión Bibliográfica

**Sistema sin Zotero** — Git + CSV + Markdown.

### Workflow
1. **Clonar** el repo
2. **Leer** un PDF de `bibliografia/Bibliografía/`
3. **Fichar** en `bibliografia/fichas/CLAVE.md` (usando template)
4. **Marcar** estado en `INDICE.csv` como "fichado"
5. **Commit & push**

### Regla fundamental
> **Sin PDF leído no hay cita.**

Cada referencia que uses en el escrito debe tener:
- ✓ PDF descargado en `fuentes/BLOQUE/`
- ✓ Ficha completada en `fichas/CLAVE.md`
- ✓ Estado = "fichado" en INDICE.csv

### Bloques bibliográficos (A–O)
- **A–L:** Núcleo (sistemas dinámicos, SIR clásico, parámetros, México, método)
- **M–O:** Expansión (pronóstico, intervenciones, respuesta mexicana)
- **LIB:** Libros (Strogatz, Pawitan, Murray, Pearl, Gelman, McElreath, Kucharski)

Ver `bibliografia/README.md` para detalles completos.

---

## 📖 Cómo empezar

```bash
# Clonar
git clone https://github.com/omargah/SIRCOVID19MX.git
cd SIRCOVID19MX

# Ver guía de F1
cat bibliografia/README.md

# Crear estructura local (si no existe)
mkdir -p bibliografia/fuentes/{A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,LIB}
mkdir -p bibliografia/fichas

# Regenerar referencias.bib después de editar INDICE.csv
python3 scripts/generar_referencias.py

# Trabajar y hacer commit
git add bibliografia/
git commit -m "F1: Ficha B03 (Diekmann 1990) — Definición de R₀"
git push
```

---

## 📝 Referencia rápida: Estructura de una ficha

```markdown
# B03 · Diekmann et al. (1990)

**Referencia:** [APA completa]

## Qué afirma (en tus palabras)
[Tu resumen del argumento principal]

## Cifra clave con página
- [Cifra], pág. [n]

## Método
[Cómo lo investigaron]

## Limitaciones
[Qué no cubre]

## Dónde la usas
[Capítulo/sección/pregunta de tu tesis]

## Estado
- [ ] PDF leído
- [ ] Ficha completada
```

Usa `bibliografia/fichas/TEMPLATE.md` como plantilla.

---

## 🔗 Enlaces útiles

- **INDICE.csv:** Lista de todas las 79 referencias con DOI
- **referencias.bib:** BibTeX para usar en LaTeX
- **Guía F1:** `bibliografia/README.md`

---

## 📅 Calendario orientativo (F1)

| Semana | Bloques | Lectura |
|--------|---------|---------|
| 1 | A, B, D | Strogatz, Kermack-McKendrick, Hethcote |
| 2 | C, F, G | Sistemas complejos, r→R₀, parámetros |
| 3 | E, H, I | COVID internacional, olas, serología |
| 4 | J, L, K | Identificabilidad, límites, método MLE |
| 5+ | M, N, O | Pronóstico, intervenciones, respuesta |

---

## ⚙️ Reglas de oro

1. **Sin PDF leído no hay cita** — antes de citar, ficha.
2. **Git es la fuente de verdad** — nada en local, todo en GitHub.
3. **Markdown para fichas** — fácil de versionar y buscar.
4. **INDICE.csv + referencias.bib** — mantén sincronizados (script: `generar_referencias.py`).
5. **Commit descriptivo** — `F1: [Qué se hizo]`

---

## 📧 Contacto

**Omar García Hernández**  
cbi2203043236@izt.uam.mx  
Licenciatura en Física · UAM-Iztapalapa

---

**Última actualización:** 2026-10-27  
**Versión:** F1 (Revisión bibliográfica)
