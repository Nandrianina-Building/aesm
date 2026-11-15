from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.audit.services import log
from apps.core.permissions import perm_required

from . import services
from .forms import ContributionForm, ReasonForm, VerifyPaymentForm, WaiveForm
from .models import ContributionDue, ContributionType, Payment


@perm_required("contributions.view")
def contribution_list(request):
    rows = []
    can_manage = request.user.can("contributions.manage")
    for c in ContributionType.objects.all():
        actions = []
        if can_manage:
            actions = [
                {"label": "Modifier", "url": reverse("gestion:contribution_edit", args=[c.pk])},
                {"label": "Facturer aux membres", "url": reverse("gestion:contribution_generate", args=[c.pk]), "method": "post"},
            ]
        rows.append({"cells": [c.name, f"{int(c.amount)} Ar", c.period_label, c.end_date, c.get_audience_display(),
                               "Active" if c.is_active else "Inactive", c.dues.filter(status="paid").count(), c.dues.count()],
                     "actions": actions})
    ctx = {"title": "Cotisations", "headers": ["Nom", "Montant", "Période", "Date limite", "Public", "Statut", "Payées", "Facturées"],
           "rows": rows, "create_url": reverse("gestion:contribution_create") if can_manage else None, "create_label": "Nouvelle cotisation"}
    return render(request, "gestion/list.html", ctx)


@perm_required("contributions.manage")
def contribution_edit(request, pk=None):
    obj = get_object_or_404(ContributionType, pk=pk) if pk else None
    old = (obj.amount, obj.is_active, obj.end_date) if obj else None
    form = ContributionForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        if not c.pk:
            c.created_by = request.user
        c.save()
        form.save_m2m()
        log(request.user, "cotisation_modifiee" if obj else "cotisation_creee", f"contribution:{c.pk}", old=old,
            new=(c.amount, c.is_active, c.end_date))
        messages.success(request, "Cotisation enregistrée.")
        return redirect("gestion:contributions")
    return render(request, "gestion/form.html", {"form": form, "title": "Cotisation", "back": "gestion:contributions"})


@perm_required("contributions.manage")
@require_POST
def contribution_generate(request, pk):
    c = get_object_or_404(ContributionType, pk=pk)
    n = services.generate_dues_for_contribution(c)
    log(request.user, "cotisation_facturee", f"contribution:{c.pk}", new=f"{n} membres")
    messages.success(request, f"{n} cotisation(s) facturée(s) (les doublons sont ignorés).")
    return redirect("gestion:contributions")


@perm_required("contributions.manage")
def due_waive(request, pk):
    due = get_object_or_404(ContributionDue.objects.select_related("user", "contribution"), pk=pk)
    form = WaiveForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            services.waive_due(due, request.user, form.cleaned_data["reason"])
            messages.success(request, "Exonération enregistrée.")
            return redirect("gestion:contributions")
        except services.PaymentError as exc:
            messages.error(request, str(exc))
    return render(request, "gestion/form.html", {"form": form, "title": f"Exonérer {due.user} - {due.contribution.name}",
                                                 "back": "gestion:contributions"})


@perm_required("payments.view")
def payment_list(request):
    qs = Payment.objects.select_related("user", "due__contribution", "reservation__event")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(reference__icontains=q) | Q(external_reference__icontains=q) | Q(user__matricule__icontains=q)
                       | Q(user__last_name__icontains=q))
    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    rows = [{"cells": [p.reference, p.user.full_name, p.object_label, f"{int(p.amount)} Ar", p.get_method_display(),
                       p.external_reference or "-", p.get_status_display(), p.created_at],
             "actions": [{"label": "Ouvrir", "url": reverse("gestion:payment_detail", args=[p.reference])}]} for p in page]
    ctx = {"title": "Paiements", "headers": ["Référence", "Membre", "Objet", "Montant", "Moyen", "Réf. transaction", "Statut", "Date"],
           "rows": rows, "page": page, "search": True, "q": q, "status_filter": Payment.STATUS_CHOICES, "status": status}
    return render(request, "gestion/list.html", ctx)


@perm_required("payments.view")
def payment_detail(request, reference):
    p = get_object_or_404(Payment.objects.select_related("user", "due__contribution", "reservation__event"), reference=reference)
    return render(request, "gestion/payment_detail.html", {
        "p": p, "verify_form": VerifyPaymentForm(), "reason_form": ReasonForm(),
        "can_verify": request.user.can("payments.verify"), "can_refund": request.user.can("payments.refund")})


@perm_required("payments.verify")
@require_POST
def payment_confirm(request, reference):
    p = get_object_or_404(Payment, reference=reference)
    form = VerifyPaymentForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Saisissez le montant reçu.")
        return redirect("gestion:payment_detail", reference)
    try:
        p = services.confirm_payment(p.pk, by=request.user, received_amount=form.cleaned_data["received_amount"])
        if p.status == Payment.CONFIRMED:
            messages.success(request, "Paiement confirmé. Reçu généré.")
        else:
            messages.warning(request, f"Paiement placé en vérification : {p.failure_reason}")
    except services.PaymentError as exc:
        messages.error(request, str(exc))
    return redirect("gestion:payment_detail", reference)


@perm_required("payments.verify")
@require_POST
def payment_reject(request, reference):
    p = get_object_or_404(Payment, reference=reference)
    form = ReasonForm(request.POST)
    if form.is_valid():
        try:
            services.reject_payment(p.pk, request.user, form.cleaned_data["reason"])
            messages.success(request, "Paiement rejeté.")
        except services.PaymentError as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Un motif est obligatoire.")
    return redirect("gestion:payment_detail", reference)


@perm_required("payments.refund")
@require_POST
def payment_refund(request, reference):
    p = get_object_or_404(Payment, reference=reference)
    form = ReasonForm(request.POST)
    if form.is_valid():
        try:
            services.refund_payment(p.pk, request.user, form.cleaned_data["reason"])
            messages.success(request, "Paiement remboursé, écriture d'annulation créée.")
        except services.PaymentError as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Un motif est obligatoire.")
    return redirect("gestion:payment_detail", reference)


@perm_required("contributions.view")
def due_list(request):
    qs = ContributionDue.objects.select_related("user", "contribution")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(user__matricule__icontains=q) | Q(user__last_name__icontains=q) | Q(contribution__name__icontains=q))
    can = request.user.can("contributions.manage")
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    rows = []
    for d in page:
        actions = [{"label": "Exonérer", "url": reverse("gestion:due_waive", args=[d.pk])}] if can and d.status == "unpaid" else []
        rows.append({"cells": [d.user.full_name, d.user.matricule, d.contribution.name, f"{int(d.amount)} Ar", d.due_date,
                               d.get_status_display()], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Cotisations par membre", "headers": ["Membre", "Matricule", "Cotisation", "Montant", "Date limite", "Statut"],
                  "rows": rows, "page": page, "search": True, "q": q, "status_filter": ContributionDue.STATUS_CHOICES, "status": status})
