from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.audit.services import log
from apps.core.permissions import perm_required

from .forms import CategoryForm, PublicationForm
from .models import Comment, Publication, PublicationCategory, PublicationImage


@perm_required("publications.manage", "publications.view")
def publication_list(request):
    can = request.user.can("publications.manage")
    rows = []
    for p in Publication.objects.prefetch_related("images")[:300]:
        actions = []
        if can:
            actions = [{"label": "Modifier", "url": reverse("gestion:publication_edit", args=[p.pk])}]
            if p.status != "archived":
                actions.append({"label": "Archiver", "url": reverse("gestion:publication_archive", args=[p.pk]), "method": "post",
                                "confirm": "Archiver cette publication ?"})
        rows.append({"thumb": p.cover_url, "cells": [p.title, p.get_kind_display(), p.get_visibility_display(), p.get_status_display(), p.publish_at or "-",
                               "Oui" if p.pinned else ""], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Publications", "headers": ["Titre", "Type", "Visibilité", "Statut", "Publication", "Épinglée"],
                  "rows": rows, "create_url": reverse("gestion:publication_create") if can else None, "create_label": "Nouvelle publication"})


@perm_required("publications.manage")
def publication_edit(request, pk=None):
    obj = get_object_or_404(Publication, pk=pk) if pk else None
    form = PublicationForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        if not p.author_id:
            p.author = request.user
        if p.status == Publication.PUBLISHED and not p.publish_at:
            from django.utils import timezone
            p.publish_at = timezone.now()
        p.save()
        for img in form.cleaned_data.get("remove_images") or []:
            img.delete()
        start = p.images.count()
        for n, f in enumerate(form.cleaned_data.get("gallery") or []):
            PublicationImage.objects.create(publication=p, image=f, position=start + n)
        log(request.user, "publication_modifiee" if obj else "publication_creee", f"publication:{p.pk}", new=p.title)
        messages.success(request, "Publication enregistrée.")
        return redirect("gestion:publications")
    return render(request, "gestion/form.html", {"form": form, "title": "Publication", "back": "gestion:publications", "multipart": True,
                  "gallery_items": obj.images.all() if obj else [], "cover": obj.image if obj and obj.image else None})


@perm_required("publications.manage")
@require_POST
def publication_archive(request, pk):
    p = get_object_or_404(Publication, pk=pk)
    p.status = Publication.ARCHIVED
    p.save(update_fields=["status"])
    log(request.user, "publication_archivee", f"publication:{p.pk}")
    return redirect("gestion:publications")


@perm_required("comments.moderate")
def comment_moderation(request):
    rows = []
    for c in Comment.objects.select_related("user", "publication").prefetch_related("reports").order_by("-created_at")[:200]:
        actions = [{"label": "Démasquer" if c.is_hidden else "Masquer", "url": reverse("gestion:comment_hide", args=[c.pk]), "method": "post"},
                   {"label": "Supprimer", "url": reverse("gestion:comment_remove", args=[c.pk]), "method": "post", "cls": "danger",
                    "confirm": "Supprimer ce commentaire ?"}]
        rows.append({"avatar": c.user, "cells": [c.created_at, c.user.full_name, c.publication.title, c.body[:120], c.reports.count(),
                               "Masqué" if c.is_hidden else "Visible"], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Modération des commentaires", "headers": ["Date", "Auteur", "Publication", "Commentaire", "Signalements", "État"], "rows": rows})


@perm_required("comments.moderate")
@require_POST
def comment_hide(request, pk):
    c = get_object_or_404(Comment, pk=pk)
    c.is_hidden = not c.is_hidden
    c.save(update_fields=["is_hidden"])
    log(request.user, "commentaire_masque", f"comment:{c.pk}", new=c.is_hidden)
    return redirect("gestion:comments")


@perm_required("comments.moderate")
@require_POST
def comment_remove(request, pk):
    c = get_object_or_404(Comment, pk=pk)
    log(request.user, "commentaire_supprime", f"comment:{c.pk}", old=c.body[:200])
    c.delete()
    return redirect("gestion:comments")


@perm_required("publications.manage", "publications.view")
def category_list(request):
    can = request.user.can("publications.manage")
    rows = [{"thumb": c.image.url if c.image else "", "cells": [c.name, c.publication_set.count(), "Oui" if c.image else "Non (dernière image utilisée)"],
             "actions": [{"label": "Modifier", "url": reverse("gestion:category_edit", args=[c.pk])}] if can else []}
            for c in PublicationCategory.objects.all()]
    return render(request, "gestion/list.html", {"title": "Catégories d'actualités", "headers": ["Catégorie", "Publications", "Photo"], "rows": rows,
                  "create_url": reverse("gestion:category_create") if can else None, "create_label": "Nouvelle catégorie"})


@perm_required("publications.manage")
def category_edit(request, pk=None):
    obj = get_object_or_404(PublicationCategory, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        c = form.save()
        log(request.user, "categorie_modifiee" if obj else "categorie_creee", f"categorie:{c.pk}", new=c.name)
        messages.success(request, "Catégorie enregistrée" + (" avec sa photo." if c.image else "."))
        return redirect("gestion:categories")
    return render(request, "gestion/form.html", {"form": form, "title": "Catégorie d'actualités", "back": "gestion:categories", "multipart": True,
                  "cover": obj.image if obj and obj.image else None})
