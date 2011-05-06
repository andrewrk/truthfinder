from django import forms
from richtext.fields import RichTextField
from richtext.custom_widgets import RichTextWidget
        
class TestingForm(forms.Form):
    """This form is simply for testing the RichTextField outside of the django-admin"""
    #content = RichTextField(photologue=True)
    content = RichTextField()
    description = forms.CharField()
        