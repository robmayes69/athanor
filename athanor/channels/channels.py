import re
from django.db.models import Q

from evennia.typeclasses.managers import TypeclassManager
from evennia.typeclasses.models import TypeclassBase
from athanor.models import ChannelDB
from athanor.utils.text import clean_and_ansi


class DefaultChannel(ChannelDB, metaclass=TypeclassBase):
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    objects = TypeclassManager()

    def at_first_save(self):
        pass

    def generate_substitutions(self, viewer):
        return {"name": self.key,
                "cname": self.ckey,
                'typename': 'Channel'}

    @classmethod
    def create(cls, owner, key):
        clean_key, key = clean_and_ansi(key, thing_name="Channel Name")
        if not cls.re_name.match(clean_key):
            raise ValueError("Channel Names must be EXPLANATION HERE.")
        if (conflict := owner.owned_channels.filter(db_key__iexact=clean_key).first()):
            raise ValueError("Name conflicts with another Channel.")
        new_channel = cls(db_key=clean_key, db_ckey=key, db_owner=owner)
        new_channel.save()
        return new_channel

    def rename(self, key):
        """
        Renames a channel and updates all relevant fields.

        Args:
            key (str): The channel's new name. Can include ANSI codes.

        Returns:
            key (ANSIString): The successful key set.
        """
        clean_key, key = clean_and_ansi(key, thing_name="Channel Name")
        if not self.re_name.match(clean_key):
            raise ValueError("Channel name does not meet standards. Avoid double spaces and special characters.")
        if (conflict := self.owner.owned_channels.filter(db_key__iexact=clean_key).exclude(pk=self.pk).first()):
            raise ValueError("Name conflicts with another Character.")
        self.db_key = clean_key
        self.db_ckey = key
        self.save(update_fields=['db_key', 'db_ckey'])
        return key

    def __str__(self):
        return str(self.key)

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet_or_account()

    def render_prefix(self, recipient, sender):
        return f"<{self.owner.abbreviation}>"

    def allowed_listeners(self):
        subscriptions = self.subscriptions.exclude(Q(db_muted=True) | Q(db_enabled=False))
        return {sub for sub in subscriptions if self.check_position(sub.owner, 'listener')}

    def active_listeners(self, allowed=None):
        if allowed is None:
            allowed = self.allowed_listeners()
        return {sub for sub in allowed if sub.owner.sessions.count()}

    def broadcast(self, text, sending_session=None):
        sender = self.get_sender(sending_session)
        for subscription in self.active_listeners():
            owner = subscription.owner
            prefix = self.render_prefix(owner, sender)
            owner.msg(f"{prefix} {text.render(viewer=owner)}")

    def check_access(self, checker, lock):
        return self.access(checker, lock) or self.category.access(checker, lock)
