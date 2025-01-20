from django import forms

class MultipleImageUploadForm(forms.Form):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}), required=False,
        label='Upload Face Images'
    )