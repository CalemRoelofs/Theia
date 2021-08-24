# -*- coding: utf-8 -*-
from datetime import datetime

import django
import pytest
from _pytest.outcomes import fail
from pytz import timezone

django.setup()

from sentinel.models import ProfileChangelog
from sentinel.models import Server
from sentinel.models import ServerProfile
from sentinel.utils import log_changes, create_or_update_tasks


CHANGED_FIELD_VALUES = [
    ("open_ports", {"key": "value"}),
    ("dns_records", {"key": "value"}),
    ("security_headers", {"key": "value"}),
    ("ssl_certs", {"key": "value"}),
    ("latency", {"key": "value"}),
]


@pytest.fixture
def setup_server():
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
    server.refresh_from_db()
    return server


@pytest.mark.django_db
class TestLogChanges:
    @pytest.mark.parametrize("field_name,field_value", CHANGED_FIELD_VALUES)
    def test_WhenChangedFieldIsValid_ChangelogGetsCreated(
        self, field_name, field_value, setup_server
    ):
        server = setup_server
        log_changes(server, field_name, field_value)

        try:
            change = ProfileChangelog.objects.get(id=1)
        except ProfileChangelog.DoesNotExist:
            pytest.fail("ProfileChanglog was not created")

        assert change.changed_field == field_name

    @pytest.mark.parametrize("field_name,field_value", CHANGED_FIELD_VALUES)
    def test_WhenChangedFieldIsValid_ProfileValueChanges(
        self, field_name, field_value, setup_server
    ):
        server = setup_server
        log_changes(server, field_name, field_value)
        server.refresh_from_db()

        # Create a dictionary of the updated server profile
        # to compare with the parametrize decorator in the assert
        profile_dict = {
            "open_ports": server.serverprofile.open_ports,
            "dns_records": server.serverprofile.dns_records,
            "ssl_certs": server.serverprofile.ssl_certs,
            "security_headers": server.serverprofile.security_headers,
            "latency": server.serverprofile.latency,
        }

        assert profile_dict[field_name] == field_value

    def test_WhenChangedFieldIsNotValid_ChangelogIsNotCreated(self):
        server = setup_server

        with pytest.raises(RuntimeError):
            log_changes(server, "invalid field name", {"fake_key": "not a real value"})


@pytest.mark.django_db
class TestCreateOrUpdateTasks:
    def test_WhenCheckOpenPortsIsTrue_TaskIsCreated(self):
        server = setup_server
