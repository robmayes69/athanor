from django.conf import settings

from collections import defaultdict
from evennia.objects.objects import DefaultObject
from evennia.utils.utils import lazy_property, make_iter, class_from_module, list_to_string
from evennia.utils.ansi import ANSIString

from athanor.utils.events import EventEmitter
from athanor.utils.text import tabular_table
from athanor.utils import styling

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

        if self.account and self.sessions.all():
            self.sessions.all()[-1].execute_cmd("look")

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


class AthanorRoom(AthanorObject):
    object_types = ['room']


class AthanorExit(AthanorObject):
    object_types = ['exit']
