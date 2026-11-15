import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.permissions import member_required, user_has_perm

from . import services
from .models import Event, Reservation


def _visible(user):
    qs = Event.objects.exclude(status=Event.DRAFT).prefetch_related("images")
    if not (user.is_authenticated and (user.is_active_member or user.is_staff_member)):
        qs = qs.filter(visibility="public")
    return qs


def event_list(request):
    upcoming = _visible(request.user).filter(starts_at__gte=timezone.now())
    past = _visible(request.user).filter(starts_at__lt=timezone.now()).order_by("-starts_at")[:6]
    return render(request, "events/list.html", {"upcoming": upcoming, "past": past})


def event_detail(request, pk):
    event = get_object_or_404(_visible(request.user), pk=pk)
    my_res = None
    if request.user.is_authenticated:
        my_res = Reservation.objects.filter(event=event, user=request.user).filter(services.active_filter()).first()
    return render(request, "events/detail.html", {"event": event, "seats_left": services.seats_left(event), "my_res": my_res})


@login_required
@require_POST
def reserve(request, pk):
    event = get_object_or_404(_visible(request.user), pk=pk)
    try:
        res = services.reserve(event.pk, request.user)
    except (services.ReservationError, services.CapacityError) as exc:
        messages.error(request, str(exc))
        return redirect("events:detail", pk)
    if res.status == Reservation.PENDING:
        messages.success(request, "Place retenue. Réglez le paiement pour confirmer votre réservation.")
        return redirect("payments:pay_reservation", res.pk)
    messages.success(request, "Réservation confirmée. Votre billet est disponible.")
    return redirect("events_member:list")


@member_required
def my_reservations(request):
    qs = Reservation.objects.filter(user=request.user).select_related("event", "ticket")
    return render(request, "events/my_reservations.html", {"reservations": qs})


@member_required
@require_POST
def cancel(request, pk):
    res = get_object_or_404(Reservation, pk=pk, user=request.user)  # anti-IDOR
    try:
        services.cancel_reservation(res.pk, request.user, "Annulation par le membre")
        messages.success(request, "Réservation annulée.")
    except services.ReservationError as exc:
        messages.error(request, str(exc))
    return redirect("events_member:list")


@login_required
def ticket_pdf(request, pk):
    from apps.certificates import pdf
    res = get_object_or_404(Reservation.objects.select_related("event", "user", "ticket"), pk=pk)
    if res.user_id != request.user.pk and not user_has_perm(request.user, "reservations.manage"):
        raise Http404
    if res.status != Reservation.CONFIRMED or not hasattr(res, "ticket"):
        raise Http404
    return FileResponse(pdf.ticket_pdf(res.ticket), content_type="application/pdf", filename=f"{res.ticket.number}.pdf")
