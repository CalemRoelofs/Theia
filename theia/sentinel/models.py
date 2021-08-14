# -*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now
from django.views.generic import ListView
from django_celery_beat.models import PeriodicTask

SCAN_FREQUENCY_CHOICES = (
    ("minutes", "Minutes"),
    ("hours", "Hours"),
    ("days", "Days"),
    ("weeks", "Weeks"),
)

ENDPOINT_TYPE_CHOICES = (
    ("discord", "Discord"),
    ("msteams", "Microsoft Teams"),
    ("slack", "Slack"),
    ("telegram", "Telegram"),
    ("email", "Email"),
)


class AlertEndpoint(models.Model):
    class Meta:
        verbose_name = "Alert Endpoint"
        verbose_name_plural = "Alert Endpoints"

    name = models.CharField("Name", max_length=512, null=False, blank=False)
    endpoint_type = models.CharField(
        "Endpoint Type",
        max_length=30,
        null=False,
        blank=False,
        choices=ENDPOINT_TYPE_CHOICES,
    )
    endpoint_value = models.CharField(
        "Webhook URL/Email Address", max_length=512, null=False, blank=False
    )

    def __str__(self):
        return self.name


class ContactGroup(models.Model):
    class Meta:
        verbose_name = "Contact Group"
        verbose_name_plural = "Contact Groups"

    name = models.CharField("Name", max_length=255, null=False, blank=False)
    alert_endpoints = models.ManyToManyField(
        AlertEndpoint, blank=True, related_name="contact_groups"
    )

    def __str__(self):
        return self.name


class Server(models.Model):
    class Meta:
        verbose_name = "Server"
        verbose_name_plural = "Servers"

    name = models.CharField("Name", unique=True, blank=False, max_length=255)
    ip_address = models.GenericIPAddressField("IP Address", unique=True, blank=False)
    domain_name = models.CharField(
        "Fully Qualified Domain Name", blank=True, max_length=255
    )
    description = models.CharField("Description", max_length=512)
    developer = models.CharField("Developer", max_length=255)
    sysadmin = models.CharField("Sysadmin", max_length=255)
    date_added = models.DateTimeField("Date Added", default=now, editable=False)
    date_last_checked = models.DateTimeField("Last Checked", default=now)
    contact_group = models.ForeignKey(
        ContactGroup, on_delete=models.SET_NULL, null=True, blank=True
    )
    scan_frequency_value = models.IntegerField("Scan Frequency Value", default=10)
    scan_frequency_period = models.CharField(
        "Scan Frequency Period", max_length=20, choices=SCAN_FREQUENCY_CHOICES
    )
    check_open_ports = models.BooleanField("Check Open Ports", default=True)
    check_security_headers = models.BooleanField("Check Security Headers", default=True)
    check_ssl_certs = models.BooleanField("Check SSL Certificates", default=True)
    check_latency = models.BooleanField("Check Latency", default=True)
    check_dns_records = models.BooleanField("Check DNS Records", default=True)

    def __str__(self):
        return self.name


class ServerProfile(models.Model):
    class Meta:
        verbose_name = "Server Profile"
        verbose_name_plural = "Server Profiles"

    server = models.OneToOneField(Server, on_delete=models.CASCADE, primary_key=True)
    is_up = models.BooleanField(
        "Host Reachable", null=False, blank=False, default=False
    )
    open_ports = models.JSONField("Open Ports", null=True, blank=True, default=None)
    security_headers = models.JSONField(
        "Security Headers", null=True, blank=True, default=None
    )
    ssl_certs = models.JSONField(
        "SSL Certificates", null=True, blank=True, default=None
    )
    latency = models.JSONField("Latency Results", null=True, blank=True, default=None)
    dns_records = models.JSONField("DNS Records", null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.server.name} Profile"


class ProfileChangelog(models.Model):
    class Meta:
        verbose_name = "Profile Changelog"
        verbose_name_plural = "Profile Changelogs"

    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=False)
    date_modified = models.DateTimeField("Date Modified", default=now, editable=False)
    changed_field = models.CharField("Changed Field", max_length=255)
    old_value = models.JSONField("Old Value", null=True, blank=True)
    new_value = models.JSONField("New Value", null=True, blank=True)
    acknowledged = models.BooleanField("Acknowledged", default=False)

    def __str__(self):
        return f"{self.server.name} - {self.changed_field} - {self.date_modified}"


class AlertLog(models.Model):
    class Meta:
        verbose_name = "Alert Log"
        verbose_name_plural = "Alert Logs"

    timestamp = models.DateTimeField("Timestamp")
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=False)
    alert_endpoint = models.ForeignKey("AlertEndpoint", AlertEndpoint)
    message = models.TextField("Message", null=False, blank=False)
    status_code = models.IntegerField("Status Code", null=True, blank=True)

    def __str__(self):
        return f"{self.alert_endpoint.name} - {self.id} - {self.timestamp}"


class ServerTask(models.Model):
    """Interim table to map tasks to server ids"""

    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    task = models.OneToOneField(PeriodicTask, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.server.name} - {self.task_name}"
