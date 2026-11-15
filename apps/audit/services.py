from apps.core.utils import client_ip

from .models import AuditLog

SENSITIVE = ("password", "secret", "token", "api_key", "mot_de_passe")


def _clean(value):
    text = "" if value is None else str(value)
    low = text.lower()
    if any(s in low for s in SENSITIVE):
        return "[masqué]"
    return text[:2000]


def log(actor, action, resource="", old=None, new=None, result="succès", request=None):
    """Enregistre une opération sensible. `actor` peut être un utilisateur ou None."""
    ip = None
    if request is not None:
        ip = client_ip(request)
        if actor is None and getattr(request, "user", None) is not None and request.user.is_authenticated:
            actor = request.user
    user = actor if actor is not None and getattr(actor, "pk", None) else None
    return AuditLog.objects.create(
        user=user,
        user_label=(str(user) if user else "système"),
        action=action,
        resource=str(resource)[:200],
        old_value=_clean(old),
        new_value=_clean(new),
        result=result,
        ip_address=ip,
    )
