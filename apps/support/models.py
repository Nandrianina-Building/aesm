from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.storage import internal_name, private_storage
from apps.core.validators import validate_attachment


def support_path(instance, filename):
    return internal_name("support", filename)


class SupportTicket(TimeStampedModel):
    PENDING, IN_PROGRESS, RESOLVED, REJECTED, CLOSED = "pending", "in_progress", "resolved", "rejected", "closed"
    STATUS_CHOICES = [(PENDING, "En attente"), (IN_PROGRESS, "En cours"), (RESOLVED, "Résolu"), (REJECTED, "Rejeté"), (CLOSED, "Fermé")]
    REASON_CHOICES = [("paiement", "Paiement non confirmé"), ("infos", "Erreur sur les informations personnelles"),
                      ("quitus", "Problème de quitus"), ("reservation", "Problème de réservation"),
                      ("connexion", "Problème de connexion"), ("autre", "Autre demande")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets")
    reason = models.CharField("motif", max_length=20, choices=REASON_CHOICES)
    subject = models.CharField("objet", max_length=150)
    description = models.TextField("description du problème", max_length=3000)
    attachment = models.FileField("pièce justificative", upload_to=support_path, storage=private_storage, blank=True,
                                  validators=[validate_attachment])
    status = models.CharField("statut", max_length=12, choices=STATUS_CHOICES, default=PENDING)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")

    class Meta:
        verbose_name = "réclamation"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.subject}"

    @property
    def is_open(self):
        return self.status in (self.PENDING, self.IN_PROGRESS)


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    body = models.TextField(max_length=3000)
    from_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
