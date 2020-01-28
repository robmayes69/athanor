import time
from django.conf import settings

from collections import defaultdict

from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString
from evennia.utils import logger

from athanor.utils.events import EventEmitter
from athanor.utils.text import tabular_table
from athanor.utils import styling


class AthanorBaseObjectMixin(EventEmitter):
    """
    This class implements most of the actual LOGIC of Athanor's particulars around how Objects work.
    It is provided as a mixin so other code besides AthanorObject can reference it.
    """
    hook_prefixes = ['object']
    object_types = ['object']

    @lazy_property
    def contents_index(self):
        indexed = defaultdict(list)
        for obj in self.contents:
            for obj_type in obj.object_types:
                indexed[obj_type].append(obj)
        return indexed

    def register_index(self, obj):
        index = self.contents_index
        for obj_type in obj.object_types:
            if obj in index[obj_type]:
                continue
            index[obj_type].append(obj)

    def unregister_index(self, obj):
        index = self.contents_index
        for obj_type in obj.object_types:
            if obj not in index[obj_type]:
                continue
            index[obj_type].remove(obj)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        super().at_object_receive(moved_obj, source_location, **kwargs)
        self.register_index(moved_obj)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        super().at_object_leave(moved_obj, target_location, **kwargs)
        self.unregister_index(moved_obj)

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
        self.account.db._last_puppet = self
        for pref in self.hook_prefixes:
            self.emit_global(f"{pref}_puppet", **kwargs)
        if len(self.sessions.all()) == 1:
            for pref in self.hook_prefixes:
                self.emit_global(f"{pref}_online")


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

    def get_exit_formatted(self, looker, **kwargs):
        aliases = self.aliases.all()
        alias = aliases[0] if aliases else ''
        alias = ANSIString(f"<|w{alias}|n>")
        display = f"{self.key} to {self.destination.key}"
        return f"""{alias:<6} {display}"""

    def return_appearance_exits(self, looker, **kwargs):
        exits = sorted([ex for ex in self.contents_index['exit'] if ex.access(looker, "view")],
                       key=lambda ex: ex.key)
        message = list()
        if not exits:
            return message
        message.append(styling.styled_separator(looker, "Exits"))
        exits_formatted = [ex.get_exit_formatted(looker, **kwargs) for ex in exits]

        message.append(tabular_table(exits_formatted, field_width=37, line_length=78))

    def return_appearance_characters(self, looker, **kwargs):
        users = sorted([user for user in self.contents_index['character'] if user.access(looker, "view")],
                       key=lambda user: user.get_display_name(looker))
        message = list()
        if not users:
            return message
        message.append(styling.styled_separator(looker, "Characters"))
        message.extend([user.get_room_appearance(looker, **kwargs) for user in users])
        return message

    def get_room_appearance(self, looker, **kwargs):
        return self.get_display_name(looker, **kwargs)

    def return_appearance_items(self, looker, **kwargs):
        visible = (con for con in self.contents_index['item'] if con.access(looker, "view"))
        things = defaultdict(list)
        for con in visible:
            things[con.get_display_name(looker)].append(con)
        message = list()
        if not things:
            return message
        message.append(styling.styled_separator(looker, "Items"))
        for key, itemlist in sorted(things.items()):
            nitem = len(itemlist)
            if nitem == 1:
                key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
            else:
                key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                    0
                ]
            message.append(key)
        return message

    def return_appearance_description(self, looker, **kwargs):
        message = list()
        if (desc := self.db.desc):
            message.append(desc)
        return message

    def return_appearance_header(self, looker, **kwargs):
        return [styling.styled_header(looker, self.get_display_name(looker))]

    def return_appearance(self, looker, **kwargs):
        if not looker:
            return ""
        message = list()
        message.extend(self.return_appearance_header(looker, **kwargs))
        message.extend(self.return_appearance_description(looker, **kwargs))
        message.extend(self.return_appearance_items(looker, **kwargs))
        message.extend(self.return_appearance_characters(looker, **kwargs))
        message.extend(self.return_appearance_exits(looker, **kwargs))
        message.append(styling.styled_footer(looker))

        return '\n'.join(str(l) for l in message)

    @property
    def idle_time(self):
        """
        Returns the idle time of the least idle session in seconds. If
        no sessions are connected it returns nothing.
        """
        idle = [session.cmd_last_visible for session in self.sessions.all()]
        if idle:
            return time.time() - float(max(idle))
        return None

    @property
    def connection_time(self):
        """
        Returns the maximum connection time of all connected sessions
        in seconds. Returns nothing if there are no sessions.
        """
        conn = [session.conn_time for session in self.sessions.all()]
        if conn:
            return time.time() - float(min(conn))
        return None

    def move_to(self, destination, quiet=False, emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True,
                arbitrary=False, **kwargs):
        """
        Same as DefaultObject move_to but with some additions and tweaks. You should ALWAYS use this when
        writing code and not obj.location.

        Args:
            (see original)
            arbitrary: This move is happening, period, as long as the destination is valid. It cannot be stopped.
        """

        def logerr(string="", err=None):
            """Simple log helper method"""
            logger.log_trace()
            self.msg("%s%s" % (string, "" if err is None else " (%s)" % err))
            return

        errtxt = _("Couldn't perform move ('%s'). Contact an admin.")
        if not emit_to_obj:
            emit_to_obj = self

        if destination and destination.destination and use_destination:
            # traverse exits
            destination = destination.destination

        # Before the move, call eventual pre-commands.
        if move_hooks:
            try:
                if not self.at_before_move(destination) and not arbitrary:
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
                logerr(errtxt % "announce_move_from()", err)
                return False

        if not destination:
            if to_none:
                # immediately move to None. There can be no hooks called since
                # there is no destination to call them with.
                self.location = None
                return True
            emit_to_obj.msg(_("The destination doesn't exist."))
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

class AthanorBasePlayerMixin(object):
    hook_prefixes = ['object', 'character']
    object_types = ['character']

    def render_character_menu_line(self, cmd):
        return self.key

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Re-implements DefaultCharacter's at_pre_puppet. nothing to see here. Literally a direct copy.
        """
        super().at_pre_puppet(account, session=session, **kwargs)
        if self.location is None:  # Make sure character's location is never None before being puppeted.
            # Return to last location (or home, which should always exist),
            self.location = self.db.prelogout_location if self.db.prelogout_location else self.home
            self.location.at_object_receive(self, None)  # and trigger the location's reception hook.
        if self.location:  # If the character is verified to be somewhere,
            self.db.prelogout_location = self.location  # save location again to be sure.
        else:
            account.msg(
                "|r%s has no location and no home is set.|n" % self, session=session
            )  # Note to set home.

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        self.msg("\nYou become |c%s|n.\n" % self.name)
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg("%s has entered the game." % self.get_display_name(obj), from_obj=from_obj)

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        if not self.sessions.count():
            if self.location:

                def message(obj, from_obj):
                    obj.msg("%s has left the game." % self.get_display_name(obj), from_obj=from_obj)

                self.location.for_contents(message, exclude=[self], from_obj=self)
                self.db.prelogout_location = self.location
                self.location = None
