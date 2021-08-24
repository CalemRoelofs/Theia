# -*- coding: utf-8 -*-
from django import forms
from django.db.models import PositiveIntegerField

from .models import AlertEndpoint
from .models import ContactGroup
from .models import Server
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


class AlertEndpointForm(forms.ModelForm):
    class Meta:
        model = AlertEndpoint
        exclude = []


class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = ContactGroup
        exclude = []
