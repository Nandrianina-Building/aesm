from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.audit.services import log
from apps.core.models import Sequence
from apps.core.utils import get_int_setting, random_token
from apps.notifications.services import notify, notify_role

from .models import Attendance, Event, Reservation, Ticket


class CapacityError(Exception):
    pass


class ReservationError(Exception):
    pass


class TicketError(Exception):
    pass


def active_filter(now=None):
    now = now or timezone.now()
    return Q(status=Reservation.CONFIRMED) | Q(status=Reservation.PENDING, expires_at__gt=now)


def taken_seats(event, exclude=None):
    qs = Reservation.objects.filter(event=event).filter(active_filter())
    if exclude is not None:
        qs = qs.exclude(pk=exclude)
    return qs.count()


def seats_left(event):
    return max(event.capacity - taken_seats(event), 0)


def _issue_ticket(res):
    ticket, _ = Ticket.objects.get_or_create(
        reservation=res, defaults={"number": f"BIL-{res.event_id}-{Sequence.next('ticket'):06d}", "token": random_token(24)})
    return ticket


@transaction.atomic
def reserve(event_id, user, *, by_admin=False):
    """Réservation atomique : le verrou sur l'événement sérialise les demandes simultanées (RG-12)."""
    event = Event.objects.select_for_update().get(pk=event_id)
    if not by_admin:
        if event.invitation_only:
            raise ReservationError("Événement sur invitation : contactez les organisateurs.")
        if not event.registration_open:
            raise ReservationError("Les inscriptions ne sont pas ouvertes pour cet événement.")
        if event.members_only and not user.is_active_member:
            raise ReservationError("Cet événement est réservé aux membres actifs.")
        if not user.is_active:
            raise ReservationError("Compte inactif.")
    if Reservation.objects.filter(event=event, user=user).filter(active_filter()).exists():
        raise ReservationError("Vous avez déjà une réservation pour cet événement.")
    if taken_seats(event) >= event.capacity:
        raise CapacityError("Plus de places disponibles.")
    res = Reservation(event=event, user=user, price_snapshot=event.price)
    if event.is_free:
        res.status = Reservation.CONFIRMED
        res.save()
        _issue_ticket(res)
        notify(user, "reservation_confirmee", "Réservation confirmée", event.title, reverse("events_member:list"))
    else:
        res.status = Reservation.PENDING
        res.expires_at = timezone.now() + timedelta(minutes=settings.RESERVATION_HOLD_MINUTES)
        res.save()
        notify(user, "reservation_en_attente", "Réservation en attente de paiement",
               f"{event.title} : payez avant {timezone.localtime(res.expires_at):%H:%M} pour garder votre place.",
               reverse("payments:pay_reservation", args=[res.pk]))
    return res


def extend_hold(res):
    hours = settings.MANUAL_PAYMENT_HOLD_HOURS
    new = timezone.now() + timedelta(hours=hours)
    if res.expires_at is None or res.expires_at < new:
        Reservation.objects.filter(pk=res.pk, status=Reservation.PENDING).update(expires_at=new)


def release_hold(res_id):
    """Paiement rejeté : la place reste brièvement réservée pour permettre un nouvel essai."""
    Reservation.objects.filter(pk=res_id, status=Reservation.PENDING).update(
        expires_at=timezone.now() + timedelta(minutes=settings.RESERVATION_HOLD_MINUTES))


@transaction.atomic
def confirm_reservation(res_id):
    event_id = Reservation.objects.values_list("event_id", flat=True).get(pk=res_id)
    event = Event.objects.select_for_update().get(pk=event_id)
    res = Reservation.objects.select_for_update().get(pk=res_id)
    if res.status == Reservation.CONFIRMED:
        return res
    if res.status == Reservation.CANCELLED:
        raise CapacityError("La réservation a été annulée.")
    held = res.status == Reservation.PENDING and res.expires_at and res.expires_at > timezone.now()
    if not held and taken_seats(event, exclude=res.pk) >= event.capacity:
        raise CapacityError("La réservation avait expiré et il n'y a plus de place : remboursement à prévoir.")
    res.status, res.expires_at = Reservation.CONFIRMED, None
    res.save()
    _issue_ticket(res)
    notify(res.user, "reservation_confirmee", "Réservation confirmée", event.title, reverse("events_member:list"))
    return res


@transaction.atomic
def cancel_reservation(res_id, by, reason="", *, enforce_deadline=True):
    res = Reservation.objects.select_for_update().select_related("event").get(pk=res_id)
    if res.status not in (Reservation.PENDING, Reservation.CONFIRMED):
        raise ReservationError("Cette réservation ne peut plus être annulée.")
    hours = get_int_setting("event_cancel_hours", 24)
    if enforce_deadline and res.event.starts_at - timezone.now() < timedelta(hours=hours):
        raise ReservationError(f"L'annulation n'est possible que jusqu'à {hours} h avant l'événement.")
    was_confirmed = res.status == Reservation.CONFIRMED
    res.status, res.cancelled_at, res.cancelled_by, res.cancel_reason = Reservation.CANCELLED, timezone.now(), by, reason[:200]
    res.save()
    Ticket.objects.filter(reservation=res, status=Ticket.VALID).update(status=Ticket.REVOKED)
    from apps.payments.models import Payment
    for p in Payment.objects.filter(reservation=res, status__in=(Payment.PENDING, Payment.VERIFYING)):
        p.status = Payment.CANCELLED
        p.save(update_fields=["status", "updated_at"])
    if was_confirmed and res.price_snapshot > 0:
        notify_role(["treasurer"], "remboursement_a_traiter", "Annulation d'une réservation payée",
                    f"{res.user.full_name} - {res.event.title} : examiner un remboursement.", reverse("gestion:payments"))
    log(by, "reservation_annulee", f"reservation:{res.pk}", new=reason)
    return res


def cancel_after_refund(res_id):
    res = Reservation.objects.select_for_update().get(pk=res_id)
    if res.status != Reservation.CANCELLED:
        res.status, res.cancelled_at, res.cancel_reason = Reservation.CANCELLED, timezone.now(), "Remboursement"
        res.save()
    Ticket.objects.filter(reservation=res, status=Ticket.VALID).update(status=Ticket.REVOKED)


def expire_reservations():
    """Libère les places des réservations non payées dont le délai est dépassé."""
    now = timezone.now()
    return Reservation.objects.filter(status=Reservation.PENDING, expires_at__lt=now).update(status=Reservation.EXPIRED)


def check_in(token, by):
    """Enregistrement de présence : un billet ne peut être validé qu'une seule fois (mise à jour atomique)."""
    with transaction.atomic():
        ticket = Ticket.objects.select_related("reservation__event", "reservation__user").filter(token=token).first()
        if ticket is None:
            raise TicketError("Billet inconnu.")
        updated = Ticket.objects.filter(pk=ticket.pk, status=Ticket.VALID).update(
            status=Ticket.USED, used_at=timezone.now(), checked_by=by)
        if updated != 1:
            ticket.refresh_from_db()
            raise TicketError("Billet déjà utilisé." if ticket.status == Ticket.USED else "Billet révoqué ou invalide.")
        Attendance.objects.create(ticket=ticket, checked_by=by)
    log(by, "billet_valide", ticket.number)
    return ticket
