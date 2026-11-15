from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import TimeStampedModel
from apps.core.validators import validate_image


class PublicationCategory(models.Model):
    name = models.CharField("nom", max_length=80, unique=True)
    image = models.ImageField("photo de la catégorie", upload_to="categories/", blank=True, validators=[validate_image],
                              help_text="Affichée dans la barre des catégories. Sans photo, l'image de la dernière actualité de la catégorie est utilisée.")

    class Meta:
        verbose_name = "catégorie de publication"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Publication(TimeStampedModel):
    DRAFT, SCHEDULED, PUBLISHED, ARCHIVED = "draft", "scheduled", "published", "archived"
    STATUS_CHOICES = [(DRAFT, "Brouillon"), (SCHEDULED, "Programmée"), (PUBLISHED, "Publiée"), (ARCHIVED, "Archivée")]
    TYPE_CHOICES = [("actualite", "Actualité"), ("annonce", "Annonce officielle"), ("communique", "Communiqué"),
                    ("pedagogique", "Information pédagogique"), ("avis", "Avis important"), ("evenement", "Annonce d'événement"),
                    ("appel", "Appel à participation"), ("administrative", "Information administrative")]
    VIS_CHOICES = [("public", "Publique"), ("members", "Membres uniquement")]

    title = models.CharField("titre", max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    kind = models.CharField("type", max_length=20, choices=TYPE_CHOICES, default="actualite")
    category = models.ForeignKey(PublicationCategory, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="catégorie")
    summary = models.CharField("résumé", max_length=300)
    body = models.TextField("contenu")
    image = models.ImageField("image", upload_to="publications/", blank=True, validators=[validate_image])
    visibility = models.CharField("visibilité", max_length=10, choices=VIS_CHOICES, default="public")
    status = models.CharField("statut", max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    publish_at = models.DateTimeField("date de publication", null=True, blank=True)
    pinned = models.BooleanField("épinglée", default=False)
    comments_enabled = models.BooleanField("commentaires activés", default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "publication"
        ordering = ["-pinned", "-publish_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:170] or "publication"
            slug, n = base, 1
            while Publication.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def all_images(self):
        """Toutes les images : couverture (champ « image ») puis galerie."""
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
    def is_live(self):
        if self.status == self.PUBLISHED:
            return self.publish_at is None or self.publish_at <= timezone.now()
        if self.status == self.SCHEDULED:
            return self.publish_at is not None and self.publish_at <= timezone.now()  # programmée -> visible à l'échéance
        return False


class PublicationImage(models.Model):
    """Image supplémentaire (galerie) d'une publication : une actualité peut en avoir plusieurs."""
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("image", upload_to="publications/", validators=[validate_image])
    caption = models.CharField("légende", max_length=160, blank=True)
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        verbose_name = "image de publication"
        ordering = ["position", "id"]

    def __str__(self):
        return f"Image de {self.publication_id}"


class Comment(TimeStampedModel):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField(max_length=1000)
    is_hidden = models.BooleanField("masqué", default=False)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]


class Like(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["publication", "user"], name="uniq_like")]


class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["comment", "user"], name="uniq_comment_report")]


from apps.core.images import connect_optimizer  # noqa: E402

connect_optimizer(Publication, {"image": 1600})
connect_optimizer(PublicationCategory, {"image": 400})
connect_optimizer(PublicationImage, {"image": 1600})
