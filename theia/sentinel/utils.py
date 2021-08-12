# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.utils.timezone import now
from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask

from .models import ProfileChangelog
from .models import Server
from .models import ServerTask


def log_changes(server: Server, changed_field: str, new_value):
    # In an ideal scenario I'd use pattern matching for this
    # but I'm only able to pass the models fields to a dict
    # by value and not by reference so this is currently
    # the only way to do it.
    if changed_field == "open_ports":
        old_value = server.serverprofile.open_ports
        server.serverprofile.open_ports = new_value

    elif changed_field == "dns_records":
        old_value = server.serverprofile.dns_records
        server.serverprofile.dns_records = new_value

    elif changed_field == "ssl_certs":
        old_value = server.serverprofile.ssl_certs
        server.serverprofile.ssl_certs = new_value

    elif changed_field == "security_headers":
        old_value = server.serverprofile.security_headers
        server.serverprofile.security_headers = new_value

    elif changed_field == "is_up":
        old_value = server.serverprofile.is_up
        server.serverprofile.is_up = new_value

    elif changed_field == "latency":
        old_value = server.serverprofile.latency
        server.serverprofile.latency = new_value

    server.serverprofile.save()

    log = ProfileChangelog(
        server=server,
        changed_field=changed_field,
        old_value=old_value,
        new_value=new_value,
    )
    log.save()

    return None


def create_or_update_tasks(server: Server):
    """Creates or updates tasks that are mapped to a Server\n
    according to the server's check_* boolean fields.

    Args:
        server (Server): The Server to map the tasks against
    """
    interval, _ = IntervalSchedule.objects.get_or_create(
        every=server.scan_frequency_value, period=server.scan_frequency_period
    )
    args = json.dumps([server.id])

    if server.check_open_ports:
        open_ports_task = PeriodicTask(
            name=f"{server.name} - check_open_ports",
            task="port_scan",
            interval=interval,
            args=args,
            start_time=now(),
        )

        server_task, created = ServerTask.objects.get_or_create(
            server=server, task_name="open_ports"
        )

        # If there's no mapping of that server to that task
        if created:
            # Save the task and map it to the server
            open_ports_task.save()
            server_task.task = open_ports_task
            server_task.save()
        else:
            # Otherwise just update the interval
            server_task.task.interval = interval
            server_task.task.save()

    if server.check_security_headers:
        get_headers_task = PeriodicTask(
            name=f"{server.name} - check_security_headers",
            task="get_headers",
            interval=interval,
            args=args,
            start_time=now(),
        )

        server_task, created = ServerTask.objects.get_or_create(
            server=server, task_name="get_headers"
        )

        if created:
            get_headers_task.save()
            server_task.task = get_headers_task
            server_task.save()
        else:
            server_task.task.interval = interval
            server_task.task.save()

    if server.check_ssl_certs:
        ssl_certs_task = PeriodicTask(
            name=f"{server.name} - check_ssl_certs",
            task="ssl_certs",
            interval=interval,
            args=args,
            start_time=now(),
        )

        server_task, created = ServerTask.objects.get_or_create(
            server=server, task_name="ssl_certs"
        )

        if created:
            ssl_certs_task.save()
            server_task.task = ssl_certs_task
            server_task.save()
        else:
            server_task.task.interval = interval
            server_task.task.save()

    if server.check_dns_records:
        dns_records_task = PeriodicTask(
            name=f"{server.name} - check_dns_records",
            task="dns_records",
            interval=interval,
            args=args,
            start_time=now(),
        )

        server_task, created = ServerTask.objects.get_or_create(
            server=server, task_name="dns_records"
        )

        if created:
            dns_records_task.save()
            server_task.task = dns_records_task
            server_task.save()
        else:
            server_task.task.interval = interval
            server_task.task.save()

    return None
