# Pipeline de datos F3. Requiere los crudos en data/raw/ (ver data/raw/README.md).
PY ?= python3

.PHONY: todo serie determinismo comparar historicos eda inventario fuentes test

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

test:
	$(PY) -m pytest -q tests
