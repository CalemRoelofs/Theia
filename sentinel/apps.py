# -*- coding: utf-8 -*-
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SentinelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sentinel"

    def ready(self):
        import sentinel.signals
        from sentinel.utils import is_redis_available

        if not is_redis_available(timeout=60):

            logger.error(
                "!!!!!!!!!!!!!!!!!!!!!!!!Redis service does not appear to be running, tasks will not be run!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )
