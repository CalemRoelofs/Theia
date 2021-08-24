# -*- coding: utf-8 -*-
from .base import *
from theia.settings.dev import ALLOWED_HOSTS

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
SECRET_KEY = "CI-SECRET-KEY"
DEBUG = False
ALLOWED_HOSTS = ["*"]
STATICFILES_DIRS = [BASE_DIR / "static"]

# Celery Beat Settings
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
