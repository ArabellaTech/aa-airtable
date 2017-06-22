# -*- coding: utf-8 -*-
def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        USE_L10N=True,
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.admin",
            "aa_airtable",
            "tests",
        ),
        CELERY_APP_PATH='tests.celery.app',
        CELERY_TASK_ALWAYS_EAGER=True,
        TESTING=True,

        AIRTABLE_SETTINGS={
            "API_KEY": "fake",
            "DATABASES": {
                "foo": [
                    ("Media", "tests.parsers.MediaParser"),
                    ("Article", "tests.parsers.ArticleParser"),
                ]
            }
        },
    )
