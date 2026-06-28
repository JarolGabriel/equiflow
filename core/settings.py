import os
import ssl
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv("DEBUG", "False") == "True"

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        import secrets

        SECRET_KEY = "dev-only-" + secrets.token_hex(32)
    else:
        raise ValueError("SECRET_KEY must be set in production environment")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0").split(",")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "channels",
    "drf_spectacular",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "apps.market_data",
    "apps.users",
    "apps.investments",
    "apps.alerts",
    "apps.payments",
]

ASGI_APPLICATION = "core.asgi.application"
WSGI_APPLICATION = "core.wsgi.application"


REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


if (
    not DEBUG
    and REDIS_URL.startswith("redis://")
    and "render.com" in os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
):
    REDIS_URL = REDIS_URL.replace("redis://", "rediss://")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    f"{REDIS_URL}&ssl_cert_reqs=none"
                    if "?" in REDIS_URL
                    else f"{REDIS_URL}?ssl_cert_reqs=none"
                )
                if REDIS_URL.startswith("rediss")
                else REDIS_URL
            ],
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
    }
}


DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG or "supabase" in DATABASE_URL,
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{v}"}
    for v in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "equiflow-auth",
    "JWT_AUTH_REFRESH_COOKIE": "equiflow-refresh-token",
    "JWT_AUTH_HTTPONLY": False,
    "LOGOUT_ON_PASSWORD_CHANGE": True,
    "USER_DETAILS_SERIALIZER": "dj_rest_auth.serializers.UserDetailsSerializer",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "EquiFlow API",
    "DESCRIPTION": "Financial Portfolio Manager",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "POSTPROCESSING_MODS": [
        "drf_spectacular.preprocessing.filter_none",
    ],
}


ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True

ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True


ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.users.adapters.CustomSocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = "none"


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=60)}

# --- Celery ---


CELERY_BROKER_URL = REDIS_URL


if REDIS_URL.startswith("rediss"):
    CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}
    CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}

    if "ssl_cert_reqs" not in CELERY_BROKER_URL:
        separator = "&" if "?" in CELERY_BROKER_URL else "?"
        CELERY_BROKER_URL = f"{REDIS_URL}{separator}ssl_cert_reqs=none"

CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

SITE_ID = 2
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# if not DEBUG:
#     RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
#     if RENDER_EXTERNAL_HOSTNAME:
#         ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
#         CSRF_TRUSTED_ORIGINS = [f"https://{RENDER_EXTERNAL_HOSTNAME}"]
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
#     SECURE_SSL_REDIRECT = True

CSRF_TRUSTED_ORIGINS = []
if not DEBUG:
    # Capturamos el hostname de Azure (y mantenemos el de Render por si acaso)
    AZURE_HOSTNAME = os.environ.get("WEBSITE_HOSTNAME")
    RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if AZURE_HOSTNAME:
        ALLOWED_HOSTS.append(AZURE_HOSTNAME)
        CSRF_TRUSTED_ORIGINS.append(f"https://{AZURE_HOSTNAME}")

    if RENDER_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_HOSTNAME)
        CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOSTNAME}")

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True


# --- CORS (frontend en Vercel / local) ---
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# --- Email set ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True


EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = f"EquiFlow <{EMAIL_HOST_USER}>"
