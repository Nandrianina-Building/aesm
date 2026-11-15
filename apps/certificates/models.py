from datetime import date

from django.conf import settings
from django.db import models


class Receipt(models.Model):
    number = models.CharField("numéro", max_length=30, unique=True)
    payment = models.OneToOneField("payments.Payment", on_delete=models.PROTECT, related_name="receipt")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="receipts")
    issued_at = models.DateTimeField(auto_now_add=True)
    is_void = models.BooleanField("annulé (remboursement)", default=False)

    class Meta:
        verbose_name = "reçu"
        ordering = ["-issued_at"]

    def __str__(self):
        return self.number


class Quitus(models.Model):
    VALID, REVOKED = "valid", "revoked"
    number = models.CharField("numéro", max_length=30, unique=True)
    token = models.CharField(max_length=64, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="quitus")
    due = models.ForeignKey("payments.ContributionDue", null=True, on_delete=models.PROTECT, related_name="quitus")
    payment = models.ForeignKey("payments.Payment", null=True, on_delete=models.PROTECT, related_name="quitus")
    contribution_name = models.CharField(max_length=120)
    period_label = models.CharField(max_length=60, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    issued_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, default=VALID)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    revoke_reason = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "quitus"
        verbose_name_plural = "quitus"
        ordering = ["-issued_at"]

    def __str__(self):
        return self.number

    @property
    def effective_status(self):
        if self.status == self.REVOKED:
            return "revoked"
        if self.valid_until and self.valid_until < date.today():
            return "expired"
        return "valid"

    @property
    def status_label(self):
        return {"valid": "Valide", "expired": "Expiré", "revoked": "Révoqué"}[self.effective_status]


class MemberCard(models.Model):
    VALID, REVOKED = "valid", "revoked"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="card")
    number = models.CharField(max_length=30, unique=True)
    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(max_length=10, default=VALID)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "carte de membre"

    @property
    def effective_status(self):
        u = self.user
        if self.status == self.REVOKED:
            return "revoked"
        return "valid" if u.is_active_member else "revoked"

    @property
    def status_label(self):
        return {"valid": "Valide", "revoked": "Non valide"}[self.effective_status]
