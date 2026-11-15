from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.documents.views import _visible as visible_documents
from apps.events.views import _visible as visible_events
from apps.publications.views import live_publications

from .forms import ContactForm
from .models import Officer
from .utils import is_rate_limited, too_many_requests


def home(request):
    ctx = {
        "publications": live_publications(request.user).prefetch_related("images")[:3],
        "events": visible_events(request.user).filter(starts_at__gte=timezone.now())[:3],
        "documents": visible_documents(request.user).filter(visibility="public")[:4],
    }
    return render(request, "core/home.html", ctx)


def about(request):
    return render(request, "core/about.html", {"officers": Officer.objects.filter(is_archived=False).select_related("user")})


def bureau(request):
    return render(request, "core/bureau.html", {"current": Officer.objects.filter(is_archived=False).select_related("user"),
                                                 "archived": Officer.objects.filter(is_archived=True)})


def bureau_photo(request, public_id):
    officer = Officer.objects.filter(user__public_id=public_id, is_archived=False).select_related("user").first()
    if not officer or not officer.user.photo:
        raise Http404

    import mimetypes
    content_type = mimetypes.guess_type(officer.user.photo.name)[0] or "image/jpeg"
    response = FileResponse(officer.user.photo.open("rb"), content_type=content_type)
    response["Cache-Control"] = "public, max-age=3600"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def terms(request):
    return render(request, "legal/terms.html", {"updated": "13 novembre 2026"})


def privacy(request):
    return render(request, "legal/privacy.html", {"updated": "13 novembre 2026"})


def robots_txt(request):
    from django.conf import settings
    from django.http import HttpResponse
    lines = ["User-agent: *", "Disallow: /gestion/", "Disallow: /espace/", "Disallow: /compte/",
             "Disallow: /admin-aesm/", "Disallow: /verification/", "Allow: /", "",
             f"Sitemap: {settings.SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if is_rate_limited(request, "contact", 5, 300):
            return too_many_requests()
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé. Nous vous répondrons rapidement.")
            return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})


# ------------------------------------------------------------------ pages d'erreur personnalisées
def _standalone(request, template, status):
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    return HttpResponse(render_to_string(template), status=status)


def error_400(request, exception=None):
    return _standalone(request, "400.html", 400)


def error_403(request, exception=None):
    return render(request, "403.html", status=403)


def error_404(request, exception=None):
    return render(request, "404.html", status=404)


def error_500(request):
    return _standalone(request, "500.html", 500)  # sans contexte : doit fonctionner même si la base de données est en panne


def csrf_failure(request, reason=""):
    return _standalone(request, "403_csrf.html", 403)


def error_preview(request, code):
    """Aperçu des pages d'erreur en développement (DEBUG=True affiche sinon la page technique de Django)."""
    from django.http import Http404
    views = {400: error_400, 403: error_403, 404: error_404, 429: lambda r: _standalone(r, "429.html", 429),
             500: error_500, 1403: csrf_failure}
    if code not in views:
        raise Http404
    return views[code](request)
