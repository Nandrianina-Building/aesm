from datetime import date

from django.db import transaction
from django.utils import timezone

from apps.audit.services import log
from apps.core.models import Sequence
from apps.core.utils import random_token

from .models import MemberCard, Quitus, Receipt


def issue_receipt(payment):
    receipt, _ = Receipt.objects.get_or_create(
        payment=payment, defaults={"user": payment.user, "number": f"REC-{date.today().year}-{Sequence.next('receipt'):06d}"})
    return receipt


def issue_quitus(due, payment):
    existing = Quitus.objects.filter(due=due, status=Quitus.VALID).first()
    if existing:
        return existing
    c = due.contribution
    return Quitus.objects.create(
        number=f"QUI-{date.today().year}-{Sequence.next('quitus'):06d}", token=random_token(24), user=due.user, due=due,
        payment=payment, contribution_name=c.name, period_label=c.period_label, amount=due.amount)


@transaction.atomic
def revoke_quitus(quitus, by, reason):
    q = Quitus.objects.select_for_update().get(pk=quitus.pk)
    if q.status == Quitus.REVOKED:
        return q
    q.status, q.revoked_at, q.revoked_by, q.revoke_reason = Quitus.REVOKED, timezone.now(), by, reason[:250]
    q.save()
    log(by, "revocation_quitus", q.number, new=reason)
    return q


def revoke_for_payment(payment, by, reason):
    for q in Quitus.objects.filter(payment=payment, status=Quitus.VALID):
        revoke_quitus(q, by, reason)
    Receipt.objects.filter(payment=payment).update(is_void=True)


def ensure_member_card(user):
    card = MemberCard.objects.filter(user=user).first()
    if card:
        return card
    return MemberCard.objects.create(user=user, number=f"CARTE-{Sequence.next('card'):06d}", token=random_token(24))
