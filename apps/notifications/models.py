from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=40)
    title = models.CharField("titre", max_length=150)
    message = models.TextField("message", blank=True)
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField("lue", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title
