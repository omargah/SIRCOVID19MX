# Pipeline reproducible. `make` rehace todo lo que dependa de algo que cambió.
PY = python

RES = reports/resultados/sintetico_h1.json

all: reports/numeros.tex figuras tablas

$(RES): scripts/correr_sintetico.py src/*.py config/parametros.yaml
	$(PY) scripts/correr_sintetico.py

reports/numeros.tex: $(RES) scripts/make_numeros.py
	$(PY) scripts/make_numeros.py

figuras: $(RES) scripts/make_figuras.py
	$(PY) scripts/make_figuras.py

tablas: $(RES) scripts/make_tablas.py
	$(PY) scripts/make_tablas.py

test:
	$(PY) -m pytest -q

escrito: all
	cd escrito && latexmk -pdf main.tex

.PHONY: all figuras tablas test escrito
