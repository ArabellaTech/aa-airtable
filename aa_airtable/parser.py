from importlib import import_module

from django.db.models import Q

from aa_airtable.models import UploadedFile
from aa_airtable.settings import airtable_settings


class DatabasesParser(object):

    def __init__(self, data):
        self.data = data

        for db_key, tables in airtable_settings.DATABASES.items():
            if db_key not in self.data:
                continue

            for table in tables:
                if table[0] in self.data[db_key]:
                    parts = table[1].split('.')
                    module_path, class_name = '.'.join(parts[:-1]), parts[-1]
                    module = import_module(module_path)
                    parser_class = getattr(module, class_name)
                    parser_class(data[db_key][table[0]])


class AbstractParser(object):
    model = None
    manager = None
    raw_fields = []  # airtable field or tuple (model field, airtable field)
    file_fields = []
    related_fields = []  # model field, airtable field, related model

    def __init__(self, items):
        self.manager = self.model.objects
        if hasattr(self.model, "default_objects"):
            self.manager = self.model.default_objects
        items_ids = []
        fields = {}

        for item in items:
            fields = self.get_extra_fields(item)
            obj = self.parse_item(item, fields)
            if obj:
                items_ids.append(obj.id)

        self.remove_obsolete(items_ids)
        self.post_process()

    def post_process(self):
        pass

    def get_extra_fields(self, item):
        return {}

    def parse_item(self, item, fields=None):
        if not fields:
            fields = {}

        data = item["fields"]

        for field in self.raw_fields:
            if isinstance(field, str):
                field = [field.lower().replace(" ", "_"), field]
            fields[field[0]] = data.get(field[1])

        for field in self.file_fields:
            if isinstance(field, str):
                field = [field.lower().replace(" ", "_"), field]
            url = ""
            if data.get(field[1]):
                try:
                    url = UploadedFile.save_file(data[field[1]][0])
                except IndexError:
                    pass
            fields[field[0]] = url

        obj, created = self.manager.get_or_create(airtable_id=item["id"], defaults=fields)
        if not created:
            for key, value in fields.items():
                setattr(obj, key, value)
            obj.save()

        for field in self.related_fields:
            related_field = getattr(obj, field[0])
            if data.get(field[1]):
                for related in data[field[1]]:
                    if not isinstance(related_field, str) \
                            and not related_field.filter(airtable_id=related).exists():
                        try:
                            related_field.add(field[2].objects.get(airtable_id=related))
                        except getattr(field[2], "DoesNotExist"):
                            pass
            if not isinstance(related_field, str):
                if not data.get(field[1]):
                    related_field.clear()
                else:
                    related_field.remove(*related_field.exclude(airtable_id__in=data[field[1]]))
        return obj

    def remove_obsolete(self, ids, filters=None):
        qs = self.manager.all()
        if filters:
            qs = qs.filter(**filters)
        qs.exclude(Q(id__in=ids) | Q(airtable_id="")).delete()
