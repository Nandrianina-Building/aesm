from django.conf import settings


class SecurityHeadersMiddleware:
    """En-têtes de sécurité dont une politique CSP adaptée (Bootstrap via jsDelivr)."""

    PRIVATE_PREFIXES = ("/gestion/", "/espace/", "/compte/", "/admin-aesm/", "/verification/")
    CSP_BASE = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
    )
    # Google Analytics n'est autorisé que si un identifiant est configuré (et chargé seulement après consentement)
    CSP_ANALYTICS = (
        "default-src 'self'; img-src 'self' data: https://www.google-analytics.com https://*.google-analytics.com; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' https://www.googletagmanager.com; font-src 'self'; "
        "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        from .utils import get_setting
        csp = self.CSP_ANALYTICS if (get_setting("analytics_id", "") or "").strip() else self.CSP_BASE
        response.setdefault("Content-Security-Policy", csp)
        if request.path.startswith(self.PRIVATE_PREFIXES):
            response.setdefault("X-Robots-Tag", "noindex, nofollow")
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response


class StaffSessionMiddleware:
    """Expiration plus courte de la session pour les comptes administratifs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff_member:
            request.session.set_expiry(settings.STAFF_SESSION_AGE)
        return self.get_response(request)
