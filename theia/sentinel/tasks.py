# -*- coding: utf-8 -*-
import platform
import subprocess
from collections import Counter
from datetime import datetime

import dns.exception
import dns.resolver
import nmap3
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from dns import reversename
from requests.exceptions import ConnectTimeout

from .constants import SECURITY_HEADERS_WHITELIST
from .models import Server
from .sslcheck import check_if_ssl
from .sslcheck import get_alt_names
from .sslcheck import get_certificate
from .sslcheck import get_common_name
from .sslcheck import get_issuer
from .utils import log_changes


logger = get_task_logger(__name__)


@shared_task(name="port_scan", serializer="json", max_retries=3, soft_time_limit=20)
def port_scan(server_id: int):
    try:
        server = Server.objects.get(id=server_id)
    except Server.DoesNotExist:
        return f"Server with id '{server_id}' does not exist!"

    logger.debug(f"Got server {server.name}")

    nmap = nmap3.Nmap()
    # Aggressively scan (-T4) all 65535 ports (-p-)
    results = nmap.scan_top_ports(server.ip_address, args="-T4 -p-")
    if not server.ip_address in results:
        message = f"Could not find host {server.ip_address} in nmap scan!"
        logger.critical(message)
        return message

    logger.info(f"Succesfully scanned {server.ip_address}")

    server.date_last_checked = now()
    server.save()

    open_ports = [
        p["portid"] for p in results[server.ip_address]["ports"] if p["state"] == "open"
    ]

    # save the results to the server's profile
    if open_ports == server.serverprofile.open_ports:
        return "SUCCESS"
    else:
        logger.info(f"Detected change, creating new changelog")
        log_changes(server, "open_ports", open_ports)
    return "SUCCESS"


@shared_task(name="dns_records", serializer="json", max_retries=3, soft_time_limit=60)
def dns_records(server_id: int):
    try:
        server = Server.objects.get(id=server_id)
    except Server.DoesNotExist:
        return f"Server with id '{server_id}' does not exist!"
    dns_records = {
        "A": [],
        "CNAME": [],
        "MX": [],
        "TXT": [],
        "NS": [],
        "SOA": [],
        "SRV": [],
        "PTR": [],
    }

    for record in dns_records.keys():
        try:
            if record == "PTR":
                addr = reversename.from_address(server.ip_address)
                answer = dns.resolver.resolve(addr, record, lifetime=10)
            else:
                answer = dns.resolver.resolve(server.domain_name, record, lifetime=10)

            dns_records[record] = [a.to_text() for a in answer]

        except dns.resolver.NoAnswer:
            continue
        except dns.resolver.NoNameservers:
            message = f"Could not resolve domain {server.domain_name} for {server}'s {record} record!"
            logger.error(message)
            return message
        except dns.exception.Timeout:
            message = (
                f"Request timed out when querying DNS for {server}'s {record} record!"
            )
            logger.error(message)
        except dns.resolver.NXDOMAIN:
            message = (
                f"The DNS query name does not exist for {server}'s {record} record!"
            )
            logger.error(message)

    server.date_last_checked = now()
    server.save()

    old_records = server.serverprofile.dns_records

    if not old_records:
        log_changes(server, "dns_records", dns_records)
        return "SUCCESS"

    for record in dns_records.keys():
        if Counter(dns_records[record]) == Counter(old_records[record]):
            continue
        else:
            log_changes(server, "dns_records", dns_records)
            break
    return "SUCCESS"


@shared_task(name="ssl_certs", serializer="json", max_retries=3, soft_time_limit=20)
def ssl_certs(server_id: int):
    try:
        server = Server.objects.get(id=server_id)
    except Server.DoesNotExist:
        return f"Server with id '{server_id}' does not exist!"
    try:
        hostinfo = get_certificate(server.domain_name, 443)
    except TimeoutError:
        return f"Failed to make SSL connection to {server.domain_name} for {server}!"

    ssl_results = {
        "Common Name": get_common_name(hostinfo.cert),
        "SAN": get_alt_names(hostinfo.cert),
        "Issuer": get_issuer(hostinfo.cert),
        "Not Before": hostinfo.cert.not_valid_before.strftime("%Y-%m-%d %H:%M:%S"),
        "Not After": hostinfo.cert.not_valid_after.strftime("%Y-%m-%d %H:%M:%S"),
        "Expired": not (
            hostinfo.cert.not_valid_before
            < datetime.now()
            < hostinfo.cert.not_valid_after
        ),
    }

    server.date_last_checked = now()
    server.save()

    old_records = server.serverprofile.ssl_certs
    if not old_records:
        log_changes(server, "ssl_certs", ssl_results)
        return "SUCCESS"

    for record in ssl_results.keys():
        if old_records["Expired"] == ssl_results["Expired"]:
            continue
        if Counter(ssl_results[record]) == Counter(old_records[record]):
            continue
        else:
            log_changes(server, "ssl_certs", ssl_results)
            break
    return "SUCCESS"


