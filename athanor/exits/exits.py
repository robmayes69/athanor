import re
from django.db.models import Q

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from athanor.models import ExitDB
from athanor.utils.text import clean_and_ansi


class AthanorExit(ExitDB, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def at_first_save(self):
        pass
