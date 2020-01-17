from django.conf import settings
from django.utils.translation import ugettext as _

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property, make_iter, class_from_module
from evennia.utils import logger

from athanor.entities.base import AbstractGameEntity

MIXINS = []

for mixin in settings.MIXINS["OBJECT"]:
    MIXINS.append(class_from_module(mixin))
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorObject(*MIXINS, AbstractGameEntity, DefaultObject):
    """
    This is used as the new 'base' for DefaultRoom, DefaultCharacter, etc. It alters how locations and contents work.
    """
    persistent = True

    @lazy_property
    def inventory_location(self):
        return None

    @lazy_property
    def gear_location(self):
        return None

    @property
    def contents(self):
        """
        This must return a list for commands to work properly.

        Returns:
            items (list)
        """
        return self.items.all()

    def contents_get(self, exclude=None):
        if not exclude:
            return self.contents
        return list(set(self.contents) - set(make_iter(exclude)))


    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Return the character from storage in None location in `at_post_unpuppet`.
        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
        """
        # Make sure character's location is never None before being puppeted.
        # Return to last location (or home, which should always exist),
        if not self.location:
            try:
                self.locations.recall()
            except ValueError as e:
                self.location = settings.START_LOCATION

    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.

        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.

        """
        self.msg("\nYou become |c%s|n.\n" % self.name)
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg(
                "%s has entered the game." % self.get_display_name(obj),
                from_obj=from_obj,
            )

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        We stove away the character when the account goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the account logged off ("headless", so to say).

        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not self.sessions.count():
            # only remove this char from grid if no sessions control it anymore.
            if self.location:

                def message(obj, from_obj):
                    obj.msg(
                        "%s has left the game." % self.get_display_name(obj),
                        from_obj=from_obj,
                    )

                self.location.for_contents(message, exclude=[self], from_obj=self)
                self.locations.save()
                self.location = None

    def at_server_reload(self):
        self.locations.save()
