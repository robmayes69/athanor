from django.conf import settings

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property, make_iter, class_from_module

from athanor.utils.events import EventEmitter

MIXINS = [class_from_module(mixin) for mixin in settings.MIXINS["OBJECT_OBJECT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorObject(*MIXINS, DefaultObject, EventEmitter):
    pass
