from django import forms

from .models import Membership


class ApplicationForm(forms.Form):
    motivation = forms.CharField(label="Informations complémentaires (facultatif)", required=False,
                                 widget=forms.Textarea(attrs={"rows": 3}), max_length=1000)
    accept_conditions = forms.BooleanField(label="Je certifie l'exactitude de mes informations et j'accepte les conditions d'adhésion.")


class RefuseForm(forms.Form):
    reason = forms.CharField(label="Motif du refus", widget=forms.Textarea(attrs={"rows": 3}), max_length=500)


class VerifyForm(forms.Form):
    note = forms.CharField(label="Pièces manquantes / remarques", widget=forms.Textarea(attrs={"rows": 3}), max_length=500)
