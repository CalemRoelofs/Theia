from django.db import models


class ServerProfile(models.Model):
    is_up = models.BooleanField("Host Reachable", null=False, blank=False)
    open_ports = models.JSONField("Open Ports", null=True, blank=True)
    security_headers = models.JSONField("Security Headers", null=True, blank=True)
    ssl_certs = models.JSONfield("SSL Certificates", null=True, blank=True)
    latency = models.IntegerField("Latency")
    dns_records = models.JSONField("DNS Records", null=True, blank=True)


class Server(models.Model):
    ip_address = models.GenericIPAddressField("IP Address", unique=True, blank=False)
    domain_name = models.URLField("Fully Qualified Domain Name", blank=True)
    description = models.TextField("Description")
    developer = models.CharField("Developer", max_length=255)
    sysadmin = models.CharField("Sysadmin", max_length=255)
    date_added = models.DateTimeField("Date Added")
    date_last_checked = models.DateTimeField("Last Checked")
    check_open_ports = models.BooleanField("Check Open Ports", default=True)
    check_security_headers = models.BooleanField("Check Security Headers", default=True)
    check_ssl_certs = models.BooleanField("Check SSL Certificates", default=True)
    check_latency = models.BooleanField("Check Latency", default=True)
    check_dns_records = models.BooleanField("Check DNS Records", default=True)
    server_profile = models.ForeignKey("Server Profile", ServerProfile)


class ScanResults(models.Model):
    server_profile = models.ForeignKey("Server Profile", ServerProfile)
    date_modified = models.DateTimeField("Date Modified")
    changed_field = models.CharField("Changed Field", max_length=255)
    old_value = models.JSONField("Old Value", null=True, blank=True)
    new_value = models.JSONField("New Value", null=True, blank=True)
