# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("servers/", views.server_overview, name="server_overview"),
    path("servers/create", views.create_server, name="create_server"),
    path("server/edit", views.edit_server, name="edit_server"),
    path("servers/<int:server_id>/", views.server_view, name="server_view"),
    path("changelogs/", views.changelog_overview, name="changelog_overview"),
    path("changelogs/ack", views.acknowledge_changelog, name="ack_changelog"),
]
