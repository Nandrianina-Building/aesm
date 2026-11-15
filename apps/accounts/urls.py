from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"
urlpatterns = [
    path("inscription/", views.register, name="register"),
    path("connexion/", views.ThrottledLoginView.as_view(), name="login"),
    path("deconnexion/", views.logout_view, name="logout"),
    path("profil/", views.profile, name="profile"),
    path("mot-de-passe/", views.password_change, name="password_change"),
    path("verification-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("verification-email/renvoyer/", views.resend_verification, name="resend_verification"),
    path("photo/<uuid:public_id>/", views.photo, name="photo"),
    path("mot-de-passe-oublie/", views.ThrottledPasswordResetView.as_view(
        template_name="accounts/password_reset.html", email_template_name="accounts/password_reset_email.txt",
        success_url=reverse_lazy("accounts:password_reset_done")), name="password_reset"),
    path("mot-de-passe-oublie/envoye/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reinitialisation/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete")), name="password_reset_confirm"),
    path("reinitialisation/terminee/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
]
