# Análisis de la Dinámica de Transmisión del COVID-19 en México

**Un enfoque de Sistemas Dinámicos No Lineales**

> Proyecto Terminal I · Licenciatura en Física · Universidad Autónoma Metropolitana (UAM-I)  
> *Autor:* Ángel Omar García Hernández · *Asesor:* Dr. Adrian Mauricio Escobar Ruiz

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![LaTeX](https://img.shields.io/badge/LaTeX-Report-red)
![Status](https://img.shields.io/badge/Status-F1:%20Revisión%20Bibliográfica-orange)

---

## 🎯 Pregunta de Investigación

¿Qué tanto de cada ola de COVID-19 en México (2020–2022) es consistente con un **modelo SIR de parámetros constantes**? ¿Cuáles parámetros son **identificables** usando casos confirmados y datos serológicos (ENSANUT)?

---

## 📊 Metodología

Este proyecto reconstruye las dinámicas epidemiológicas del COVID-19 en México bajo el paradigma de la **Física de Sistemas Dinámicos**. A diferencia de enfoques estadísticos convencionales, se analiza la propagación del virus en el **espacio de fases**, identificando atractores y bifurcaciones.

### Modelo matemático
Un sistema SIR modificado que incorpora:
- **Corrección por subregistro:** Calibración con datos de seroprevalencia
- **Identificabilidad estructural:** Análisis de parámetros distinguibles  
- **Incertidumbre cuantificada:** Métodos de máxima verosimilitud con perfiles de confianza

### Ecuaciones fundamentales
$$\frac{dS}{dt} = -\beta \frac{SI}{N}$$
$$\frac{dI}{dt} = \beta \frac{SI}{N} - \gamma I$$
$$\frac{dR}{dt} = \gamma I$$

---

## 📚 Fases del Proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| **F0** | Decisiones de alcance y metodología | ✅ Completada |
| **F1** | Revisión sistemática de bibliografía | 🔄 En curso |
| **F2** | Desarrollo de teoría (Cap. 2) | ⏳ Próxima |
| **F3** | Análisis de datos y olas epidemiológicas | ⏳ Pendiente |
| **F4** | Validación con datos sintéticos | ⏳ Pendiente |
| **F5** | Análisis cuantitativo (datos reales) | ⏳ Pendiente |
| **F6** | Integración del manuscrito | ⏳ Pendiente |
| **F7** | Presentación final | ⏳ Pendiente |

---

## 📁 Estructura del Repositorio

```
SIRCOVID19MX/
├── bibliografia/         Fase F1: Revisión bibliográfica
│   ├── INDICE.csv        Referencias indexadas (79 fuentes)
│   ├── referencias.bib   BibTeX para manuscrito
│   ├── fichas/           Análisis de lecturas clave
│   └── fuentes/          PDFs organizados por tema
│
├── v0-anterior/          Desarrollo anterior (archivo histórico)
│
└── scripts/              Utilidades
    └── generar_referencias.py
```

---

## 🔬 Hipótesis Principales

- **H1:** Los parámetros R₀ y S₀ no son identificables por separado; sin embargo, R_eff(0) sí lo es.
- **H2:** La suposición de β constante deja residuos sistemáticos en olas con intervenciones no farmacéuticas significativas.
- **H3:** El tamaño final predicho por el modelo sobrestima el aumento real de seroprevalencia observado en ENSANUT.

---

## 📖 Resultados Esperados

Al cerrar cada fase se espera producir:
- Caracterización cuantitativa de parámetros epidemiológicos por ola y variante
- Estimación de incertidumbre estructural en el modelo SIR
- Identificación de limitaciones y propuestas de mejora
- Manuscrito completo con código reproducible

---

## 🛠️ Herramientas y Tecnología

- **Python 3.9+:** Simulación numérica y análisis de datos
- **SciPy & NumPy:** Solución de ODEs y computación científica
- **LaTeX:** Redacción del manuscrito
- **Git:** Control de versión y reproducibilidad
- **BibTeX:** Gestión de referencias

---

## 📅 Cronograma

**Semana 1–2 (Bibliografía):** Bloques A, B, D (Sistemas dinámicos, SIR clásico, epidemiología)  
**Semana 3–4:** Bloques C–L (Física, parámetros, México, método de estimación)  
**Semana 5–8:** Bloques M–O (Pronóstico, intervenciones, respuesta mexicana)

---

## 📧 Contacto

**Ángel Omar García Hernández**  

- Licenciatura en Física · Universidad Autónoma Metropolitana (UAM-I)  
  cbi2203043236@izt.uam.mx

- Primer Año de Medicina · Facultad de Medicina, UNAM  
  mc24gaha7938@facmed.unam.mx

**Asesor:** Dr. Adrian Mauricio Escobar Ruiz

---

**Última actualización:** Octubre 2026  
**Fase actual:** F1 — Revisión Bibliográfica Sistemática
