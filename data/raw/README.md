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
