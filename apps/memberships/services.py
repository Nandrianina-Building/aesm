from datetime import date, timedelta

from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import MemberProfile, User
from apps.audit.services import log
from apps.core.models import Sequence
from apps.core.utils import get_int_setting
from apps.notifications.services import notify

from .models import Membership


class TransitionError(Exception):
    pass


def _go(m, new_status):
    if not m.can_go(new_status):
        raise TransitionError(f"Transition interdite : {m.get_status_display()} -> {new_status}")
    m.status = new_status


@transaction.atomic
def submit_application(user, motivation=""):
    year = date.today().year
    m, created = Membership.objects.select_for_update().get_or_create(
        user=user, year=year, defaults={"status": Membership.PENDING, "submitted_at": timezone.now(), "motivation": motivation})
    if not created:
        if m.status == Membership.REFUSED:  # nouvelle soumission après refus
            log(user, "adhesion_resoumise", f"membership:{m.pk}", old=m.refusal_reason)
            _go(m, Membership.PENDING)
            m.submitted_at, m.motivation, m.refusal_reason = timezone.now(), motivation, ""
            m.save()
            user.set_account_status(User.PENDING)
        else:
            raise TransitionError("Une demande existe déjà pour cette année.")
    notify_staff_new_application(m)
    return m


def notify_staff_new_application(m):
    from apps.notifications.services import notify_role
    notify_role(["secretary", "super_admin"], "adhesion_a_traiter", "Nouvelle demande d'adhésion",
                f"{m.user.full_name} ({m.user.matricule})", reverse("gestion:memberships"))


@transaction.atomic
def auto_enroll(user):
    """Inscription = adhésion immédiate : le compte devient membre actif sans validation manuelle."""
    year = date.today().year
    m, _ = Membership.objects.get_or_create(
        user=user, year=year, defaults={"status": Membership.PENDING, "submitted_at": timezone.now()})
    if m.status == Membership.PENDING:
        accept(m, None)
    return m


@transaction.atomic
def accept(m, by):
    m = Membership.objects.select_for_update().get(pk=m.pk)
    old = m.status
    _go(m, Membership.ACCEPTED)
    months = get_int_setting("membership_validity_months", 12)
    m.starts_on = date.today()
    m.ends_on = date.today() + timedelta(days=30 * months)
    m.reviewed_by, m.reviewed_at, m.refusal_reason = by, timezone.now(), ""
    m.save()
    user = m.user
    user.set_account_status(User.ACTIVE)
    if not hasattr(user, "profile"):
        number = f"AESM-{m.year}-{Sequence.next('member'):04d}"
        MemberProfile.objects.create(user=user, member_number=number, joined_year=m.year)
    from apps.certificates.services import ensure_member_card
    ensure_member_card(user)
    from apps.payments.services import generate_dues_for_user
    generate_dues_for_user(user, audiences=("all_members", "new_members"))
    log(by, "adhesion_acceptee", f"membership:{m.pk}", old=old, new=m.status)
    notify(user, "inscription_acceptee", "Bienvenue parmi les membres",
           "Votre adhésion est active. Consultez vos cotisations à régler.", reverse("payments:dues"))
    return m


@transaction.atomic
def refuse(m, by, reason):
    m = Membership.objects.select_for_update().get(pk=m.pk)
    old = m.status
    _go(m, Membership.REFUSED)
    m.refusal_reason, m.reviewed_by, m.reviewed_at = reason, by, timezone.now()
    m.save()
    if m.user.account_status == User.PENDING:
        m.user.set_account_status(User.REFUSED)
    log(by, "adhesion_refusee", f"membership:{m.pk}", old=old, new=reason)
    notify(m.user, "inscription_refusee", "Adhésion refusée", reason, reverse("memberships:apply"))
    return m


@transaction.atomic
def set_verifying(m, by, note):
    m = Membership.objects.select_for_update().get(pk=m.pk)
    _go(m, Membership.VERIFYING)
    m.missing_documents, m.reviewed_by = note, by
    m.save()
    notify(m.user, "adhesion_verification", "Adhésion en cours de vérification", note, reverse("memberships:apply"))
    return m


@transaction.atomic
def suspend(m, by, reason=""):
    m = Membership.objects.select_for_update().get(pk=m.pk)
    _go(m, Membership.SUSPENDED)
    m.save()
    m.user.set_account_status(User.SUSPENDED)
    log(by, "adhesion_suspendue", f"membership:{m.pk}", new=reason)
    notify(m.user, "adhesion_suspendue", "Adhésion suspendue", reason)
    return m


@transaction.atomic
def reactivate(m, by):
    m = Membership.objects.select_for_update().get(pk=m.pk)
    _go(m, Membership.ACCEPTED)
    m.save()
    m.user.set_account_status(User.ACTIVE)
    log(by, "adhesion_reactivee", f"membership:{m.pk}")
    return m


def expire_memberships():
    n = 0
    for m in Membership.objects.filter(status=Membership.ACCEPTED, ends_on__lt=date.today()):
        m.status = Membership.EXPIRED
        m.save(update_fields=["status"])
        n += 1
    return n
