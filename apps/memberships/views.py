from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ApplicationForm
from .models import Membership
from . import services


@login_required
def apply(request):
    memberships = request.user.memberships.all()
    form = ApplicationForm(request.POST or None)
    can_apply = request.user.account_status in ("pending", "refused", "active") and not any(
        m.status in ("pending", "verifying", "accepted", "suspended") for m in memberships) and request.user.is_active
    if request.method == "POST" and can_apply and form.is_valid():
        try:
            services.submit_application(request.user, form.cleaned_data["motivation"])
            messages.success(request, "Votre demande d'adhésion a été soumise.")
        except services.TransitionError as exc:
            messages.error(request, str(exc))
        return redirect("memberships:apply")
    return render(request, "memberships/apply.html", {"memberships": memberships, "form": form, "can_apply": can_apply})
