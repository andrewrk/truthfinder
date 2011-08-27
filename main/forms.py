from django import forms
from main.models import TruthNode
import bleach

allowed_tags = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'em',
    'i',
    'li',
    'ol',
    'strong',
    'ul',
    'br',
    'font',
    'span',
    'div',
    'p',
    'sup',
    'sub',
    'table',
    'tr',
    'td',
    'img',
    'pre',
    'dl',
    'dd',
    'dt',
]

allowed_attrs = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    'span': ['style'],
}

allowed_styles = [
    'font-size',
    'line-height',
]

class CreateNodeForm(forms.ModelForm):
    class Meta:
        model = TruthNode
        exclude = ('create_date', 'edit_date')

    def clean_content(self):
        content = self.cleaned_data['content']
        return bleach.clean(content, tags=allowed_tags,
            attributes=allowed_attrs, styles=allowed_styles)
