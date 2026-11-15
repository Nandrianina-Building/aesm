from django.core.management.base import BaseCommand

from apps.events.services import expire_reservations


class Command(BaseCommand):
    help = "Libère les places des réservations non payées expirées (à planifier toutes les 5 min avec cron)."

    def handle(self, *args, **opts):
        self.stdout.write(f"{expire_reservations()} réservation(s) expirée(s).")
