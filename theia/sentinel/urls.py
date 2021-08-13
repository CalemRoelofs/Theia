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
    path("alerts/", views.alerts_overview, name="alerts_overview"),
    path("alerts/create", views.create_alert_endpoint, name="create_alert_endpoint"),
    path("alerts/edit", views.edit_alert_endpoint, name="edit_alert_endpoint"),
    path("alerts/delete", views.delete_alert_endpoint, name="delete_alert_endpoint"),
    path("alerts/test", views.send_test_alert, name="send_test_alert"),
]
