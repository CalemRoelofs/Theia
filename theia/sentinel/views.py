# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "sentinel/layout.html", context={})


def server_overview(request):
    pass


def server_view():
    pass


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
