from django import forms

class UploadImageForm(forms.Form):
    image = forms.ImageField(label="Select Image")
    text = forms.CharField(label="Enter Text", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional Text'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['text'].widget.attrs.update({'class': 'form-control'})
