from django import forms

from apps.publications.forms import MultiFileInput, MultiImageField

from .models import Event, EventImage


class EventForm(forms.ModelForm):
    gallery = MultiImageField(label="Images supplémentaires (une ou plusieurs)", required=False,
                              widget=MultiFileInput(attrs={"accept": "image/*", "multiple": True, "data-preview": "1"}),
                              help_text="Vous pouvez sélectionner plusieurs images à la fois.")
    remove_images = forms.ModelMultipleChoiceField(required=False, queryset=EventImage.objects.none(),
                                                   widget=forms.MultipleHiddenInput)

    class Meta:
        model = Event
        fields = ["title", "description", "image", "category", "starts_at", "location", "capacity",
                  "registration_deadline", "price", "members_only", "invitation_only", "visibility", "conditions", "status"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "registration_deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "description": forms.Textarea(attrs={"rows": 4}),
            "conditions": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].label = "Affiche / image principale"
        self.fields["image"].widget.attrs.update({"accept": "image/*", "data-preview": "1"})
        if self.instance and self.instance.pk:
            self.fields["remove_images"].queryset = self.instance.images.all()
        else:
            del self.fields["remove_images"]

    def clean(self):
        d = super().clean()
        if d.get("starts_at") and d.get("registration_deadline") and d["registration_deadline"] > d["starts_at"]:
            self.add_error("registration_deadline", "La date limite doit précéder l'événement.")
        if self.instance.pk and d.get("capacity") is not None:
            from .services import taken_seats
            if d["capacity"] < taken_seats(self.instance):
                self.add_error("capacity", "La capacité ne peut pas être inférieure au nombre de places déjà réservées.")
        return d
