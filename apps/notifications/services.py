from .models import Notification


def notify(user, kind, title, message="", url=""):
    if user is None:
        return None
    return Notification.objects.create(user=user, kind=kind, title=title[:150], message=message, url=url)


def notify_many(users, kind, title, message="", url=""):
    Notification.objects.bulk_create(
        [Notification(user=u, kind=kind, title=title[:150], message=message, url=url) for u in users])


def notify_role(role_codes, kind, title, message="", url=""):
    from apps.accounts.models import User
    users = User.objects.filter(roles__code__in=role_codes, is_active=True).distinct()
    notify_many(users, kind, title, message, url)
