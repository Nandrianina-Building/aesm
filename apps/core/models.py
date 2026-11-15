from django.db import models, transaction
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        abstract = True


class SiteSetting(models.Model):
    """Paramètres modifiables depuis l'administration (clé / valeur texte)."""
    key = models.CharField(max_length=60, unique=True)
    value = models.TextField(blank=True)
    label = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "paramètre"
        ordering = ["key"]

    def __str__(self):
        return self.key


class Sequence(models.Model):
    """Compteur atomique pour générer des numéros uniques (reçus, quitus, références)."""
    name = models.CharField(max_length=40, unique=True)
    value = models.PositiveBigIntegerField(default=0)

    @classmethod
    def next(cls, name):
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(name=name)
            seq.value += 1
            seq.save(update_fields=["value"])
            return seq.value


class Officer(TimeStampedModel):
    """Responsable (membre du bureau) - page publique."""
    last_name = models.CharField("nom", max_length=80)
    first_name = models.CharField("prénom", max_length=80)
    user = models.ForeignKey("accounts.User", verbose_name="compte membre", null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="officer_terms")
    function = models.CharField("fonction", max_length=120)
    mandate_start = models.DateField("début du mandat")
    mandate_end = models.DateField("fin du mandat", null=True, blank=True)
    photo = models.ImageField("photo", upload_to="officers/", blank=True)
    description = models.TextField("description", blank=True)
    is_archived = models.BooleanField("mandat archivé", default=False)

    class Meta:
        verbose_name = "responsable"
        ordering = ["is_archived", "-mandate_start", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.function}"


class ContactMessage(TimeStampedModel):
    name = models.CharField("nom", max_length=120)
    email = models.EmailField("e-mail")
    subject = models.CharField("objet", max_length=150)
    message = models.TextField("message", max_length=4000)
    is_handled = models.BooleanField("traité", default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.subject}"


from apps.core.images import connect_optimizer  # noqa: E402

connect_optimizer(Officer, {"photo": 900})
