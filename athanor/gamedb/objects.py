from collections import defaultdict

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property

import athanor
from athanor.gamedb.base import AthanorBaseObjectMixin, AthanorExitMixin, HasRenderExamine
from athanor.utils.events import EventEmitter
from athanor.models import LocationStorage


class AthanorBaseObject(HasRenderExamine, EventEmitter, DefaultObject):
    """
    Events Triggered:
        object_puppet (session): Fired whenever a Session puppets this object.
        object_disconnect (session): Triggered whenever a Session disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    dbtype = 'ObjectDB'
    hook_prefixes = ['object']
    contents_categories = ['item']
    examine_type = "object"
    examine_caller_type = 'object'

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
        return message

    def render_examine_contents(self, viewer, cmdset, styling):
        if not (contents_index := self.contents_index):
            return list()
        message = list()
        for category, contents in contents_index.items():
            message.append(styling.styled_separator(f"Contents: {category.capitalize()}s"))
            message.append(', '.join([f'{t.name}({t.dbref})' for t in contents]))
        return message

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
        }

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

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")


class AthanorOOCObject(AthanorBaseObject):
    """
    This is the base class used by all Objects which do NOT have an in-game-world presence.
    They will not be 'looked' at, they will not be entered. They are never loot... really, they're just here as
    data storage containers and foreign key shenanigans.
    """



class AthanorICObject(AthanorBaseObject):
    """
    The base class for all player avatars, mobiles, rooms, exits, items, etc. These are 'tangible' objects that have an
    in-game presence and thus require material properties and interaction rules.
    """

    @property
    def exits(self):
        return self.contents_index['exit']

    @lazy_property
    def contents_index(self):
        indexed = defaultdict(list)
        for obj in self.contents:
            self.register_index(obj, index=indexed)
        return indexed

    def delete(self):
        if self.location:
            self.location.unregister_index(self)
        return super().delete()

    def register_index(self, obj, index=None):
        if index is None:
            index = self.contents_index
        for obj_type in obj.contents_categories:
            if obj in index[obj_type]:
                continue
            index[obj_type].append(obj)

    def unregister_index(self, obj, index=None):
        if index is None:
            index = self.contents_index
        for obj_type in obj.contents_categories:
            if obj not in index[obj_type]:
                continue
            index[obj_type].remove(obj)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        super().at_object_receive(moved_obj, source_location, **kwargs)
        self.register_index(moved_obj)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        super().at_object_leave(moved_obj, target_location, **kwargs)
        self.unregister_index(moved_obj)

    def save_location(self, name, location=None):
        if not location:
            location = self.location
        if not location:
            return False

    def delete_location(self, name):
        LocationStorage.objects.filter(obj=self, name=name).delete()

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

class AthanorRoom(AthanorICObject):
    contents_categories = ['room']


class AthanorExit(AthanorExitMixin, AthanorICObject):
    """
    Re-implements most of DefaultExit...
    """
    pass
