from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.audit.services import log
from apps.core.permissions import member_required, perm_required, user_has_perm

from . import exports, services
from .forms import EntryForm, FilterForm, ReportForm
from .models import BudgetEntry, FinancialReport


# ----------------------------------------------------------------- membres
def _published():
    return FinancialReport.objects.filter(status=FinancialReport.PUBLISHED)


@member_required
def report_list(request):
    return render(request, "finance/reports.html", {"reports": _published()})


@member_required
def report_detail(request, pk):
    r = get_object_or_404(_published(), pk=pk)
    max_inc = max([v for _, v in r.snapshot["income_by_category"]] + [1])
    max_exp = max([v for _, v in r.snapshot["expense_by_category"]] + [1])
    inc = [(k, v, round(v * 100 / max_inc)) for k, v in r.snapshot["income_by_category"]]
    exp = [(k, v, round(v * 100 / max_exp)) for k, v in r.snapshot["expense_by_category"]]
    return render(request, "finance/report_detail.html", {"r": r, "s": r.snapshot, "inc": inc, "exp": exp})


@member_required
def report_xlsx(request, pk):
    r = get_object_or_404(_published(), pk=pk)
    return FileResponse(exports.report_xlsx(r), as_attachment=True, filename=f"rapport-{r.pk}.xlsx")


@member_required
def report_pdf(request, pk):
    r = get_object_or_404(_published(), pk=pk)
    return FileResponse(exports.report_pdf(r), content_type="application/pdf", filename=f"rapport-{r.pk}.pdf")


# ----------------------------------------------------------------- gestion
@perm_required("finance.view", "finance.manage")
def finance_home(request):
    from datetime import date
    year = date.today().year
    s = services.summary(date(year, 1, 1), date(year, 12, 31))
    mx = max([v for _, v in s["income_by_category"] + s["expense_by_category"]] + [1])
    s["inc"] = [(k, v, round(v * 100 / mx)) for k, v in s["income_by_category"]]
    s["exp"] = [(k, v, round(v * 100 / mx)) for k, v in s["expense_by_category"]]
    return render(request, "gestion/finance_home.html", {"s": s, "year": year,
                  "pending": BudgetEntry.objects.filter(status="pending").count()})


@perm_required("finance.view", "finance.manage")
def entry_list(request):
    qs = BudgetEntry.objects.select_related("responsible")
    f = FilterForm(request.GET or None)
    if f.is_valid():
        cd = f.cleaned_data
        if cd["kind"]:
            qs = qs.filter(kind=cd["kind"])
        if cd["status"]:
            qs = qs.filter(status=cd["status"])
        if cd["start"]:
            qs = qs.filter(date__gte=cd["start"])
        if cd["end"]:
            qs = qs.filter(date__lte=cd["end"])
    if request.GET.get("export") == "xlsx" and request.user.can("finance.manage"):
        log(request.user, "export_financier", "operations", request=request)
        return FileResponse(exports.entries_xlsx(qs[:5000]), as_attachment=True, filename="operations.xlsx")
    can_validate = request.user.can("finance.validate")
    can_manage = request.user.can("finance.manage")
    rows = []
    for e in qs[:300]:
        actions = []
        if e.status == "pending" and can_validate:
            actions.append({"label": "Valider", "url": reverse("gestion:entry_validate", args=[e.pk]), "method": "post"})
            actions.append({"label": "Rejeter", "url": reverse("gestion:entry_reject", args=[e.pk]), "method": "post", "cls": "danger",
                            "confirm": "Rejeter cette opération ?"})
        if e.status == "validated" and can_manage and not e.reverses_id and not e.is_reversed:
            actions.append({"label": "Annuler (écriture inverse)", "url": reverse("gestion:entry_reverse", args=[e.pk])})
        rows.append({"cells": [e.reference, e.date, e.get_kind_display(), e.get_category_display(), e.description,
                               f"{int(e.amount)} Ar", e.get_status_display()], "actions": actions})
    ctx = {"title": "Opérations financières", "headers": ["Référence", "Date", "Type", "Catégorie", "Description", "Montant", "Statut"],
           "rows": rows, "filter_form": f, "create_url": reverse("gestion:entry_create") if can_manage else None,
           "create_label": "Nouvelle opération", "extra_links": [{"label": "Exporter Excel", "url": request.get_full_path() + ("&" if request.GET else "?") + "export=xlsx"}] if can_manage else []}
    return render(request, "gestion/list.html", ctx)


