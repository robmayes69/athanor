from evennia.utils.utils import lazy_property, make_iter, logger
from athanor.identities.models import IdentityDB
from athanor.entities.handlers import EntityCmdHandler, EntityCmdSetHandler, EntityAclHandler
from athanor.zones.models import ZoneLink


class FakeSessionHandler:

    def all(self):
        return []

    def count(self):
        return 0

    def remove(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def add(self, *args, **kwargs):
        pass


FAKE_SESSION_HANDLER = FakeSessionHandler()


class AthanorBaseObjectMixin:

    @lazy_property
    def acl(self):
        return EntityAclHandler(self)

    @lazy_property
    def cmdset(self):
        return EntityCmdSetHandler(self)

    @lazy_property
    def cmd(self):
        return EntityCmdHandler(self)

    def get_playtime(self):
        return self.db._playtime

    def get_identity(self):
        return IdentityDB.objects.filter(content_type=self.get_concrete_content_type(), object_id=self.id).first()

    def get_zone(self):
        if (result := ZoneLink.objects.filter(db_object=self).first()):
            return result.db_zone
        return None

    def is_owner(self, to_check):
        if (zone := self.get_zone()):
            return zone.is_owner(to_check)
        return False

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
        return bool(self.sessions.count())

    @property
    def is_superuser(self):
        if (playtime := self.get_playtime()):
            return playtime.is_superuser and playtime.db_elevated
        else:
            return False

    @property
    def is_elevated(self) -> bool:
        if (playtime := self.get_playtime()):
            return bool(playtime.db_elevated)
        return False

    @property
    def is_building(self) -> bool:
        if (playtime := self.get_playtime()):
            return bool(playtime.db_building)
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

    def system_msg(self, text=None, system_name: str = "SYSTEM", target=None, enactor=None):
        if not text:
            return
        if not target:
            target = self
        if not enactor:
            enactor = self
        target.msg(f"|w{system_name}:|n {text}", from_obj=enactor)
