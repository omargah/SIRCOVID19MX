# Uso:
#   make env      crea el entorno (conda si existe; si no, .venv con pip)
#   make test     corre las pruebas
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

.PHONY: all env test figuras tablas escrito recuperacion resumen
