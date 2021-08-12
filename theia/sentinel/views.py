# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from sentinel.forms import ServerForm
from sentinel.models import AlertEndpoint
from sentinel.models import AlertLog
from sentinel.models import ContactGroup
from sentinel.models import ProfileChangelog
from sentinel.models import Server
from sentinel.models import ServerProfile

from .utils import create_or_update_tasks


logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    context = {
        "page_title": "Index",
        "server_count": Server.objects.count(),
        "changelog_count": ProfileChangelog.objects.filter(acknowledged=False).count(),
    }
    return render(request, "sentinel/index.html", context=context)


def server_overview(request):
    servers = Server.objects.all()
    changelog = ProfileChangelog.objects.all().order_by("-date_modified")[:10]
    context = {
        "page_title": "Server Overview",
        "server_count": Server.objects.count(),
        "changelog_count": ProfileChangelog.objects.filter(acknowledged=False).count(),
        "servers": servers,
        "changelog": changelog,
        "add_server_form": ServerForm(),
    }
    return render(request, "sentinel/server_overview.html", context=context)


def server_view(request, server_id: int):
    server = get_object_or_404(Server, id=server_id)
    changelog = ProfileChangelog.objects.filter(server=server.id).order_by(
        "-date_modified"
    )
    context = {
        "page_title": f"Server - {server.name}",
        "server_count": Server.objects.count(),
        "changelog_count": ProfileChangelog.objects.filter(acknowledged=False).count(),
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
            create_or_update_tasks(new_server)
            return redirect("server_view", server_id=new_server.id)
    return redirect("server_overview")


def edit_server(request):
    if request.method == "POST":
        server = get_object_or_404(Server, id=request.POST["id"])
        logger.error(request.POST)
        form = ServerForm(request.POST or None, instance=server)
        if form.is_valid():
            form.save()
            server.refresh_from_db()
            create_or_update_tasks(server)
            return redirect("server_view", server_id=server.id)
    return redirect("server_overview")


def server_logs(server_id):
    server = get_object_or_404(Server, id=server_id)
    changelog = ProfileChangelog.objects.filter(server=server.id).order_by(
        "-date_modified"
    )
    context = {
        "page_title": f"Changelog - { server.name }",
        "server_count": Server.objects.count(),
        "changelog_count": ProfileChangelog.objects.filter(acknowledged=False).count(),
        "server": server,
        "changelog": changelog,
        "edit_server_form": ServerForm(instance=server),
    }
    pass


def changelog_overview(request):
    changelog = ProfileChangelog.objects.all().order_by("-date_modified")
    context = {
        "page_title": "Changelog Overview",
        "server_count": Server.objects.count(),
        "changelog_count": ProfileChangelog.objects.filter(acknowledged=False).count(),
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


def changelog_view():
    pass


def alerts_view():
    pass


def alerts_logs():
    pass
