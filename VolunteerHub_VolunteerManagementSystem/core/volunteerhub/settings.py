# File: volunteerhub/settings.py
# Purpose:
#   Main configuration for the VolunteerHub Django project.
#   Includes Jet theme for admin styling and DRF for the API.
#   This version adds the scheduling app so Django can load its models.
# =====================================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-_no*d(!r#yf-$!d$(tat81s0p&19_g%(77ss^(k(fpco%$f&ic"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# CSRF and security settings for local development
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ---------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",      # Enables the REST API endpoints
    "signups",             # Local app handling volunteers, roles, etc.
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "volunteerhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Django will search these template folders first
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "signups" / "templates",
            BASE_DIR / "core" / "scheduling" / "templates",
        ],

        # This allows Django to find templates inside installed apps
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "volunteerhub.wsgi.application"

# ---------------------------------------------------------------------
# Database (SQLite for dev)
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internationalization
# Saskatoon local time (Saskatchewan - Central Standard Time, no DST)
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Regina"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Session configuration (30 minutes of inactivity)
# ---------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request to track activity

# Static and Media-
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------
# REST Framework configuration
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
