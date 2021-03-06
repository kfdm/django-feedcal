# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 07:44
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=32)),
                ('calendar', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=32)),
                ('feed', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='MergedCalendar',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=32)),
                ('calendars', models.ManyToManyField(to='feedcal.Calendar')),
            ],
        ),
        migrations.CreateModel(
            name='MergedFeed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=32)),
                ('feeds', models.ManyToManyField(to='feedcal.Feed')),
            ],
        ),
    ]
