from django import template
from django.db.models import DateField

register = template.Library()

@register.filter
def is_date_field(field):
    return isinstance(field.field, DateField)


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
