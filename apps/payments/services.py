import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from apps.audit.services import log
from apps.core.models import Sequence
from apps.notifications.services import notify, notify_role

from .models import ContributionDue, ContributionType, Payment, PaymentAttempt
from .providers import ProviderNotConfigured, get_provider


class PaymentError(Exception):
    pass


def new_reference():
    return f"PAY-{date.today().year}-{Sequence.next('payment'):06d}"


def transition(payment, new_status):
    if new_status not in Payment.TRANSITIONS.get(payment.status, set()):
        raise PaymentError(f"Transition interdite : {payment.get_status_display()} -> {new_status}")
    payment.status = new_status


# ---------------------------------------------------------------- cotisations
def _create_due(user, c):
    due, created = ContributionDue.objects.get_or_create(
        user=user, contribution=c, defaults={"amount": c.amount, "due_date": c.end_date})
    return due, created


def generate_dues_for_contribution(c):
    """Idempotent : ne facture jamais deux fois la même cotisation (unicité user+cotisation)."""
    from apps.accounts.models import User
    if not c.is_active:
        return 0
    if c.audience == ContributionType.SELECTED:
        users = c.target_users.filter(account_status=User.ACTIVE)
    elif c.audience == ContributionType.ALL:
        users = User.objects.filter(account_status=User.ACTIVE)
    else:
        users = User.objects.none()
    n = 0
    for u in users:
        _, created = _create_due(u, c)
        if created:
            n += 1
            notify(u, "cotisation_creee", "Nouvelle cotisation", f"{c.name} - {int(c.amount)} Ar", reverse("payments:dues"))
    return n


def generate_dues_for_user(user, audiences=("all_members", "new_members")):
    today = date.today()
    for c in ContributionType.objects.filter(is_active=True, audience__in=audiences, start_date__lte=today, end_date__gte=today):
        _create_due(user, c)


@transaction.atomic
def waive_due(due, by, reason):
    due = ContributionDue.objects.select_for_update().get(pk=due.pk)
    if due.status != ContributionDue.UNPAID:
        raise PaymentError("Seule une cotisation à payer peut être exonérée.")
    if not reason.strip():
        raise PaymentError("Un motif est obligatoire.")
    due.status, due.waiver_reason, due.waived_by = ContributionDue.WAIVED, reason, by
    due.save()
    log(by, "exoneration_cotisation", f"due:{due.pk}", new=reason)
    return due


# ---------------------------------------------------------------- création
def _open_payment_exists(**filters):
    return Payment.objects.filter(status__in=Payment.OPEN_STATUSES, **filters).exists()


@transaction.atomic
def create_payment(user, *, due=None, reservation=None, method, external_reference="", payer_phone="",
                   proof=None, idempotency_key):
    """Crée une transaction. Le montant vient TOUJOURS du serveur (jamais du navigateur)."""
    if (due is None) == (reservation is None):
        raise PaymentError("Cible de paiement invalide.")
    if not user.is_active_member:
        raise PaymentError("Seuls les membres actifs peuvent payer.")
    external_reference = (external_reference or "").strip() or None
    if method == "simulation" and not external_reference:
        external_reference = f"SIM-{uuid.uuid4().hex[:12].upper()}"
    existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing, False  # double soumission : on renvoie la transaction déjà créée
    if due is not None:
        due = ContributionDue.objects.select_for_update().get(pk=due.pk, user=user)
        if due.status != ContributionDue.UNPAID:
            raise PaymentError("Cette cotisation est déjà réglée ou exonérée.")
        if _open_payment_exists(due=due):
            raise PaymentError("Un paiement est déjà en cours pour cette cotisation.")
        amount, target = due.amount, {"due": due}
    else:
        from apps.events.models import Reservation
        reservation = Reservation.objects.select_for_update().get(pk=reservation.pk, user=user)
        if reservation.status not in (Reservation.PENDING,):
            raise PaymentError("Cette réservation ne peut pas être payée.")
        if _open_payment_exists(reservation=reservation):
            raise PaymentError("Un paiement est déjà en cours pour cette réservation.")
        amount, target = reservation.price_snapshot, {"reservation": reservation}
    try:
        with transaction.atomic():
            payment = Payment.objects.create(
                reference=new_reference(), idempotency_key=idempotency_key, user=user, amount=amount,
                currency=settings.CURRENCY, method=method, payer_phone=payer_phone,
                external_reference=external_reference, **target)
    except IntegrityError:
        raise PaymentError("Cette référence de transaction a déjà été utilisée.")
    if proof:
        payment.proof = proof
        payment.save(update_fields=["proof"])
    provider = get_provider(method)
    try:
        result = provider.initiate(payment)
    except ProviderNotConfigured as exc:
        raise PaymentError(str(exc))
    PaymentAttempt.objects.create(payment=payment, provider=method, request_summary=f"montant={amount}",
                                  response_summary=result.message or result.status, success=result.status != "failed")
    transition(payment, Payment.PENDING)
    payment.save(update_fields=["status", "updated_at"])
    if provider.manual:
        # vérification humaine : on retient la place plus longtemps et on prévient le trésorier
        if reservation is not None:
            from apps.events.services import extend_hold
            extend_hold(reservation)
        notify_role(["treasurer"], "paiement_a_verifier", "Paiement à vérifier", f"{payment.reference} - {int(amount)} Ar",
                    reverse("gestion:payments"))
    log(user, "paiement_cree", payment.reference, new=f"{amount} {method}")
    payment.redirect_url = result.redirect_url
    return payment, True


