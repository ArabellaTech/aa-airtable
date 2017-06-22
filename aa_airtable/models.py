# -*- coding: utf-8 -*-
import os
import uuid

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save

from aa_airtable.settings import airtable_settings
from aa_airtable.tasks import process_job_task


class Job(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    STATUS_PENDING = "pending"
    STATUS_PRE_LOCK = "pre_lock"
    STATUS_STARTED = "started"
    STATUS_ERROR = "error"
    STATUS_SUCCESS = "success"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PRE_LOCK, "Pre lock"),
        (STATUS_STARTED, "Started"),
        (STATUS_ERROR, "Error"),
        (STATUS_SUCCESS, "Success"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    error = models.TextField()
    file = models.FileField(upload_to=airtable_settings.DATA_DIRECTORY)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created", "-id"]


class UploadedFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    original_url = models.URLField(blank=True)
    file = models.FileField(upload_to=airtable_settings.FILES_DIRECTORY)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=255, blank=True)

    def get_absolute_url(self):
        if self.file:
            return self.file.url

    @classmethod
    def save_file(cls, obj):
        if not airtable_settings.SAVE_FILES:
            return obj.get("url", "")

        try:
            instance = UploadedFile.objects.get(key=obj["id"])
        except UploadedFile.DoesNotExist:
            content = requests.get(obj["url"]).content
            file_name = os.path.join(airtable_settings.FILES_DIRECTORY, str(uuid.uuid4()) + obj["filename"])
            instance = UploadedFile(
                original_url=obj["url"],
                name=obj["filename"],
                key=obj["id"],
                type=obj["type"],
            )
            instance.file.save(file_name, ContentFile(content))
            instance.file.close()
            instance.save()

        return instance.get_absolute_url()


class AbstractContent(models.Model):
    airtable_id = models.CharField(max_length=255, blank=True, db_index=True)

    def __str__(self):
        return self.airtable_id

    class Meta:
        ordering = ["airtable_id"]
        abstract = True


def job_post_save(sender, instance, created, **kwargs):
    if created:
        process_job_task.apply_async(args=[instance.id], countdown=10)


post_save.connect(job_post_save, sender=Job)
