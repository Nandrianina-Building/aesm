import secrets

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

from .models import SiteSetting

DEFAULT_SETTINGS = {
    "association_name": ("Association des Étudiants en Sociologie de Madagascar", "Nom de l'association"),
    "association_short": ("AESM", "Sigle"),
    "contact_email": ("contact@aesm.mg", "E-mail de contact"),
    "contact_phone": ("+261 00 00 000 00", "Téléphone de contact"),
    "contact_address": ("Université d'Antananarivo, Madagascar", "Adresse"),
    "facebook_url": ("", "Page Facebook"),
    "opening_balance": ("0", "Solde initial de la caisse (Ar)"),
    "membership_validity_months": ("12", "Durée de validité de l'adhésion (mois)"),
    "max_document_mb": ("10", "Taille maximale d'un document (Mo)"),
    "event_cancel_hours": ("24", "Annulation possible jusqu'à X heures avant l'événement"),
    "analytics_id": ("", "Google Analytics : identifiant de mesure (G-XXXXXXX). Vide = aucun suivi ni bannière cookies"),
    "require_email": ("0", "E-mail obligatoire à l'inscription (1 = oui)"),
    "require_photo": ("0", "Photo obligatoire à l'inscription (1 = oui)"),
}


def get_setting(key, default=None):
    cached = cache.get(f"setting:{key}")
    if cached is not None:
        return cached
    try:
        value = SiteSetting.objects.get(key=key).value
    except SiteSetting.DoesNotExist:
        value = DEFAULT_SETTINGS.get(key, (default, ""))[0]
    cache.set(f"setting:{key}", value, 60)
    return value


def get_int_setting(key, default=0):
    try:
        return int(get_setting(key, default))
    except (TypeError, ValueError):
        return default


def client_ip(request):
    """Adresse du client. Derrière nginx, REMOTE_ADDR vaut 127.0.0.1 : on lit alors la DERNIÈRE valeur de
    X-Forwarded-For (celle ajoutée par notre propre proxy), jamais la première (falsifiable par le client)."""
    remote = request.META.get("REMOTE_ADDR", "0.0.0.0")
    if getattr(settings, "TRUST_X_FORWARDED_FOR", False):
        import ipaddress
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[-1].strip()
        try:
            return str(ipaddress.ip_address(forwarded))
        except ValueError:
            pass
    return remote


def is_rate_limited(request, scope, limit, window=60):
    """Limitation simple de débit par IP (vérification publique de QR, contact...)."""
    key = f"rl:{scope}:{client_ip(request)}"
    added = cache.add(key, 1, window)
    if added:
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, window)
        return False
    return count > limit


def too_many_requests():
    from django.template.loader import render_to_string
    return HttpResponse(render_to_string("429.html"), status=429)


def random_token(n=24):
    return secrets.token_urlsafe(n)


def format_ariary(value):
    try:
        return f"{int(value):,}".replace(",", " ") + " Ar"
    except (TypeError, ValueError):
        return f"{value} Ar"
