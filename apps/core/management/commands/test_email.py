"""Envoie un e-mail de test : python manage.py test_email vous@gmail.com"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Vérifie que l'envoi d'e-mails (SMTP) fonctionne."

    def add_arguments(self, parser):
        parser.add_argument("destinataire")

    def handle(self, *args, **opts):
        self.stdout.write(f"Serveur : {settings.EMAIL_HOST}:{settings.EMAIL_PORT} · expéditeur : {settings.DEFAULT_FROM_EMAIL}")
        try:
            n = send_mail("AESM - e-mail de test", "Si vous lisez ceci, l'envoi d'e-mails fonctionne.",
                          settings.DEFAULT_FROM_EMAIL, [opts["destinataire"]], fail_silently=False)
        except Exception as exc:  # affichage clair pour un débutant
            raise CommandError(f"ÉCHEC de l'envoi : {type(exc).__name__}: {exc}")
        self.stdout.write(self.style.SUCCESS(f"OK : {n} e-mail envoyé à {opts['destinataire']}. Vérifiez la boîte (et les spams)."))
