# -*- coding: utf-8 -*-
from django import forms
from django.core import validators

from .models import AlertEndpoint
from .models import ContactGroup
from .models import Server
from .validators import webhook_validator
from sentinel.constants import SCAN_FREQUENCY_CHOICES


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        exclude = ["date_added", "date_last_checked", "check_latency"]

    def __init__(self, *args, **kwargs):
        super(ServerForm, self).__init__(*args, **kwargs)
        self.fields["scan_frequency_period"] = forms.ChoiceField(
            choices=SCAN_FREQUENCY_CHOICES, widget=forms.Select(), required=True
        )
        self.fields["scan_frequency_value"] = forms.IntegerField(
            min_value=1, max_value=2147483646, initial=10
        )
        self.fields["ip_address"] = forms.CharField(
            validators=[validators.ip_address_validators]
        )
        self.fields["domain_name"] = forms.CharField(
            validators=[validators.URLValidator]
        )


class AlertEndpointForm(forms.ModelForm):
    class Meta:
        model = AlertEndpoint
        exclude = []

    def __init___(self, *args, **kwargs):
        super(AlertEndpointForm, self).__init__(*args, **kwargs)
        self.fields["url"] = forms.URLField(validators=[validators.URLValidator])


class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = ContactGroup
        exclude = []
