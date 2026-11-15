from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "description", "doc_type", "category", "level", "file", "visibility", "status"]
        # FileInput (et non ClearableFileInput) : le fichier est privé, son URL ne doit jamais être générée par le widget
        widgets = {"description": forms.Textarea(attrs={"rows": 3}),
                   "file": forms.FileInput(attrs={"accept": "application/pdf"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["file"].required = False
