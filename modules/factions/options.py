from evennia.utils.optionclasses import BaseOption as _BaseOption
from modules.factions.factions import DefaultFaction as _DefaultFaction


class Faction(_BaseOption):

    def validate(self, value, **kwargs):
        return _DefaultFaction.search(value, kwargs.get('character', None))
