from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.core.permissions import perm_required

from .models import Notification
from .services import notify_many


@login_required
def notification_list(request):
    qs = Notification.objects.filter(user=request.user)
    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    return render(request, "notifications/list.html", {"page": page})


@login_required
@require_POST
def toggle_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)  # anti-IDOR
    n.is_read = not n.is_read
    n.save(update_fields=["is_read"])
    return redirect("notifications:list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")


@login_required
@require_POST
def delete(request, pk):
    get_object_or_404(Notification, pk=pk, user=request.user).delete()
    return redirect("notifications:list")


@login_required
def open_notification(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    if not n.is_read:
        n.is_read = True
        n.save(update_fields=["is_read"])
    target = n.url if n.url.startswith("/") and not n.url.startswith("//") else "notifications:list"
    return redirect(target)


@perm_required("notifications.send")
def broadcast(request):
    """Annonce ciblée vers les membres actifs (module Notifications, côté gestion)."""
    from django import forms

    class BroadcastForm(forms.Form):
        title = forms.CharField(label="Titre", max_length=150)
        message = forms.CharField(label="Message", widget=forms.Textarea, max_length=1000)
        audience = forms.ChoiceField(label="Destinataires", choices=[("members", "Membres actifs"), ("all", "Tous les comptes")])

    form = BroadcastForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        users = User.objects.filter(is_active=True)
        if form.cleaned_data["audience"] == "members":
            users = users.filter(account_status=User.ACTIVE)
        notify_many(users, "annonce", form.cleaned_data["title"], form.cleaned_data["message"])
        from apps.audit.services import log
        log(request.user, "notification_diffusee", form.cleaned_data["title"], new=f"{users.count()} destinataires", request=request)
        messages.success(request, f"Notification envoyée à {users.count()} utilisateur(s).")
        return redirect("gestion:home")
    return render(request, "gestion/form.html", {"form": form, "title": "Envoyer une annonce ciblée", "back": "gestion:home"})
