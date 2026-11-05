# Uso:
#   make env      crea el entorno (conda si existe; si no, .venv con pip)
#   make test     corre las pruebas
#   make teoria   solo la verificación simbólica+numérica del Cap. 2 (tests/teoria/)
#   make todo     pipeline de datos DGE (F3): fuentes, serie, comparar, EDA (ver data/raw/README.md)
#   make figuras  regenera figuras (y el experimento sintético si cambió algo)
#   make          números + figuras + tablas para el escrito
#
# Intérprete: si existe .venv/ (creado por `make env` sin conda) se usa ese;
# si no, el `python` del entorno activo (p. ej. tras `conda activate sircovid`).
PY ?= $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python)

RES = reports/resultados/sintetico_h1.json

all: reports/numeros.tex figuras tablas

env:
	@if command -v conda >/dev/null 2>&1; then \
		conda env create -f environment.yml || conda env update -f environment.yml --prune; \
		echo "Listo. Activa con: conda activate sircovid"; \
	else \
		echo "conda no encontrado: creo .venv con pip"; \
		python3 -m venv .venv && \
		.venv/bin/pip install --upgrade pip && \
		.venv/bin/pip install `python3 scripts/deps_pip.py`; \
	fi

test:
	$(PY) -m pytest -q

teoria:
	$(PY) -m pytest -m teoria -q -rx

$(RES): scripts/correr_sintetico.py src/*.py config/parametros.yaml
	$(PY) scripts/correr_sintetico.py

reports/numeros.tex: $(RES) scripts/make_numeros.py
	$(PY) scripts/make_numeros.py

figuras: $(RES) scripts/make_figuras.py
	$(PY) scripts/make_figuras.py

tablas: $(RES) scripts/make_tablas.py
	$(PY) scripts/make_tablas.py

escrito: all
	cd escrito && latexmk -pdf main.tex

# Recuperación sintética (F4). Reanudable: si se corta, volver a correr.
recuperacion:
	$(PY) scripts/recuperacion_sintetica.py --datos casos
	$(PY) scripts/recuperacion_sintetica.py --datos casos_sero

resumen:
	$(PY) scripts/resumen_recuperacion.py
	$(PY) scripts/listar_supuestos.py

# ---------------------------------------------------------------------------
# Pipeline de datos F3 (microdatos DGE por fecha de inicio de síntomas).
# Requiere los crudos en data/raw/ (ver data/raw/README.md). No corre en `make test`.
# ---------------------------------------------------------------------------
todo: fuentes serie determinismo comparar inventario eda

fuentes:            ## verifica que los crudos no cambiaron desde su registro
	$(PY) scripts/registrar_fuente.py --verificar

serie:              ## (3)+(6) serie diaria nacional y serie de hospitalizaciones/defunciones
	$(PY) -m src.datos

determinismo:       ## dos corridas idénticas byte a byte
	$(PY) -m src.datos --verificar-determinismo

comparar:           ## (4) nota de diferencias vs. tablero CONAHCYT
	$(PY) -m src.comparar_tablero

historicos:         ## series por versión histórica (insumo de EDA §3)
	$(PY) -m src.series_historicas

eda:                ## (5) EDA de artefactos de medición
	$(PY) -m src.eda $(if $(wildcard data/processed/historicos/*),--historicos data/processed/historicos,)

inventario:         ## (7) inventario de versiones semanales
	$(PY) scripts/inventario_historicos.py

.PHONY: all env test teoria figuras tablas escrito recuperacion resumen todo serie determinismo comparar historicos eda inventario fuentes
