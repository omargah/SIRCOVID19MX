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
2. **Ningún parámetro sin fuente** en `config/parametros.yaml` (DOI + página,
   cifra oficial con año, o regla de cálculo). Lo que no tiene fuente se marca
   `supuesto: true` con un rango y entra al análisis de sensibilidad.
   `src/parametros.py` lo hace cumplir: truena si falta. El tiempo característico
   D (γ = 1/D) es uno solo por ola, el mismo para estimar y simular, y es
   intervalo de generación o periodo infeccioso, nunca incubación.
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
data/processed/          series derivadas del pipeline DGE (serie principal y manifiesto en git)
data/fuentes.csv         procedencia de cada crudo: URL, fecha de descarga, SHA-256
data/inventario_historicos.csv  inventario de versiones semanales de la DGE
sirmx/                   F4 (rama kind-newton): SIR por ola con RK4+numba, verosimilitud diaria, perfiles, r, puntos de cambio, pronóstico
src/
  parametros.py          carga y valida config/parametros.yaml (regla 2)
  datos.py               pipeline de microdatos DGE: serie nacional por inicio de síntomas (python -m src.datos)
  comparar_tablero.py    diferencias contra el tablero CONAHCYT (PT1)
  eda.py                 EDA: día de la semana, retrasos, truncamiento
  series_historicas.py, fuentes.py   series por versión histórica; registro de fuentes
  olas.py                (F3) regla de olas declarada + A1 + frontera 1.ª/2.ª (docs/regla_olas.md)
  olas_provisional.py    (F3) otra regla de olas, "provisional"; ver docs/pendientes_integracion.md
  sir.py                 SIR en personas (β constante y por tramos), relaciones exactas, modelo de observación
  verosimilitud.py       log-verosimilitud, MLE, perfiles, bootstrap
  identificabilidad.py   simetría de escala (H1), IC por perfil
tests/                   pytest: contra soluciones exactas y datos sintéticos (incl. test_olas*.py)
tests/test_1_observacion.py … test_8_reproducibilidad.py   pruebas de sirmx (F4)
tests/test_equivalencia_simuladores.py   sirmx contra src/sir.py (la referencia oficial)
tests/teoria/            derivaciones a–k del Cap. 2: SymPy + sir.py (make teoria)
scripts/
  correr_sintetico.py    experimento sintético (lento) -> reports/resultados/
  make_numeros.py        -> reports/numeros.tex
  make_figuras.py        -> reports/figuras/
  make_tablas.py         -> reports/tablas/
  validacion_sintetica.py   F4: regenera docs/validacion_sintetica.md
  registrar_fuente.py, inventario_historicos.py   procedencia de crudos; inventario de versiones
data/*.csv               series de casos de las olas (JHU CSSE; DGE vía mexicovid19), versionadas
resultados/olas/         tablas y figuras de la regla de olas (declarada/, A1/, A1_frontera/)
reports/                 todo lo generado que cita el escrito
escrito/                 LaTeX
docs/actas/              acta de cierre de cada fase
docs/plan_analisis.md    plan (borrador hasta cerrar F4); docs/plan_analisis_f4.md: el plan que escribió F4 (hay dos, ver pendientes)
docs/decisiones.md       decisiones D0, I2–I4 y correcciones de F4 (I2–I4 provisionales)
docs/validacion_sintetica.md  tablas real vs estimado (generadas por F4)
docs/pendientes_integracion.md, decisiones_integracion.md   lo no decidido / lo decidido al integrar
docs/desviaciones.md     registro de desviaciones
docs/diccionario_datos.md, nota_diferencias.md, inventario_historicos.md   pipeline DGE (F3)
docs/regla_olas.md       regla de olas declarada antes de aplicarse; docs/olas_resultados.md: resultados
docs/teoria_verificacion.md  tabla derivación → test y discrepancias halladas
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

## Datos (F3): pipeline de microdatos DGE

Fuente primaria: microdatos de la **DGE** (Secretaría de Salud, Datos Abiertos COVID-19).
Fuente secundaria (solo para comparar con el PT1): **tablero CONAHCYT**, que deriva de la DGE.

```bash
pip install -r requirements.txt   # o `make env` (environment.yml)
```

```bash
make todo    # verifica hashes, genera series, comprueba determinismo, compara, inventario y EDA
```

Los crudos se descargan a mano; ver [`data/raw/README.md`](data/raw/README.md). Definiciones y cambios de
criterio 2020–2022 en [`docs/diccionario_datos.md`](docs/diccionario_datos.md).

## Validación sintética (F4, `sirmx/`)

`sirmx/` conserva su integrador RK4 con numba (~170 veces más rápido que LSODA);
`src/sir.py` sigue siendo la referencia oficial y
`tests/test_equivalencia_simuladores.py` comprueba que coinciden.

```bash
OPENBLAS_NUM_THREADS=1 python -m pytest -n 4 tests/test_[1-8]_*.py    # unos 7 min
```

```bash
OPENBLAS_NUM_THREADS=1 python scripts/validacion_sintetica.py         # regenera docs/validacion_sintetica.md
```

## Fases

Cada fase cierra con acta (`docs/actas/Fx-nombre.md`), commit etiquetado
`v0.x` y revisión crítica.

| Fase | Contenido | Estado |
|---|---|---|
| F0 | Alcance, hipótesis, reglas, estructura | Cerrada (`v0.0`, [acta](docs/actas/F0-alcance.md)) |
| F1 | Bibliografía: fichas con cifra y página | En curso |
| F2 | Teoría: SIR, identificabilidad, verosimilitud | En curso (derivación de H1 en borrador) |
| F3 | Datos SSA y ENSANUT; regla de olas ([regla](docs/regla_olas.md), [resultados](docs/olas_resultados.md)) | En curso (olas calculadas con JHU; datos DGE pendientes) |
| F4 | Validación sintética de todos los métodos; **congela el plan** | En curso (H1 hecho; `sirmx/` trae la validación sintética de la rama F4; el plan sigue sin congelar, ver pendientes) |
| F5 | Análisis con datos reales | Bloqueada hasta cerrar F4 |
| F6 | Escrito | Pendiente |
| F7 | Presentación | Pendiente |

## Contacto

Ángel Omar García Hernández

- Licenciatura en Física, UAM-I · cbi2203043236@izt.uam.mx
- Facultad de Medicina, UNAM · mc24gaha7938@facmed.unam.mx
