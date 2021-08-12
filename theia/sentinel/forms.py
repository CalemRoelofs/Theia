# -*- coding: utf-8 -*-
from django.forms import ModelForm

from .models import Server
from .models import ServerProfile


class ServerForm(ModelForm):
    class Meta:
        model = Server
        exclude = ["date_added", "date_last_checked", "check_latency"]
