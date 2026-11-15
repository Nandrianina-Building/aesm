from django import forms

from apps.core.validators import validate_image

from .models import Comment, Publication, PublicationCategory, PublicationImage


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiImageField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else ([data] if data else [])
        out = []
        for f in files:
            out.append(super().clean(f, initial))
            validate_image(out[-1])
        return out


class PublicationForm(forms.ModelForm):
    gallery = MultiImageField(label="Images supplémentaires (une ou plusieurs)", required=False,
                              widget=MultiFileInput(attrs={"accept": "image/*", "multiple": True, "data-preview": "1"}),
                              help_text="Vous pouvez sélectionner plusieurs images à la fois.")
    remove_images = forms.ModelMultipleChoiceField(label="Images à retirer", required=False,
                                                    queryset=PublicationImage.objects.none(),
                                                    widget=forms.MultipleHiddenInput)

    class Meta:
        model = Publication
        fields = ["title", "kind", "category", "summary", "body", "image", "visibility", "status", "publish_at", "pinned", "comments_enabled"]
        widgets = {"publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
                   "body": forms.Textarea(attrs={"rows": 10})}

    field_order = ["title", "kind", "category", "summary", "body", "image", "gallery", "remove_images", "visibility",
                   "status", "publish_at", "pinned", "comments_enabled"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].label = "Image de couverture"
        self.fields["image"].widget.attrs.update({"accept": "image/*", "data-preview": "1"})
        if self.instance and self.instance.pk and self.instance.images.exists():
            self.fields["remove_images"].queryset = self.instance.images.all()
        else:
            del self.fields["remove_images"]

    def clean(self):
        d = super().clean()
        if d.get("status") == Publication.SCHEDULED and not d.get("publish_at"):
            self.add_error("publish_at", "Indiquez la date de publication pour une publication programmée.")
        return d


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Votre commentaire..."})}
        labels = {"body": ""}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = PublicationCategory
        fields = ["name", "image"]
        widgets = {"image": forms.ClearableFileInput(attrs={"accept": "image/*", "data-preview": "1"})}
