# -*- coding: utf-8 -*-
# Generated by Django 3.2.5 on 2021-08-08 12:16
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("sentinel", "0003_auto_20210807_2015")]

    operations = [
        migrations.AlterModelOptions(
            name="alertendpoint", options={"verbose_name": "AlertEndpoint"}
        ),
        migrations.AlterModelOptions(
            name="alertlog", options={"verbose_name": "AlertLog"}
        ),
        migrations.AlterModelOptions(
            name="contactgroup", options={"verbose_name": "ContactGroup"}
        ),
        migrations.AlterModelOptions(
            name="profilechangelog", options={"verbose_name": "ProfileChangelog"}
        ),
        migrations.AlterModelOptions(
            name="serverprofile", options={"verbose_name": "ServerProfile"}
        ),
    ]