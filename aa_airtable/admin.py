# -*- coding: utf-8 -*-
from django.contrib import admin

from aa_airtable.models import Job


class JobAdmin(admin.ModelAdmin):
    list_display = ("created", "status")
    list_filter = ["status"]
    readonly_fields = ["status", "error", "file", "user"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


admin.site.register(Job, JobAdmin)
