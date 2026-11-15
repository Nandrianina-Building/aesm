from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.core.permissions import perm_required

from . import services
from .forms import RefuseForm, VerifyForm
from .models import Membership


@perm_required("memberships.manage", "memberships.view")
def membership_list(request):
    qs = Membership.objects.select_related("user")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(user__matricule__icontains=q) | Q(user__last_name__icontains=q) | Q(user__first_name__icontains=q))
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    can = request.user.can("memberships.manage")
    rows = []
    for m in page:
        actions = []
        if can:
            if m.can_go("accepted"):
                actions.append({"label": "Accepter", "url": reverse("gestion:membership_accept", args=[m.pk]), "method": "post"})
            if m.can_go("verifying"):
                actions.append({"label": "Vérifier", "url": reverse("gestion:membership_verify", args=[m.pk])})
            if m.can_go("refused"):
                actions.append({"label": "Refuser", "url": reverse("gestion:membership_refuse", args=[m.pk]), "cls": "danger"})
            if m.status == "accepted":
                actions.append({"label": "Suspendre", "url": reverse("gestion:membership_suspend", args=[m.pk]), "method": "post",
                                "cls": "danger", "confirm": "Suspendre cette adhésion ?"})
            if m.status == "suspended":
                actions.append({"label": "Réactiver", "url": reverse("gestion:membership_reactivate", args=[m.pk]), "method": "post"})
        rows.append({"avatar": m.user, "cells": [m.user.full_name, m.user.matricule, m.user.phone, m.year, m.get_status_display(), m.submitted_at or "-"], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Adhésions", "headers": ["Membre", "Matricule", "Téléphone", "Année", "Statut", "Soumise le"],
                  "rows": rows, "page": page, "search": True, "q": q, "status_filter": Membership.STATUS_CHOICES, "status": status})


def _run(request, pk, func, ok, *args):
    m = get_object_or_404(Membership, pk=pk)
    try:
        func(m, request.user, *args)
        messages.success(request, ok)
    except services.TransitionError as exc:
        messages.error(request, str(exc))
    return redirect("gestion:memberships")


@perm_required("memberships.manage")
@require_POST
def membership_accept(request, pk):
    return _run(request, pk, services.accept, "Adhésion acceptée.")


@perm_required("memberships.manage")
@require_POST
def membership_suspend(request, pk):
    return _run(request, pk, services.suspend, "Adhésion suspendue.", "Suspension par l'administration")


@perm_required("memberships.manage")
@require_POST
def membership_reactivate(request, pk):
    return _run(request, pk, services.reactivate, "Adhésion réactivée.")


@perm_required("memberships.manage")
def membership_refuse(request, pk):
    m = get_object_or_404(Membership, pk=pk)
    form = RefuseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        return _run(request, pk, services.refuse, "Adhésion refusée.", form.cleaned_data["reason"])
    return render(request, "gestion/form.html", {"form": form, "title": f"Refuser l'adhésion de {m.user}", "back": "gestion:memberships"})


@perm_required("memberships.manage")
def membership_verify(request, pk):
    m = get_object_or_404(Membership, pk=pk)
    form = VerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        return _run(request, pk, services.set_verifying, "Demande placée en vérification.", form.cleaned_data["note"])
    return render(request, "gestion/form.html", {"form": form, "title": f"Vérification - {m.user}", "back": "gestion:memberships"})
