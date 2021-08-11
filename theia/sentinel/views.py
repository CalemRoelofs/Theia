# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from sentinel.models import AlertEndpoint
from sentinel.models import AlertLog
from sentinel.models import ContactGroup
from sentinel.models import ProfileChangelog
from sentinel.models import Server
from sentinel.models import ServerProfile

# Create your views here.
def index(request):
    context = {"page_title": "Index"}
    return render(request, "sentinel/index.html", context=context)


def server_overview(request):
    servers = Server.objects.all()
    changelog = ProfileChangelog.objects.all().order_by("-date_modified")[:10]
    context = {"servers": servers, "changelog": changelog}
    return render(request, "sentinel/server_overview.html", context=context)


def server_view(request, server_id: int):
    server = get_object_or_404(Server, id=server_id)
    changelog = ProfileChangelog.objects.filter(server=server.id).order_by(
        "-date_modified"
    )
    context = {"server": server, "changelog": changelog}
    return render(request, "sentinel/server_view.html", context=context)


def server_logs():
    pass


def scan_logs():
    pass


def scan_view():
    pass


def alerts_view():
    pass


def alerts_logs():
    pass
