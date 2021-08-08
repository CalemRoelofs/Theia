# -*- coding: utf-8 -*-
import subprocess
from datetime import datetime

import dns.exception
import dns.resolver
import nmap3
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from requests.exceptions import SSLError
from requests.models import HTTPError

from .models import ProfileChangelog
from .models import Server
from .sslcheck import get_alt_names
from .sslcheck import get_certificate
from .sslcheck import get_common_name
from .sslcheck import get_issuer


@shared_task(name="port_scan", serializer="json")
def port_scan(server_id: int):
    server = Server.objects.get(id=server_id)
    nmap = nmap3.Nmap()
    # Aggressively scan (-T4) all 65535 ports (-p-)
    results = nmap.scan_top_ports(server.ip_address, args="-T4 -p-")
    if not results[server.ip_address]:
        raise RuntimeError(f"Could not find host {server.ip_address} in nmap scan!")

    open_ports = [
        p["portid"] for p in results[server.ip_address]["ports"] if p["state"] == "open"
    ]

    # save the results to the server's profile
    if open_ports == server.server_profile.open_ports:
        # If there's no change don't do anything
        pass
    else:
        log = ProfileChangelog(
            server_profile=server.server_profile,
            date_modified=datetime.now(),
            changed_field="open_ports",
            old_value=server.server_profile.open_ports,
            new_value=open_ports,
        )
        log.save()
        server.server_profile.open_ports = open_ports
        server.save()
    return None


@shared_task(name="dns_records", serializer="json")
def dns_records(server_id: int):
    server = Server.objects.get(id=server_id)
    dns_results = {
        "A": [],
        "CNAME": [],
        "MX": [],
        "TXT": [],
        "NS": [],
        "SOA": [],
        "SRV": [],
        "PTR": [],
    }

    for record in dns_results.keys():
        try:
            if record == "PTR":
                answer = dns.resolver.resolve(server.ip_address, record, lifetime=10)
            else:
                answer = dns.resolver.resolve(server.domain_name, record, lifetime=10)

            dns_results[record] = [a.to_text() for a in answer]

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            continue

    if dns_results == server.server_profile.dns_records:
        # If there's no change don't do anything
        pass
    else:
        log = ProfileChangelog(
            server_profile=server.server_profile,
            date_modified=datetime.now(),
            changed_field="dns_records",
            old_value=server.server_profile.dns_records,
            new_value=dns_results,
        )
        log.save()
        server.server_profile.dns_records = dns_results
        server.save()
    return None


@shared_task(name="ssl_certs", serializer="json")
def ssl_certs(server_id: int):
    server = Server.objects.get(id=server_id)
    hostinfo = get_certificate(server.domain_name, 443)
    ssl_results = {
        "common_name": get_common_name(hostinfo.cert),
        "SAN": get_alt_names(hostinfo.cert),
        "issuer": get_issuer(hostinfo.cert),
        "not_before": hostinfo.cert.not_valid_before,
        "not_after": hostinfo.cert.not_valid_after,
        "expired": not (
            hostinfo.cert.not_valid_before
            < datetime.now()
            < hostinfo.cert.not_valid_after
        ),
    }

    if ssl_results == server.server_profile.ssl_certs:
        # If there's no change don't do anything
        pass
    else:
        log = ProfileChangelog(
            server_profile=server.server_profile,
            date_modified=datetime.now(),
            changed_field="ssl_certs",
            old_value=server.server_profile.ssl_certs,
            new_value=ssl_results,
        )
        log.save()
        server.server_profile.ssl_certs = ssl_results
        server.save()
    return None


@shared_task(name="get_headers", serializer="json")
def get_headers(server_id: int):
    logger = get_task_logger(__name__)
    logger.info(f"Task started, getting server_ID {server_id}")
    print("Started task!")
    logger.critical("HELP")
    server = Server.objects.get(id=server_id)
    logger.info(f"Got server {server.name} from database")
    # Try making a HEAD request first and if it fails, do a GET request
    try:
        response = requests.head(f"https://{server.domain_name}", timeout=3)
        response.raise_for_status()
    except SSLError:
        response = requests.head(f"http://{server.domain_name}", timeout=3)
    except HTTPError:
        response = requests.get(f"https://{server.domain_name}", timeout=3)

    logger.info(response.headers)

    if response.headers == server.server_profile.security_headers:
        logger.info("Not updating headers!")
        pass
    else:
        logger.info("Updating headers!")
        log = ProfileChangelog(
            server_profile=server.server_profile,
            date_modified=datetime.now(),
            changed_field="ssl_certs",
            old_value=server.server_profile.security_headers,
            new_value=response.headers,
        )
        log.save()
        server.server_profile.security_headers = response.headers
        server.save()
    return None


@shared_task(name="ping")
def ping(server_id: int):
    server = Server.objects.get(id=server_id)
    ping = subprocess.Popen(
        ["ping", "-n", "30", server.ip_address],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output_bytes, error = ping.communicate()
    out = output_bytes.decode("utf-8").lower()
    if "unreachable" in out or "failure" in out:
        server.reachable = False
    server.reachable = True
    stats = out.split("\n")[-2].strip().split(",")
    latency_results = [v.split(" ")[-1] for v in stats]
    return latency_results
