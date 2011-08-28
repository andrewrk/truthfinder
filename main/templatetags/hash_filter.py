from django import template

register = template.Library()

@register.filter
def hash(attr, obj):
    pseudo_context = { 'object' : obj }
    try:
        value = template.Variable('object.%s' % attr).resolve(pseudo_context)
    except template.VariableDoesNotExist:
        value = None

    return value
