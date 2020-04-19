from collections import defaultdict
from evennia.utils.ansi import ANSIString
from athanor.utils.text import tabular_table


class AppearanceHandler:
    hooks = []

    def __init__(self, obj):
        self.obj = obj

    def description(self, looker, styling, **kwargs):
        message = list()
        if (desc := self.obj.db.desc):
            message.append(desc)
        return message

    def header(self, looker, styling, **kwargs):
        return [styling.styled_header(self.obj.get_display_name(looker))]

    def render(self, looker, **kwargs):
        if not looker:
            return ""
        styling = looker.styler
        message = list()
        for hook in self.hooks:
            message.extend(getattr(self, hook)(looker, styling, **kwargs))
        message.append(styling.blank_footer)

        return '\n'.join(str(l) for l in message)


class ObjectAppearanceHandler(AppearanceHandler):
    hooks = ['header', 'description', 'items', 'characters', 'exits']

    def get_exit_formatted(self, looker, **kwargs):
        aliases = self.obj.aliases.all()
        alias = aliases[0] if aliases else ''
        alias = ANSIString(f"<|w{alias}|n>")
        display = f"{self.obj.key} to {self.obj.destination.key}"
        return f"""{alias:<6} {display}"""

    def exits(self, looker, styling, **kwargs):
        exits = sorted([ex for ex in self.obj.exits if ex.access(looker, "view")],
                       key=lambda ex: ex.key)
        message = list()
        if not exits:
            return message
        message.append(styling.styled_separator("Exits"))
        exits_formatted = [ex.get_exit_formatted(looker, **kwargs) for ex in exits]
        message.append(tabular_table(exits_formatted, field_width=37, line_length=78))
        return message

    def characters(self, looker, styling, **kwargs):
        users = sorted([user for user in self.obj.contents_get(content_type='mobile') if user.access(looker, "view")],
                       key=lambda user: user.get_display_name(looker))
        message = list()
        if not users:
            return message
        message.append(styling.styled_separator("Characters"))
        message.extend([user.get_room_appearance(looker, **kwargs) for user in users])
        return message

    def get_room_appearance(self, looker, **kwargs):
        return self.obj.get_display_name(looker, **kwargs)

    def items(self, looker, styling, **kwargs):
        visible = (con for con in self.obj.contents_get(content_type='item') if con.access(looker, "view"))
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
