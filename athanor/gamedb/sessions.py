from django.conf import settings
from evennia.server.serversession import ServerSession
from evennia.utils.utils import class_from_module


MIXINS = []

for mixin in settings.MIXINS["SESSION"]:
    MIXINS.append(class_from_module(mixin))
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorSession(*MIXINS, ServerSession):

    def at_sync(self):
        super().at_sync()
        if self.puppet and self.puppet.persistent and self.puppet.location is None:
            self.puppet.locations.recall()
