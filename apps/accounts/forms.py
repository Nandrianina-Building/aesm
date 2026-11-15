import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from apps.core.antispam import AntiSpamMixin
from apps.core.utils import get_setting

from .models import User

PHONE_RE = re.compile(r"^\+?[0-9 ]{9,18}$")


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Matricule ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé. Contactez le bureau.",
    }
    username = forms.CharField(label="Matricule", widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username", "autocapitalize": "characters"}))

    def clean_username(self):
        return self.cleaned_data["username"].strip().upper()


class RegisterForm(AntiSpamMixin, forms.ModelForm):
    accept_terms = forms.BooleanField(
        label="Conditions d'utilisation",
        error_messages={"required": "Vous devez accepter les conditions d'utilisation pour créer un compte."})
    accept_privacy = forms.BooleanField(
        label="Confidentialité et RGPD",
        error_messages={"required": "Vous devez accepter la politique de confidentialité et le traitement de vos données (RGPD)."})
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, strip=False,
                                help_text="12 caractères minimum, pas de mot de passe courant.")
    password2 = forms.CharField(label="Confirmation du mot de passe", widget=forms.PasswordInput, strip=False)

    class Meta:
        model = User
        fields = ["last_name", "first_name", "matricule", "email", "phone", "sex", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.urls import reverse
        from django.utils.html import format_html
        self.fields["accept_terms"].label = format_html(
            "J'ai lu et j'accepte les <a href=\"{}\" target=\"_blank\" rel=\"noopener\">Conditions d'utilisation</a>.",
            reverse("core:terms"))
        self.fields["accept_privacy"].label = format_html(
            "J'ai lu la <a href=\"{}\" target=\"_blank\" rel=\"noopener\">politique de Confidentialité et RGPD</a> "
            "et j'accepte que mes données personnelles soient traitées par l'AESM pour la gestion de mon compte et de mon adhésion.",
            reverse("core:privacy"))
        self.order_fields([f for f in self.fields if f not in ("accept_terms", "accept_privacy")] + ["accept_terms", "accept_privacy"])
        self.fields["email"].required = True  # nécessaire pour l'e-mail de confirmation
        self.fields["photo"].required = get_setting("require_photo", "0") == "1"
        self.fields["sex"].required = False
        attrs = {"last_name": {"autocomplete": "family-name"}, "first_name": {"autocomplete": "given-name"},
                 "matricule": {"autocomplete": "username", "autocapitalize": "characters", "maxlength": 30},
                 "email": {"autocomplete": "email", "inputmode": "email"},
                 "phone": {"autocomplete": "tel", "inputmode": "tel", "pattern": r"\+?[0-9 ]{9,18}",
                           "title": "Exemple : 034 12 345 67"},
                 "password1": {"autocomplete": "new-password", "minlength": 12},
                 "password2": {"autocomplete": "new-password", "minlength": 12}}
        self.fields["phone"].widget.input_type = "tel"
        for name, a in attrs.items():
            self.fields[name].widget.attrs.update(a)

    def clean_matricule(self):
        m = self.cleaned_data["matricule"].strip().upper()
        if User.objects.filter(matricule=m).exists():
            raise forms.ValidationError("Ce matricule est déjà associé à un compte.")
        return m

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            return None
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Numéro de téléphone invalide.")
        normalized = phone.replace(" ", "")
        if User.objects.exclude(account_status=User.REFUSED).filter(phone=normalized).exists():
            raise forms.ValidationError("Ce numéro est déjà utilisé par un autre compte (doublon détecté).")
        return normalized

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        elif p1:
            candidate = User(matricule=data.get("matricule", ""), first_name=data.get("first_name", ""),
                             last_name=data.get("last_name", ""), email=data.get("email"))
            try:
                password_validation.validate_password(p1, candidate)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.account_status = User.ACTIVE  # inscription = membre actif (pas de validation manuelle)
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["last_name", "first_name", "email", "phone", "sex", "photo"]
        # FileInput (et non ClearableFileInput) : la photo est privée, son URL ne doit jamais être générée par le widget
        widgets = {"photo": forms.FileInput(attrs={"accept": "image/*"})}

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower() or None
        if email and User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Numéro de téléphone invalide.")
        normalized = phone.replace(" ", "")
        if User.objects.exclude(pk=self.instance.pk).exclude(account_status=User.REFUSED).filter(phone=normalized).exists():
            raise forms.ValidationError("Ce numéro est déjà utilisé par un autre compte.")
        return normalized

    def save(self, commit=True):
        old_email = User.objects.get(pk=self.instance.pk).email
        user = super().save(commit=False)
        if user.email != old_email:
            user.email_verified = False
        if commit:
            user.save()
        return user


class UserAdminForm(forms.ModelForm):
    """Gestion d'un membre par un administrateur : statut, rôles et photo d'identité."""
    class Meta:
        model = User
        fields = ["account_status", "roles", "photo"]
        widgets = {"roles": forms.CheckboxSelectMultiple,
                   "photo": forms.FileInput(attrs={"accept": "image/*", "data-preview": "1"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].help_text = "JPG ou PNG, 3 Mo maximum. Laissez vide pour conserver la photo actuelle."
