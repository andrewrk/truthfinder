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


import re
from main.models import TruthNode
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

node_expansion_re = re.compile(r'\[\[node (\d+)\]\]')
invalid_text = 'Unknown Claim'
html_invalid_text = '<span style="text-decoration: underline">%s</span>' % invalid_text
@register.filter
def expand_node_titles(text, hyperlink=False):
    def get_expansion(match):
        try:
            node_id = int(match.group(1))
        except ValueError:
            return html_invalid_text
        try:
            title = '{%s}' % TruthNode.objects.get(pk=node_id).title
        except TruthNode.DoesNotExist:
            return html_invalid_text
        if hyperlink:
            return '<a href="%s">%s</a>' % (reverse('node', args=[node_id]), title)
        else:
            return title
    return mark_safe(node_expansion_re.sub(get_expansion, text))

@register.filter
def expand_node_links(text):
    return expand_node_titles(text, hyperlink=True)
