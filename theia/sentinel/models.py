# -*- coding: utf-8 -*-
from django.db import models


class Server(models.Model):
    class Meta:
        verbose_name = "Server"

    name = models.TextField("Name", unique=True, blank=False)
    ip_address = models.GenericIPAddressField("IP Address", unique=True, blank=False)
    domain_name = models.URLField("Fully Qualified Domain Name", blank=True)
    description = models.TextField("Description")
    developer = models.CharField("Developer", max_length=255)
    sysadmin = models.CharField("Sysadmin", max_length=255)
    date_added = models.DateTimeField("Date Added")
    date_last_checked = models.DateTimeField("Last Checked")
    scan_frequency_value = models.IntegerField("Scan Frequency Value", default=10)
    scan_frequency_period = models.TextField("Scan Frequency Period", default="minutes")
    check_open_ports = models.BooleanField("Check Open Ports", default=True)
    check_security_headers = models.BooleanField("Check Security Headers", default=True)
    check_ssl_certs = models.BooleanField("Check SSL Certificates", default=True)
    check_latency = models.BooleanField("Check Latency", default=True)
    check_dns_records = models.BooleanField("Check DNS Records", default=True)

    def __str__(self):
        return self.name


class ServerProfile(models.Model):
    class Meta:
        verbose_name = "ServerProfile"

    server = models.OneToOneField(Server, on_delete=models.CASCADE, primary_key=True)
    is_up = models.BooleanField("Host Reachable", null=False, blank=False)
    open_ports = models.JSONField("Open Ports", null=True, blank=True)
    security_headers = models.JSONField("Security Headers", null=True, blank=True)
    ssl_certs = models.JSONField("SSL Certificates", null=True, blank=True)
    latency = models.IntegerField("Latency")
    dns_records = models.JSONField("DNS Records", null=True, blank=True)

    def __str__(self):
        return f"{self.server.name} Profile"


class ProfileChangelog(models.Model):
    class Meta:
        verbose_name = "ProfileChangelog"

    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    date_modified = models.DateTimeField("Date Modified")
    changed_field = models.CharField("Changed Field", max_length=255)
    old_value = models.JSONField("Old Value", null=True, blank=True)
    new_value = models.JSONField("New Value", null=True, blank=True)

    def __str__(self):
        return f"{self.server_profile.server.name} - {self.date_modified}"


class ContactGroup(models.Model):
    class Meta:
        verbose_name = "ContactGroup"

    name = models.TextField("Name", null=False, blank=False)

    def __str__(self):
        return self.name


class AlertEndpoint(models.Model):
    class Meta:
        verbose_name = "AlertEndpoint"

    name = models.TextField("Name", null=False, blank=False)
    endpoint_type = models.TextField("Endpoint Type", null=False, blank=False)
    endpoint_value = models.TextField("Endpoint Value", null=False, blank=False)
    contact_groups = models.ManyToManyField(ContactGroup)

    def __str__(self):
        return self.name


class AlertLog(models.Model):
    class Meta:
        verbose_name = "AlertLog"

    timestamp = models.DateTimeField("Timestamp")
    server = models.ForeignKey("Server", Server)
    alert_endpoint = models.ForeignKey("AlertEndpoint", AlertEndpoint)
    message = models.TextField("Message", null=False, blank=False)
    status_code = models.IntegerField("Status Code", null=True, blank=True)

    def __str__(self):
        return f"{self.alert_endpoint.name} - {self.id} - {self.timestamp}"
