from django.core.management.base import BaseCommand

from apps.events.services import expire_reservations
from apps.memberships.services import expire_memberships


class Command(BaseCommand):
    help = "Tâches périodiques : expiration des réservations et des adhésions (cron quotidien)."

    def handle(self, *args, **opts):
        self.stdout.write(f"Réservations expirées : {expire_reservations()}")
        self.stdout.write(f"Adhésions expirées : {expire_memberships()}")
