from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.audit.services import log
from apps.core.permissions import perm_required
from apps.notifications.services import notify

from .forms import StaffUpdateForm
from .models import SupportMessage, SupportTicket


@perm_required("support.manage")
def ticket_list(request):
    qs = SupportTicket.objects.select_related("user", "assigned_to")
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    rows = [{"cells": [t.pk, t.user.full_name, t.get_reason_display(), t.subject, t.get_status_display(), t.assigned_to or "-", t.created_at],
             "actions": [{"label": "Traiter", "url": reverse("gestion:support_detail", args=[t.pk])}]} for t in qs[:300]]
    return render(request, "gestion/list.html", {"title": "Réclamations", "headers": ["N°", "Membre", "Motif", "Objet", "Statut", "Assignée à", "Date"],
                  "rows": rows, "status_filter": SupportTicket.STATUS_CHOICES, "status": status or ""})


@perm_required("support.manage")
def ticket_detail(request, pk):
    t = get_object_or_404(SupportTicket.objects.select_related("user"), pk=pk)
    form = StaffUpdateForm(request.POST or None, initial={"status": t.status})
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        if cd["body"].strip():
            SupportMessage.objects.create(ticket=t, author=request.user, body=cd["body"], from_staff=True)
        if t.assigned_to_id is None:
            t.assigned_to = request.user
        old = t.status
        t.status = cd["status"]
        t.save()
        log(request.user, "reclamation_traitee", f"ticket:{t.pk}", old=old, new=t.status)
        if cd["status"] in ("resolved", "rejected", "closed") or cd["body"].strip():
            notify(t.user, "reclamation_traitee", "Réclamation mise à jour", t.subject, reverse("support:detail", args=[t.pk]))
        messages.success(request, "Réclamation mise à jour.")
        return redirect("gestion:support")
    return render(request, "gestion/support_detail.html", {"t": t, "form": form})