@perm_required("finance.manage")
def entry_create(request):
    form = EntryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        e = form.save(commit=False)
        e.reference, e.responsible, e.status = services.new_reference(), request.user, BudgetEntry.PENDING
        e.save()
        log(request.user, "ecriture_creee", e.reference, new=e.amount, request=request)
        messages.success(request, "Opération enregistrée, en attente de validation.")
        return redirect("gestion:entries")
    return render(request, "gestion/form.html", {"form": form, "title": "Nouvelle opération", "back": "gestion:entries", "multipart": True})


def _entry_action(request, pk, func, ok_msg, *args):
    entry = get_object_or_404(BudgetEntry, pk=pk)
    try:
        func(entry, request.user, *args)
        messages.success(request, ok_msg)
    except (services.FinanceError, PermissionError) as exc:
        messages.error(request, str(exc))
    return redirect("gestion:entries")


@perm_required("finance.validate")
@require_POST
def entry_validate(request, pk):
    return _entry_action(request, pk, services.validate_entry, "Opération validée.")


@perm_required("finance.validate")
@require_POST
def entry_reject(request, pk):
    return _entry_action(request, pk, services.reject_entry, "Opération rejetée.", "Rejetée par le validateur")


@perm_required("finance.manage")
def entry_reverse(request, pk):
    from django import forms

    class ReasonForm(forms.Form):
        reason = forms.CharField(label="Motif de l'annulation", max_length=200)

    entry = get_object_or_404(BudgetEntry, pk=pk)
    form = ReasonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        return _entry_action(request, pk, services.reverse_entry, "Écriture d'annulation créée.", form.cleaned_data["reason"])
    return render(request, "gestion/form.html", {"form": form, "title": f"Annuler {entry.reference} ({int(entry.amount)} Ar)", "back": "gestion:entries"})


@perm_required("reports.manage", "reports.validate", "reports.publish")
def report_admin_list(request):
    rows = []
    for r in FinancialReport.objects.all():
        actions = [{"label": "PDF", "url": reverse("finance_member:report_pdf", args=[r.pk])}] if user_has_perm(request.user, "finance.view") else []
        if r.status == "draft":
            if request.user.can("reports.manage"):
                actions.append({"label": "Actualiser", "url": reverse("gestion:report_refresh", args=[r.pk]), "method": "post"})
            if request.user.can("reports.validate"):
                actions.append({"label": "Valider", "url": reverse("gestion:report_validate", args=[r.pk]), "method": "post"})
        if r.status == "validated" and request.user.can("reports.publish"):
            actions.append({"label": "Publier", "url": reverse("gestion:report_publish", args=[r.pk]), "method": "post",
                            "confirm": "Publier ce rapport à tous les membres ?"})
        s = r.snapshot
        rows.append({"cells": [r.title, f"{r.period_start} → {r.period_end}", f"v{r.version}", f"{s.get('closing', 0)} Ar", r.get_status_display(), r.published_at or "-"], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Rapports financiers", "headers": ["Titre", "Période", "Version", "Solde final", "Statut", "Publié le"], "rows": rows,
                  "create_url": reverse("gestion:report_create") if request.user.can("reports.manage") else None, "create_label": "Nouveau rapport"})


@perm_required("reports.manage")
def report_create(request):
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        services.create_report(cd["title"], cd["period_start"], cd["period_end"], request.user)
        messages.success(request, "Rapport créé (instantané des écritures validées).")
        return redirect("gestion:reports")
    return render(request, "gestion/form.html", {"form": form, "title": "Nouveau rapport financier", "back": "gestion:reports"})


def _report_action(request, pk, func, msg):
    r = get_object_or_404(FinancialReport, pk=pk)
    try:
        func(r, request.user)
        messages.success(request, msg)
    except services.FinanceError as exc:
        messages.error(request, str(exc))
    return redirect("gestion:reports")


@perm_required("reports.manage")
@require_POST
def report_refresh(request, pk):
    return _report_action(request, pk, services.refresh_report, "Rapport actualisé.")


@perm_required("reports.validate")
@require_POST
def report_validate(request, pk):
    return _report_action(request, pk, services.validate_report, "Rapport validé.")


@perm_required("reports.publish")
@require_POST
def report_publish(request, pk):
    return _report_action(request, pk, services.publish_report, "Rapport publié.")
