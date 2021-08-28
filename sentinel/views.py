# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings
from django.http.response import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.timezone import now

from .alerts import send_alert
from .utils import manage_server_tasks
from sentinel.constants import ENDPOINT_TYPE_CHOICES
from sentinel.forms import AlertEndpointForm
from sentinel.forms import ContactGroupForm
from sentinel.forms import ServerForm
from sentinel.models import AlertEndpoint
from sentinel.models import AlertLog
from sentinel.models import ContactGroup
from sentinel.models import ProfileChangelog
from sentinel.models import Server
from sentinel.models import ServerProfile


logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    context = {
        "page_title": "Index",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "total_alert_count": AlertLog.objects.count(),
        "total_changelog_count": ProfileChangelog.objects.count(),
    }
    return render(request, "sentinel/index.html", context=context)


def server_overview(request):
    servers = Server.objects.all()
    changelog = ProfileChangelog.objects.all().order_by("-date_modified")[:10]
    context = {
        "page_title": "Server Overview",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "servers": servers,
        "changelog": changelog,
        "add_server_form": ServerForm(),
    }
    return render(request, "sentinel/server_overview.html", context=context)


def server_view(request, server_id: int):
    server = get_object_or_404(Server, id=server_id)
    changelog = ProfileChangelog.objects.filter(server=server.id).order_by(
        "-date_modified"
    )[:5]
    context = {
        "page_title": f"Server - {server.name}",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "server": server,
        "changelog": changelog,
        "edit_server_form": ServerForm(instance=server),
    }
    return render(request, "sentinel/server_view.html", context=context)


def create_server(request):
    if request.method == "POST":
        form = ServerForm(request.POST)
        if form.is_valid():
            new_server = form.save()
            new_server.serverprofile = ServerProfile()
            new_server.serverprofile.save()
            manage_server_tasks(new_server)
            return redirect("server_view", server_id=new_server.id)
        else:
            logger.error(form.errors)
    return redirect("server_overview")


def edit_server(request):
    if request.method == "POST":
        server = get_object_or_404(Server, id=request.POST["id"])
        form = ServerForm(request.POST or None, instance=server)
        if form.is_valid():
            form.save()
            server.refresh_from_db()
            manage_server_tasks(server)
            return redirect("server_view", server_id=server.id)
    return redirect("server_overview")


def delete_server(request):
    if request.method == "POST":
        server = get_object_or_404(Server, id=request.POST["id"])
        server.delete()
    return redirect("server_overview")


def server_logs(request, server_id: int):
    server = get_object_or_404(Server, id=server_id)
    changelog = ProfileChangelog.objects.filter(server=server.id).order_by(
        "-date_modified"
    )
    context = {
        "page_title": f"Changelogs - {server.name}",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "changelog": changelog,
    }
    return render(request, "sentinel/changelog_overview.html", context=context)


def changelog_overview(request):
    changelog = ProfileChangelog.objects.all().order_by("-date_modified")
    context = {
        "page_title": "Changelog Overview",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "changelog": changelog,
    }
    return render(request, "sentinel/changelog_overview.html", context=context)


def acknowledge_changelog(request):
    data = json.loads(request.read().decode("utf-8"))
    try:
        changelog = get_object_or_404(ProfileChangelog, id=data["id"])
    except Http404:
        return JsonResponse({"message": f"Could not find id: {id}"})
    changelog.acknowledged = True
    changelog.save()
    return JsonResponse({"message": "Acknowleged"})


def alerts_overview(request, errors=None):
    endpoints = AlertEndpoint.objects.all()
    context = {
        "page_title": "Alerts Overview",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "alert_endpoints": endpoints,
        "contact_groups": ContactGroup.objects.all(),
        "services": ENDPOINT_TYPE_CHOICES,
        "add_endpoint_form": AlertEndpointForm(),
        "add_group_form": ContactGroupForm(),
        "debug_flag": settings.DEBUG,
    }
    if errors:
        logger.error(errors)
        context["form_errors"] == errors
    return render(request, "sentinel/alerts_overview.html", context=context)


def send_test_alert(request):
    data = json.loads(request.read().decode("utf-8"))
    server = Server(
        name="Debug Server",
        ip_address="127.0.0.1",
        check_open_ports=False,
        check_security_headers=False,
        check_ssl_certs=False,
        check_dns_records=False,
        check_latency=False,
    )
    server.save()

    try:
        endpoint = get_object_or_404(AlertEndpoint, id=data["id"])
    except Http404:
        return JsonResponse({"message": f"Could not find id: {id}"})

    test_changelog = ProfileChangelog(
        server=server,
        date_modified=now(),
        changed_field="debug message",
        old_value="debug message",
        new_value="debug message",
        acknowledged=True,
    )

    message = f"""
    Alert: Change Detected!\n
    \tServer:       {test_changelog.server.name}\n
    \tService:      {test_changelog.changed_field}\n
    \tOld Value:    {test_changelog.old_value}\n
    \tNew Value:    {test_changelog.new_value}\n
    """

    status_code = send_alert(endpoint, test_changelog, message)
    server.delete()
    return JsonResponse({"message": f"{status_code}"})


def create_alert_endpoint(request):
    if request.method == "POST":
        form = AlertEndpointForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            logger.error(form.errors)
    return redirect("alerts_overview")


def edit_alert_endpoint(request):
    pass


def delete_alert_endpoint(request):
    if request.method == "POST":
        endpoint = get_object_or_404(AlertEndpoint, id=request.POST["id"])
        endpoint.delete()
    return redirect("alerts_overview")


def alerts_logs(request):
    alertlog = AlertLog.objects.all().order_by("-timestamp")
    context = {
        "page_title": "Alert Logs",
        "server_count": Server.objects.count(),
        "unack_changelog_count": ProfileChangelog.objects.filter(
            acknowledged=False
        ).count(),
        "alert_count": AlertEndpoint.objects.count(),
        "alertlog": alertlog,
    }
    return render(request, "sentinel/alert_logs.html", context=context)


def create_contact_group(request):
    if request.method == "POST":
        form = ContactGroupForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return form.errors
    return redirect("alerts_overview")


def edit_contact_group(request):
    if request.method == "POST":
        cg = get_object_or_404(ContactGroup, id=request.POST["id"])
        form = ContactGroupForm(request.POST or None, instance=cg)
        if form.is_valid():
            form.save()
    return redirect("alerts_overview")


def delete_contact_group(request):
    if request.method == "POST":
        cg = get_object_or_404(ContactGroup, id=request.POST["id"])
        cg.delete()
    return redirect("alerts_overview")
