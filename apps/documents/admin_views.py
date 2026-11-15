from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.audit.services import log
from apps.core.permissions import perm_required

from .forms import DocumentForm
from .models import Document


@perm_required("documents.manage")
def document_list(request):
    rows = []
    for d in Document.objects.select_related("category"):
        actions = [{"label": "Modifier", "url": reverse("gestion:document_edit", args=[d.pk])}]
        if d.status == "published":
            actions.append({"label": "Archiver", "url": reverse("gestion:document_archive", args=[d.pk]), "method": "post",
                            "confirm": "Archiver ce document ?"})
        rows.append({"cells": [d.title, d.get_doc_type_display(), d.category or "-", d.get_level_display(), d.get_visibility_display(),
                               d.get_status_display(), d.download_count], "actions": actions})
    return render(request, "gestion/list.html", {"title": "Documents pédagogiques", "headers": ["Titre", "Type", "Catégorie", "Niveau", "Visibilité", "Statut", "Téléchargements"],
                  "rows": rows, "create_url": reverse("gestion:document_create"), "create_label": "Ajouter un document"})


@perm_required("documents.manage")
def document_edit(request, pk=None):
    obj = get_object_or_404(Document, pk=pk) if pk else None
    form = DocumentForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        d = form.save(commit=False)
        if not d.uploaded_by_id:
            d.uploaded_by = request.user
        d.save()
        log(request.user, "document_modifie" if obj else "document_ajoute", f"document:{d.pk}", new=d.title, request=request)
        messages.success(request, "Document enregistré.")
        return redirect("gestion:documents")
    return render(request, "gestion/form.html", {"form": form, "title": "Document", "back": "gestion:documents", "multipart": True})


@perm_required("documents.manage")
@require_POST
def document_archive(request, pk):
    d = get_object_or_404(Document, pk=pk)
    d.status = Document.ARCHIVED
    d.save(update_fields=["status"])
    log(request.user, "document_archive", f"document:{d.pk}")
    return redirect("gestion:documents")
