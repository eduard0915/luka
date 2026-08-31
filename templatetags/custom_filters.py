"""Filtros personalizados para las plantillas de Django de Luka LIS.

Incluye el filtro ``index`` para acceder a elementos de secuencias
por su posición.
"""

from django import template

register = template.Library()


@register.filter
def index(sequence, position):
    """Retorna el elemento de *sequence* en la *position* indicada.

    Args:
        sequence: Secuencia (lista, tupla, dict, etc.) a la que se accede.
        position: Índice o clave del elemento deseado.

    Returns:
        El elemento en la posición solicitada o ``None`` si ocurre un error.
    """
    try:
        return sequence[position]
    except (IndexError, TypeError, KeyError):
        return None
    