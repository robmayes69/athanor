from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.search import object_search
from athanor.characters.characters import AthanorPlayerCharacter
from evennia.utils.utils import lazy_property


class AthanorCommand(MuxCommand):
    locks = 'cmd:all();admin:perm(Admin)'

    @lazy_property
    def _column_color(self):
        if not hasattr(self, 'account'):
            return 'n'
        return self.account.options.column_names_color

    @lazy_property
    def _blank_separator(self):
        return self.styled_separator()

    @lazy_property
    def _blank_footer(self):
        return self.styled_footer()

    def styled_columns(self, text):
        return f"|{self._column_color}{text}|n"

    def func(self):
        try:
            if self.switches:
                if len(self.switches) > 1:
                    raise ValueError(f"{self.key} does not support multiple simultaneous switches!")
                switch = self.switches[0]
                return getattr(self, f"switch_{switch}")()

            self.switch_main()
        except ValueError as err:
            self.msg(f"ERROR: {str(err)}")
            return

    def search_characters(self, name, exact=False):
        return object_search(name, exact=exact, candidates=AthanorPlayerCharacter.objects.filter_family())

    def search_one_character(self, name, exact=False):
        results = self.search_characters(name, exact)
        if not results:
            raise ValueError(f"Cannot locate character named {name}!")
        if len(results) == 1:
            return results[0]
        raise ValueError(f"That matched: {results}")

    def sys_msg(self, msg, target=None):
        if not target:
            target = self.caller
        target.system_msg(msg, system_name=self.system_name, enactor=self.caller)

    def error(self, msg, target=None):
        self.sys_msg(f"ERROR: {msg}", target=target)