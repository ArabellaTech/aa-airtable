# -*- coding: utf-8 -*-
import sys
import traceback
from importlib import import_module

from django.conf import settings
from django.core.cache import cache

from aa_airtable.download import get

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes

__path, __symbol = getattr(settings, "CELERY_APP_PATH").rsplit(".", 1)
app = getattr(import_module(__path), __symbol)


@app.task(ignore_result=True)
def process_job_task(job_id):
    from aa_airtable.parser import DatabasesParser
    from aa_airtable.models import Job

    lock_id = "airtable-job-{}".format(job_id)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)   # noqa: E731
    release_lock = lambda: cache.delete(lock_id)   # noqa: E731

    job = Job.objects.get(id=job_id)
    job.status = Job.STATUS_PRE_LOCK
    job.save()

    if acquire_lock():
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            release_lock()
            raise

        job.status = Job.STATUS_STARTED
        job.save()
        try:
            file_path, data = get()
            job.file = file_path
            job.save()
            DatabasesParser(data)
            job.status = Job.STATUS_SUCCESS
            job.save()
            release_lock()
        except Exception as e:
            job.status = Job.STATUS_ERROR
            exc_type, exc_value, exc_traceback = sys.exc_info()
            job.error = str(traceback.format_exception(exc_type, exc_value, exc_traceback))
            job.save()
            release_lock()
            raise e
