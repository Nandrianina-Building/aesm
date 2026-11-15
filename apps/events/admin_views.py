import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.audit.services import log
from apps.core.permissions import perm_required

from . import services
from .forms import EventForm
from .models import Event, EventImage, Reservation, Ticket


@perm_required("events.view", "events.manage")
def event_list(request):
    can = request.user.can("events.manage")
    rows = []
    for e in Event.objects.prefetch_related("images"):
        actions = [{"label": "Réservations", "url": reverse("gestion:event_reservations", args=[e.pk])}]
        if can:
            actions.insert(0, {"label": "Modifier", "url": reverse("gestion:event_edit", args=[e.pk])})
        rows.append({"thumb": e.cover_url, "cells": [e.title, e.starts_at, e.location, f"{services.taken_seats(e)}/{e.capacity}",
                               "Gratuit" if e.is_free else f"{int(e.price)} Ar", e.get_status_display()], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Événements", "headers": ["Titre", "Date", "Lieu", "Places", "Prix", "Statut"],
                  "rows": rows, "create_url": reverse("gestion:event_create") if can else None, "create_label": "Nouvel événement"})


@perm_required("events.manage")
def event_edit(request, pk=None):
    obj = get_object_or_404(Event, pk=pk) if pk else None
    form = EventForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        e = form.save()
        for img in form.cleaned_data.get("remove_images") or []:
            img.delete()
        start = e.images.count()
        for n, f in enumerate(form.cleaned_data.get("gallery") or []):
            EventImage.objects.create(event=e, image=f, position=start + n)
        log(request.user, "evenement_modifie" if obj else "evenement_cree", f"event:{e.pk}", new=e.title)
        messages.success(request, "Événement enregistré.")
        return redirect("gestion:events")
    return render(request, "gestion/form.html", {"form": form, "title": "Événement", "back": "gestion:events", "multipart": True,
                  "gallery_items": obj.images.all() if obj else [], "cover": obj.image if obj and obj.image else None})


@perm_required("reservations.manage", "events.view")
def event_reservations(request, pk):
    event = get_object_or_404(Event, pk=pk)
    can = request.user.can("reservations.manage")
    rows = []
    for r in event.reservations.select_related("user", "ticket"):
        actions = []
        if can and r.status in ("pending", "confirmed"):
            actions.append({"label": "Annuler", "url": reverse("gestion:reservation_cancel", args=[r.pk]), "method": "post",
                            "cls": "danger", "confirm": "Annuler cette réservation ?"})
        t = getattr(r, "ticket", None)
        rows.append({"avatar": r.user, "cells": [r.user.full_name, r.user.matricule, r.get_status_display(), t.status if t else "-", r.created_at],
                     "actions": actions})
    return render(request, "gestion/list.html", {
        "title": f"Réservations - {event.title}", "headers": ["Participant", "Matricule", "Statut", "Billet", "Date"], "rows": rows,
        "extra_links": [{"label": "Exporter CSV", "url": reverse("gestion:event_export", args=[pk])}]})


@perm_required("reservations.manage")
@require_POST
def reservation_cancel(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    try:
        services.cancel_reservation(res.pk, request.user, "Annulation par l'administration", enforce_deadline=False)
        messages.success(request, "Réservation annulée.")
    except services.ReservationError as exc:
        messages.error(request, str(exc))
    return redirect("gestion:event_reservations", res.event_id)


def _csv_safe(v):
    v = str(v)
    return "'" + v if v[:1] in "=+-@" else v  # protège contre l'injection de formules Excel


@perm_required("reservations.manage")
def event_export(request, pk):
    event = get_object_or_404(Event, pk=pk)
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="participants-{event.pk}.csv"'
    resp.write("\ufeff")
    w = csv.writer(resp, delimiter=";")
    w.writerow(["Nom", "Prénom", "Matricule", "Téléphone", "Statut", "Billet", "Présent"])
    for r in event.reservations.filter(status="confirmed").select_related("user", "ticket"):
        t = getattr(r, "ticket", None)
        w.writerow([_csv_safe(r.user.last_name), _csv_safe(r.user.first_name), _csv_safe(r.user.matricule),
                    _csv_safe(r.user.phone), r.get_status_display(), t.number if t else "", "oui" if t and t.status == "used" else "non"])
    log(request.user, "export_participants", f"event:{event.pk}", request=request)
    return resp


@perm_required("tickets.scan")
def scan(request):
    """Validation d'un billet : saisie/scan du jeton (le QR pointe vers /verification/<jeton>/)."""
    result = None
    if request.method == "POST":
        token = request.POST.get("token", "").strip().rstrip("/").split("/")[-1]
        try:
            t = services.check_in(token, request.user)
            result = {"ok": True, "message": f"Présence enregistrée : {t.reservation.user.full_name} - {t.reservation.event.title}"}
        except services.TicketError as exc:
            result = {"ok": False, "message": str(exc)}
    return render(request, "gestion/scan.html", {"result": result})


@perm_required("tickets.scan")
@require_POST
def scan_ticket(request, token):
    try:
        t = services.check_in(token, request.user)
        messages.success(request, f"Présence enregistrée : {t.reservation.user.full_name}.")
    except services.TicketError as exc:
        messages.error(request, str(exc))
    return redirect("verify:check", token)
