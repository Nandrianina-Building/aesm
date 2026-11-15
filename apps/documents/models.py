from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.storage import internal_name, private_storage
from apps.core.validators import validate_pdf


def document_path(instance, filename):
    return internal_name("documents", filename)


class DocumentCategory(models.Model):
    name = models.CharField("nom", max_length=80, unique=True)

    class Meta:
        verbose_name = "catégorie de document"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Document(TimeStampedModel):
    PUBLISHED, ARCHIVED = "published", "archived"
    TYPE_CHOICES = [("cours", "Cours"), ("td", "Travaux dirigés"), ("tp", "Travaux pratiques"), ("exercice", "Exercices"),
                    ("examen", "Examens"), ("corrige", "Corrigés"), ("formation", "Supports de formation"),
                    ("rapport", "Rapports"), ("administratif", "Documents administratifs")]
    LEVEL_CHOICES = [("all", "Tous niveaux"), ("L1", "Licence 1"), ("L2", "Licence 2"), ("L3", "Licence 3"), ("M1", "Master 1"), ("M2", "Master 2")]
    VIS_CHOICES = [("public", "Public"), ("members", "Membres uniquement")]

    title = models.CharField("nom du document", max_length=180)
    description = models.TextField("description", blank=True)
    doc_type = models.CharField("type", max_length=15, choices=TYPE_CHOICES, default="cours")
    category = models.ForeignKey(DocumentCategory, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="catégorie")
    level = models.CharField("niveau", max_length=5, choices=LEVEL_CHOICES, default="all")
    file = models.FileField("fichier PDF", upload_to=document_path, storage=private_storage, validators=[validate_pdf])
    visibility = models.CharField("visibilité", max_length=10, choices=VIS_CHOICES, default="members")
    status = models.CharField("statut", max_length=10, default=PUBLISHED, choices=[(PUBLISHED, "Publié"), (ARCHIVED, "Archivé")])
    download_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        verbose_name = "document"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
