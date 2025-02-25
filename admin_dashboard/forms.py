from django import forms
from .models import ServiceConfig

class ServiceConfigForm(forms.ModelForm):
    class Meta:
        model = ServiceConfig
        fields = ['service', 'key', 'value']
        widgets = {
            'service': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'key': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'value': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
        }