import time

from django.conf import settings

from .permissions import user_has_perm
from .utils import get_setting


_ASSET_V = str(int(time.time()))  # change à chaque redémarrage du serveur : le navigateur recharge le CSS/JS


def site(request):
    ctx = {
        "SITE_NAME": get_setting("association_short", "AESM"),
        "SITE_FULL_NAME": get_setting("association_name", ""),
        "CONTACT_EMAIL": get_setting("contact_email", ""),
        "CONTACT_PHONE": get_setting("contact_phone", ""),
        "CONTACT_ADDRESS": get_setting("contact_address", ""),
        "FACEBOOK_URL": get_setting("facebook_url", ""),
        "PAYMENT_SIMULATION": settings.PAYMENT_SIMULATION_ENABLED and settings.PAYMENT_PROVIDER == "simulation",
        "SITE_URL": settings.SITE_URL,
        "ASSET_V": _ASSET_V,
        "ANALYTICS_ID": (get_setting("analytics_id", "") or "").strip(),
        "CANONICAL_URL": settings.SITE_URL + request.path,
        "unread_notifications": 0,
        "can_access_gestion": False,
    }
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        from apps.notifications.models import Notification
        ctx["unread_notifications"] = Notification.objects.filter(user=user, is_read=False).count()
        ctx["can_access_gestion"] = user.is_staff_member or user.is_superuser
        ctx["perm"] = {c: user_has_perm(user, c) for c in (
            "members.view", "memberships.manage", "contributions.view", "payments.view", "quitus.manage",
            "publications.manage", "comments.moderate", "documents.manage", "events.manage", "reservations.manage",
            "tickets.scan", "finance.view", "finance.manage", "reports.manage", "reports.validate",
            "notifications.send", "support.manage", "officers.manage", "audit.view", "users.manage",
            "settings.manage", "contact.manage", "dashboard.view")}
    return ctx
