import re
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import inherits_from, lazy_property
from evennia.utils.search import object_search

import athanor
from athanor.utils.text import partial_match


class AthanorCommand(MuxCommand):
    locks = 'cmd:all();admin:perm(Admin)'
    system_name = None
    arg_regex = r"(?:^(?:\s+|\/).*$)|^$"
    re_command = re.compile(r"(?si)^(?P<prefix>[@+?$&%-]+)?(?P<cmd>\w+)(?P<switches>(\/\S+)+?)?(?:\s+(?P<args>(?P<lhs>[^=]+)(?:=(?P<rhs>.*))?)?)?")
    rhs_delim = ","
    lhs_delim = ","
    args_delim = " "
    switch_syntax = dict()
    controller_key = None
    switch_options = []

    @lazy_property
    def controller(self):
        return self.controllers.get(self.controller_key)

    def syntax_error(self):
        rules = self.switch_syntax.get(self.chosen_switch, '')
        switch = '' if self.chosen_switch == 'main' else f"/{self.chosen_switch}"
        raise ValueError(f"Usage: {self.key}{switch} {rules}")

    @lazy_property
    def styler(self):
        return self.caller.styler

    def styled_footer(self, *args, **kwargs):
        return self.styler.styled_footer(*args, **kwargs)

    def styled_header(self, *args, **kwargs):
        return self.styler.styled_header(*args, **kwargs)

    def styled_separator(self, *args, **kwargs):
        return self.styler.styled_separator(*args, **kwargs)

    def styled_table(self, *args, **kwargs):
        return self.styler.styled_table(*args, **kwargs)

    def styled_columns(self, *args, **kwargs):
        return self.styler.styled_columns(*args, **kwargs)

    @property
    def blank_footer(self):
        return self.styler.blank_footer

    @property
    def blank_header(self):
        return self.styler.blank_header

    @property
    def blank_separator(self):
        return self.styler.blank_separator

    @property
    def controllers(self):
        return athanor.CONTROLLER_MANAGER

    def switch_main(self):
        pass

    def func(self):
        self.chosen_switch = None
        try:
            if self.switches:
                if len(self.switches) > 1:
                    raise ValueError(f"{self.key} does not support multiple simultaneous switches!")
                if not (switch := partial_match(self.switches[0], self.switch_options)):
                    raise ValueError(f"{self.key} does not support switch '{self.switches[0]}`")
                if not (found := getattr(self, f"switch_{switch}", None)):
                    raise ValueError(f"Command does not support switch {switch}")
                self.chosen_switch = switch
                return found()
            self.chosen_switch = 'main'
            return self.switch_main()
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
        """
        Re-implementation of MuxCommand parse(). Just adds/changes a few things.

        rhs_split is not used. It will always be an = for AthanorCommand.

        This method supports the following class property options:
            lhs_delim (list of str): Used to generate .split() data from lhs args. results go to lhslist
            rhs_delim (list of str): Used to generate .split() data from rhs args. results go to rhslist
            args_delim (list of str): Used to generate .split() data from all args. results go to argslist

        Returns:
            None
        """
        raw = self.args
        args = raw.strip()
        # Without explicitly setting these attributes, they assume default values:
        if not hasattr(self, "switch_options"):
            self.switch_options = None
        if not hasattr(self, "account_caller"):
            self.account_caller = False

        # Regex magic!
        matched = self.re_command.match(self.raw_string)
        self.parsed = {key: value for key, value in matched.groupdict().items() if value is not None}

        # Get values from regex dict or set default values if not found.
        for thing in ('prefix', 'cmd', 'lhs', 'rhs', 'args'):
            if (text := self.parsed.get(thing, None)) is not None:
                setattr(self, thing, text.strip())
            else:
                setattr(self, thing, text)

        # Process all delimiters.
        for thing in ('args', 'lhs', 'rhs'):
            delim = getattr(self, f"{thing}_delim")
            if (text := getattr(self, thing)) is not None:
                setattr(self, f"{thing}list", [stripped for clean in text.split(delim) if (stripped := clean.strip())])
            else:
                setattr(self, f"{thing}list", list())

        # split out switches, strip out empty switches, clean not-empty ones.
        self.switches = [switch.strip() for raw in self.parsed.get('switches', '').split('/') if (switch := raw.strip())]

        if self.switch_options:
            self.switch_options = [opt.lower() for raw in self.switch_options if (opt := raw.strip())]

        # if the class has the account_caller property set on itself, we make
        # sure that self.caller is always the account if possible. We also create
        # a special property "character" for the puppeted object, if any. This
        # is convenient for commands defined on the Account only.
        if self.account_caller:
            if inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
                # caller is an Object/Character
                self.character = self.caller
                self.caller = self.caller.account
            elif inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
                # caller was already an Account
                self.character = self.caller.get_puppet(self.session)
            else:
                self.character = None


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
