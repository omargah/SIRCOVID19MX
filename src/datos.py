"""Lectura de configuración y (a partir de F3) de los datos de la SSA y ENSANUT.

Por ahora solo contiene el cargador de config/parametros.yaml. La carga y
limpieza de datos reales se escribe en F3; por la regla (3), ningún método
de estimación se aplica a datos reales antes de cerrar F4.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_PARAMETROS = RAIZ / "config" / "parametros.yaml"

# Un DOI siempre empieza con "10." seguido del prefijo del editor y "/".
_PATRON_DOI = re.compile(r"^10\.\d{4,9}/\S+$")


class ParametroSinFuente(ValueError):
    """Se lanza cuando un parámetro viola la regla (2)."""


def _validar(nombre, entrada):
    """Revisa que una entrada cumpla la regla (2); lanza error si no."""
    for campo in ("valor", "unidad", "fuente", "estado"):
        if campo not in entrada:
            raise ParametroSinFuente(f"{nombre}: falta el campo '{campo}'")
    fuente = entrada["fuente"]
    tipo = fuente.get("tipo")
    if tipo == "doi":
        if not _PATRON_DOI.match(str(fuente.get("doi", ""))):
            raise ParametroSinFuente(f"{nombre}: DOI ausente o mal formado")
        if not fuente.get("pagina"):
            raise ParametroSinFuente(f"{nombre}: una cifra de artículo necesita página")
    elif tipo == "regla":
        if not str(fuente.get("regla", "")).strip():
            raise ParametroSinFuente(f"{nombre}: la regla de cálculo está vacía")
    else:
        raise ParametroSinFuente(f"{nombre}: tipo de fuente '{tipo}' no es 'doi' ni 'regla'")
    if entrada["estado"] not in ("fijo", "pendiente"):
        raise ParametroSinFuente(f"{nombre}: estado '{entrada['estado']}' no válido")
    if entrada["estado"] == "fijo" and entrada["valor"] is None:
        raise ParametroSinFuente(f"{nombre}: está 'fijo' pero no tiene valor")


def cargar_parametros(seccion, archivo=ARCHIVO_PARAMETROS):
    """Devuelve {nombre: valor} de una sección ('sintetico' o 'real').

    Valida TODAS las entradas del archivo (no solo la sección pedida), para
    que un error en cualquier parte se note de inmediato. Si la sección
    tiene parámetros 'pendiente', se lanza error: no se puede correr un
    análisis con cifras que todavía no tienen fuente.
    """
    with open(archivo, encoding="utf-8") as f:
        todo = yaml.safe_load(f)
    for sec, entradas in todo.items():
        for nombre, entrada in entradas.items():
            _validar(f"{sec}.{nombre}", entrada)
    pendientes = [n for n, e in todo[seccion].items() if e["estado"] == "pendiente"]
    if pendientes:
        raise ParametroSinFuente(
            f"Sección '{seccion}' tiene parámetros pendientes: {', '.join(pendientes)}"
        )
    return {n: e["valor"] for n, e in todo[seccion].items()}
