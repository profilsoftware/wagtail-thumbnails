from __future__ import annotations

import tempfile
from pathlib import Path

SECRET_KEY = "test-secret-key-not-for-production"

DEBUG = False

ALLOWED_HOSTS = ["*"]

BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = tempfile.mkdtemp(prefix="wagtail-thumbnails-test-media-")
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.sessions",
    "taggit",
    "rest_framework",
    "wagtail.users",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail_thumbnails",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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

ROOT_URLCONF = "tests.urls"

USE_TZ = True
TIME_ZONE = "UTC"

WAGTAIL_SITE_NAME = "Test"
WAGTAILADMIN_BASE_URL = "http://localhost"