@shared_task(name="get_headers", serializer="json", max_retries=3, soft_time_limit=20)
def get_headers(server_id: int):
    try:
        server = Server.objects.get(id=server_id)
    except Server.DoesNotExist:
        return f"Server with id '{server_id}' does not exist!"

    try:
        if check_if_ssl(server.domain_name, 443):
            response = requests.get(f"https://{server.domain_name}", timeout=5)
        else:
            response = requests.get(f"http://{server.domain_name}", timeout=5)

    except ConnectTimeout:
        message = f"Connection to {server.domain_name} timed out for {server}!"
        logger.error(message)
        return message
    except requests.RequestException as e:
        message = f"There was an error connecting to {server.domain_name} for {server}!"
        logger.error(e)
        return message

    server.date_last_checked = now()
    server.save()

    # Requests response headers are a CaseInsensitiveDict
    # and need to be casted to a regular Dict before they
    # can be serialized into JSON.
    response_headers = dict(response.headers)

    # Remove all the header fields we don't care about
    response_keys = list(response_headers.keys())
    for header in response_keys:
        if header not in SECURITY_HEADERS_WHITELIST:
            del response_headers[header]

    old_records = server.serverprofile.security_headers
    if not old_records:
        log_changes(server, "security_headers", response_headers)
        return "SUCCESS"

    for header in response_headers.keys():
        if Counter(response_headers[header]) == Counter(old_records[header]):
            continue
        else:
            log_changes(server, "security_headers", response_headers)
            break
    return "SUCCESS"


@shared_task(name="ping_server", max_retries=3, soft_time_limit=20)
def ping_server(server_id: int):
    try:
        server = Server.objects.get(id=server_id)
    except Server.DoesNotExist:
        return f"Server with id '{server_id}' does not exist!"

    param = "-n" if platform.system().lower() == "windows" else "-c"
    ping = subprocess.Popen(
        ["ping", param, "2", server.ip_address],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    server.date_last_checked = now()
    server.save()

    output_bytes, error = ping.communicate()
    out = output_bytes.decode("utf-8").lower()
    if "unreachable" in out or "failure" in out or "100% packet loss" in out:
        message = f"Could not ping {server.ip_address}"
        logger.error(message)

        if server.serverprofile.is_up:
            log_changes(server, "is_up", False)

        return message

    if server.serverprofile.is_up == False:
        log_changes(server, "is_up", True)

    latency_results = {"min": "", "max": "", "avg": ""}
    latency_values = []

    try:
        if platform.system().lower() == "windows":
            # Windows: Minimum = 5ms, Maximum = 5ms, Average = 5ms
            stats = out.split("\n")[-2].strip().split(",")
            latency_values = [v.split(" ")[-1] for v in stats]
            latency_results["min"] = latency_values[0]
            latency_results["max"] = latency_values[1]
            latency_results["avg"] = latency_values[2]

        else:
            # Linux: rtt min/avg/max/mdev = 4.513/5.296/5.577/0.399 ms
            stats = out.split("\n")[-2].split(" ")[-2]
            latency_values = [v for v in stats.split("/")][:-1]
            latency_results["min"] = latency_values[0]
            latency_results["max"] = latency_values[1]
            latency_results["avg"] = latency_values[2]
    except Exception:
        message = f"Something went wrong parsing the ping values for {server}!."
        logger.error(message)
        return "Something went wrong parsing the ping values."

    log_changes(server, "latency", latency_results)

    return "SUCCESS"


@shared_task(name="debug_task")
def debug_task():
    """Debug task to make sure beat, workers and message queue are operational

    Args:
        server_id (int): A PK of any Server Object

    Returns:
        str: The name of the Server object
    """
    return "SUCCESS"
