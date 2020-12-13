from evennia.utils.utils import lazy_property, make_iter, logger, to_str
from evennia.objects.models import ObjectDB
from athanor.access.acl import ACLMixin
from athanor.playtimes.models import PlaytimeDB
from athanor.identities.models import IdentityDB


class FakeSessionHandler:

    def all(self):
        return []

    def count(self):
        return 0

    def remove(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def add(self):
        pass


FAKE_SESSION_HANDLER = FakeSessionHandler()


class AthanorBaseObjectMixin(ACLMixin):

    def get_playtime(self):
        return self.db._playtime

    def get_identity(self):
        return IdentityDB.objects.filter(content_type=self.get_concrete_content_type(), object_id=self.id).first()

    @property
    def sessions(self):
        """
        Overloaded so that it transparently returns the SessionHandler of a playtime.
        If no playtime, then it returns a fake Session handler that has Sessions in order
        to satisfy the API.
        """
        if (playtime := self.get_playtime()):
            return playtime.sessions
        else:
            return FAKE_SESSION_HANDLER

    @property
    def is_connected(self):
        return bool(self.get_playtime())

    @property
    def is_superuser(self):
        if (playtime := self.get_playtime()):
            return playtime.is_superuser
        else:
            return False

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        Refer to evennia.objects.objects.DefaultObject's .msg().

        This overloaded approach ignores the session settings. Instead, it relays everything to the
        connected Playtime, if present.
        """
        if not (playtime := self.get_playtime()):
            # no reason to do anything if there's nobody listening...
            return

        if from_obj:
            for obj in make_iter(from_obj):
                try:
                    obj.at_msg_send(text=text, to_obj=self, **kwargs)
                except Exception:
                    logger.log_trace()

        try:
            if not self.at_msg_receive(text=text, **kwargs):
                # if at_msg_receive returns false, we abort message to this object
                return
        except Exception:
            logger.log_trace()

        # relay to playtime
        playtime.msg(text=text, from_obj=from_obj, puppet_obj=self, session=session, options=options, **kwargs)