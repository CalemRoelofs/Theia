# -*- coding: utf-8 -*-
from datetime import datetime

import django
import pytest
from celery.exceptions import Retry
from django.test import TestCase
from pytz import timezone

django.setup()

from sentinel.models import ProfileChangelog
from sentinel.models import Server
from sentinel.models import ServerProfile
from sentinel.tasks import debug_task
from sentinel.tasks import dns_records
from sentinel.tasks import get_headers
from sentinel.tasks import ping_server
from sentinel.tasks import port_scan
from sentinel.tasks import ssl_certs


class TestTasks(TestCase):
    def setUp(self):
        server = Server(
            name="test_server",
            ip_address="1.1.1.1",
            domain_name="one.one.one.one",
            description="test_description",
            developer="test_developer",
            sysadmin="test_sysadmin",
            date_added=datetime.now(timezone("Europe/Dublin")),
            date_last_checked=datetime.now(timezone("Europe/Dublin")),
        )
        server.save()

        server.serverprofile = ServerProfile(
            server=server,
            is_up=True,
            open_ports=None,
            security_headers=None,
            ssl_certs=None,
            latency=None,
            dns_records=None,
        )

        server.serverprofile.save()


class test_port_scan(TestTasks):
    def test_WhenServerFoundAndScanRuns_ReturnsSuccess(self):
        task = port_scan.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    def test_port_scan_WhenServerNotFound_ReturnsError(self):
        task = port_scan.s(server_id=2).apply()

        self.assertEqual(task.result, "Server with id '2' does not exist!")

    def test_WhenHostNotFound_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.ip_address = "192.168.255.254"
        server.save()

        task = port_scan.s(server_id=1).apply()

        self.assertEqual(
            task.result, f"Could not find host {server.ip_address} in nmap scan!"
        )

    def test_WhenPortChangeDetected_ProfileChangelogCreated(self):
        server = Server.objects.get(id=1)

        task = port_scan.s(server_id=1).apply()
        try:
            change = ProfileChangelog.objects.get(id=1)
        except ProfileChangelog.DoesNotExist:
            self.fail("ProfileChanglog was not created")

        self.assertEqual(task.result, "SUCCESS")
        self.assertEqual(change.server, server)
        self.assertEqual(change.changed_field, "open_ports")

    def test_WhenNoPortChangeDetected_ProfileChangelogNotCreated(self):
        first_task = port_scan.s(server_id=1).apply()
        second_task = port_scan.s(server_id=1).apply()

        with self.assertRaises(ProfileChangelog.DoesNotExist):
            change = ProfileChangelog.objects.get(id=2)


class test_dns_records(TestTasks):
    def test_WhenServerFoundAndDomainResolves_ReturnsSuccess(self):
        task = dns_records.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    def test_dns_records_WhenServerNotFound_ReturnsError(self):
        task = dns_records.s(server_id=2).apply()

        self.assertEqual(task.result, "Server with id '2' does not exist!")

    def test_WhenDomainDoesNotExist_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.domain_name = "fshagighaaslgsdgjhsghdksalndv"
        server.save()

        task = dns_records.s(server_id=1).apply()

        self.assertEqual(
            task.result,
            f"Could not resolve domain {server.domain_name} for test_server's A record!",
        )

    def test_WhenDNSChangeDetected_ProfileChangelogCreated(self):
        server = Server.objects.get(id=1)

        task = dns_records.s(server_id=1).apply()
        try:
            change = ProfileChangelog.objects.get(id=1)
        except ProfileChangelog.DoesNotExist:
            self.fail("ProfileChanglog was not created")

        self.assertEqual(task.result, "SUCCESS")
        self.assertEqual(change.server, server)
        self.assertEqual(change.changed_field, "dns_records")

    def test_WhenNoDNSChangeDetected_ProfileChangelogNotCreated(self):
        first_task = dns_records.s(server_id=1).apply()
        second_task = dns_records.s(server_id=1).apply()

        with self.assertRaises(ProfileChangelog.DoesNotExist):
            change = ProfileChangelog.objects.get(id=2)


class test_ssl_certs(TestTasks):
    def test_WhenServerFoundAndIsHTTPS_ReturnsSuccess(self):
        task = ssl_certs.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    def test_ssl_certs_WhenServerNotFound_ReturnsError(self):
        task = ssl_certs.s(server_id=2).apply()

        self.assertEqual(task.result, "Server with id '2' does not exist!")

    def test_WhenServerNotHTTPS_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.domain_name = "mainbox.lan"
        server.save()

        task = ssl_certs.s(server_id=1).apply()

        self.assertEqual(
            task.result,
            f"Failed to make SSL connection to {server.domain_name} for {server.name}!",
        )

    def test_WhenSSLChangeDetected_ProfileChangelogCreated(self):
        server = Server.objects.get(id=1)

        task = ssl_certs.s(server_id=1).apply()
        try:
            change = ProfileChangelog.objects.get(id=1)
        except ProfileChangelog.DoesNotExist:
            self.fail("ProfileChanglog was not created")

        self.assertEqual(task.result, "SUCCESS")
        self.assertEqual(change.server, server)
        self.assertEqual(change.changed_field, "ssl_certs")

    def test_WhenNoSSLChangeDetected_ProfileChangelogNotCreated(self):
        first_task = ssl_certs.s(server_id=1).apply()
        second_task = ssl_certs.s(server_id=1).apply()

        with self.assertRaises(ProfileChangelog.DoesNotExist):
            change = ProfileChangelog.objects.get(id=2)


