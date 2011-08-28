from django import forms
from main.models import TruthNode, NodeRelationship
import bleach

allowed_tags = [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
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
    'u',
    'ul',
    'br',
    'font',
    'span',
    'div',
    'p',
    'sup',
    'sub',
    'table',
    'tbody',
    'tr',
    'td',
    'img',
    'pre',
    'dl',
    'dd',
    'dt',
]

allowed_attrs = {
    'a': ['href', 'title', 'style'],
    'abbr': ['title', 'style'],
    'acronym': ['title', 'style'],
    'span': ['style'],
    'img': ['src', 'width', 'height', 'alt', 'title', 'style'],
    'div': ['style'],
    'code': ['style'],
    'pre': ['style'],
}

allowed_styles = [
    'font-size',
    'line-height',
]

class CreateNodeForm(forms.ModelForm):
    class Meta:
        model = TruthNode
        exclude = ('create_date', 'edit_date')

    def __init__(self, *args, **kwargs):
        super(CreateNodeForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = False

    def clean_content(self):
        content = self.cleaned_data['content']
        return bleach.clean(content, tags=allowed_tags,
            attributes=allowed_attrs, styles=allowed_styles)

class NodeRelationshipForm(forms.ModelForm):
    class Meta:
        model = NodeRelationship

    def clean(self):
        parent_node = self.cleaned_data['parent_node']
        child_node = self.cleaned_data['child_node']
        relationship = self.cleaned_data['relationship']

        if NodeRelationship.objects.filter(parent_node=parent_node, child_node=child_node, relationship=relationship).count() > 0:
            self._errors['parent_node'] = self.error_class(["This relationship already exists."])

        return self.cleaned_data
