from django import forms

from .antispam import AntiSpamMixin
from .models import ContactMessage, Officer, SiteSetting


class ContactForm(AntiSpamMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5, "minlength": 10}),
                   "name": forms.TextInput(attrs={"autocomplete": "name"}),
                   "email": forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"})}

    def clean_message(self):
        msg = self.cleaned_data["message"].strip()
        if len(msg) < 10:
            raise forms.ValidationError("Votre message est trop court (10 caractères minimum).")
        if msg.lower().count("http") > 2:
            raise forms.ValidationError("Trop de liens dans le message.")
        return msg


class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ["last_name", "first_name", "user", "function", "mandate_start", "mandate_end", "photo", "description", "is_archived"]
        widgets = {"mandate_start": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
                   "mandate_end": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
                   "description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].required = False
        self.fields["photo"].help_text = "Photo publique du responsable, utilisée si aucun compte membre n'est associé."
        self.fields["user"].label = "Compte membre associé"
        self.fields["user"].help_text = (
            "La photo de profil privée de ce compte sera publiée sur la page À propos tant que ce mandat est actif."
        )

    def clean(self):
        cleaned_data = super().clean()
        photo = cleaned_data.get("photo")
        user = cleaned_data.get("user")
        if not photo and not (user and user.photo):
            self.add_error("photo", "Ajoutez une photo publique ou associez un compte avec une photo de profil.")
        return cleaned_data


class SettingForm(forms.Form):
    value = forms.CharField(label="Valeur", widget=forms.Textarea(attrs={"rows": 3}), required=False)
