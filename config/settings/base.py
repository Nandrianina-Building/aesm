"""Paramètres communs à tous les environnements (AESM)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


def env(name, default=None):
    return os.environ.get(name, default)


def env_list(name, default=""):
    return [x.strip() for x in env(name, default).split(",") if x.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = False
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
SITE_URL = env("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "apps.core",
    "apps.accounts",
    "apps.audit",
    "apps.memberships",
    "apps.payments",
    "apps.certificates",
    "apps.publications",
    "apps.documents",
    "apps.events",
    "apps.finance",
    "apps.notifications",
    "apps.support",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.StaffSessionMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
        },
    },
]

# --- Base de données : MySQL par défaut (sqlite uniquement si DB_ENGINE=sqlite) ---
if env("DB_ENGINE", "mysql") == "sqlite":
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME", "aesm"),
            "USER": env("DB_USER", "root"),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "127.0.0.1"),
            "PORT": env("DB_PORT", "3306"),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_unicode_ci"},
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

LANGUAGE_CODE = "fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "core:home"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # images publiques uniquement (actualités, événements, bureau)
PRIVATE_ROOT = Path(env("PRIVATE_ROOT", str(BASE_DIR / "private")))  # fichiers privés, jamais servis directement

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# --- Sessions / cookies ---
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 2          # expiration après 2 h d'inactivité
SESSION_SAVE_EVERY_REQUEST = True
STAFF_SESSION_AGE = 60 * 30               # responsables : 30 min d'inactivité
X_FRAME_OPTIONS = "DENY"
CSRF_FAILURE_VIEW = "apps.core.views.csrf_failure"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# --- E-mail ---
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
# Sans EMAIL_HOST : les e-mails s'affichent dans la console (développement). Avec EMAIL_HOST : envoi réel (SMTP).
EMAIL_BACKEND = ("django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST
                 else "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "AESM <no-reply@aesm.mg>")

# --- Cache (limitation de débit, verrouillage de connexion) ---
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "aesm"}}

# --- Règles métier configurables (valeurs par défaut ; surchargeables via Paramètres) ---
CURRENCY = "MGA"
RESERVATION_HOLD_MINUTES = 60
MANUAL_PAYMENT_HOLD_HOURS = 48
LOGIN_MAX_FAILURES = 5
# Mettre TRUST_X_FORWARDED_FOR=1 UNIQUEMENT derrière nginx (gunicorn écoute sur 127.0.0.1) : sinon REMOTE_ADDR vaut 127.0.0.1 pour tous.
TRUST_X_FORWARDED_FOR = env("TRUST_X_FORWARDED_FOR", "0") == "1"
ANTISPAM_MIN_SECONDS = 3   # un humain met plus de 3 s à remplir un formulaire

# --- Paiements : "simulation" pour le moment, puis "tokipay" (voir docs/PAIEMENTS_TOKIPAY.md) ---
PAYMENT_PROVIDER = env("PAYMENT_PROVIDER", "simulation")
PAYMENT_SIMULATION_ENABLED = env("PAYMENT_SIMULATION_ENABLED", "1") == "1"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

from django.contrib.messages import constants as _m  # noqa: E402
MESSAGE_TAGS = {_m.ERROR: "danger"}
