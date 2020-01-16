from django.conf import settings
from django.utils.translation import ugettext as _

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property, make_iter
from evennia.utils import logger

from athanor.entities.base import AbstractGameEntity


class AthanorObject(DefaultObject, AbstractGameEntity):
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
    def location(self):
        return self.locations.room

    @location.setter
    def location(self, value):
        self.locations.set(value)

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

    def move_to(self, destination, quiet=False, emit_to_obj=None, use_destination=False, to_none=False, move_hooks=True,
                **kwargs):
        """
        Re-implementation of Evennia's move_to to account for the new grid. See original documentation.

        Destination MUST be in the format of:
        1. A Room object.
        2. None
        3. #DBREF/room_key - For structures. example: #5/docking_bay
        4. region_key/room_key - For example, limbo_dimension/northern_limbo

        use_destination will be ignored.
        """
        def logerr(string="", err=None):
            """Simple log helper method"""
            logger.log_trace()
            self.msg("%s%s" % (string, "" if err is None else " (%s)" % err))
            return

        errtxt = _("Couldn't perform move ('%s'). Contact an admin.")
        if not emit_to_obj:
            emit_to_obj = self

        if not destination:
            if to_none:
                # immediately move to None. There can be no hooks called since
                # there is no destination to call them with.
                self.location = None
                return True
            emit_to_obj.msg(_("The destination doesn't exist."))
            return False
        if use_destination and hasattr(destination, 'destination'):
            # traverse exits
            # destination = destination.destination
            pass

        if isinstance(destination, str):
            from evennia import GLOBAL_SCRIPTS
            destination = GLOBAL_SCRIPTS.plugin.resolve_room_path(destination)

        # Before the move, call eventual pre-commands.
        if move_hooks:
            try:
                if not self.at_before_move(destination):
                    return False
            except Exception as err:
                logerr(errtxt % "at_before_move()", err)
                return False

        # Save the old location
        source_location = self.location

        # Call hook on source location
        if move_hooks and source_location:
            try:
                source_location.at_object_leave(self, destination)
            except Exception as err:
                logerr(errtxt % "at_object_leave()", err)
                return False

        if not quiet:
            # tell the old room we are leaving
            try:
                self.announce_move_from(destination, **kwargs)
            except Exception as err:
                logerr(errtxt % "at_announce_move()", err)
                return False

        # Perform move
        try:
            self.location = destination
        except Exception as err:
            logerr(errtxt % "location change", err)
            return False

        if not quiet:
            # Tell the new room we are there.
            try:
                self.announce_move_to(source_location, **kwargs)
            except Exception as err:
                logerr(errtxt % "announce_move_to()", err)
                return False

        if move_hooks:
            # Perform eventual extra commands on the receiving location
            # (the object has already arrived at this point)
            try:
                destination.at_object_receive(self, source_location)
            except Exception as err:
                logerr(errtxt % "at_object_receive()", err)
                return False

        # Execute eventual extra commands on this object after moving it
        # (usually calling 'look')
        if move_hooks:
            try:
                self.at_after_move(source_location)
            except Exception as err:
                logerr(errtxt % "at_after_move", err)
                return False
        return True

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
