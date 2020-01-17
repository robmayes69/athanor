from django.conf import settings
from evennia.server.serversession import ServerSession
from evennia.utils.utils import class_from_module

MIXINS = [class_from_module(mixin) for mixin in settings.MIXINS["SESSION"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorSession(*MIXINS, ServerSession):

    def at_sync(self):
        super().at_sync()
        for mixin in MIXINS:
            if hasattr(mixin, "mixin_at_sync"):
                mixin.mixin_at_sync(self)
