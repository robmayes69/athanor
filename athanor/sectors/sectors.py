import re

from evennia.typeclasses.models import TypeclassBase
from evennia.utils.ansi import ANSIString
from athanor.sectors.models import SectorDB, SectorLink


class DefaultSector(SectorDB, metaclass=TypeclassBase):
    _verbose_name = 'Sector'
    _verbose_name_plural = "Sectors"
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def at_first_save(self):
        pass

    def is_owner(self, to_check):
        return self.db_owner == to_check.get_identity()