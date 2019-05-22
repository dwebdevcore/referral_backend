# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.db import migrations

from referral_project.users.enums import GroupName


def create_groups(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).bulk_create([
        Group(name=name) for name in GroupName
    ])


def delete_groups(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).filter(name__in=GroupName).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_user_status'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_code=delete_groups),
    ]
