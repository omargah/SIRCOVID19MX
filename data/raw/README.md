# data/raw — datos tal como se descargaron

**Estos archivos no están en git** (pesan GB; ver `.gitignore`). Este README
dice cómo obtenerlos y registra cada descarga. Nada aquí se edita a mano.

## Cómo obtenerlos

1. **Casos COVID-19 (SSA, Dirección General de Epidemiología).**
   Portal de datos abiertos del Gobierno de México, conjunto
   "Información referente a casos COVID-19 en México" (base por registro
   individual: un ZIP con un CSV, más el diccionario de datos).
   - Descargar el ZIP de la fecha de corte elegida y su diccionario.
   - Guardarlos sin descomprimir ni renombrar en `data/raw/ssa/`.
   - Para H4 (pronóstico en tiempo real) se necesitan **cortes históricos
     fechados**, no solo el más reciente (ver `docs/plan_analisis.md`, nota 3).
   - La URL exacta y la fecha de corte se fijan en F3 y se anotan abajo.
2. **Seroprevalencia (ENSANUT).** No se descargan microdatos: se usan las
   estimaciones publicadas (bibliografía I01, I03). Cada cifra entra en
   `config/parametros.yaml` con su DOI y su página.

Después de descargar, calcula el hash y anótalo en la tabla:

```bash
sha256sum data/raw/ssa/*.zip
```

## Registro de descargas

| Archivo | Fuente (URL) | Fecha de corte | Fecha de descarga | SHA-256 |
|---|---|---|---|---|
| (vacío hasta F3) | | | | |

---

## Pipeline de microdatos DGE (rama compassionate-dijkstra)

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
