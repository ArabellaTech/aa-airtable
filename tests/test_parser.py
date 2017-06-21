# -*- coding: utf-8 -*-
from django.test import TestCase
from tests.models import Article, Media

from aa_airtable.parser import DatabasesParser


class ParserTests(TestCase):

    def test_parse(self):
        Media.objects.create(name="mX", airtable_id="mOld")
        Article.objects.create(name="aX", airtable_id="aOld")
        data = {
            "foo": {
                "Media": [{
                        "id": "m1",
                        "fields": {
                            "Name": "M1",
                            "NY Logo": [{
                                "url": "http://example.com/logo.png",
                                "id": "logo",
                                "filename": "logo.png",
                                "type": "image/jpeg",
                            }],
                        }
                    }, {
                        "id": "m2",
                        "fields": {
                            "Name": "M2",
                        },
                    },
                ],
                "Article": [{
                        "id": "a1",
                        "fields": {
                            "Name": "A1",
                            "Title": "at1",
                            "Description": "Lorem Ipsum",
                            "Gallery": ["m1", "m2"],
                        }
                    }
                ]
            }
        }
        DatabasesParser(data)

        media = Media.objects.all().order_by("airtable_id")
        self.assertEqual(media.count(), 2)
        self.assertEqual(media[0].name, "M1")
        self.assertTrue(media[0].ny_logo)
        self.assertEqual(media[1].name, "M2")
        self.assertFalse(media[1].ny_logo)

        art = Article.objects.all()
        self.assertEqual(art.count(), 1)
        self.assertEqual(art[0].name, "A1")
        self.assertEqual(art[0].custom_name, "at1")
        self.assertEqual(art[0].description, "Lorem Ipsum")
        self.assertEqual(list(art[0].gallery.all().values_list("id", flat=True)), [m.id for m in media])
