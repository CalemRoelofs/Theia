# -*- coding: utf-8 -*-
import uuid

from django.db.models.signals import post_delete
from django.dispatch import receiver
from sentinel.models import ServerTask


@receiver(post_delete, sender=ServerTask, dispatch_uid=str(uuid.uuid4()))
def delete_task(sender, instance, *args, **kwargs):
    if instance.task:
        instance.task.delete()