# ---------------------------------------------------------------- confirmation
@transaction.atomic
def confirm_payment(payment_id, by=None, received_amount=None, source="manuel"):
    """Confirmation fiable côté serveur. Idempotente : une 2e confirmation ne fait rien."""
    p = Payment.objects.select_for_update().get(pk=payment_id)
    if p.status == Payment.CONFIRMED:
        return p
    expected = p.expected_amount
    if expected is None or Decimal(p.amount) != Decimal(expected):
        raise PaymentError("Le montant de la transaction ne correspond pas au montant attendu.")
    if received_amount is not None and Decimal(received_amount) != Decimal(p.amount):
        raise PaymentError("Le montant reçu ne correspond pas au montant attendu : paiement non confirmé.")
    if p.status not in (Payment.PENDING, Payment.PROCESSING, Payment.VERIFYING):
        raise PaymentError(f"Un paiement « {p.get_status_display()} » ne peut pas être confirmé.")

    if p.due_id:
        due = ContributionDue.objects.select_for_update().get(pk=p.due_id)
        if due.status != ContributionDue.UNPAID:
            raise PaymentError("Cotisation déjà réglée : risque de double paiement, vérification manuelle requise.")
    elif p.reservation_id:
        from apps.events.services import CapacityError, confirm_reservation
        try:
            confirm_reservation(p.reservation_id)
        except CapacityError as exc:
            p.failure_reason = str(exc)[:250]
            transition(p, Payment.VERIFYING)
            p.save()
            notify_role(["treasurer", "event_manager"], "paiement_a_verifier", "Paiement sans place disponible",
                        f"{p.reference} : {exc}", reverse("gestion:payments"))
            return p

    transition(p, Payment.CONFIRMED)
    p.confirmed_at, p.verified_by, p.failure_reason = timezone.now(), by, ""
    p.save()

    from apps.certificates.services import issue_quitus, issue_receipt
    from apps.finance.services import record_income
    issue_receipt(p)
    record_income(p)
    if p.due_id:
        due.status, due.paid_at = ContributionDue.PAID, p.confirmed_at
        due.save()
        if due.contribution.issue_quitus:
            issue_quitus(due, p)
            notify(p.user, "quitus_disponible", "Quitus disponible", due.contribution.name, reverse("certificates:quitus_list"))
    log(by, "validation_paiement", p.reference, new=f"{p.amount} ({source})")
    notify(p.user, "paiement_confirme", "Paiement confirmé", f"{p.reference} - {int(p.amount)} Ar", reverse("payments:detail", args=[p.reference]))
    return p


@transaction.atomic
def reject_payment(payment_id, by, reason):
    p = Payment.objects.select_for_update().get(pk=payment_id)
    if not reason.strip():
        raise PaymentError("Un motif est obligatoire.")
    transition(p, Payment.FAILED)
    p.failure_reason, p.verified_by = reason[:250], by
    p.save()
    if p.reservation_id:
        from apps.events.services import release_hold
        release_hold(p.reservation_id)
    log(by, "paiement_rejete", p.reference, new=reason)
    notify(p.user, "paiement_echoue", "Paiement non validé", reason, reverse("payments:detail", args=[p.reference]))
    return p


@transaction.atomic
def refund_payment(payment_id, by, reason):
    p = Payment.objects.select_for_update().get(pk=payment_id)
    if not reason.strip():
        raise PaymentError("Un motif est obligatoire.")
    transition(p, Payment.REFUNDED)
    p.failure_reason = reason[:250]
    p.save()
    from apps.certificates.services import revoke_for_payment
    from apps.finance.services import reverse_income
    reverse_income(p, by, reason)
    revoke_for_payment(p, by, f"Remboursement : {reason}")
    if p.due_id:
        ContributionDue.objects.filter(pk=p.due_id).update(status=ContributionDue.UNPAID, paid_at=None)
    if p.reservation_id:
        from apps.events.services import cancel_after_refund
        cancel_after_refund(p.reservation_id)
    log(by, "remboursement_paiement", p.reference, new=reason)
    notify(p.user, "paiement_rembourse", "Paiement remboursé", reason)
    return p


# ---------------------------------------------------------------- simulation
@transaction.atomic
def simulate_outcome(payment_id, user, outcome):
    """Résultat d'un paiement simulé (success | fail | cancel). Jamais disponible hors simulation."""
    if not settings.PAYMENT_SIMULATION_ENABLED:
        raise PaymentError("La simulation de paiement est désactivée.")
    p = Payment.objects.select_for_update().get(pk=payment_id, user=user, method="simulation")  # anti-IDOR
    if p.status != Payment.PENDING:
        raise PaymentError("Ce paiement simulé n'est plus en attente.")
    if outcome == "success":
        return confirm_payment(p.pk, by=None, source="simulation")
    if outcome == "fail":
        return reject_payment(p.pk, None, "Échec simulé")
    if outcome == "cancel":
        transition(p, Payment.CANCELLED)
        p.failure_reason = "Annulé par le membre"
        p.save()
        if p.reservation_id:
            from apps.events.services import release_hold
            release_hold(p.reservation_id)
        log(user, "paiement_annule", p.reference)
        return p
    raise PaymentError("Résultat de simulation inconnu.")
