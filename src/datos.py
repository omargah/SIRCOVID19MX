"""Lectura de configuración y (a partir de F3) de los datos de la SSA y ENSANUT.

Por ahora contiene el cargador de config/parametros.yaml, que hace cumplir
la regla (2): ningún parámetro sin fuente. El esquema está documentado en la
cabecera de ese archivo. La carga y limpieza de datos reales se escribe en
F3; por la regla (3), ningún método de estimación se aplica a datos reales
antes de cerrar F4.

Qué rechaza el cargador (lanza ParametroSinFuente)
--------------------------------------------------
* Entradas sin `valor`, `unidad` o `supuesto` (supuesto no tiene valor por
  omisión: hay que decidir explícitamente).
* supuesto: false sin fuente válida:
    - doi: DOI mal formado, sin página, clave que no está en
      bibliografia/INDICE.csv o DOI distinto al del índice;
    - institucional: sin institución, documento, año o ubicación;
    - regla: regla vacía o `depende_de` con parámetros inexistentes.
* supuesto: true sin justificación o sin rango de sensibilidad válido.
* D_* (tiempo característico de gamma = 1/D) que sea incubación u otra cosa
  distinta de periodo infeccioso / intervalo de generación, definiciones
  mezcladas entre olas, o un `gamma` declarado aparte junto a D_*.
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_PARAMETROS = RAIZ / "config" / "parametros.yaml"
ARCHIVO_INDICE = RAIZ / "bibliografia" / "INDICE.csv"

# Un DOI siempre empieza con "10." seguido del prefijo del editor y "/".
_PATRON_DOI = re.compile(r"^10\.\d{4,9}/\S+$")

# Lo único que puede ser D en un SIR: el tiempo medio en I (periodo
# infeccioso) o el intervalo de generación, que en el SIR coincide con 1/gamma.
DEFINICIONES_D = ("periodo_infeccioso", "intervalo_generacion")
PREFIJO_D = "D_"


class ParametroSinFuente(ValueError):
    """Se lanza cuando un parámetro viola la regla (2) o el esquema."""


def _leer_indice(archivo=ARCHIVO_INDICE):
    """{clave: doi} de bibliografia/INDICE.csv ('' si la clave no tiene DOI)."""
    with open(archivo, encoding="utf-8") as f:
        return {r["Clave"].strip(): r["DOI"].strip() for r in csv.DictReader(f)}


def _vacio(x):
    return x is None or not str(x).strip()


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _validar_fuente(nombre, fuente, indice, nombres_seccion):
    if not isinstance(fuente, dict):
        raise ParametroSinFuente(f"{nombre}: supuesto: false pero no trae 'fuente'")
    tipo = fuente.get("tipo")
    if tipo == "doi":
        doi = str(fuente.get("doi", ""))
        if not _PATRON_DOI.match(doi):
            raise ParametroSinFuente(f"{nombre}: DOI ausente o mal formado ('{doi}')")
        if _vacio(fuente.get("pagina")):
            raise ParametroSinFuente(f"{nombre}: una cifra de artículo necesita página")
        clave = str(fuente.get("clave", "")).strip()
        if clave not in indice:
            raise ParametroSinFuente(f"{nombre}: clave '{clave}' no está en bibliografia/INDICE.csv")
        if indice[clave] and indice[clave].lower() != doi.lower():
            raise ParametroSinFuente(
                f"{nombre}: DOI '{doi}' no coincide con el de {clave} en INDICE.csv ('{indice[clave]}')"
            )
    elif tipo == "institucional":
        for campo in ("institucion", "documento", "anio", "ubicacion"):
            if _vacio(fuente.get(campo)):
                raise ParametroSinFuente(f"{nombre}: fuente institucional sin '{campo}'")
        if not isinstance(fuente["anio"], int):
            raise ParametroSinFuente(f"{nombre}: 'anio' debe ser un entero (año de la cifra)")
    elif tipo == "regla":
        if _vacio(fuente.get("regla")):
            raise ParametroSinFuente(f"{nombre}: la regla de cálculo está vacía")
        for dep in fuente.get("depende_de", []) or []:
            if dep not in nombres_seccion:
                raise ParametroSinFuente(f"{nombre}: depende de '{dep}', que no existe en la sección")
    else:
        raise ParametroSinFuente(
            f"{nombre}: tipo de fuente '{tipo}' no es 'doi', 'institucional' ni 'regla'"
        )


def _validar_supuesto(nombre, entrada):
    if _vacio(entrada.get("justificacion")):
        raise ParametroSinFuente(f"{nombre}: supuesto sin 'justificacion'")
    sens = entrada.get("sensibilidad")
    if not isinstance(sens, dict) or not (_es_numero(sens.get("min")) and _es_numero(sens.get("max"))):
        raise ParametroSinFuente(f"{nombre}: supuesto sin rango 'sensibilidad: {{min, max}}' numérico")
    if sens["min"] > sens["max"]:
        raise ParametroSinFuente(f"{nombre}: sensibilidad con min > max")
    v = entrada["valor"]
    if _es_numero(v) and not sens["min"] <= v <= sens["max"]:
        raise ParametroSinFuente(f"{nombre}: valor {v} fuera de su rango de sensibilidad")


def _validar_entrada(nombre, entrada, indice, nombres_seccion):
    """Revisa que una entrada cumpla la regla (2); lanza error si no."""
    if not isinstance(entrada, dict):
        raise ParametroSinFuente(f"{nombre}: la entrada debe ser un diccionario")
    for campo in ("valor", "unidad", "supuesto"):
        if campo not in entrada:
            raise ParametroSinFuente(f"{nombre}: falta el campo '{campo}'")
    if entrada["supuesto"] not in (True, False):
        raise ParametroSinFuente(f"{nombre}: 'supuesto' debe ser true o false")
    if entrada["supuesto"]:
        _validar_supuesto(nombre, entrada)
    else:
        _validar_fuente(nombre, entrada.get("fuente"), indice, nombres_seccion)


def _validar_D(seccion, entradas):
    """D es uno solo por ola y siempre periodo infeccioso o Tg, nunca incubación."""
    ds = {n: e for n, e in entradas.items() if n.startswith(PREFIJO_D)}
    if not ds:
        return
    for n, e in ds.items():
        if e.get("definicion") not in DEFINICIONES_D:
            raise ParametroSinFuente(
                f"{seccion}.{n}: D debe ser {' o '.join(DEFINICIONES_D)}, "
                f"no '{e.get('definicion')}' (la incubación no es el tiempo en I)"
            )
        if e.get("unidad") != "dia":
            raise ParametroSinFuente(f"{seccion}.{n}: D debe estar en 'dia'")
        if e["valor"] is not None and not (_es_numero(e["valor"]) and e["valor"] > 0):
            raise ParametroSinFuente(f"{seccion}.{n}: D debe ser un número positivo")
    definiciones = {e["definicion"] for e in ds.values()}
    if len(definiciones) > 1:
        raise ParametroSinFuente(
            f"{seccion}: las D_* mezclan definiciones {sorted(definiciones)}; deben ser la misma"
        )
    if "gamma" in entradas:
        raise ParametroSinFuente(
            f"{seccion}: hay D_* y también 'gamma'; gamma se deriva de D (gamma = 1/D), no se declara aparte"
        )


def cargar_entradas(archivo=ARCHIVO_PARAMETROS, indice=ARCHIVO_INDICE):
    """Lee y valida TODO el archivo; devuelve {seccion: {nombre: entrada}}.

    Se valida el archivo entero (no solo la sección pedida) para que un error
    en cualquier parte se note de inmediato.
    """
    with open(archivo, encoding="utf-8") as f:
        todo = yaml.safe_load(f)
    if not isinstance(todo, dict):
        raise ParametroSinFuente(f"{archivo}: el archivo no tiene secciones")
    claves = _leer_indice(indice)
    for sec, entradas in todo.items():
        if not isinstance(entradas, dict):
            raise ParametroSinFuente(f"Sección '{sec}' vacía o mal formada")
        for nombre, entrada in entradas.items():
            _validar_entrada(f"{sec}.{nombre}", entrada, claves, entradas)
        _validar_D(sec, entradas)
    return todo


def cargar_parametros(seccion, archivo=ARCHIVO_PARAMETROS, permitir_pendientes=False):
    """Devuelve {nombre: valor} de una sección ('sintetico' o 'real').

    Si la sección tiene parámetros pendientes (valor null), lanza error salvo
    que se pida explícitamente `permitir_pendientes=True` (para inspección):
    no se corre un análisis con cifras que todavía no existen.
    """
    todo = cargar_entradas(archivo)
    if seccion not in todo:
        raise KeyError(f"No existe la sección '{seccion}' en {archivo}")
    entradas = todo[seccion]
    pendientes = [n for n, e in entradas.items() if e["valor"] is None]
    if pendientes and not permitir_pendientes:
        raise ParametroSinFuente(
            f"Sección '{seccion}' tiene parámetros pendientes (valor null): {', '.join(pendientes)}"
        )
    return {n: e["valor"] for n, e in entradas.items()}


def rangos_sensibilidad(seccion, archivo=ARCHIVO_PARAMETROS):
    """{nombre: (min, max)} de cada parámetro marcado supuesto: true.

    Es la lista de entrada del análisis de sensibilidad: todo lo que no tiene
    fuente se barre en su rango en vez de tratarse como dato.
    """
    entradas = cargar_entradas(archivo)[seccion]
    return {
        n: (e["sensibilidad"]["min"], e["sensibilidad"]["max"])
        for n, e in entradas.items()
        if e["supuesto"]
    }


def gamma_ola(parametros, ola):
    """gamma = 1/D_ola. Única forma de obtener gamma en la sección 'real'."""
    D = parametros[f"{PREFIJO_D}{ola}"]
    if D is None:
        raise ParametroSinFuente(f"{PREFIJO_D}{ola} está pendiente")
    return 1.0 / D
