"""Etiquetas de template para ayudar en la navegación de la interfaz.

Provee etiquetas que añaden clases CSS dinámicamente según la ruta
activa, facilitando la implementación del menú lateral colapsable
(treeview).
"""

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_section(context, *paths):
    """Retorna la clase CSS 'treeview-item active' si la ruta actual coincide con *paths*.

    Args:
        context: Contexto de la plantilla (debe contener ``request``).
        paths: Rutas parciales contra las cuales comparar.

    Returns:
        str: Clase CSS para el elemento del menú.
    """
    request_path = context['request'].path
    return 'treeview-item active' if any(path in request_path for path in paths) else 'treeview-item'

@register.simple_tag(takes_context=True)
def is_expanded(context, *paths):
    """Retorna la clase CSS 'treeview is-expanded' si la ruta actual coincide con *paths*.

    Args:
        context: Contexto de la plantilla (debe contener ``request``).
        paths: Rutas parciales contra las cuales comparar.

    Returns:
        str: Clase CSS para el contenedor treeview expandido.
    """
    request_path = context['request'].path
    return 'treeview is-expanded' if any(path in request_path for path in paths) else 'treeview'


# @register.simple_tag(takes_context=True)
# def is_active_section(context, *paths):
#     request_path = context['request'].path
#     return 'active' if any(path in request_path for path in paths) else ''
#
# @register.simple_tag(takes_context=True)
# def should_show_collapse(context, *paths):
#     request_path = context['request'].path
#     return 'collapse show' if any(path in request_path for path in paths) else 'collapse'
