# ¿Qué tanto de la COVID-19 en México cabe en un SIR?

> Proyecto Terminal 1 (rehecho) · Licenciatura en Física · UAM-Iztapalapa
> Autor: Ángel Omar García Hernández · Trabajo personal, sin asesor.

Solo modelo SIR. La versión anterior está archivada en `v0-anterior/` y **no**
se usa como base de código: tenía errores conocidos.

## Pregunta

¿Qué parte de la dinámica 2020–2023 es consistente con un SIR de parámetros
constantes? ¿Qué parámetros son identificables con casos + serología? ¿Qué
tan útil habría sido en tiempo real? ¿Cuándo cambió la transmisión respecto a
las medidas de la SSA?

## Hipótesis

- **H1** R0 y S0 no son identificables por separado; solo R_eff(0) = R0·S0/N.
- **H2** β constante por ola deja residuos sistemáticos.
- **H3** El tamaño final sobrestima el aumento de seroprevalencia (ENSANUT).
- **H4a** El SIR supera a la persistencia a 1–2 semanas (WIS).
- **H4b** El SIR no estabiliza la fecha del pico antes de que ocurra.
- **H5** La transmisión bajó después de la JNSD, no antes.

Criterios de decisión y notas críticas: [`docs/plan_analisis.md`](docs/plan_analisis.md).

## Método

Máxima verosimilitud con perfiles (nada bayesiano). β constante por ola
(H2), β por tramos (H5). Intervalos por bootstrap paramétrico.

## Reglas del proyecto

1. **Ninguna cifra a mano.** El escrito usa `reports/numeros.tex`, generado por
   `scripts/make_numeros.py`.
2. **Ningún parámetro sin fuente** en `config/parametros.yaml` (DOI + página, o
   regla de cálculo). `src/datos.py` lo hace cumplir: truena si falta.
3. **Primero datos sintéticos.** Ningún método toca datos reales hasta
   recuperar parámetros conocidos.
4. **El plan se congela al cerrar F4.** Cada desviación posterior va a
   `docs/desviaciones.md` con su motivo.
5. **Nada se borra para que una figura se vea bien.**
6. **Cada línea debe poder explicarse.** El código comenta el porqué.

## Estructura

```
config/parametros.yaml   parámetros con fuente (regla 2)
data/raw/                datos descargados, sin tocar (no van a git; registro en README)
data/processed/          datos derivados, regenerables
src/
  datos.py               carga y valida parámetros; (F3) datos SSA y ENSANUT
  olas.py                (F3) delimitación de olas
  sir.py                 SIR en personas (β constante y por tramos), relaciones exactas, modelo de observación
  verosimilitud.py       log-verosimilitud, MLE, perfiles, bootstrap
  identificabilidad.py   simetría de escala (H1), IC por perfil
tests/                   pytest: contra soluciones exactas y datos sintéticos
scripts/
  correr_sintetico.py    experimento sintético (lento) -> reports/resultados/
  make_numeros.py        -> reports/numeros.tex
  make_figuras.py        -> reports/figuras/
  make_tablas.py         -> reports/tablas/
reports/                 todo lo generado que cita el escrito
escrito/                 LaTeX
docs/actas/              acta de cierre de cada fase
docs/plan_analisis.md    plan (borrador hasta cerrar F4)
docs/desviaciones.md     registro de desviaciones
bibliografia/            índice, BibTeX y fichas de lectura (F1)
v0-anterior/             archivo histórico; no se reutiliza
```

## Cómo reproducir

Requisitos: `git`, `make` y Python ≥ 3.11 (o conda).

```bash
git clone https://github.com/omargah/SIRCOVID19MX.git
```

```bash
cd SIRCOVID19MX
```

```bash
make env
```

```bash
make test
```

`make env` usa conda si está instalado (luego `conda activate sircovid`);
si no, crea `.venv/` con pip usando los mismos paquetes de
`environment.yml`. `make figuras` regenera las figuras (corre el
experimento sintético, unos minutos, si algo cambió). `make` regenera
números, figuras y tablas; `make escrito` además compila el PDF (requiere LaTeX).

## Fases

Cada fase cierra con acta (`docs/actas/Fx-nombre.md`), commit etiquetado
`v0.x` y revisión crítica.

| Fase | Contenido | Estado |
|---|---|---|
| F0 | Alcance, hipótesis, reglas, estructura | Cerrada (`v0.0`, [acta](docs/actas/F0-alcance.md)) |
| F1 | Bibliografía: fichas con cifra y página | En curso |
| F2 | Teoría: SIR, identificabilidad, verosimilitud | En curso (derivación de H1 en borrador) |
| F3 | Datos SSA y ENSANUT; regla de olas | Pendiente |
| F4 | Validación sintética de todos los métodos; **congela el plan** | En curso (H1 hecho; H2–H5 pendientes) |
| F5 | Análisis con datos reales | Bloqueada hasta cerrar F4 |
| F6 | Escrito | Pendiente |
| F7 | Presentación | Pendiente |

## Contacto

Ángel Omar García Hernández

- Licenciatura en Física, UAM-I · cbi2203043236@izt.uam.mx
- Facultad de Medicina, UNAM · mc24gaha7938@facmed.unam.mx
