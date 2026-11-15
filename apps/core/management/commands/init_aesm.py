"""Initialise les rôles, paramètres et catégories par défaut. `--demo` ajoute des données d'exemple."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.core.models import Officer, SiteSetting
from apps.core.permissions import ROLE_CHOICES
from apps.core.utils import DEFAULT_SETTINGS
from apps.documents.models import DocumentCategory
from apps.publications.models import PublicationCategory


class Command(BaseCommand):
    help = "Crée les rôles, paramètres et catégories par défaut."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Ajoute des comptes et contenus de démonstration (NE PAS utiliser en production).")

    def handle(self, *args, **opts):
        for code, name in ROLE_CHOICES:
            Role.objects.get_or_create(code=code, defaults={"name": name})
        for key, (value, label) in DEFAULT_SETTINGS.items():
            SiteSetting.objects.get_or_create(key=key, defaults={"value": value, "label": label})
        for n in ["Cours", "Travaux dirigés", "Examens", "Méthodologie", "Administratif"]:
            DocumentCategory.objects.get_or_create(name=n)
        for n in ["Vie associative", "Pédagogie", "Événements", "Administration"]:
            PublicationCategory.objects.get_or_create(name=n)
        self.stdout.write(self.style.SUCCESS("Rôles, paramètres et catégories initialisés."))
        if opts["demo"]:
            self._demo()

    def _demo(self):
        from django.core.management import call_command
        call_command("seed_demo")
