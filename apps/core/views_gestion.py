from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.services import log
from apps.events.models import Event, Reservation
from apps.finance import services as fin
from apps.memberships.models import Membership
from apps.payments.models import ContributionDue, Payment
from apps.support.models import SupportTicket

from .forms import OfficerForm, SettingForm
from .models import ContactMessage, Officer, SiteSetting
from .permissions import perm_required
from .utils import DEFAULT_SETTINGS


@perm_required("dashboard.view")
def home(request):
    s = fin.summary()
    stats = [
        ("Comptes", User.objects.count()),
        ("Membres actifs", User.objects.filter(account_status="active").count()),
        ("Demandes d'adhésion en attente", Membership.objects.filter(status__in=("pending", "verifying")).count()),
        ("Cotisations exigibles (impayées)", ContributionDue.objects.filter(status="unpaid").count()),
        ("Paiements confirmés", Payment.objects.filter(status="confirmed").count()),
        ("Paiements en attente / vérification", Payment.objects.filter(status__in=("pending", "processing", "verifying")).count()),
        ("Recettes validées (Ar)", s["income"]),
        ("Dépenses validées (Ar)", s["expense"]),
        ("Solde (Ar)", s["closing"]),
        ("Événements à venir", Event.objects.filter(starts_at__gte=timezone.now()).exclude(status="draft").count()),
        ("Réservations confirmées", Reservation.objects.filter(status="confirmed").count()),
        ("Réclamations ouvertes", SupportTicket.objects.filter(status__in=("pending", "in_progress")).count()),
    ]
    return render(request, "gestion/home.html", {"stats": stats})


# ------------------------------------------------------------------ responsables
@perm_required("officers.manage")
def officer_list(request):
    rows = [{"avatar": o, "cells": [o.last_name, o.first_name, o.function, o.mandate_start, o.mandate_end or "-", "Archivé" if o.is_archived else "En cours"],
             "actions": [{"label": "Modifier", "url": reverse("gestion:officer_edit", args=[o.pk])}]} for o in Officer.objects.all()]
    return render(request, "gestion/list.html", {"title": "Responsables (bureau)", "headers": ["Nom", "Prénom", "Fonction", "Début", "Fin", "Mandat"], "rows": rows,
                  "create_url": reverse("gestion:officer_create"), "create_label": "Ajouter un responsable"})


@perm_required("officers.manage")
def officer_edit(request, pk=None):
    obj = get_object_or_404(Officer, pk=pk) if pk else None
    form = OfficerForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Responsable enregistré.")
        return redirect("gestion:officers")
    return render(request, "gestion/form.html", {"form": form, "title": "Responsable", "back": "gestion:officers", "multipart": True})


# ------------------------------------------------------------------ audit
@perm_required("audit.view")
def audit_list(request):
    qs = AuditLog.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(action__icontains=q) | Q(user_label__icontains=q) | Q(resource__icontains=q))
    page = Paginator(qs, 40).get_page(request.GET.get("page"))
    rows = [{"cells": [a.created_at, a.user_label, a.action, a.resource, a.old_value[:60], a.new_value[:60], a.result, a.ip_address or "-"]} for a in page]
    return render(request, "gestion/list.html", {"title": "Journal d'audit", "headers": ["Date", "Utilisateur", "Action", "Ressource", "Avant", "Après", "Résultat", "IP"],
                  "rows": rows, "page": page, "search": True, "q": q})


# ------------------------------------------------------------------ paramètres
@perm_required("settings.manage")
def settings_list(request):
    from django.core.cache import cache
    for key, (default, label) in DEFAULT_SETTINGS.items():
        SiteSetting.objects.get_or_create(key=key, defaults={"value": default, "label": label})
    rows = [{"cells": [s.label or s.key, s.value[:80]], "actions": [{"label": "Modifier", "url": reverse("gestion:setting_edit", args=[s.pk])}]}
            for s in SiteSetting.objects.all()]
    return render(request, "gestion/list.html", {"title": "Paramètres généraux", "headers": ["Paramètre", "Valeur"], "rows": rows})


@perm_required("settings.manage")
def setting_edit(request, pk):
    from django.core.cache import cache
    s = get_object_or_404(SiteSetting, pk=pk)
    form = SettingForm(request.POST or None, initial={"value": s.value})
    if request.method == "POST" and form.is_valid():
        old = s.value
        s.value = form.cleaned_data["value"]
        s.save()
        cache.delete(f"setting:{s.key}")
        log(request.user, "parametre_modifie", s.key, old=old, new=s.value, request=request)
        messages.success(request, "Paramètre enregistré.")
        return redirect("gestion:settings")
    return render(request, "gestion/form.html", {"form": form, "title": s.label or s.key, "back": "gestion:settings"})


# ------------------------------------------------------------------ messages de contact
@perm_required("contact.manage")
def contact_list(request):
    rows = []
    for m in ContactMessage.objects.all()[:200]:
        rows.append({"cells": [m.created_at, m.name, m.email, m.subject, m.message[:150], "Traité" if m.is_handled else "À traiter"],
                     "actions": [] if m.is_handled else [{"label": "Marquer traité", "url": reverse("gestion:contact_handled", args=[m.pk]), "method": "post"}]})
    return render(request, "gestion/list.html", {"title": "Messages de contact", "headers": ["Date", "Nom", "E-mail", "Objet", "Message", "État"], "rows": rows})


@perm_required("contact.manage")
@require_POST
def contact_handled(request, pk):
    ContactMessage.objects.filter(pk=pk).update(is_handled=True)
    return redirect("gestion:contacts")
