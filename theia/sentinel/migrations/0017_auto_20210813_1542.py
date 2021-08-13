# -*- coding: utf-8 -*-
# Generated by Django 3.2.5 on 2021-08-13 14:42
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("sentinel", "0016_auto_20210813_1539")]

    operations = [
        migrations.RemoveField(model_name="alertendpoint", name="contact_groups"),
        migrations.AddField(
            model_name="contactgroup",
            name="alert_endpoints",
            field=models.ManyToManyField(
                blank=True, related_name="contact_groups", to="sentinel.AlertEndpoint"
            ),
        ),
        migrations.AlterField(
            model_name="contactgroup",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Name"),
        ),
    ]