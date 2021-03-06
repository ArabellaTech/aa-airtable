# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-21 15:58
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('pre_lock', 'Pre lock'), ('started', 'Started'), ('error', 'Error'), ('success', 'Success')], db_index=True, default='pending', max_length=10)),
                ('error', models.TextField()),
                ('file', models.FileField(upload_to='airtable-data')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-id'],
            },
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('original_url', models.URLField(blank=True)),
                ('file', models.FileField(upload_to='airtable-files')),
                ('name', models.CharField(max_length=255)),
                ('key', models.CharField(db_index=True, max_length=255)),
                ('type', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
