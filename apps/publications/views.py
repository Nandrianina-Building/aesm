from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.core.permissions import member_required, user_has_perm

from .forms import CommentForm
from .models import Comment, CommentReport, Like, Publication, PublicationCategory


def live_publications(user):
    now = timezone.now()
    qs = Publication.objects.filter(
        Q(status=Publication.PUBLISHED, publish_at__isnull=True) | Q(status__in=[Publication.PUBLISHED, Publication.SCHEDULED], publish_at__lte=now))
    if not (user.is_authenticated and (user.is_active_member or user.is_staff_member)):
        qs = qs.filter(visibility="public")
    return qs


def publication_list(request):
    qs = (live_publications(request.user).select_related("category").prefetch_related("images")
          .annotate(n_likes=Count("likes", distinct=True),
                    n_comments=Count("comments", filter=Q(comments__is_hidden=False), distinct=True))
          .order_by("-pinned", "-publish_at", "-created_at"))
    cat = request.GET.get("categorie")
    if cat:
        qs = qs.filter(category_id=cat)
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    # Catégories : photo de la catégorie, sinon image de sa dernière actualité visible, sinon initiales
    categories = list(PublicationCategory.objects.all())
    live = live_publications(request.user).prefetch_related("images")
    for c in categories:
        c.thumb = c.image.url if c.image else ""
        if not c.thumb:
            last = next((p for p in live.filter(category=c).order_by("-publish_at", "-created_at")[:5] if p.cover_url), None)
            c.thumb = last.cover_url if last else ""
    liked = set()
    if request.user.is_authenticated:
        liked = set(Like.objects.filter(user=request.user, publication__in=[p.pk for p in page]).values_list("publication_id", flat=True))
    return render(request, "publications/list.html", {"page": page, "categories": categories, "cat": cat,
                                                      "can_manage_pubs": user_has_perm(request.user, "publications.manage"),
                                                      "liked_ids": liked, "qs_extra": f"categorie={cat}" if cat else ""})


def publication_detail(request, slug):
    pub = get_object_or_404(live_publications(request.user), slug=slug)
    liked = request.user.is_authenticated and pub.likes.filter(user=request.user).exists()
    comments = pub.comments.select_related("user")
    if not user_has_perm(request.user, "comments.moderate"):
        comments = comments.filter(is_hidden=False)
    return render(request, "publications/detail.html", {
        "pub": pub, "liked": liked, "comments_total": pub.comments.filter(is_hidden=False).count(), "likes_count": pub.likes.count(), "comments": comments, "form": CommentForm(),
        "can_moderate": user_has_perm(request.user, "comments.moderate")})


def _toggle_response(request, pub, message, level="success"):
    from django.http import JsonResponse
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "pinned": pub.pinned, "locked": pub.visibility == "members",
                             "message": message, "level": level})
    getattr(messages, level)(request, message)
    return redirect(request.POST.get("next") or "publications:list")


@member_required
@require_POST
def toggle_pin(request, slug):
    """Épingler / désépingler une actualité (réservé à la gestion des publications)."""
    from django.core.exceptions import PermissionDenied
    from apps.audit.services import log
    if not user_has_perm(request.user, "publications.manage"):
        raise PermissionDenied
    pub = get_object_or_404(Publication, slug=slug)
    pub.pinned = not pub.pinned
    pub.save(update_fields=["pinned"])
    log(request.user, "publication_epinglee" if pub.pinned else "publication_desepinglee", f"publication:{pub.pk}", request=request)
    msg = ("Actualité épinglée : elle s'affiche désormais en haut du fil des actualités."
           if pub.pinned else "Épinglage retiré : l'actualité reprend sa place normale dans le fil.")
    return _toggle_response(request, pub, msg)


@member_required
@require_POST
def toggle_lock(request, slug):
    """Basculer la visibilité : publique <-> réservée aux membres (cadenas)."""
    from django.core.exceptions import PermissionDenied
    from apps.audit.services import log
    if not user_has_perm(request.user, "publications.manage"):
        raise PermissionDenied
    pub = get_object_or_404(Publication, slug=slug)
    pub.visibility = "public" if pub.visibility == "members" else "members"
    pub.save(update_fields=["visibility"])
    log(request.user, "publication_visibilite", f"publication:{pub.pk}", new=pub.visibility, request=request)
    msg = ("Actualité verrouillée : seuls les membres connectés peuvent la voir."
           if pub.visibility == "members" else "Actualité déverrouillée : elle est visible par tous les visiteurs.")
    return _toggle_response(request, pub, msg)


@member_required
@require_POST
def like(request, slug):
    pub = get_object_or_404(live_publications(request.user), slug=slug)
    obj, created = Like.objects.get_or_create(publication=pub, user=request.user)
    if not created:
        obj.delete()
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(nxt)
    return redirect("publications:detail", slug)


@member_required
@require_POST
def comment_add(request, slug):
    pub = get_object_or_404(live_publications(request.user), slug=slug)
    if not pub.comments_enabled:
        messages.error(request, "Les commentaires sont désactivés pour cette publication.")
        return redirect("publications:detail", slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.publication, c.user = pub, request.user
        c.save()
    return redirect("publications:detail", slug)


@member_required
def comment_edit(request, pk):
    c = get_object_or_404(Comment, pk=pk, user=request.user)  # un membre ne modifie que ses commentaires (RG-09)
    form = CommentForm(request.POST or None, instance=c)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.edited = True
        obj.save()
        return redirect("publications:detail", c.publication.slug)
    return render(request, "publications/comment_edit.html", {"form": form, "pub": c.publication})


@member_required
@require_POST
def comment_delete(request, pk):
    c = get_object_or_404(Comment, pk=pk)
    if c.user_id != request.user.pk and not user_has_perm(request.user, "comments.moderate"):
        raise Http404
    slug = c.publication.slug
    c.delete()
    return redirect("publications:detail", slug)


@member_required
@require_POST
def comment_report(request, pk):
    c = get_object_or_404(Comment, pk=pk)
    CommentReport.objects.get_or_create(comment=c, user=request.user)
    messages.info(request, "Commentaire signalé aux modérateurs.")
    return redirect("publications:detail", c.publication.slug)
