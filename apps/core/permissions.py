"""RBAC : rôles -> permissions (principe du moindre privilège).

Modifier ce fichier suffit à ajuster les droits d'un rôle (points 3.x / 16 du cahier des charges).
"""
from functools import wraps

from django.core.exceptions import PermissionDenied

SUPER_ADMIN = "super_admin"
PRESIDENT = "president"
TREASURER = "treasurer"
SECRETARY = "secretary"
EVENT_MANAGER = "event_manager"

ROLE_CHOICES = [
    (SUPER_ADMIN, "Super administrateur"),
    (PRESIDENT, "Président"),
    (TREASURER, "Trésorier"),
    (SECRETARY, "Secrétaire"),
    (EVENT_MANAGER, "Responsable événementiel"),
]

ROLE_PERMISSIONS = {
    SUPER_ADMIN: {"*"},
    PRESIDENT: {
        "dashboard.view", "members.view", "memberships.view", "payments.view", "finance.view",
        "finance.validate", "reports.validate", "publications.view", "events.view", "audit.view",
        "contributions.view",
    },
    TREASURER: {
        "dashboard.view", "payments.view", "payments.verify", "payments.refund", "contributions.view",
        "contributions.manage", "finance.view", "finance.manage", "reports.manage", "reports.publish",
        "quitus.manage", "members.view",
    },
    SECRETARY: {
        "dashboard.view", "members.view", "memberships.manage", "publications.manage",
        "documents.manage", "comments.moderate", "support.manage", "officers.manage",
        "notifications.send", "contact.manage",
    },
    EVENT_MANAGER: {
        "dashboard.view", "events.manage", "reservations.manage", "tickets.scan", "events.view",
    },
}

# Permissions réservées strictement au super administrateur
SUPER_ONLY = {"users.manage", "roles.manage", "settings.manage", "security.manage"}


def user_has_perm(user, code):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    roles = set(user.roles.values_list("code", flat=True))
    if SUPER_ADMIN in roles:
        return True
    if code in SUPER_ONLY:
        return False
    for role in roles:
        perms = ROLE_PERMISSIONS.get(role, set())
        if code in perms or "*" in perms:
            return True
    return False


def _redirect_to_login(request):
    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(request.get_full_path())


def perm_required(*codes):
    """Décorateur de vue : contrôle côté serveur (jamais seulement dans les templates)."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _redirect_to_login(request)
            if not any(user_has_perm(request.user, c) for c in codes):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def member_required(view):
    """Compte authentifié ET membre actif (RG-02, RG-14)."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)
        if not request.user.is_active_member:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper
