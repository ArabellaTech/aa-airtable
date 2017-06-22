# -*- coding: utf-8 -*-
import mock
import requests_mock
from django.contrib.auth import get_user_model
from django.test import TestCase

from aa_airtable.models import Job
from aa_airtable.tasks import process_job_task

UserModel = get_user_model()


class FlowTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.user = UserModel.objects.create(email="foo@bar.bar", username="foo", password="dump-password")

    def test_run(self):
        with requests_mock.Mocker() as m:
            url = "https://api.airtable.com/v0/foo/Article"
            m.register_uri("GET", url, [{"json": {"records": ["a"]}}])
            url = "https://api.airtable.com/v0/foo/Media"
            m.register_uri("GET", url, [{"json": {"records": ["a"]}}])

            with mock.patch("aa_airtable.models.process_job_task.apply_async") as task_mock:
                job = Job.objects.create(user=self.user)
                job.refresh_from_db()
                self.assertEqual(job.status, Job.STATUS_PENDING)
                task_mock.assert_called_once_with(countdown=10, args=[job.id])
                self.assertFalse(m.called)

            with mock.patch("aa_airtable.parser.DatabasesParser") as parser_mock:
                process_job_task.delay(job.id)
                self.assertTrue(parser_mock.called)
                self.assertTrue(m.called)

        jobs = Job.objects.all()
        self.assertEqual(jobs.count(), 1)
        self.assertTrue(jobs[0].file)
        self.assertEqual(jobs[0].status, Job.STATUS_SUCCESS)

    def test_error(self):
        with mock.patch("aa_airtable.tasks.get") as get_mock:
            get_mock.side_effect = Exception("Boom!")
            job = Job.objects.create(user=self.user)

        job = Job.objects.all().first()
        self.assertFalse(job.file)
        self.assertEqual(job.status, Job.STATUS_ERROR)
