from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.audit.services import log
from apps.core.permissions import perm_required

from .forms import UserAdminForm
from .models import User


@perm_required("members.view")
def user_list(request):
    qs = User.objects.prefetch_related("roles")
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(Q(matricule__icontains=q) | Q(last_name__icontains=q) | Q(first_name__icontains=q) | Q(phone__icontains=q))
    if status:
        qs = qs.filter(account_status=status)
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    can = request.user.can("users.manage")
    rows = []
    for u in page:
        actions = [{"label": "Gérer", "url": reverse("gestion:user_edit", args=[u.pk])}] if can else []
        rows.append({"avatar": u, "cells": [u.full_name, u.matricule, u.phone, u.email or "-", u.get_account_status_display(),
                               ", ".join(r.name for r in u.roles.all()) or "-"], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Utilisateurs et membres", "headers": ["Nom", "Matricule", "Téléphone", "E-mail", "Statut", "Rôles"],
                  "rows": rows, "page": page, "search": True, "q": q, "status_filter": User.STATUS_CHOICES, "status": status})


@perm_required("users.manage")
def user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    old = (u.account_status, ",".join(sorted(u.roles.values_list("code", flat=True))))
    form = UserAdminForm(request.POST or None, request.FILES or None, instance=u)  # request.FILES : sinon la photo est ignorée
    had_photo = bool(u.photo)
    if request.method == "POST" and form.is_valid():
        if u.pk == request.user.pk and "super_admin" not in [r.code for r in form.cleaned_data["roles"]] and not u.is_superuser:
            messages.error(request, "Vous ne pouvez pas retirer votre propre rôle de super administrateur.")
        else:
            user = form.save(commit=False)
            user.is_active = user.account_status != User.DISABLED
            user.save()
            form.save_m2m()
            new = (user.account_status, ",".join(sorted(user.roles.values_list("code", flat=True))))
            log(request.user, "utilisateur_modifie", f"user:{u.pk}", old=old, new=new, request=request)
            if old[1] != new[1]:
                log(request.user, "modification_role", f"user:{u.pk}", old=old[1], new=new[1], request=request)
            if "photo" in form.changed_data and user.photo:
                log(request.user, "photo_membre_modifiee", f"user:{u.pk}", request=request)
                messages.success(request, "Utilisateur mis à jour. Photo " + ("remplacée." if had_photo else "ajoutée."))
            else:
                messages.success(request, "Utilisateur mis à jour.")
            return redirect("gestion:users")
    return render(request, "gestion/form.html", {"form": form, "title": f"Gérer {u.full_name} ({u.matricule})", "back": "gestion:users", "subject": u, "multipart": True})
