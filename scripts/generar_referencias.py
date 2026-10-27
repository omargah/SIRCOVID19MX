#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera referencias.bib desde INDICE.csv.
Uso: python3 scripts/generar_referencias.py
"""

import csv
from pathlib import Path

# Rutas relativas al repo
csv_file = Path(__file__).parent.parent / "bibliografia" / "INDICE.csv"
bib_file = Path(__file__).parent.parent / "bibliografia" / "referencias.bib"

def crear_entrada_bib(row):
    """Crea una entrada BibTeX en formato APA 7."""
    clave = row['Clave'].strip()
    autor = row['Autor'].strip()
    año = row['Año'].strip()
    doi = row['DOI'].strip()
    bloque = row['Bloque'].strip()

    # Construcción de la entrada
    entrada = f"""@article{{{clave},
  author = {{{autor}}},
  year = {{{año}}},
  keywords = {{{bloque}}}"""

    if doi:
        entrada += f",\n  doi = {{{doi}}}"

    entrada += "\n}\n"
    return entrada

# Generar BibTeX
try:
    entradas = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entradas.append(crear_entrada_bib(row))

    # Guardar
    with open(bib_file, 'w', encoding='utf-8') as f:
        f.write("% Referencias generadas automáticamente desde INDICE.csv\n")
        f.write("% Omar García Hernández — Proyecto Terminal 1, SIR COVID-19 en México\n\n")
        f.writelines(entradas)

    print(f"✓ referencias.bib creado: {bib_file}")
    print(f"✓ Total de entradas: {len(entradas)}")

except FileNotFoundError as e:
    print(f"✗ Error: {e}")
    print(f"Asegúrate de que INDICE.csv existe en: {csv_file}")
