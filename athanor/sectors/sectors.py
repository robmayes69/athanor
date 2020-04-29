import re
from django.db.models import Q

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from athanor.models import SectorDB
from athanor.utils.text import clean_and_ansi


class DefaultSector(SectorDB, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def at_first_save(self):
        pass
