"""Anti-spam sans service externe : champ piège (honeypot) + délai minimum de remplissage."""
import time

from django import forms
from django.conf import settings
from django.core import signing

SALT = "aesm.antispam"


def make_token(age=0):
    """Jeton daté. `age` (secondes) sert uniquement aux tests pour simuler un formulaire rempli depuis un moment."""
    return signing.TimestampSigner(salt=SALT).sign(str(int(time.time()) - age))


class AntiSpamMixin(forms.Form):
    """À placer en premier parmi les classes du formulaire."""
    website = forms.CharField(label="Ne pas remplir", required=False,
                              widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))
    form_token = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_token"] = make_token()

    def clean(self):
        data = super().clean()
        if data.get("website"):
            raise forms.ValidationError("Envoi refusé.")
        try:
            raw = signing.TimestampSigner(salt=SALT).unsign(data.get("form_token") or "", max_age=60 * 60 * 6)
            age = time.time() - int(raw)
        except (signing.BadSignature, signing.SignatureExpired, ValueError):
            raise forms.ValidationError("Le formulaire a expiré. Rechargez la page puis réessayez.")
        if age < getattr(settings, "ANTISPAM_MIN_SECONDS", 3):
            raise forms.ValidationError("Envoi trop rapide. Patientez quelques secondes puis réessayez.")
        return data