class test_get_headers(TestTasks):
    def test_WhenServerFoundAndResponseRecieved_ReturnsSuccess(self):
        task = get_headers.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    def test_get_headers_WhenServerNotFound_ReturnsError(self):
        task = get_headers.s(server_id=2).apply()

        self.assertEqual(task.result, "Server with id '2' does not exist!")

    def test_WhenServerNotHTTPS_FallsbackToHTTP(self):
        server = Server.objects.get(id=1)
        server.domain_name = "http.badssl.com"
        server.save()

        task = get_headers.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    def test_WhenConnectionTimesOut_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.domain_name = "mainbox.lan"
        server.save()

        task = get_headers.s(server_id=1).apply()

        self.assertEqual(
            task.result,
            f"There was an error connecting to {server.domain_name} for {server}!",
        )

    def test_WhenConnectionFails_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.domain_name = "sdkljfnsgdsg"
        server.save()

        task = get_headers.s(server_id=1).apply()

        self.assertEqual(
            task.result,
            f"There was an error connecting to sdkljfnsgdsg for {server.name}!",
        )

    def test_WhenHeadersChangeDetected_ProfileChangelogCreated(self):
        server = Server.objects.get(id=1)

        task = get_headers.s(server_id=1).apply()
        try:
            change = ProfileChangelog.objects.get(id=1)
        except ProfileChangelog.DoesNotExist:
            self.fail("ProfileChanglog was not created")

        self.assertEqual(task.result, "SUCCESS")
        self.assertEqual(change.server, server)
        self.assertEqual(change.changed_field, "security_headers")

    def test_WhenNoHeadersChangeDetected_ProfileChangelogNotCreated(self):
        server = Server.objects.get(id=1)

        first_task = get_headers.s(server_id=1).apply()
        server.refresh_from_db()

        second_task = get_headers.s(server_id=1).apply()
        server.refresh_from_db()

        with self.assertRaises(ProfileChangelog.DoesNotExist):
            change = ProfileChangelog.objects.get(id=2)


class test_ping_server(TestTasks):
    """These tests are skipped in CI as GitHub Actions runners
    are hosted on Azure which doe not allow pinging. Whack."""

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency()
    def test_CanPing(self):
        task = ping_server.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_WhenServerFoundAndPingReturnsOutput_ReturnsSuccess(self):
        task = ping_server.s(server_id=1).apply()

        self.assertEqual(task.result, "SUCCESS")

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_ping_server_WhenServerNotFound_ReturnsError(self):
        task = ping_server.s(server_id=2).apply()

        self.assertEqual(task.result, "Server with id '2' does not exist!")

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_WhenServerNotReachable_ReturnsError(self):
        server = Server.objects.get(id=1)
        server.ip_address = "192.168.255.254"
        server.save()

        task = ping_server.s(server_id=1).apply()

        self.assertEqual(task.result, f"Could not ping {server.ip_address}")

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_WhenServerNotReachable_is_up_ChangesToFalse(self):
        server = Server.objects.get(id=1)
        server.ip_address = "192.168.255.254"
        server.save()

        task = ping_server.s(server_id=1).apply()
        server.refresh_from_db()

        self.assertFalse(server.serverprofile.is_up)

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_WhenServerReachable_is_up_ChangesToTrue(self):
        server = Server.objects.get(id=1)
        server.serverprofile.is_up = False
        server.serverprofile.save()

        task = ping_server.s(server_id=1).apply()

        server.refresh_from_db()

        self.assertEqual(task.result, "SUCCESS")
        self.assertEqual(server.serverprofile.is_up, True)

    @pytest.mark.skip_in_CI
    @pytest.mark.dependency(depends=["test_ping_server::test_CanPing"])
    def test_WhenPingSucceeds_LatencyValuesUpdated(self):
        server = Server.objects.get(id=1)

        old_values = server.serverprofile.latency

        task = ping_server.s(server_id=1).apply()
        server.refresh_from_db()

        self.assertNotEqual(server.serverprofile.latency, old_values)


class test_debug_task(TestTasks):
    def test_debug_task_ReturnsSuccess(self):
        task = debug_task.s().apply()
        self.assertEqual(task.result, "SUCCESS")
