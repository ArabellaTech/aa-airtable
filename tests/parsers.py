from tests.models import Article, Media

from aa_airtable.parser import AbstractParser


class MediaParser(AbstractParser):
    model = Media
    raw_fields = [
        "Name",
    ]
    file_fields = [
        "NY Logo"
    ]


class ArticleParser(AbstractParser):
    model = Article
    raw_fields = [
        "Name",
        ("custom_name", "Title"),
        "Description",
    ]
    related_fields = [
        ("gallery", "Gallery", Media),
    ]
