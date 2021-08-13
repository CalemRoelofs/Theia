# -*- coding: utf-8 -*-
# Generated by Django 3.2.5 on 2021-08-13 14:58
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("sentinel", "0017_auto_20210813_1542")]

    operations = [
        migrations.AddField(
            model_name="server",
            name="contact_groups",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="sentinel.contactgroup",
            ),
        )
    ]
