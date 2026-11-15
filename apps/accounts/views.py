import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

from apps.audit.services import log
from apps.core.permissions import user_has_perm
from apps.core.utils import client_ip, get_setting, is_rate_limited, too_many_requests
from apps.notifications.services import notify

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User
from .tokens import email_token_generator


def _send_verification(request, user, welcome=False):
    """E-mail de confirmation (HTML + texte). `welcome=True` : message de bienvenue juste après l'inscription."""
    if not user.email:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    ctx = {"user": user, "welcome": welcome, "SITE_NAME": get_setting("association_short", "AESM"),
           "SITE_FULL_NAME": get_setting("association_name", ""),
           "verify_url": settings.SITE_URL + reverse("accounts:verify_email", args=[uid, token]),
           "space_url": settings.SITE_URL + reverse("dashboard:home")}
    subject = ("Bienvenue à l'AESM : confirmez votre adresse e-mail" if welcome
               else "AESM : confirmez votre adresse e-mail")
    msg = EmailMultiAlternatives(subject, render_to_string("emails/confirm.txt", ctx), None, [user.email])
    msg.attach_alternative(render_to_string("emails/confirm.html", ctx), "text/html")
    try:
        msg.send(fail_silently=False)
    except Exception:  # un incident SMTP ne doit jamais bloquer l'inscription
        logging.getLogger(__name__).exception("Envoi de l'e-mail de confirmation impossible")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and is_rate_limited(request, "register", 8, 900):
        return too_many_requests()
    if request.method == "POST" and form.is_valid():
        user = form.save()
        from apps.memberships.services import auto_enroll
        log(user, "cgu_acceptees", user.matricule, request=request)  # preuve du consentement
        log(user, "rgpd_accepte", user.matricule, request=request)
        auto_enroll(user)  # membre actif immédiatement, sans validation d'un administrateur
        _send_verification(request, user, welcome=True)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Bienvenue ! Votre compte est actif : vous êtes membre. Un e-mail de confirmation vient de vous être envoyé.")
        return redirect("dashboard:home")
    return render(request, "accounts/register.html", {"form": form})


class ThrottledPasswordResetView(auth_views.PasswordResetView):
    """Limite les demandes (anti « e-mail bombing ») : 5 par IP / 15 min et 3 par adresse / 15 min."""

    def post(self, request, *args, **kwargs):
        import hashlib
        email = request.POST.get("email", "").strip().lower()
        mail_key = "pwreset-mail:" + hashlib.sha256(email.encode()).hexdigest()
        if is_rate_limited(request, "pwreset", 5, 900):
            return too_many_requests()
        if email:
            cache.add(mail_key, 0, 900)
            if cache.incr(mail_key) > 3:
                return too_many_requests()
        return super().post(request, *args, **kwargs)


class ThrottledLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def _key(self, request):
        ident = request.POST.get("username", "").strip().upper()
        return f"loginfail:{client_ip(request)}:{ident}"

    def post(self, request, *args, **kwargs):
        key = self._key(request)
        if cache.get(f"{key}:lock"):
            messages.error(request, "Trop de tentatives échouées. Réessayez plus tard.")
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._key(self.request)
        n = cache.get(key, 0) + 1
        cache.set(key, n, 3600)
        if n >= settings.LOGIN_MAX_FAILURES:
            delay = min(15 * 60 * 2 ** (n - settings.LOGIN_MAX_FAILURES), 6 * 3600)  # délai progressif
            cache.set(f"{key}:lock", True, delay)
        if n >= 3:
            log(None, "connexion_echec_suspecte", form.data.get("username", "")[:60], new=f"{n} échecs",
                result="échec", request=self.request)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._key(self.request))
        response = super().form_valid(form)
        messages.success(self.request, "Connexion réussie. Bienvenue !")
        if self.request.user.is_staff_member:
            log(self.request.user, "connexion_administrative", self.request.user.matricule, request=self.request)
        return response


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("core:home")


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        email_changed = "email" in form.changed_data
        user = form.save()
        if email_changed:
            _send_verification(request, user)
        messages.success(request, "Profil mis à jour.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def password_change(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # conserve la session courante, invalide les autres
        messages.success(request, "Mot de passe modifié.")
        return redirect("accounts:profile")
    for f in form.fields.values():
        f.widget.attrs["class"] = "form-control"
    return render(request, "accounts/password_change.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        user = User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None
    if user and email_token_generator.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        messages.success(request, "Adresse e-mail vérifiée.")
    else:
        messages.error(request, "Lien de vérification invalide ou expiré.")
    return redirect("core:home")


@login_required
@require_POST
def resend_verification(request):
    _send_verification(request, request.user)
    messages.info(request, "Un e-mail de confirmation vient d'être envoyé.")
    return redirect("accounts:profile")


@login_required
def photo(request, public_id):
    """Photo privée : propriétaire ou responsable autorisé uniquement (anti-IDOR)."""
    target = get_object_or_404(User, public_id=public_id)
    if target.pk != request.user.pk and not user_has_perm(request.user, "members.view"):
        raise Http404
    if not target.photo:
        raise Http404
    import mimetypes
    ctype = mimetypes.guess_type(target.photo.name)[0] or "image/jpeg"
    resp = FileResponse(target.photo.open("rb"), content_type=ctype)
    resp["Cache-Control"] = "private, max-age=3600"
    resp["X-Content-Type-Options"] = "nosniff"
    return resp
