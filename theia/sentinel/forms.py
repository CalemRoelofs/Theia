# -*- coding: utf-8 -*-
from django.forms import ModelForm

from .models import AlertEndpoint
from .models import Server


class ServerForm(ModelForm):
    class Meta:
        model = Server
        exclude = ["date_added", "date_last_checked", "check_latency"]


class AlertEndpointForm(ModelForm):
    class Meta:
        model = AlertEndpoint
        exclude = []
