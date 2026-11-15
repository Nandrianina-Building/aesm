from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Jeton de confirmation d'e-mail : indépendant de la dernière connexion (sinon le lien casse dès qu'on se connecte)."""
    key_salt = "apps.accounts.EmailVerificationTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email}{user.email_verified}{timestamp}"


email_token_generator = EmailVerificationTokenGenerator()
