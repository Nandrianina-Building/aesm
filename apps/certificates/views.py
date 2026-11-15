from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.permissions import member_required, perm_required, user_has_perm
from apps.core.utils import is_rate_limited, too_many_requests

from . import pdf, services
from .models import MemberCard, Quitus, Receipt


def _pdf_response(buf, name):
    return FileResponse(buf, content_type="application/pdf", filename=name)


@member_required
def receipt_list(request):
    return render(request, "certificates/receipts.html", {"receipts": Receipt.objects.filter(user=request.user).select_related("payment")})


@login_required
def receipt_pdf(request, number):
    r = get_object_or_404(Receipt.objects.select_related("payment__due__contribution", "payment__reservation__event", "user"), number=number)
    if r.user_id != request.user.pk and not user_has_perm(request.user, "payments.view"):
        raise Http404
    return _pdf_response(pdf.receipt_pdf(r), f"{r.number}.pdf")


@member_required
def quitus_list(request):
    return render(request, "certificates/quitus.html", {"quitus": Quitus.objects.filter(user=request.user)})


@login_required
def quitus_pdf(request, number):
    q = get_object_or_404(Quitus.objects.select_related("user"), number=number)
    if q.user_id != request.user.pk and not user_has_perm(request.user, "quitus.manage"):
        raise Http404
    return _pdf_response(pdf.quitus_pdf(q), f"{q.number}.pdf")


@member_required
def card_view(request):
    card = services.ensure_member_card(request.user)
    return render(request, "certificates/card.html", {"card": card})


@member_required
def card_pdf(request):
    card = services.ensure_member_card(request.user)
    return _pdf_response(pdf.card_pdf(card), f"{card.number}.pdf")


# ------------------------------------------------------------ vérification publique
def verify(request, token):
    if is_rate_limited(request, "verify", 30, 60):
        return too_many_requests()
    from apps.events.models import Ticket
    ctx = {"found": False}
    q = Quitus.objects.select_related("user").filter(token=token).first()
    if q:
        ctx.update(found=True, kind="Quitus", number=q.number, status=q.effective_status, status_label=q.status_label,
                   issued=q.issued_at, holder=f"{q.user.short_name} (matricule {q.user.masked_matricule})", detail=q.contribution_name)
    else:
        card = MemberCard.objects.select_related("user").filter(token=token).first()
        if card:
            ctx.update(found=True, kind="Carte de membre", number=card.number, status=card.effective_status,
                       status_label=card.status_label, issued=card.issued_at,
                       holder=f"{card.user.short_name} (matricule {card.user.masked_matricule})", detail="")
        else:
            t = Ticket.objects.select_related("reservation__user", "reservation__event").filter(token=token).first()
            if t:
                st = t.effective_status
                ctx.update(found=True, kind="Billet d'événement", number=t.number, status=st,
                           status_label={"valid": "Valide", "used": "Déjà utilisé", "revoked": "Révoqué"}[st],
                           issued=t.issued_at, holder=f"{t.reservation.user.short_name}", detail=t.reservation.event.title,
                           ticket=t, can_scan=user_has_perm(request.user, "tickets.scan"))
    return render(request, "certificates/verify.html", ctx)


# ------------------------------------------------------------ gestion
@perm_required("quitus.manage", "payments.view")
def quitus_admin_list(request):
    from django.urls import reverse
    rows = []
    can_revoke = request.user.can("quitus.manage")
    for q in Quitus.objects.select_related("user")[:200]:
        actions = [{"label": "PDF", "url": reverse("certificates:quitus_pdf", args=[q.number])}]
        if can_revoke and q.effective_status == "valid":
            actions.append({"label": "Révoquer", "url": reverse("gestion:quitus_revoke", args=[q.pk]), "method": "post",
                            "cls": "danger", "confirm": "Révoquer ce quitus ? Cette action est définitive."})
        rows.append({"cells": [q.number, q.user.full_name, q.contribution_name, f"{int(q.amount)} Ar", q.issued_at, q.status_label],
                     "actions": actions})
    return render(request, "gestion/list.html", {"title": "Quitus", "headers": ["Numéro", "Membre", "Cotisation", "Montant", "Délivré", "Statut"], "rows": rows})


@perm_required("quitus.manage")
@require_POST
def quitus_revoke(request, pk):
    q = get_object_or_404(Quitus, pk=pk)
    services.revoke_quitus(q, request.user, "Révocation manuelle (erreur ou fraude)")
    messages.success(request, "Quitus révoqué.")
    return redirect("gestion:quitus")


@perm_required("members.view")
def cards_admin_list(request):
    from django.urls import reverse
    rows = []
    for c in MemberCard.objects.select_related("user")[:300]:
        actions = []
        if request.user.can("quitus.manage"):
            actions.append({"label": "Révoquer" if c.status == "valid" else "Réactiver",
                            "url": reverse("gestion:card_toggle", args=[c.pk]), "method": "post"})
        rows.append({"cells": [c.number, c.user.full_name, c.user.matricule, c.status_label, c.issued_at], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Cartes de membre", "headers": ["Numéro", "Membre", "Matricule", "Statut", "Émise"], "rows": rows})


@perm_required("quitus.manage")
@require_POST
def card_toggle(request, pk):
    from apps.audit.services import log
    c = get_object_or_404(MemberCard, pk=pk)
    c.status = MemberCard.REVOKED if c.status == MemberCard.VALID else MemberCard.VALID
    c.save(update_fields=["status"])
    log(request.user, "carte_statut_modifie", c.number, new=c.status)
    return redirect("gestion:cards")
