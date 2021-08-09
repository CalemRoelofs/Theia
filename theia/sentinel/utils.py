# -*- coding: utf-8 -*-
from datetime import datetime

from pytz import timezone

from .models import ProfileChangelog
from .models import Server

tz = timezone("Europe/Dublin")


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
        date_modified=datetime.now(tz),
        changed_field=changed_field,
        old_value=old_value,
        new_value=new_value,
    )
    log.save()

    return None
