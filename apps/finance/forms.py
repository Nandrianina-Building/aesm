from django import forms

from .models import EXPENSE_CATEGORIES, INCOME_CATEGORIES, BudgetEntry


class EntryForm(forms.ModelForm):
    class Meta:
        model = BudgetEntry
        fields = ["kind", "category", "description", "amount", "date", "proof"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def clean(self):
        d = super().clean()
        kind, cat = d.get("kind"), d.get("category")
        allowed = dict(INCOME_CATEGORIES if kind == "income" else EXPENSE_CATEGORIES)
        if kind and cat and cat not in allowed:
            self.add_error("category", "Catégorie incompatible avec le type d'opération.")
        if d.get("amount") is not None and d["amount"] <= 0:
            self.add_error("amount", "Le montant doit être strictement positif.")
        return d


class ReportForm(forms.Form):
    title = forms.CharField(label="Titre du rapport", max_length=150)
    period_start = forms.DateField(label="Début de période", widget=forms.DateInput(attrs={"type": "date"}))
    period_end = forms.DateField(label="Fin de période", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        d = super().clean()
        if d.get("period_start") and d.get("period_end") and d["period_end"] < d["period_start"]:
            self.add_error("period_end", "La fin doit suivre le début.")
        return d


class FilterForm(forms.Form):
    kind = forms.ChoiceField(required=False, choices=[("", "Tous types")] + BudgetEntry.KIND_CHOICES)
    status = forms.ChoiceField(required=False, choices=[("", "Tous statuts")] + BudgetEntry.STATUS_CHOICES)
    start = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
