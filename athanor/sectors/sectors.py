import re

from evennia.typeclasses.models import TypeclassBase
from evennia.utils.ansi import ANSIString
from athanor.sectors.models import SectorDB, SectorLink
from athanor.access.acl import ACLMixin


class DefaultSector(ACLMixin, SectorDB, metaclass=TypeclassBase):
    _verbose_name = 'Sector'
    _verbose_name_plural = "Sectors"
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def at_first_save(self):
        pass
