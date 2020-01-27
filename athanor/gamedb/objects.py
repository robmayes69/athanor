from django.conf import settings

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property, make_iter, class_from_module

from athanor.utils.events import EventEmitter

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["OBJECT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorObject(*MIXINS, DefaultObject, EventEmitter):
    """
    Events Triggered:
        object_puppet (session): Fired whenever a Session puppets this object.
        object_disconnect (session): Triggered whenever a Session disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    hook_prefixes = ['object']

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
        }

    def at_post_puppet(self, **kwargs):
        """
        Calls the superclass at_post_puppet and also is sure to trigger relevant Events.

        Args:
            **kwargs: Whatever you want. it'll be passed to the Events.

        Returns:
            None
        """
        super().at_post_puppet(**kwargs)
        for pref in self.hook_prefixes:
            self.emit_global(f"{pref}_puppet", **kwargs)
        if len(self.sessions.all()) == 1:
            for pref in self.hook_prefixes:
                self.emit_global(f"{pref}_online")

        if self.account:
            # Execute a 'look' so the puppeter knows what's going on.
            self.msg((self.at_look(self.location), {"type": "look"}), options=None)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        Calls the superclass at_post_unpuppet and also is sure to trigger relevant Events.

        Args:
            account (AccountDB): The account that is un-puppeting.
            session (ServerSession): The Session that is un-puppeting.
            **kwargs: Any other relevant information?

        Returns:
            None
        """
        super().at_post_unpuppet(account, session, **kwargs)
        for pref in self.hook_prefixes:
            self.emit_global(f"{pref}_unpuppet", account=account, session=session, **kwargs)
        if not self.sessions.all():
            for pref in self.hook_prefixes:
                self.emit_global(f"{pref}_offline")

    def system_msg(self, text=None, system_name=None, enactor=None):
        if self.account:
            sysmsg_border = self.account.options.sys_msg_border
            sysmsg_text = self.account.options.sys_msg_text
        else:
            sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
            sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def get_puppet(self):
        return self

    def get_account(self):
        return self.account
