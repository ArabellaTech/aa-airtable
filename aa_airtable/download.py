import json

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.dateformat import format
from django.utils.timezone import now

from aa_airtable.settings import airtable_settings


def get():
    if not airtable_settings.API_KEY:
        raise NotImplementedError("Missing API_KEY")

    headers = {
        "Authorization": "Bearer {}".format(airtable_settings.API_KEY),
    }

    dbs = airtable_settings.DATABASES
    if not dbs:
        raise NotImplementedError("Missing DATABASES")

    full_dump = {}
    for db_key, tables in dbs.items():
        dump = {}
        for table in tables:
            dump[table[0]] = []
            url = "{url}{db}/{table}".format(url=airtable_settings.ENDPOINT_URL, db=db_key, table=table[0])
            params = {
                "limit": 100
            }
            while (True):
                response = requests.get(url, params=params, headers=headers)
                if response.status_code != requests.codes.ok:
                    raise Exception(response.text)
                data = response.json()
                dump[table[0]] += data.get("records", [])
                if not data.get("offset"):
                    break
                params["offset"] = data["offset"]
        full_dump[db_key] = dump

    path = "{dir}/{date}.json".format(dir=airtable_settings.DATA_DIRECTORY, date=format(now(), "Y-m-d-H-i-s"))
    default_storage.save(path, ContentFile(json.dumps(full_dump)))
    return path, full_dump
