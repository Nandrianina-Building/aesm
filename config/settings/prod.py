from .base import *  # noqa

DEBUG = False
# Sur PythonAnywhere : activer « Force HTTPS » dans l'onglet Web ; mettre SECURE_SSL_REDIRECT=0 si boucle de redirection
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", "1") == "1"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# HSTS : valeur courte pendant les tests (3600 = 1 h) ; 31536000 (1 an) seulement pour le site définitif
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS >= 31536000
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS >= 31536000
CSRF_TRUSTED_ORIGINS = [SITE_URL]

if SECRET_KEY.startswith(("dev-insecure", "change")) or len(SECRET_KEY) < 50:
    raise RuntimeError("DJANGO_SECRET_KEY doit être une vraie clé secrète d'au moins 50 caractères (pas la valeur de .env.example).")
if (PAYMENT_SIMULATION_ENABLED or PAYMENT_PROVIDER == "simulation") and env("ALLOW_PAYMENT_SIMULATION_IN_PROD", "0") != "1":
    raise RuntimeError("Paiement SIMULÉ actif en production : un membre pourrait se déclarer lui-même « payé ». "
                       "Pour une V1 de TEST uniquement : ALLOW_PAYMENT_SIMULATION_IN_PROD=1 dans .env. "
                       "Sinon : PAYMENT_SIMULATION_ENABLED=0 et brancher un vrai prestataire.")
if not env("EMAIL_HOST", ""):
    raise RuntimeError("EMAIL_HOST est vide : les e-mails de confirmation ne partiraient pas. Renseignez EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD dans .env.")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True

# Cache partagé entre processus Gunicorn : python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "aesm_cache",
    }
}
