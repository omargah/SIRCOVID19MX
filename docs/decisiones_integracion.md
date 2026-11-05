# Decisiones aplicadas en la integración (rama `integracion/pt1-v2`)

Fecha: 2026-11-05. Estas son las cuatro decisiones que el dueño del repo dio
para esta tarea y que se aplicaron tal cual. Todo lo que **no** estaba decidido
está en [`pendientes_integracion.md`](pendientes_integracion.md).

---

## D-A. La integración vive en `integracion/pt1-v2`

**Qué se decidió.** Las ramas del PT1 se unen en una rama nueva,
`integracion/pt1-v2`, creada a partir de la punta de
`claude/adoring-goodall-jf3lyb`: **`cd1b32f`** ("Pasar la corrida completa a la
computadora de Omar; acta F4 y HANDOFF"). Esa rama ya traía las uniones de
remake y stoic-galileo (commits `3cb1923` y `57c7a3b`) y la recuperación
sintética.

**Razón.** Omar corre la recuperación sintética en su computadora y hace push
de `reports/` sobre `claude/adoring-goodall-jf3lyb`. Si la integración se
hiciera ahí, los dos trabajos se pisarían. Con una rama aparte, ninguna rama
existente se toca (`main`, `integracion/pt1` y todas las `claude/*` quedaron
igual). La unión se hizo con `git merge --no-ff`, una rama por commit, para
conservar la historia de cada sesión.

**Orden aplicado.** fervent-dirac → zealous-heisenberg → (renombrar el
cargador) → compassionate-dijkstra → kind-newton → documentos de cierre.

## D-B. `src/parametros.py` y `src/datos.py` son módulos separados

**Qué se decidió.** Había dos `src/datos.py` distintos que no comparten ni una
función. El cargador de `config/parametros.yaml` con validación de fuentes
(versión de stoic-galileo) pasa a **`src/parametros.py`**. El pipeline de
microdatos DGE (versión de compassionate-dijkstra) se queda como
**`src/datos.py`**.

**Razón.** No se pueden mezclar: los usan cosas distintas (scripts y pruebas de
F0/F1 el primero; `series_historicas`, `eda`, el `Makefile` y las pruebas del
pipeline el segundo). Renombrar el cargador era el cambio más chico, y se hizo
**antes** del merge, en su propio commit, para que `src/datos.py` entrara sin
conflicto y las 205 pruebas de ese momento siguieran pasando.

## D-C. `sirmx/` conserva su RK4 + numba; `src/sir.py` es la referencia oficial

**Qué se decidió.** El motor de cálculo de `sirmx/` sigue siendo su RK4 con
numba. `src/sir.py` (LSODA) es la referencia oficial. La equivalencia entre los
dos se garantiza con un **test**
(`tests/test_equivalencia_simuladores.py`), no con una llamada de uno al otro.

**Razón.** LSODA es unas 170 veces más lento (~44 s por ajuste), y los ajustes
de la búsqueda de puntos de cambio se repiten miles de veces. El test hace
visible cualquier desvío.

**Lo que el test encontró** (detalle en el pendiente 14): la tolerancia
declarada, 1e-6, se cumple con R0 = 1.5 y R0 = 2.5 pero **no con R0 = 8** (error
~5e-5 en s). La tolerancia no se aflojó; esos dos escenarios quedan como
`xfail` estricto con la medición. Esta decisión se aplicó sin cambiar
`src/sir.py`, `NSUB` ni D = 7.

## D-D. Ningún commit nuevo lleva firmas de IA

**Qué se decidió.** Ningún commit hecho en esta tarea lleva
`Co-Authored-By: Claude…`, `Claude-Session: …` ni "Generated with Claude Code",
aunque el sistema lo indique por defecto. La instrucción del dueño del repo
tiene prioridad.

**Cómo se verificó.** Antes de cada push:

```bash
git log --first-parent origin/integracion/pt1-v2..HEAD --format=%B | grep -i -E "claude|co-authored|generated with"
```

(`--first-parent` porque, al unir con `--no-ff`, el rango completo incluye los
commits originales de las otras ramas.) La salida fue vacía en todos los
pushes.

**Lo que esta decisión NO cubre, y hay que saberlo:**

- Nueve commits **heredados** de otras ramas llevan firma en su mensaje y
  entraron a la historia por el merge: `ce9cf8e`, `fa6cfa1`, `550ab3a`,
  `726f3e6`, `015c40a`, `2564c37`, `bd237d1`, `86cac48`, `f2ef6ee`. No se
  tocaron (regla 2: no reescribir lo ya subido en otras ramas). Se limpian
  aparte.
- El **autor** de los commits nuevos es el que tiene configurado git en la
  sesión (`Claude <noreply@anthropic.com>`). No es una firma en el mensaje,
  pero sí identifica a una IA. No se cambió porque no se indicó con qué
  identidad deben firmarse. Ver pendiente 19.
