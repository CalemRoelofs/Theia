# -*- coding: utf-8 -*-
from django.apps import AppConfig


class SentinelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sentinel"

    def ready(self):
        import sentinel.signals
