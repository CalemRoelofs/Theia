# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.helpers import checkbox

from .models import AlertEndpoint
from .models import AlertLog
from .models import ContactGroup
from .models import ProfileChangelog
from .models import Server
from .models import ServerProfile

# Register your models here.


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    pass


@admin.register(ServerProfile)
class ServerProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ProfileChangelog)
class ProfileChangelogAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(AlertEndpoint)
class AlertEndpointAdmin(admin.ModelAdmin):
    pass


@admin.register(AlertLog)
class AlertEndpointAdmin(admin.ModelAdmin):
    pass
