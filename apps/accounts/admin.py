from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from .models import MemberProfile, Role, User


class UserAdminChangeForm(UserChangeForm):
    """Affiche la photo actuelle sous le champ (via la vue protégée) : le FileInput seul affiche
    toujours « Aucun fichier sélectionné », même quand la photo est bien enregistrée."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get("photo")
        if field is not None and self.instance and self.instance.pk and self.instance.photo:
            url = reverse("accounts:photo", args=[self.instance.public_id])
            field.help_text = format_html(
                '<br><img src="{}" alt="Photo actuelle" style="max-height:110px;border-radius:8px;margin:.4rem 0;display:block">'
                "Photo actuelle enregistrée. Choisissez un nouveau fichier uniquement pour la remplacer.", url)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    ordering = ("last_name",)
    list_display = ("matricule", "last_name", "first_name", "account_status", "is_active")
    list_filter = ("account_status", "roles")
    search_fields = ("matricule", "last_name", "first_name", "email", "phone")
    fieldsets = (
        (None, {"fields": ("matricule", "password")}),
        ("Identité", {"fields": ("first_name", "last_name", "email", "phone", "sex", "photo")}),
        ("Statut", {"fields": ("account_status", "email_verified", "is_active", "roles", "is_staff", "is_superuser")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("matricule", "first_name", "last_name", "password1", "password2")}),)
    filter_horizontal = ("roles",)
    formfield_overrides = {models.ImageField: {"widget": forms.FileInput}}  # photo privée : pas d'URL générée par le widget


admin.site.register(Role)
admin.site.register(MemberProfile)
