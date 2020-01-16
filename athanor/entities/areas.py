from django.conf import settings
from evennia.utils.utils import class_from_module
from athanor.entities.base import AbstractMapEntity

AREA_MIXINS = []

for mixin in settings.AREA_MIXINS:
    AREA_MIXINS.append(class_from_module(mixin))


class AthanorArea(*AREA_MIXINS, AbstractMapEntity):

    def __init__(self, unique_key, handler, data):
        AbstractMapEntity.__init__(self, unique_key, handler, data)
        self.description = data.get("description", "")
        self.entities = set()
        self.rooms = set()
