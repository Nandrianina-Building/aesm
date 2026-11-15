import os

from django.db.models import F, Q
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from apps.core.permissions import user_has_perm

from .models import Document, DocumentCategory


def _visible(user):
    qs = Document.objects.filter(status=Document.PUBLISHED)
    if user.is_authenticated and (user.is_active_member or user_has_perm(user, "documents.manage")):
        return qs
    return qs.filter(visibility="public")


def document_list(request):
    qs = _visible(request.user).select_related("category")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("categorie", "")
    level = request.GET.get("niveau", "")
    dtype = request.GET.get("type", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if cat.isdigit():
        qs = qs.filter(category_id=cat)
    if level:
        qs = qs.filter(level=level)
    if dtype:
        qs = qs.filter(doc_type=dtype)
    page = Paginator(qs, 12).get_page(request.GET.get("page"))
    return render(request, "documents/list.html", {"page": page, "categories": DocumentCategory.objects.all(), "q": q, "cat": cat,
                  "level": level, "dtype": dtype, "levels": Document.LEVEL_CHOICES, "types": Document.TYPE_CHOICES})


def document_download(request, pk):
    """Téléchargement contrôlé : visibilité vérifiée côté serveur pour chaque accès (RG-10)."""
    doc = get_object_or_404(_visible(request.user), pk=pk)
    Document.objects.filter(pk=doc.pk).update(download_count=F("download_count") + 1)
    response = FileResponse(doc.file.open("rb"), content_type="application/pdf", as_attachment=True,
                            filename=f"{doc.title[:80]}.pdf".replace("/", "-").replace("\\", "-"))
    return response
