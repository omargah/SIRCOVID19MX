# data/raw — archivos crudos (no versionados en git)

Los archivos de esta carpeta se descargan **a mano** (el entorno de desarrollo puede no alcanzar
gob.mx) y no se suben al repositorio por su tamaño. Lo que sí se versiona es su procedencia:
`data/fuentes.csv`.

```
data/raw/
├── dge/                      microdato vigente o bases anuales (fuente primaria)
│   └── historicos/           versiones semanales datos_abiertos_covid19_DD.MM.AAAA.zip
└── tablero/                  Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv (PT1)
```

## Pasos

1. Descargar el microdato de la DGE (zip con un único CSV) en `data/raw/dge/`.
   Portal: <https://www.gob.mx/salud/documentos/datos-abiertos-152127>. Bajar también el
   diccionario y catálogos (`diccionario_datos_covid19.zip`) para verificar `docs/diccionario_datos.md`.
2. Copiar el CSV del tablero CONAHCYT usado en el PT1 a `data/raw/tablero/`.
3. Registrar cada archivo **el mismo día de la descarga**:

   ```bash
   python scripts/registrar_fuente.py data/raw/dge/datos_abiertos_covid19.zip --nivel DGE --url URL_EXACTA --fecha-descarga AAAA-MM-DD
   ```

   ```bash
   python scripts/registrar_fuente.py data/raw/tablero/Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv --nivel tablero --url https://datos.covid-19.conacyt.mx/ --fecha-descarga AAAA-MM-DD --nota "archivo original del PT1"
   ```

   Para los históricos, la URL se deduce del nombre:

   ```bash
   python scripts/registrar_fuente.py data/raw/dge/historicos/*.zip --nivel DGE --url-historico --fecha-descarga AAAA-MM-DD
   ```

4. `make todo` (o los pasos sueltos del `Makefile`).

`python scripts/registrar_fuente.py --pendientes` lista lo que falta registrar y
`--verificar` comprueba que ningún archivo cambió desde su registro.
