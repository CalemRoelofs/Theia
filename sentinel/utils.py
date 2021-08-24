# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

from celery import current_app
from django.utils.timezone import now
from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask
from kombu.utils.json import loads

from .alerts import send_alert
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

    else:
        raise RuntimeError(
            f"{server}: {changed_field} is not a valid option for changed_field"
        )

    server.serverprofile.save()

    changelog = ProfileChangelog(
        server=server,
        changed_field=changed_field,
        old_value=old_value,
        new_value=new_value,
    )
    changelog.save()

    message = f"""
    Alert: Change Detected!\n
    \tServer:       {changelog.server.name}\n
    \tService:      {changelog.changed_field}\n
    \tOld Value:    {changelog.old_value}\n
    \tNew Value:    {changelog.new_value}\n
    """
    if not server.contact_group:
        return None
    for endpoint in server.contact_group.alert_endpoints.all():
        send_alert(endpoint, changelog, message)
    return None


def manage_server_tasks(server: Server):
    """Creates or updates tasks that are mapped to a Server\n
    according to the server's check_* boolean fields.

    Args:
        server (Server): The Server to map the tasks against
    """
    current_app.loader.import_default_modules()
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

        save_server_task(server, open_ports_task, interval)

    elif not server.check_open_ports:
        delete_server_task(server, "port_scan")

    if server.check_security_headers:
        get_headers_task = PeriodicTask(
            name=f"{server.name} - check_security_headers",
            task="get_headers",
            interval=interval,
            args=args,
            start_time=now(),
        )

        save_server_task(server, get_headers_task, interval)

    elif not server.check_security_headers:
        delete_server_task(server, "get_headers")

    if server.check_ssl_certs:
        ssl_certs_task = PeriodicTask(
            name=f"{server.name} - check_ssl_certs",
            task="ssl_certs",
            interval=interval,
            args=args,
            start_time=now(),
        )

        save_server_task(server, ssl_certs_task, interval)

    elif not server.check_ssl_certs:
        delete_server_task(server, "ssl_certs")

    if server.check_dns_records:
        dns_records_task = PeriodicTask(
            name=f"{server.name} - check_dns_records",
            task="dns_records",
            interval=interval,
            args=args,
            start_time=now(),
        )

        save_server_task(server, dns_records_task, interval)

    elif not server.check_dns_records:
        delete_server_task(server, "dns_records")

    return None


def save_server_task(server: Server, task: PeriodicTask, interval: IntervalSchedule):
    """Intermediate function to save a created task, map it to a server
    and run it if necessary

    Args:
        server (Server): The Server to create the task for.
        task (PeriodicTask): The created task to be saved.
        interval (IntervalSchedule): The interval schedule for updating
                                        the task if it already exists.
    """
    server_task, created = ServerTask.objects.get_or_create(
        server=server, task_name=task.task
    )

    # If there's no mapping of that server to that task
    if created:
        # Save the task and map it to the server
        task.save()
        server_task.task = task
        server_task.save()
        _run_task_on_creation(task)
    else:
        # Otherwise just update the interval
        server_task.task.interval = interval
        server_task.task.save()

    return None


def delete_server_task(server: Server, task_name: str):
    try:
        server_task = ServerTask.objects.get(server=server, task_name=task_name)
        server_task.delete()
    except ServerTask.DoesNotExist:
        pass

    return None


def _run_task_on_creation(task: PeriodicTask):
    """Private function for use in manage_server_tasks


    Args:
        task (PeriodicTask): The task to run

    Returns:
        str : The ID of the task ran
    """

    current_app.loader.import_default_modules()
    task_args = loads(task.args)
    task_kwargs = loads(task.kwargs)
    celery_task = current_app.tasks.get(task.task)

    if task.queue and len(task.queue):
        task_id = celery_task.apply_async(
            args=task_args, kwargs=task_kwargs, queue=task.queue
        )
    else:
        task_id = celery_task.apply_async(args=task_args, kwargs=task_kwargs)

    return task_id
