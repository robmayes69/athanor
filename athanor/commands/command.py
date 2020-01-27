from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import lazy_property
from evennia.utils.search import object_search

import athanor


class AthanorCommand(MuxCommand):
    locks = 'cmd:all();admin:perm(Admin)'
    system_name = None

    @property
    def controllers(self):
        return athanor.CONTROLLER_MANAGER

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

    def sys_msg(self, msg, target=None):
        if not target:
            target = self.caller
        target.system_msg(msg, system_name=self.system_name, enactor=self.caller)

    def error(self, msg, target=None):
        self.sys_msg(f"ERROR: {msg}", target=target)

    def parse(self):
        super().parse()
        self.argscomma = [arg.strip() for arg in self.args.split(',')]

    def select_character(self, char_name, exact=False):
        """
        Select a character owned by the Account using this command.

        Args:
            char_name (str): The character name to search for.
            exact (bool): Search using exact name or not.

        Returns:
            discovered character (AthanorPlayerCharacter)
        """
        if not self.account:
            raise ValueError("Must be logged in to use this feature!")
        candidates = self.controllers.get('character').all().filter(character_bridge__db_account=self.account,
                                                                   character_bridge__db_namespace=0)
        if not candidates:
            raise ValueError("No characters to select from!")

        results = object_search(char_name, exact=exact, candidates=candidates)

        if not results:
            raise ValueError(f"Cannot locate character named {char_name}!")
        if len(results) == 1:
            return results[0]
        raise ValueError(f"That matched: {results}")
