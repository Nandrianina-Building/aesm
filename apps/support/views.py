import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.core.permissions import user_has_perm
from apps.notifications.services import notify, notify_role

from .forms import MessageForm, TicketForm
from .models import SupportMessage, SupportTicket


@login_required
def ticket_list(request):
    return render(request, "support/list.html", {"tickets": SupportTicket.objects.filter(user=request.user)})


@login_required
def ticket_create(request):
    form = TicketForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        t = form.save(commit=False)
        t.user = request.user
        t.save()
        notify_role(["secretary", "super_admin"], "reclamation_recue", "Nouvelle réclamation", t.subject, reverse("gestion:support"))
        messages.success(request, "Réclamation enregistrée.")
        return redirect("support:detail", t.pk)
    return render(request, "support/form.html", {"form": form})


@login_required
def ticket_detail(request, pk):
    t = get_object_or_404(SupportTicket, pk=pk, user=request.user)  # anti-IDOR
    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid() and t.is_open:
        m = form.save(commit=False)
        m.ticket, m.author = t, request.user
        m.save()
        return redirect("support:detail", pk)
    return render(request, "support/detail.html", {"t": t, "form": form})


@login_required
def attachment(request, pk):
    t = get_object_or_404(SupportTicket, pk=pk)
    if t.user_id != request.user.pk and not user_has_perm(request.user, "support.manage"):
        raise Http404
    if not t.attachment:
        raise Http404
    return FileResponse(t.attachment.open("rb"), as_attachment=True, filename=f"piece-{t.pk}{os.path.splitext(t.attachment.name)[1]}")
