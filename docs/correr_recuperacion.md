# Cómo correr la recuperación sintética en tu computadora

La sesión en la nube no puede correr cálculos largos sin vigilancia (el
contenedor se recicla minutos después de quedar inactivo). Decisión de Omar
(2026-11-05): la corrida completa se hace en su computadora con el mismo
código. El script es reanudable: si se corta, se vuelve a lanzar igual y sigue
donde se quedó.

## 1. Preparar

```bash
git fetch origin claude/adoring-goodall-jf3lyb
```

```bash
git checkout claude/adoring-goodall-jf3lyb
```

```bash
git pull origin claude/adoring-goodall-jf3lyb
```

Entorno (una de las dos):

```bash
make env
```

o, sin conda, en un entorno virtual con Python >= 3.11:

```bash
pip install numpy scipy pandas pyyaml pytest
```

Comprobar que todo pasa antes de lanzar (deben pasar todas las pruebas):

```bash
python -m pytest -q
```

## 2. Lanzar

Las dos corridas, una tras otra (en macOS, `caffeinate -i` evita que la
computadora se duerma):

```bash
caffeinate -i make recuperacion
```

Sin `make`:

```bash
python scripts/recuperacion_sintetica.py --datos casos
```

```bash
python scripts/recuperacion_sintetica.py --datos casos_sero
```

Por omisión usa todos los núcleos (`--procesos N` para usar menos). Cada línea
que imprime es una réplica terminada. Si se corta (Ctrl-C, se apaga, se
suspende), vuelve a correr el mismo comando: salta las réplicas hechas y
descarta una última línea incompleta si la hubiera.

Tiempo: en la nube, con 4 núcleos, una réplica tardó en promedio unos 45 s de
reloj (unos 180 s de CPU). Para las réplicas que faltan, el tiempo de reloj es
aproximadamente (réplicas que faltan) × 180 s / (núcleos). Es una estimación:
depende de tu procesador.

No edites `src/`, `config/` ni `scripts/` mientras corre: el manifiesto
registra el commit y marca si el árbol tenía cambios sin commit.

Ya hay 19 réplicas de "casos" hechas en la nube con el mismo código y las
mismas semillas (cada réplica usa `SeedSequence([semilla, escenario, réplica,
con_sero])`). Se pueden conservar. Si prefieres que todas salgan de la misma
máquina, borra `reports/resultados/recuperacion/casos.jsonl` antes de lanzar.

## 3. Al terminar

```bash
make resumen
```

```bash
git add reports/
```

```bash
git commit -m "Recuperación sintética: corrida completa (casos y casos_sero)"
```

```bash
git push origin claude/adoring-goodall-jf3lyb
```

Con eso, en el chat de código se escribe el acta con las cifras de
`reports/recuperacion_sintetica_casos.md` y `..._casos_sero.md`.
