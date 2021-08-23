# -*- coding: utf-8 -*-
import environ

from .base import *

env = environ.Env()
environ.Env.read_env(".env.prod")

# Throw an error if no secret key is configured
SECRET_KEY = env("DJANGO_SECRET_KEY")

# Override timezone if present
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}

# Celery Beat Settings
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
