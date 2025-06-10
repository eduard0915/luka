from django import template
from django.db.models import DateField

register = template.Library()

@register.filter
def is_date_field(field):
    return isinstance(field.field, DateField)
