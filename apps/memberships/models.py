from datetime import date

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Membership(TimeStampedModel):
    DRAFT, PENDING, VERIFYING, ACCEPTED, REFUSED, EXPIRED, SUSPENDED = (
        "draft", "pending", "verifying", "accepted", "refused", "expired", "suspended")
    STATUS_CHOICES = [
        (DRAFT, "Brouillon"), (PENDING, "En attente"), (VERIFYING, "En cours de vérification"),
        (ACCEPTED, "Acceptée"), (REFUSED, "Refusée"), (EXPIRED, "Expirée"), (SUSPENDED, "Suspendue"),
    ]
    # Transitions autorisées (annexe A.5)
    TRANSITIONS = {
        DRAFT: {PENDING},
        PENDING: {VERIFYING, ACCEPTED, REFUSED},
        VERIFYING: {ACCEPTED, REFUSED, PENDING},
        ACCEPTED: {SUSPENDED, EXPIRED},
        SUSPENDED: {ACCEPTED, EXPIRED},
        REFUSED: {PENDING},
        EXPIRED: set(),
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    year = models.PositiveIntegerField("année")
    status = models.CharField("statut", max_length=12, choices=STATUS_CHOICES, default=PENDING)
    submitted_at = models.DateTimeField("soumise le", null=True, blank=True)
    starts_on = models.DateField("début", null=True, blank=True)
    ends_on = models.DateField("fin", null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    refusal_reason = models.TextField("motif de refus", blank=True)
    missing_documents = models.TextField("pièces manquantes / remarques", blank=True)
    motivation = models.TextField("informations complémentaires", blank=True, max_length=1000)

    class Meta:
        verbose_name = "adhésion"
        ordering = ["-year", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "year"], name="uniq_membership_user_year")]

    def __str__(self):
        return f"{self.user} - {self.year} ({self.get_status_display()})"

    def can_go(self, new_status):
        return new_status in self.TRANSITIONS.get(self.status, set())

    @property
    def is_current(self):
        return self.status == self.ACCEPTED and (self.ends_on is None or self.ends_on >= date.today())
