from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_section(context, *paths):
    request_path = context['request'].path
    return 'treeview-item active' if any(path in request_path for path in paths) else 'treeview-item'

@register.simple_tag(takes_context=True)
def is_expanded(context, *paths):
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
