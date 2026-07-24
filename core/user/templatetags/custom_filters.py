"""Filtros personalizados de template para la aplicación de usuarios."""

from django import template
from django.db.models import DateField

register = template.Library()

@register.filter
def is_date_field(field):
    """Retorna True si el campo del formulario es de tipo DateField."""
    return isinstance(field.field, DateField)


@register.filter(name='has_group')
def has_group(user, group_name):
    """Retorna True si el usuario pertenece al grupo de nombre indicado."""
    return user.groups.filter(name=group_name).exists()
