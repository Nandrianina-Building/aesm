from django import forms

from apps.core.validators import validate_attachment

from .models import ContributionType, Payment


class PaymentForm(forms.Form):
    """Le montant et le moyen de paiement sont imposés par le serveur ; seule la clé anti-doublon voyage."""
    idempotency_key = forms.CharField(widget=forms.HiddenInput)


class ContributionForm(forms.ModelForm):
    class Meta:
        model = ContributionType
        fields = ["name", "description", "amount", "period_label", "start_date", "end_date", "category",
                  "audience", "target_users", "is_active", "issue_quitus"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 3}),
            "target_users": forms.SelectMultiple(attrs={"size": 8}),
        }

    LOCKED_WHEN_BILLED = ["amount", "period_label", "start_date", "category", "audience", "target_users", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_users"].queryset = self.fields["target_users"].queryset.filter(account_status="active")
        if self.instance.pk and self.instance.is_billed:  # modifiable uniquement si non encore facturée
            for f in self.LOCKED_WHEN_BILLED:
                self.fields[f].disabled = True

    def clean(self):
        data = super().clean()
        if data.get("start_date") and data.get("end_date") and data["end_date"] < data["start_date"]:
            self.add_error("end_date", "La date limite doit suivre la date de début.")
        if data.get("amount") is not None and data["amount"] <= 0:
            self.add_error("amount", "Le montant doit être positif.")
        return data


class WaiveForm(forms.Form):
    reason = forms.CharField(label="Motif de l'exonération", max_length=200)


class VerifyPaymentForm(forms.Form):
    received_amount = forms.DecimalField(label="Montant effectivement reçu (Ar)", max_digits=12, decimal_places=0)


class ReasonForm(forms.Form):
    reason = forms.CharField(label="Motif", max_length=250)
