from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import SITEMAPS

urlpatterns = [
    path("admin-aesm/", admin.site.urls),
    path("compte/", include("apps.accounts.urls")),
    path("espace/", include("apps.core.urls_dashboard")),
    path("espace/adhesion/", include("apps.memberships.urls")),
    path("espace/paiements/", include("apps.payments.urls")),
    path("espace/documents-officiels/", include("apps.certificates.urls_member")),
    path("espace/reservations/", include("apps.events.urls_member")),
    path("espace/finances/", include("apps.finance.urls_member")),
    path("espace/notifications/", include("apps.notifications.urls")),
    path("espace/reclamations/", include("apps.support.urls")),
    path("verification/", include("apps.certificates.urls_public")),
    path("actualites/", include("apps.publications.urls")),
    path("evenements/", include("apps.events.urls")),
    path("documents/", include("apps.documents.urls")),
    path("gestion/", include("apps.core.urls_gestion")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("", include("apps.core.urls")),
]
handler400 = "apps.core.views.error_400"
handler403 = "apps.core.views.error_403"
handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"

if settings.DEBUG:
    from apps.core.views import error_preview
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Aperçu : /apercu-erreur/404/ (aussi 403, 400, 429, 500 et 1403 = session expirée)
    urlpatterns += [path("apercu-erreur/<int:code>/", error_preview)]
