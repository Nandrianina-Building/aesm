import hashlib
import hmac
import json
import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.permissions import member_required, user_has_perm

from . import services
from .forms import PaymentForm
from .models import ContributionDue, Payment, PaymentProviderEvent


@member_required
def dues(request):
    qs = ContributionDue.objects.filter(user=request.user).select_related("contribution")
    return render(request, "payments/dues.html", {"dues": qs})


def _handle_payment(request, *, due=None, reservation=None, back):
    method = settings.PAYMENT_PROVIDER
    form = PaymentForm(request.POST or None, initial={"idempotency_key": uuid.uuid4().hex})
    if request.method == "POST" and form.is_valid():
        try:
            payment, created = services.create_payment(
                request.user, due=due, reservation=reservation, method=method,
                idempotency_key=form.cleaned_data["idempotency_key"])
        except services.PaymentError as exc:
            messages.error(request, str(exc))
            form = PaymentForm(initial={"idempotency_key": uuid.uuid4().hex})
        else:
            if method == "simulation" and payment.status == Payment.PENDING:
                return redirect("payments:simulate", payment.reference)
            redirect_url = getattr(payment, "redirect_url", "")
            if redirect_url.startswith("https://"):
                return redirect(redirect_url)  # page de paiement du prestataire
            messages.success(request, "Paiement enregistré.")
            return redirect("payments:detail", payment.reference)
    amount = due.amount if due else reservation.price_snapshot
    return render(request, "payments/pay.html", {
        "form": form, "due": due, "reservation": reservation, "amount": amount, "back": back,
        "simulation": method == "simulation"})


@member_required
def pay_due(request, pk):
    due = get_object_or_404(ContributionDue.objects.select_related("contribution"), pk=pk, user=request.user)  # anti-IDOR
    if due.status != ContributionDue.UNPAID:
        messages.info(request, "Cette cotisation n'est plus à payer.")
        return redirect("payments:dues")
    return _handle_payment(request, due=due, back="payments:dues")


@member_required
def pay_reservation(request, pk):
    from apps.events.models import Reservation
    res = get_object_or_404(Reservation.objects.select_related("event"), pk=pk, user=request.user)
    if res.status != Reservation.PENDING:
        messages.info(request, "Cette réservation n'attend pas de paiement.")
        return redirect("events_member:list")
    return _handle_payment(request, reservation=res, back="events_member:list")


@login_required
def payment_list(request):
    qs = Payment.objects.filter(user=request.user).select_related("due__contribution", "reservation__event")
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "payments/list.html", {"page": page})


@login_required
def payment_detail(request, reference):
    p = get_object_or_404(Payment.objects.select_related("due__contribution", "reservation__event"), reference=reference)
    if p.user_id != request.user.pk and not user_has_perm(request.user, "payments.view"):
        raise Http404  # ne révèle pas l'existence de la ressource
    ctx = {"p": p, "can_resume": p.method == "simulation" and p.status == Payment.PENDING and p.user_id == request.user.pk and settings.PAYMENT_SIMULATION_ENABLED}
    return render(request, "payments/detail.html", ctx)


@login_required
def proof_download(request, reference):
    p = get_object_or_404(Payment, reference=reference)
    if p.user_id != request.user.pk and not user_has_perm(request.user, "payments.view"):
        raise Http404
    if not p.proof:
        raise Http404
    return FileResponse(p.proof.open("rb"), as_attachment=True, filename=f"preuve-{p.reference}{os.path.splitext(p.proof.name)[1]}")


@member_required
def simulate(request, reference):
    """Page de paiement FICTIVE (aucun argent réel). Disparaît quand PAYMENT_SIMULATION_ENABLED=0."""
    if not settings.PAYMENT_SIMULATION_ENABLED:
        raise Http404
    p = get_object_or_404(Payment.objects.select_related("due__contribution", "reservation__event"),
                          reference=reference, user=request.user, method="simulation")
    if request.method == "POST":
        try:
            result = services.simulate_outcome(p.pk, request.user, request.POST.get("outcome", ""))
        except services.PaymentError as exc:
            messages.error(request, str(exc))
        else:
            if result.status == Payment.CONFIRMED:
                messages.success(request, "Paiement simulé réussi : reçu généré.")
            elif result.status == Payment.VERIFYING:
                messages.warning(request, "Paiement reçu mais en vérification : " + (result.failure_reason or ""))
            elif result.status == Payment.FAILED:
                messages.error(request, "Paiement simulé échoué.")
            else:
                messages.info(request, "Paiement annulé.")
        return redirect("payments:detail", p.reference)
    if p.status != Payment.PENDING:
        return redirect("payments:detail", p.reference)
    return render(request, "payments/simulate.html", {"p": p})


@csrf_exempt
@require_POST
def webhook(request, provider):
    """Réception d'une notification prestataire : signature HMAC obligatoire, rejeu ignoré.

    Le format JSON attendu est générique {event_id, reference, status, amount, currency} ;
    à adapter à la documentation officielle du prestataire lors du branchement de l'API.
    """
    if provider != "tokipay":
        raise Http404
    secret = os.environ.get(f"WEBHOOK_SECRET_{provider.upper()}", "")
    if not secret:
        return HttpResponseForbidden("webhook non configuré")
    expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, request.headers.get("X-Signature", "")):
        return HttpResponseForbidden("signature invalide")
    try:
        data = json.loads(request.body)
        event_id = str(data["event_id"])[:100]
    except (ValueError, KeyError, TypeError):
        return HttpResponse("requête invalide", status=400)
    event, created = PaymentProviderEvent.objects.get_or_create(
        provider=provider, event_id=event_id, defaults={"payload": data, "signature_valid": True})
    if not created:
        return HttpResponse("déjà traité", status=200)  # protection contre les notifications répétées
    try:
        payment = Payment.objects.get(reference=data.get("reference"), method=provider)
        if data.get("currency", payment.currency) != payment.currency:
            raise services.PaymentError("devise différente")
        if data.get("status") == "success":
            services.confirm_payment(payment.pk, received_amount=data.get("amount"), source=f"api:{provider}")
            result = "confirmé"
        else:
            services.reject_payment(payment.pk, None, data.get("message", "Échec signalé par le prestataire"))
            result = "échec enregistré"
    except (Payment.DoesNotExist, services.PaymentError) as exc:
        result = f"ignoré: {exc}"[:200]
    event.processed, event.result = True, result
    event.save()
    return HttpResponse(result)
