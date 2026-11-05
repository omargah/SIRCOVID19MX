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
* sensibilidad en forma lista con un rango sin tipo, clave o página, o con
  una clave que no está en INDICE.csv.
* D_* (tiempo característico de gamma = 1/D) que sea incubación u otra cosa
  distinta de periodo infeccioso / intervalo de generación, definiciones
  mezcladas entre olas, o un `gamma` declarado aparte junto a D_*.
* D_* sin `estimador`, o con estimador distinto de "intrinseco" y
  supuesto: false (solo el GI intrínseco cuenta como fuente de D).
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
# Cómo se estimó el intervalo de generación. La decisión del 2026-11-03 es
# D = GI INTRÍNSECO; uno que no lo es (p. ej. G02, estimado bajo
# aislamiento y cuarentena) solo entra como supuesto (decisión 2026-11-04).
ESTIMADORES_D = ("intrinseco", "realizado_bajo_contencion")
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


def _validar_rango(nombre, r, indice, con_fuente):
    """Un rango de sensibilidad {min, max} y, si es de la forma lista, su fuente."""
    if not isinstance(r, dict) or not (_es_numero(r.get("min")) and _es_numero(r.get("max"))):
        raise ParametroSinFuente(f"{nombre}: rango de sensibilidad sin 'min'/'max' numéricos")
    if r["min"] > r["max"]:
        raise ParametroSinFuente(f"{nombre}: sensibilidad con min > max")
    if con_fuente:
        for campo in ("tipo", "clave", "pagina"):
            if _vacio(r.get(campo)):
                raise ParametroSinFuente(f"{nombre}: rango de sensibilidad sin '{campo}'")
        if str(r["clave"]).strip() not in indice:
            raise ParametroSinFuente(
                f"{nombre}: clave '{r['clave']}' del rango no está en bibliografia/INDICE.csv"
            )


def _rangos(entrada):
    """Lista de rangos de una entrada (la forma dict antigua es una lista de uno)."""
    sens = entrada.get("sensibilidad")
    if sens is None:
        return []
    return sens if isinstance(sens, list) else [sens]


def _validar_sensibilidad(nombre, entrada, indice):
    """Dos formas válidas de `sensibilidad`:

    * {min, max}: un rango (forma original de stoic-galileo).
    * [{min, max, tipo, clave, pagina, nota}, ...]: varios rangos, cada uno
      con su fuente (decisión de Omar 2026-11-04, para D: CrI95 de la fuente
      del valor base + rango de Byrne 2020). La clave debe estar en INDICE.csv.
    El valor (si es número) debe caer dentro de la envolvente de los rangos.
    """
    sens = entrada.get("sensibilidad")
    if isinstance(sens, list):
        if not sens:
            raise ParametroSinFuente(f"{nombre}: lista de sensibilidad vacía")
        for r in sens:
            _validar_rango(nombre, r, indice, con_fuente=True)
    else:
        _validar_rango(nombre, sens, indice, con_fuente=False)
    lo = min(r["min"] for r in _rangos(entrada))
    hi = max(r["max"] for r in _rangos(entrada))
    v = entrada["valor"]
    if _es_numero(v) and not lo <= v <= hi:
        raise ParametroSinFuente(f"{nombre}: valor {v} fuera de su rango de sensibilidad")


def _validar_supuesto(nombre, entrada, indice):
    if _vacio(entrada.get("justificacion")):
        raise ParametroSinFuente(f"{nombre}: supuesto sin 'justificacion'")
    if entrada.get("sensibilidad") is None:
        raise ParametroSinFuente(f"{nombre}: supuesto sin rango 'sensibilidad: {{min, max}}' numérico")
    _validar_sensibilidad(nombre, entrada, indice)


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
        _validar_supuesto(nombre, entrada, indice)
    else:
        _validar_fuente(nombre, entrada.get("fuente"), indice, nombres_seccion)
        # Un parámetro con fuente también puede declarar sensibilidad (D: su
        # CrI95 y el rango de Byrne); si la declara, se valida igual.
        if entrada.get("sensibilidad") is not None:
            _validar_sensibilidad(nombre, entrada, indice)


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
        if e.get("estimador") not in ESTIMADORES_D:
            raise ParametroSinFuente(
                f"{seccion}.{n}: 'estimador' debe ser {' o '.join(ESTIMADORES_D)}"
            )
        if e["estimador"] != "intrinseco" and not e["supuesto"]:
            raise ParametroSinFuente(
                f"{seccion}.{n}: un D que no es intervalo de generación intrínseco "
                "solo puede entrar como supuesto: true"
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
    fuente se barre en su rango en vez de tratarse como dato. Si la entrada
    trae varios rangos (forma lista), aquí se devuelve su envolvente; el
    detalle con fuente de cada rango está en rangos_sensibilidad_detalle.
    """
    entradas = cargar_entradas(archivo)[seccion]
    return {
        n: (min(r["min"] for r in _rangos(e)), max(r["max"] for r in _rangos(e)))
        for n, e in entradas.items()
        if e["supuesto"]
    }


def rangos_sensibilidad_detalle(seccion, archivo=ARCHIVO_PARAMETROS):
    """{nombre: [rango, ...]} de TODA entrada que declare sensibilidad.

    Incluye parámetros con fuente que también se barren (D_ola3, D_ola4:
    su CrI95 y el rango de Byrne). Cada rango es el dict del YAML
    (min, max y, en la forma lista, tipo, clave, pagina, nota).
    """
    entradas = cargar_entradas(archivo)[seccion]
    return {n: [dict(r) for r in _rangos(e)] for n, e in entradas.items() if _rangos(e)}


def gamma_ola(parametros, ola):
    """gamma = 1/D_ola. Única forma de obtener gamma en la sección 'real'."""
    D = parametros[f"{PREFIJO_D}{ola}"]
    if D is None:
        raise ParametroSinFuente(f"{PREFIJO_D}{ola} está pendiente")
    return 1.0 / D
