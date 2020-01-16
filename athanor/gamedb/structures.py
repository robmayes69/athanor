from django.conf import settings

from evennia.utils.utils import class_from_module
from athanor.gamedb.objects import AthanorObject

STRUCTURE_MIXINS = []

for mixin in settings.STRUCTURE_MIXINS:
    STRUCTURE_MIXINS.append(class_from_module(mixin))


class AthanorStructure(*STRUCTURE_MIXINS, AthanorObject):
    pass
