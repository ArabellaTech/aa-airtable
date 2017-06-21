# -*- coding: utf-8 -*-
import requests_mock
from django.test import TestCase
from django.test.utils import override_settings

from aa_airtable.models import UploadedFile


class ModelsTests(TestCase):
    maxDiff = None

    @requests_mock.Mocker()
    @override_settings(AIRTABLE_SETTINGS={"SAVE_FILES": False})
    def test_skip_settings(self, mocker):
        data = {
            "url": "http://a.com/xxx_foo.ext",
        }
        url = UploadedFile.save_file(data)
        self.assertEqual(url, data["url"])
        self.assertEqual(mocker.call_count, 0)

    @requests_mock.Mocker()
    def test_save_file(self, mocker):
        self.assertEqual(UploadedFile.objects.count(), 0)

        file_url = "http://a.com/xxx_foo.ext"
        mocker.register_uri("GET", file_url, [{"content": b"foo.ext"}])

        data = {
            "id": "fooX",
            "url": file_url,
            "filename": "foo.ext",
            "type": "image/jpeg",
        }
        url = UploadedFile.save_file(data)
        self.assertTrue(url.endswith("foo.ext"))

        self.assertEqual(UploadedFile.objects.count(), 1)
        f = UploadedFile.objects.first()
        self.assertEqual(f.key, data["id"])
        self.assertEqual(f.original_url, data["url"])
        self.assertEqual(f.type, data["type"])
        self.assertEqual(f.name, data["filename"])
        self.assertEqual(mocker.call_count, 1)

        # Do not save again
        url = UploadedFile.save_file(data)
        self.assertEqual(UploadedFile.objects.count(), 1)
        self.assertEqual(mocker.call_count, 1)

    def test_url(self):
        f = UploadedFile(type="image/jpeg", file="foo/foo.jpg", key=123)
        url = f.get_absolute_url()
        self.assertEqual(url, f.file.url)
