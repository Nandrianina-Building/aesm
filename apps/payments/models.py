from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.storage import internal_name, private_storage
from apps.core.validators import validate_attachment


def proof_path(instance, filename):
    return internal_name("payment_proofs", filename)


class ContributionType(TimeStampedModel):
    ALL, NEW, SELECTED = "all_members", "new_members", "selected"
    AUDIENCE_CHOICES = [(ALL, "Tous les membres actifs"), (NEW, "Nouveaux membres à l'adhésion"), (SELECTED, "Membres sélectionnés")]
    CATEGORY_CHOICES = [("adhesion", "Adhésion"), ("speciale", "Cotisation spéciale"), ("exceptionnelle", "Participation exceptionnelle")]

    name = models.CharField("nom", max_length=120)
    description = models.TextField("description", blank=True)
    amount = models.DecimalField("montant (Ar)", max_digits=12, decimal_places=0)
    period_label = models.CharField("année / période concernée", max_length=60, blank=True)
    start_date = models.DateField("date de début")
    end_date = models.DateField("date limite de paiement")
    category = models.CharField("catégorie", max_length=20, choices=CATEGORY_CHOICES, default="adhesion")
    audience = models.CharField("public concerné", max_length=12, choices=AUDIENCE_CHOICES, default=ALL)
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="targeted_contributions")
    is_active = models.BooleanField("active", default=True)
    issue_quitus = models.BooleanField("délivrer un quitus après paiement", default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "type de cotisation"
        ordering = ["-start_date", "name"]

    def __str__(self):
        return f"{self.name} ({int(self.amount)} Ar)"

    @property
    def is_billed(self):
        return self.pk is not None and self.dues.exists()


class ContributionDue(TimeStampedModel):
    UNPAID, PAID, WAIVED = "unpaid", "paid", "waived"
    STATUS_CHOICES = [(UNPAID, "À payer"), (PAID, "Payée"), (WAIVED, "Exonérée")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="dues")
    contribution = models.ForeignKey(ContributionType, on_delete=models.PROTECT, related_name="dues")
    amount = models.DecimalField("montant facturé (Ar)", max_digits=12, decimal_places=0)  # copie figée (RG-06)
    due_date = models.DateField("date limite")
    status = models.CharField("statut", max_length=8, choices=STATUS_CHOICES, default=UNPAID)
    paid_at = models.DateTimeField(null=True, blank=True)
    waiver_reason = models.CharField("motif d'exonération", max_length=200, blank=True)
    waived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "cotisation exigible"
        ordering = ["due_date"]
        constraints = [models.UniqueConstraint(fields=["user", "contribution"], name="uniq_due_user_contribution")]

    def __str__(self):
        return f"{self.user} - {self.contribution.name}"


class Payment(TimeStampedModel):
    CREATED, PENDING, PROCESSING, CONFIRMED, FAILED, CANCELLED, REFUNDED, VERIFYING = (
        "created", "pending", "processing", "confirmed", "failed", "cancelled", "refunded", "verifying")
    STATUS_CHOICES = [
        (CREATED, "Créée"), (PENDING, "En attente"), (PROCESSING, "En cours"), (CONFIRMED, "Confirmée"),
        (FAILED, "Échouée"), (CANCELLED, "Annulée"), (REFUNDED, "Remboursée"), (VERIFYING, "En cours de vérification"),
    ]
    TRANSITIONS = {
        CREATED: {PENDING, CANCELLED, FAILED},
        PENDING: {PROCESSING, VERIFYING, CONFIRMED, FAILED, CANCELLED},
        PROCESSING: {CONFIRMED, FAILED, VERIFYING},
        VERIFYING: {CONFIRMED, FAILED, CANCELLED},
        CONFIRMED: {REFUNDED},
        FAILED: set(), CANCELLED: set(), REFUNDED: set(),
    }
    METHOD_CHOICES = [("simulation", "Paiement simulé"), ("tokipay", "Tokipay (MVola / Orange Money)")]
    OPEN_STATUSES = (CREATED, PENDING, PROCESSING, VERIFYING)

    reference = models.CharField("référence", max_length=30, unique=True)
    idempotency_key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    due = models.ForeignKey(ContributionDue, null=True, blank=True, on_delete=models.PROTECT, related_name="payments")
    reservation = models.ForeignKey("events.Reservation", null=True, blank=True, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField("montant", max_digits=12, decimal_places=0)
    currency = models.CharField("devise", max_length=3, default="MGA")
    method = models.CharField("moyen de paiement", max_length=12, choices=METHOD_CHOICES)
    payer_phone = models.CharField("numéro payeur", max_length=20, blank=True)
    external_reference = models.CharField("référence de transaction", max_length=60, null=True, blank=True)
    proof = models.FileField("preuve", upload_to=proof_path, storage=private_storage, blank=True, validators=[validate_attachment])
    status = models.CharField("statut", max_length=12, choices=STATUS_CHOICES, default=CREATED)
    failure_reason = models.CharField("motif d'échec", max_length=250, blank=True)
    confirmed_at = models.DateTimeField("confirmée le", null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "paiement"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["method", "external_reference"], name="uniq_payment_method_extref")]

    def __str__(self):
        return self.reference

    @property
    def object_label(self):
        if self.due_id:
            return self.due.contribution.name
        if self.reservation_id:
            return f"Événement : {self.reservation.event.title}"
        return "-"

    @property
    def expected_amount(self):
        if self.due_id:
            return self.due.amount
        if self.reservation_id:
            return self.reservation.price_snapshot
        return None


class PaymentAttempt(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="attempts")
    provider = models.CharField(max_length=20)
    request_summary = models.TextField(blank=True)
    response_summary = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentProviderEvent(models.Model):
    provider = models.CharField(max_length=20)
    event_id = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    signature_valid = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    result = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["provider", "event_id"], name="uniq_provider_event")]
