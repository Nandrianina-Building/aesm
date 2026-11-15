from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.validators import validate_image


class Event(TimeStampedModel):
    DRAFT, OPEN, CLOSED, CANCELLED = "draft", "open", "closed", "cancelled"
    STATUS_CHOICES = [(DRAFT, "Brouillon"), (OPEN, "Inscriptions ouvertes"), (CLOSED, "Inscriptions fermées"), (CANCELLED, "Annulé")]
    VIS_CHOICES = [("public", "Public"), ("members", "Membres uniquement")]

    title = models.CharField("titre", max_length=150)
    description = models.TextField("description")
    image = models.ImageField("image", upload_to="events/", blank=True, validators=[validate_image])
    category = models.CharField("catégorie", max_length=60, blank=True)
    starts_at = models.DateTimeField("date et heure")
    location = models.CharField("lieu", max_length=200)
    capacity = models.PositiveIntegerField("nombre de places")
    registration_deadline = models.DateTimeField("date limite d'inscription")
    price = models.DecimalField("prix (Ar, 0 = gratuit)", max_digits=12, decimal_places=0, default=0)
    members_only = models.BooleanField("réservé aux membres", default=True)
    invitation_only = models.BooleanField("sur invitation (réservation par l'administration)", default=False)
    visibility = models.CharField("visibilité", max_length=10, choices=VIS_CHOICES, default="public")
    conditions = models.TextField("conditions de participation", blank=True)
    status = models.CharField("statut", max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    class Meta:
        verbose_name = "événement"
        ordering = ["starts_at"]

    def __str__(self):
        return self.title

    @property
    def all_images(self):
        """Toutes les images : affiche (champ « image ») puis galerie."""
        urls = [self.image.url] if self.image else []
        urls += [i.image.url for i in self.images.all()]
        return urls

    @property
    def cover_url(self):
        if self.image:
            return self.image.url
        first = self.images.first()
        return first.image.url if first else ""

    @property
    def is_free(self):
        return self.price == 0

    @property
    def registration_open(self):
        now = timezone.now()
        return self.status == self.OPEN and now < self.registration_deadline and now < self.starts_at


class EventImage(models.Model):
    """Image supplémentaire (galerie) d'un événement : un événement peut en avoir plusieurs."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("image", upload_to="events/", validators=[validate_image])
    caption = models.CharField("légende", max_length=160, blank=True)
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        verbose_name = "image d'événement"
        ordering = ["position", "id"]

    def __str__(self):
        return f"Image de {self.event_id}"


class Reservation(TimeStampedModel):
    PENDING, CONFIRMED, CANCELLED, EXPIRED = "pending", "confirmed", "cancelled", "expired"
    STATUS_CHOICES = [(PENDING, "En attente de paiement"), (CONFIRMED, "Confirmée"), (CANCELLED, "Annulée"), (EXPIRED, "Expirée")]

    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="reservations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservations")
    status = models.CharField("statut", max_length=10, choices=STATUS_CHOICES, default=PENDING)
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=200, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "réservation"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event", "status"])]

    def __str__(self):
        return f"{self.user} -> {self.event}"


class Ticket(models.Model):
    VALID, USED, REVOKED = "valid", "used", "revoked"
    reservation = models.OneToOneField(Reservation, on_delete=models.PROTECT, related_name="ticket")
    number = models.CharField(max_length=30, unique=True)
    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(max_length=10, default=VALID)
    issued_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    @property
    def effective_status(self):
        return self.status

    def __str__(self):
        return self.number


class Attendance(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.PROTECT, related_name="attendance")
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    checked_at = models.DateTimeField(auto_now_add=True)


from apps.core.images import connect_optimizer  # noqa: E402

connect_optimizer(Event, {"image": 1600})
connect_optimizer(EventImage, {"image": 1600})
