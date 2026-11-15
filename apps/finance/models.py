from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.storage import internal_name, private_storage
from apps.core.validators import validate_attachment

INCOME, EXPENSE = "income", "expense"
INCOME_CATEGORIES = [("cotisations", "Cotisations"), ("evenements", "Participations aux événements"), ("dons", "Dons"),
                     ("contributions", "Contributions exceptionnelles"), ("autres_recettes", "Autres recettes")]
EXPENSE_CATEGORIES = [("organisation", "Organisation d'événements"), ("transport", "Transport"), ("fournitures", "Fournitures"),
                      ("communication", "Communication"), ("location", "Location"), ("autres_depenses", "Autres dépenses")]
CATEGORY_LABELS = dict(INCOME_CATEGORIES + EXPENSE_CATEGORIES)


def entry_proof_path(instance, filename):
    return internal_name("finance_proofs", filename)


class BudgetEntry(TimeStampedModel):
    DRAFT, PENDING, VALIDATED, REJECTED = "draft", "pending", "validated", "rejected"
    STATUS_CHOICES = [(PENDING, "En attente de validation"), (VALIDATED, "Validée"), (REJECTED, "Rejetée")]
    KIND_CHOICES = [(INCOME, "Recette"), (EXPENSE, "Dépense")]

    reference = models.CharField("référence", max_length=30, unique=True)
    kind = models.CharField("type", max_length=8, choices=KIND_CHOICES)
    category = models.CharField("catégorie", max_length=20, choices=INCOME_CATEGORIES + EXPENSE_CATEGORIES)
    description = models.CharField("description", max_length=250)
    amount = models.DecimalField("montant (Ar)", max_digits=14, decimal_places=0)  # signé : négatif pour une annulation
    date = models.DateField("date")
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    proof = models.FileField("justificatif", upload_to=entry_proof_path, storage=private_storage, blank=True,
                             validators=[validate_attachment])
    status = models.CharField("statut", max_length=10, choices=STATUS_CHOICES, default=PENDING)
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    validated_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.CharField(max_length=200, blank=True)
    reverses = models.OneToOneField("self", null=True, blank=True, on_delete=models.PROTECT, related_name="reversal")
    payment = models.ForeignKey("payments.Payment", null=True, blank=True, on_delete=models.PROTECT, related_name="budget_entries")

    class Meta:
        verbose_name = "opération financière"
        verbose_name_plural = "opérations financières"
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.reference} {self.description}"

    @property
    def is_reversed(self):
        return hasattr(self, "reversal")

    def save(self, *args, **kwargs):
        # Une opération validée est immuable : correction = nouvelle écriture d'annulation (4.11)
        if self.pk:
            old = BudgetEntry.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if old == self.VALIDATED:
                raise PermissionError("Une opération validée ne peut pas être modifiée ; créez une écriture d'annulation.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == self.VALIDATED:
            raise PermissionError("Une opération validée ne peut pas être supprimée.")
        super().delete(*args, **kwargs)


class FinancialReport(TimeStampedModel):
    DRAFT, VALIDATED, PUBLISHED = "draft", "validated", "published"
    STATUS_CHOICES = [(DRAFT, "Brouillon"), (VALIDATED, "Validé"), (PUBLISHED, "Publié")]

    title = models.CharField("titre", max_length=150)
    period_start = models.DateField("début de période")
    period_end = models.DateField("fin de période")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    snapshot = models.JSONField(default=dict)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    validated_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "rapport financier"
        ordering = ["-period_end", "-version"]
        constraints = [models.UniqueConstraint(fields=["period_start", "period_end", "version"], name="uniq_report_period_version")]

    def __str__(self):
        return f"{self.title} v{self.version}"
