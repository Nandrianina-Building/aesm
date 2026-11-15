"""Remplace le mot de passe PUBLIC de démonstration (écrit dans le README) par un mot de passe privé.

À utiliser sur un site de TEST en ligne : sans cela, n'importe qui connaissant le README pourrait se connecter
en super administrateur. Le mot de passe est lu dans la variable DEMO_PASSWORD du fichier .env.
"""
import os

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User

PUBLIC_DEMO_PASSWORD = "DemoAESM-2026!x"


class Command(BaseCommand):
    help = "Applique DEMO_PASSWORD (du .env) à tous les comptes de démonstration."

    def handle(self, *args, **opts):
        pwd = os.environ.get("DEMO_PASSWORD", "")
        if len(pwd) < 12 or pwd == PUBLIC_DEMO_PASSWORD:
            raise CommandError("DEMO_PASSWORD doit être défini dans .env (12 caractères minimum, différent du mot de passe du README).")
        admin = User.objects.filter(matricule="ADMIN01").first()
        if admin is None or not admin.check_password(PUBLIC_DEMO_PASSWORD):
            self.stdout.write("Aucun compte de démo avec le mot de passe public : rien à faire.")
            return
        # Seuls les comptes de démo partagent EXACTEMENT ce hachage : les comptes créés ensuite par des testeurs ne sont jamais touchés.
        n = User.objects.filter(password=admin.password).update(password=make_password(pwd))
        self.stdout.write(self.style.SUCCESS(f"Mot de passe privé appliqué à {n} compte(s) de démonstration."))
