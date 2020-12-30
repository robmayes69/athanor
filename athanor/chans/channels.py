import re
from django.db.models import Q
from django.db.utils import IntegrityError

from evennia.comms.comms import DefaultChannel
from evennia.utils.utils import lazy_property
from evennia.utils.create import create_channel
from athanor.utils.text import clean_and_ansi
from athanor.utils import error
from athanor.chans.models import ChannelStub
from athanor.chans.handlers import ChannelACLHandler


class AthanorChannel(DefaultChannel):
    _verbose_name = 'Channel'
    _verbose_name_plural = 'Channels'
    _name_standards = "Avoid double spaces and special characters."
    _re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    @lazy_property
    def acl(self):
        return ChannelACLHandler(self)

    @classmethod
    def _validate_channel_name(cls, name, owner, exclude=None):
        """
        Checks if an Channel name is both valid and not in use. Returns a tuple of (name, clean_name).
        """
        if not name:
            raise error.BadNameException(f"{cls._verbose_name_plural} must have a name!")
        clean_name, name = clean_and_ansi(name, thing_name="Channel Name")
        if not cls._re_name.match(clean_name):
            raise error.BadNameException(f"{cls._verbose_name} Name does not meet standards. {cls._name_standards}")
        query = owner.chans.filter(db_ikey=clean_name.lower())
        if exclude:
            query = query.exclude(id=exclude.id)
        if (found := query.first()):
            raise error.BadNameException(f"Name conflicts with another {cls._verbose_name}")
        return (name, clean_name)

    @classmethod
    def _validate_channel(cls, name, clean_name, **kwargs):
        """
        Performs all other validation checks for creating the Zone.
        """
        return None

    @classmethod
    def _create_channel(cls, name, clean_name, owner, validated_data, **kwargs):
        """
        Does the actual work of creating the Channel.
        """
        channel = None
        errors = None
        try:
            channel = create_channel(clean_name, typeclass=cls)
            stub = ChannelStub(db_channel=channel, db_owner=owner, db_ikey=clean_name.lower(),
                               db_ckey=name)
            stub.save()
        except IntegrityError as e:
            channel.delete()
            raise error.BadNameException("Invalid name for a Zone! Is it already in use?")
        return channel

    def at_first_save(self):
        pass

    def generate_substitutions(self, viewer):
        return {"name": self.key,
                "cname": self.ckey,
                'typename': 'Channel'}

    @classmethod
    def create(cls, name, owner, **kwargs):
        name, clean_name = cls._validate_channel_name(name, owner)
        validated = cls._validate_channel(name, clean_name, **kwargs)
        channel = cls._create_channel(name, clean_name, owner, validated, **kwargs)
        channel.at_zone_creation(validated)
        return channel

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

    def at_channel_creation(self, validated):
        pass
