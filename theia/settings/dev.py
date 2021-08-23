# -*- coding: utf-8 -*-
import environ

from .base import *

env = environ.Env()
environ.Env.read_env(".env.dev")


SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-secret-key")

TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

# Celery Beat Settings
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
