# Análisis de la Dinámica de Transmisión del COVID-19 en México: Un Enfoque de Sistemas Físicos No Lineales

> **Proyecto Terminal I (Licenciatura en Física)** > **Universidad Autónoma Metropolitana (UAM)** > *Autor: Ángel Omar García Hernández* > *Asesor: Dr. Adrian Mauricio Escobar Ruiz*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![SciPy](https://img.shields.io/badge/SciPy-Sistemas%20Dinámicos-red)
![Status](https://img.shields.io/badge/Status-Finalizado-success)

## 📄 Resumen Ejecutivo

Este proyecto analiza la pandemia de COVID-19 en México (2020-2023) bajo el paradigma de la **Física de Sistemas Dinámicos**. A diferencia de los enfoques puramente estadísticos, este trabajo reconstruye las trayectorias de las cinco grandes olas pandémicas en el **Espacio de Fases**, permitiendo identificar atractores y puntos de bifurcación en la propagación del virus.

El núcleo del proyecto es un modelo **SIR Estocástico (Susceptible-Infectado-Recuperado)** modificado que incorpora:
1.  **Corrección por Subregistro:** Calibración basada en datos de seroprevalencia (ENSANUT).
2.  **Evasión Inmune:** Un parámetro de ajuste para modelar la capacidad de reinfección de variantes como Ómicron.
3.  **Simulación de Monte Carlo:** Para cuantificar la incertidumbre en el Número Reproductivo Básico ($R_0$).

## 🧬 Metodología Física y Computacional

El código implementa una solución numérica de sistemas de ecuaciones diferenciales ordinarias (ODEs) no lineales.

### 1. El Modelo Matemático
Se utiliza el sistema acoplado clásico, ajustado a las condiciones de frontera de México:
$$\frac{dS}{dt} = -\beta \frac{SI}{N}$$
$$\frac{dI}{dt} = \beta \frac{SI}{N} - \gamma I$$
$$\frac{dR}{dt} = \gamma I$$

### 2. Algoritmos Implementados
* **Reconstrucción del Espacio de Fases:** Análisis topológico de las trayectorias $I(t)$ vs $I'(t)$.
* **Inferencia Bayesiana (Monte Carlo):** Se realizan 10,000 iteraciones para construir distribuciones de probabilidad del parámetro $R_0$ en lugar de estimaciones puntuales, permitiendo visualizar la "incertidumbre física" del sistema.
* **Ajuste Híbrido:** Combinación de regresión lineal en etapas de crecimiento logarítmico y optimización no lineal (Levenberg-Marquardt) para las curvas completas.

## 📊 Resultados Clave

El análisis reveló comportamientos emergentes en la dinámica de la pandemia:
* **Dinámica de $R_0$:** Se demostró una evolución no monótona, alcanzando un máximo histórico de **$R_0 \approx 4.28$** durante la ola de Ómicron BA.1.
* **Caos Determinista:** Las transiciones entre olas mostraron sensibilidad a las condiciones iniciales típica de sistemas caóticos, exacerbada por la movilidad social.
* **El "Fallo Informativo":** Las discrepancias entre el modelo teórico y los datos reales no fueron errores, sino medidas cuantitativas de fenómenos externos (intervenciones no farmacéuticas y fatiga pandémica).

## 🛠️ Estructura del Repositorio

```text
├── analisis_montecarlo.py   # Script principal (Simulación y Visualización)
├── docs/                    # Documentación y PDF del Proyecto Terminal
├── figuras/                 # Gráficas generadas (Espacios de fase, Ridgeline plots)
└── README.md                # Este archivo
