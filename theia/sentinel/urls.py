# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("servers/", views.server_overview, name="server_overview"),
    path("servers/<int:server_id>/", views.server_view, name="server_view"),
]
