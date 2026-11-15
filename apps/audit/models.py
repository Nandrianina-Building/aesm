from django.conf import settings
from django.db import models


class ImmutableQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise PermissionError("Le journal d'audit est en ajout seul.")

    def delete(self):
        raise PermissionError("Le journal d'audit est en ajout seul.")


class AuditLog(models.Model):
    """Journal d'audit en ajout seul (7.14). Aucune modification ni suppression possible via l'ORM."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    user_label = models.CharField(max_length=150, blank=True)
    action = models.CharField("action", max_length=80, db_index=True)
    resource = models.CharField("ressource", max_length=200, blank=True)
    old_value = models.TextField("ancienne valeur", blank=True)
    new_value = models.TextField("nouvelle valeur", blank=True)
    result = models.CharField("résultat", max_length=20, default="succès")
    ip_address = models.GenericIPAddressField("adresse IP", null=True, blank=True)
    created_at = models.DateTimeField("date", auto_now_add=True, db_index=True)

    objects = ImmutableQuerySet.as_manager()

    class Meta:
        verbose_name = "entrée du journal"
        verbose_name_plural = "journal d'audit"
        ordering = ["-created_at", "-id"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("Le journal d'audit est en ajout seul.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Le journal d'audit est en ajout seul.")

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action}"
