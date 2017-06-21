# -*- coding: utf-8 -*-
from django.db import models

from aa_airtable.models import AbstractContent


class Media(AbstractContent):
    name = models.CharField(max_length=255)
    ny_logo = models.CharField(max_length=255)


class Article(AbstractContent):
    name = models.CharField(max_length=255)
    custom_name = models.CharField(max_length=255)
    description = models.TextField()
    gallery = models.ManyToManyField(Media, related_name="article_gallery")
