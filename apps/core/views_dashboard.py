from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apps.events.models import Reservation
from apps.memberships.models import Membership
from apps.notifications.models import Notification
from apps.payments.models import ContributionDue, Payment
from apps.publications.views import live_publications


@login_required
def member_dashboard(request):
    u = request.user
    latest_membership = u.memberships.first()
    ctx = {
        "membership": latest_membership,
        "dues": ContributionDue.objects.filter(user=u, status="unpaid").select_related("contribution"),
        "payments": Payment.objects.filter(user=u).select_related("due__contribution", "reservation__event")[:5],
        "reservations": Reservation.objects.filter(user=u, status__in=("confirmed", "pending"), event__starts_at__gte=timezone.now()).select_related("event")[:5],
        "publications": live_publications(u)[:3],
        "notifications": Notification.objects.filter(user=u, is_read=False)[:5],
    }
    return render(request, "core/dashboard.html", ctx)
