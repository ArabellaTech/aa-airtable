# -*- coding: utf-8 -*-
import json

import mock
import requests_mock
from django.core.files.base import ContentFile
from django.test import TestCase
from django.test.utils import override_settings

from aa_airtable.download import get


@override_settings(AIRTABLE_DBS={"x": ["foo"]})
class DownloadTests(TestCase):
    maxDiff = None

    @override_settings(AIRTABLE_API_KEY=None)
    def test_missing_key(self):
        self.assertRaises(Exception, get)

    def test_offset(self):
        with requests_mock.Mocker() as m:
            url = "https://api.airtable.com/v0/foo/Media"
            m.register_uri("GET", url, [{"json": {"offset": "a"}},
                                        {"json": {"offset": "b"}},
                                        {"json": {}}])
            url = "https://api.airtable.com/v0/foo/Article"
            m.register_uri("GET", url, [{"json": {}}])

            get()
            self.assertEqual(m.call_count, 4)
            self.assertNotIn("offset", m.request_history[0].qs)
            self.assertEqual(m.request_history[1].qs["offset"], ["a"])
            self.assertEqual(m.request_history[2].qs["offset"], ["b"])

    def test_save_file(self):
        with requests_mock.Mocker() as m:
            url = "https://api.airtable.com/v0/foo/Media"
            m.register_uri("GET", url, [{"json": {"offset": "a", "records": ["a"]}},
                                        {"json": {"records": ["b"]}}])
            url = "https://api.airtable.com/v0/foo/Article"
            m.register_uri("GET", url, [{"json": {}}])

            with mock.patch("aa_airtable.download.default_storage.save") as save_mock:
                get()
                self.assertEqual(save_mock.call_count, 1)
                self.assertEqual(type(save_mock.call_args_list[0][0][1]), ContentFile)
                self.assertEqual(save_mock.call_args_list[0][0][1].read(), json.dumps({
                    "foo": {
                        "Media": ["a", "b"],
                        "Article": [],
                    }
                }))
