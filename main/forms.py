from django import forms
from main.models import TruthNode

class CreateNodeForm(forms.ModelForm):
    class Meta:
        model = TruthNode
        exclude = ('create_date', 'edit_date')
