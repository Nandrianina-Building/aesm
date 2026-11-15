from django import forms

from .models import SupportMessage, SupportTicket


class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["reason", "subject", "description", "attachment"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class MessageForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
        labels = {"body": "Votre message"}


class StaffUpdateForm(forms.Form):
    status = forms.ChoiceField(label="Statut", choices=SupportTicket.STATUS_CHOICES)
    body = forms.CharField(label="Réponse", widget=forms.Textarea(attrs={"rows": 3}), required=False, max_length=3000)
