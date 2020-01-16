from django.conf import settings
from evennia.server.serversession import ServerSession
from evennia.utils.utils import class_from_module


SESSION_MIXINS = []

for mixin in settings.SESSION_MIXINS:
    SESSION_MIXINS.append(class_from_module(mixin))


class AthanorSession(*SESSION_MIXINS, ServerSession):

    def at_sync(self):
        super().at_sync()
        if self.puppet and self.puppet.persistent and self.puppet.location is None:
            self.puppet.locations.recall()
