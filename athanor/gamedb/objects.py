import time
from collections import defaultdict
from django.conf import settings

from evennia.objects.objects import DefaultObject, DefaultCharacter, DefaultExit, DefaultRoom
from evennia.utils.ansi import ANSIString
from evennia.utils import utils

import athanor
from athanor.utils.text import tabular_table
from athanor.utils.mixins import HasSessions


class _AthanorBaseObject(HasSessions):
    """
    General mixin applied to all types of things.

    Events Triggered:
        object_puppet (session): Fired whenever a Session puppets this object.
        object_disconnect (session): Triggered whenever a Session disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    dbtype = 'ObjectDB'

    hook_prefixes = ['object']
    examine_type = "object"
    examine_caller_type = 'object'

    def cmd(self):
        pass

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        account = session.get_account()
        if not account:
            # not logged in. How did this even happen?
            raise ValueError("You are not logged in to an account!")
        if session in self.sessions.all():
            # already puppeting this object
            raise ValueError("You are already puppeting this object.")
        if not self.access(account, "puppet"):
            # no access
            raise ValueError(f"You don't have permission to puppet '{self.key}'.")
        me_account = self.get_account()
        if me_account and me_account != account:
            raise ValueError(f"|c{self.key}|R is already puppeted by another Account.")

    def at_before_link_session_multisession(self, session, force=False, sync=False, **kwargs):
        """
        Multisession logic is performed here. This should not stop the link process.
        """
        # object already puppeted
        # we check for whether it's the same account in a _validate_puppet_request.
        # if we reach here, assume that it's either no account or the same account
        if (others := self.sessions.all()):
            # we may take over another of our sessions
            # output messages to the affected sessions
            if settings.MULTISESSION_MODE in (1, 3):
                txt1 = f"Sharing |c{self.name}|n with another of your sessions."
                txt2 = f"|c{self.name}|n|G is now shared from another of your sessions.|n"
                session.msg(txt1)
                self.msg(txt2, session=others)
            else:
                txt1 = f"Taking over |c{self.name}|n from another of your sessions."
                txt2 = f"|c{self.name}|n|R is now acted from another of your sessions.|n"
                session.msg(txt1)
                self.msg(txt2, session=others)
                print(f"UNLINKING: {others}")
                for other in others:
                    other.unlink('puppet', self, force=True, reason="Taken over by another session")

    def at_before_link_session_unstow(self, session, force=False, sync=False, **kwargs):
        """
        Some things are kept in null-space or alternate locations. Use this hook for relocating
        an object before it is puppeted.
        """
        pass

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        # First, check multisession status. Kick off anyone as necessary.
        self.at_before_link_session_multisession(session, force, sync, **kwargs)
        # Next, call the hook for object relocation.
        self.at_before_link_session_unstow(session, force, sync, **kwargs)

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.puid = self.pk
        session.puppet = self
        existing = self.sessions.all()
        self.sessions.add(session)

        # Don't need to validate scripts if there already were sessions attached.
        if not existing:
            self.scripts.validate()

        if sync:
            self.locks.cache_lock_bypass(self)

    def at_after_link_session_message(self, session, force=False, sync=False, **kwargs):
        """
        Used for sending messages announcing that you have connected. Maybe to you?
        Maybe to people in the same location?
        """
        self.msg(f"You become |w{self.key}|n.")

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        session.account.db._last_puppet = self

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.puid = None
        session.puppet = None
        self.sessions.remove(session)

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass



    def render_examine(self, viewer):
        obj_session = self.sessions.get()[0] if self.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, self.account, self, self.examine_caller_type, "examine"
        ).addCallback(self.render_examine_callback, viewer)

    def render_examine_object(self, viewer, cmdset, styling, type_name="Object"):
        message = [
            styling.styled_separator(f"{type_name} Properties"),
            f"|wName/key|n: |c{self.key}|n ({self.dbref})",
            f"|wTypeclass|n: {self.typename} ({self.typeclass_path})"
        ]
        if (aliases := self.aliases.all()):
            message.append(f"|wAliases|n: {', '.join(utils.make_iter(str(aliases)))}")
        if (sessions := self.sessions.all()):
            message.append(f"|wSessions|n: {', '.join(str(sess) for sess in sessions)}")
        message.append(f"|wHome:|n {self.home} ({self.home.dbref if self.home else None})")
        message.append(f"|wLocation:|n {self.location} ({self.location.dbref if self.location else None})")
        if (destination := self.destination):
            message.append(f"|wDestination|n: {destination} ({destination.dbref})")
        return message

    def render_examine_access(self, viewer, cmdset, styling):
        locks = str(self.locks)
        if locks:
            locks_string = utils.fill("; ".join([lock for lock in locks.split(";")]), indent=6)
        else:
            locks_string = " Default"
        message = [
            styling.styled_separator("Access"),
            f"|wPermissions|n: {', '.join(perms) if (perms := self.permissions.all()) else '<None>'}",
            f"|wLocks|n:{locks_string}"
        ]
        return message

    def render_examine_puppeteer(self, viewer, cmdset, styling):
        if not (account := self.account):
            return list()
        return account.render_examine_puppeteer(viewer, cmdset, styling)

    def render_examine_scripts(self, viewer, cmdset, styling):
        if not (scripts := self.scripts.all()):
            return list()
        message = [
            styling.styled_separator("Scripts"),
            scripts
        ]
        return message()

    def render_examine_contents(self, viewer, cmdset, styling):
        if not (contents_index := self.contents_index):
            return list()
        message = list()
        for category, contents in contents_index.items():
            message.append(styling.styled_separator(f"Contents: {category.capitalize()}s"))
            message.append(', '.join([f'{t.name}({t.dbref})' for t in contents]))
        return message

    @property
    def styler(self):
        if self.account:
            return self.account.styler
        return athanor.STYLER(self)

    @property
    def colorizer(self):
        if self.account:
            return self.account.colorizer
        return dict()

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
        }

    def system_msg(self, text=None, system_name=None):
        if self.account:
            sysmsg_border = self.account.options.sys_msg_border
            sysmsg_text = self.account.options.sys_msg_text
        else:
            sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
            sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

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

    def return_appearance_exits(self, looker, styling, **kwargs):
        exits = sorted([ex for ex in self.exits if ex.access(looker, "view")],
                       key=lambda ex: ex.key)
        message = list()
        if not exits:
            return message
        message.append(styling.styled_separator("Exits"))
        exits_formatted = [ex.get_exit_formatted(looker, **kwargs) for ex in exits]
        message.append(tabular_table(exits_formatted, field_width=37, line_length=78))
        return message

    def return_appearance_characters(self, looker, styling, **kwargs):
        users = sorted([user for user in self.contents_index['character'] if user.access(looker, "view")],
                       key=lambda user: user.get_display_name(looker))
        message = list()
        if not users:
            return message
        message.append(styling.styled_separator("Characters"))
        message.extend([user.get_room_appearance(looker, **kwargs) for user in users])
        return message

    def get_room_appearance(self, looker, **kwargs):
        return self.get_display_name(looker, **kwargs)

    def return_appearance_items(self, looker, styling, **kwargs):
        visible = (con for con in self.contents_index['item'] if con.access(looker, "view"))
        things = defaultdict(list)
        for con in visible:
            things[con.get_display_name(looker)].append(con)
        message = list()
        if not things:
            return message
        message.append(styling.styled_separator("Items"))
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

    def return_appearance_description(self, looker, styling, **kwargs):
        message = list()
        if (desc := self.db.desc):
            message.append(desc)
        return message

    def return_appearance_header(self, looker, styling, **kwargs):
        return [styling.styled_header(self.get_display_name(looker))]

    def return_appearance(self, looker, **kwargs):
        if not looker:
            return ""
        styling = looker.styler
        message = list()
        message.extend(self.return_appearance_header(looker, styling, **kwargs))
        message.extend(self.return_appearance_description(looker, styling, **kwargs))
        message.extend(self.return_appearance_items(looker, styling, **kwargs))
        message.extend(self.return_appearance_characters(looker, styling, **kwargs))
        message.extend(self.return_appearance_exits(looker, styling, **kwargs))
        message.append(styling.blank_footer)

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

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")


class AthanorObject(_AthanorBaseObject, DefaultObject):
    pass


class AthanorRoom(_AthanorBaseObject, DefaultRoom):
    pass


class AthanorExit(_AthanorBaseObject, DefaultExit):
    pass


class AthanorMobile(_AthanorBaseObject, DefaultCharacter):
    """
    The concept of a 'character' has been moved to Identities in Athanor. There are no 'character' objects.
    They are installed called Mobiles. This leads to further delineation such as player avatars and NPCs.
    """
    _content_types = ("mobile",)
