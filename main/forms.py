from django import forms
from main.models import TruthNode
import bleach

class CreateNodeForm(forms.ModelForm):
    class Meta:
        model = TruthNode
        exclude = ('create_date', 'edit_date')

    def clean_content(self):
        content = self.cleaned_data['content']
        return bleach.clean(content)
