# -*- coding: utf-8 -*-
# Generated by Django 3.2.5 on 2021-08-08 16:23
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("sentinel", "0006_auto_20210808_1623")]

    operations = [
        migrations.AlterField(
            model_name="server",
            name="domain_name",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Fully Qualified Domain Name"
            ),
        ),
        migrations.AlterField(
            model_name="server",
            name="name",
            field=models.CharField(max_length=255, unique=True, verbose_name="Name"),
        ),
    ]