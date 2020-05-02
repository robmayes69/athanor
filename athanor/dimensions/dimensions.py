import re
from django.db.models import Q

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from athanor.models import DimensionDB
from athanor.utils.text import clean_and_ansi


class DefaultDimension(DimensionDB, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def at_first_save(self):
        pass

    def setup_dimension(self, **kwargs):
        pass

    @classmethod
    def create(cls, key, pluginspace, **kwargs):
        name = kwargs.pop('name', None)
        if name:
            clean_name, color_name = clean_and_ansi(name)
        else:
            clean_name = key
            color_name = key

        key, _key = clean_and_ansi(key)
        dimen = None
        try:
            dimen = cls(db_key=key, db_name=clean_name, db_cname=color_name, db_pluginspace=pluginspace)
            dimen.save()
            dimen.setup_dimension(**kwargs)
        except Exception as e:
            if dimen:
                dimen.delete()
            raise e
        return dimen
