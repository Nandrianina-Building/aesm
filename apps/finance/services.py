from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit.services import log
from apps.core.models import Sequence
from apps.core.utils import get_setting

from .models import CATEGORY_LABELS, EXPENSE, INCOME, BudgetEntry, FinancialReport


class FinanceError(Exception):
    pass


def new_reference():
    return f"FIN-{date.today().year}-{Sequence.next('finance'):06d}"


def validated():
    return BudgetEntry.objects.filter(status=BudgetEntry.VALIDATED)


@transaction.atomic
def record_income(payment):
    """Écriture automatique et validée pour un paiement confirmé."""
    existing = BudgetEntry.objects.filter(payment=payment, reverses__isnull=True).first()
    if existing:
        return existing
    category = "cotisations" if payment.due_id else "evenements"
    return BudgetEntry.objects.create(
        reference=new_reference(), kind=INCOME, category=category, description=f"{payment.object_label} ({payment.reference})",
        amount=payment.amount, date=date.today(), responsible=payment.verified_by, status=BudgetEntry.VALIDATED,
        validated_by=payment.verified_by, validated_at=timezone.now(), payment=payment)


@transaction.atomic
def reverse_entry(entry, by, reason):
    entry = BudgetEntry.objects.select_for_update().get(pk=entry.pk)
    if entry.status != BudgetEntry.VALIDATED:
        raise FinanceError("Seule une opération validée peut être annulée par écriture inverse.")
    if entry.reverses_id:
        raise FinanceError("Une écriture d'annulation ne peut pas être annulée.")
    if hasattr(entry, "reversal"):
        raise FinanceError("Cette opération a déjà été annulée.")
    if not reason.strip():
        raise FinanceError("Un motif est obligatoire.")
    rev = BudgetEntry.objects.create(
        reference=new_reference(), kind=entry.kind, category=entry.category, description=f"ANNULATION {entry.reference} : {reason}"[:250],
        amount=-entry.amount, date=date.today(), responsible=by, status=BudgetEntry.VALIDATED, validated_by=by,
        validated_at=timezone.now(), reverses=entry, payment=entry.payment)
    log(by, "ecriture_annulee", entry.reference, new=reason)
    return rev


def reverse_income(payment, by, reason):
    entry = BudgetEntry.objects.filter(payment=payment, reverses__isnull=True).first()
    if entry and not hasattr(entry, "reversal"):
        reverse_entry(entry, by, reason)


@transaction.atomic
def validate_entry(entry, by):
    entry = BudgetEntry.objects.select_for_update().get(pk=entry.pk)
    if entry.status != BudgetEntry.PENDING:
        raise FinanceError("Seule une opération en attente peut être validée.")
    entry.status, entry.validated_by, entry.validated_at = BudgetEntry.VALIDATED, by, timezone.now()
    entry.save()
    log(by, "ecriture_validee", entry.reference, new=entry.amount)
    return entry


@transaction.atomic
def reject_entry(entry, by, reason):
    entry = BudgetEntry.objects.select_for_update().get(pk=entry.pk)
    if entry.status != BudgetEntry.PENDING:
        raise FinanceError("Seule une opération en attente peut être rejetée.")
    entry.status, entry.reject_reason, entry.validated_by = BudgetEntry.REJECTED, reason[:200], by
    entry.save()
    log(by, "ecriture_rejetee", entry.reference, new=reason)
    return entry


def _by_category(qs, kind):
    rows = qs.filter(kind=kind).values("category").annotate(total=Sum("amount")).order_by("-total")
    return [[CATEGORY_LABELS.get(r["category"], r["category"]), int(r["total"] or 0)] for r in rows]


def summary(start=None, end=None):
    """Indicateurs calculés UNIQUEMENT à partir des écritures validées."""
    opening = Decimal(get_setting("opening_balance", "0") or 0)
    base = validated()
    if start:
        before = base.filter(date__lt=start)
        opening += (before.filter(kind=INCOME).aggregate(s=Sum("amount"))["s"] or 0) - (before.filter(kind=EXPENSE).aggregate(s=Sum("amount"))["s"] or 0)
    qs = base
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    income = qs.filter(kind=INCOME).aggregate(s=Sum("amount"))["s"] or 0
    expense = qs.filter(kind=EXPENSE).aggregate(s=Sum("amount"))["s"] or 0
    return {
        "opening": int(opening), "income": int(income), "expense": int(expense), "closing": int(opening + income - expense),
        "income_by_category": _by_category(qs, INCOME), "expense_by_category": _by_category(qs, EXPENSE),
    }


def build_snapshot(start, end):
    data = summary(start, end)
    entries = validated().filter(date__gte=start, date__lte=end).order_by("date", "id")
    data["entries"] = [{"reference": e.reference, "date": e.date.isoformat(), "kind": e.get_kind_display(),
                        "category": CATEGORY_LABELS.get(e.category, e.category), "description": e.description,
                        "amount": int(e.amount)} for e in entries]
    data["generated_at"] = timezone.now().isoformat(timespec="seconds")
    return data


@transaction.atomic
def create_report(title, start, end, by):
    last = FinancialReport.objects.filter(period_start=start, period_end=end).order_by("-version").first()
    version = last.version + 1 if last else 1
    r = FinancialReport.objects.create(title=title, period_start=start, period_end=end, version=version,
                                       snapshot=build_snapshot(start, end), created_by=by)
    log(by, "rapport_cree", f"report:{r.pk}", new=f"v{version}")
    return r


@transaction.atomic
def refresh_report(report, by):
    report = FinancialReport.objects.select_for_update().get(pk=report.pk)
    if report.status != FinancialReport.DRAFT:
        raise FinanceError("Un rapport validé ou publié est figé ; créez une nouvelle version.")
    report.snapshot = build_snapshot(report.period_start, report.period_end)
    report.save()
    return report


@transaction.atomic
def validate_report(report, by):
    report = FinancialReport.objects.select_for_update().get(pk=report.pk)
    if report.status != FinancialReport.DRAFT:
        raise FinanceError("Seul un brouillon peut être validé.")
    report.status, report.validated_by, report.validated_at = FinancialReport.VALIDATED, by, timezone.now()
    report.save()
    log(by, "rapport_valide", f"report:{report.pk}")
    return report


@transaction.atomic
def publish_report(report, by):
    report = FinancialReport.objects.select_for_update().get(pk=report.pk)
    if report.status != FinancialReport.VALIDATED:
        raise FinanceError("Le rapport doit être validé avant publication.")
    report.status, report.published_by, report.published_at = FinancialReport.PUBLISHED, by, timezone.now()
    report.save()
    log(by, "rapport_publie", f"report:{report.pk}", new=f"v{report.version}")
    from apps.accounts.models import User
    from apps.notifications.services import notify_many
    from django.urls import reverse
    notify_many(User.objects.filter(account_status=User.ACTIVE, is_active=True), "rapport_publie", "Nouveau rapport financier",
                report.title, reverse("finance_member:list"))
    return report
