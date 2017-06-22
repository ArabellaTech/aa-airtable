===========
aa-airtable
===========
|travis|_ |pypi|_ |coveralls|_ |requiresio|_

Airtable integration for Django-based projects

This project's target is to make the Airtable import easier in Django-based applications.


Installation
============
Add ``aa_airtable`` to your app's ``INSTALLED_APPS``, and also set ``AIRTABLE_SETTINGS`` in project settings.
After all please migrate the app (``./manage.py migrate aa_airtable``).


Settings
========
  - API_KEY - Airtable API key.
  - DATABASES - Database settings eg. ``("Media", "tests.parsers.MediaParser")`` where ``Media`` is table name and ``tests.parsers.MediaParser`` is path to table parser
  - ENDPOINT_URL - Airtable API endpoint url.
  - DATA_DIRECTORY - Folder with json data backups.
  - FILES_DIRECTORY - Folder with uploaded files to airtable.
  - SAVE_FILES - Should library save uploaded files (default: True)


Example Parser
==============

::

  from aa_airtable.parser import AbstractParser
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
      file_fields = [
          "NY Logo"
      ]


Support
=======
* Django 1.11
* Python 3.4-3.6

.. |travis| image:: https://secure.travis-ci.org/ArabellaTech/aa-airtable.svg?branch=master
.. _travis: http://travis-ci.org/ArabellaTech/aa-airtable

.. |pypi| image:: https://img.shields.io/pypi/v/aa-airtable.svg
.. _pypi: https://pypi.python.org/pypi/aa-airtable

.. |coveralls| image:: https://coveralls.io/repos/github/ArabellaTech/aa-airtable/badge.svg?branch=master
.. _coveralls: https://coveralls.io/github/ArabellaTech/aa-airtable

.. |requiresio| image:: https://requires.io/github/ArabellaTech/aa-airtable/requirements.svg?branch=master
.. _requiresio: https://requires.io/github/ArabellaTech/aa-airtable/requirements/
