from django import forms
from devices.models import TrainingImage

class TrainingImageForm(forms.ModelForm):
    class Meta:
        model = TrainingImage
        fields = ['member', 'file_path']