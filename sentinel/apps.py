# -*- coding: utf-8 -*-
from django.apps import AppConfig
from utils import is_redis_available


class SentinelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sentinel"

    def ready(self):
        import sentinel.signals

        if not is_redis_available():
            raise RuntimeWarning(
                "Redis service does not appear to be running, tasks will not be run!"
            )
