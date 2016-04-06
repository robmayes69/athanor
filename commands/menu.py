from __future__ import unicode_literals
from evennia.utils.utils import make_iter
from evennia.utils.evmenu import EvMenu, _HELP_NO_OPTION_MATCH, _ERR_NO_OPTION_DESC, EvMenuError, _HELP_FULL, \
    _HELP_NO_QUIT, _HELP_NO_OPTIONS, _HELP_NO_OPTIONS_NO_QUIT
from evennia.utils.ansi import strip_ansi
from commands.library import partial_match

class AthanorMenu(EvMenu):

    def parse_input(self, raw_string):
        """
        Processes the user' node inputs.

        Args:
            raw_string (str): The incoming raw_string from the menu
                command.
        """

        caller = self._caller
        raw_string = raw_string.strip()
        if ' ' in raw_string:
            cmd, args = raw_string.split(' ', 1)
        else:
            cmd = raw_string
            args = None
        allow_quit = self.allow_quit

        if cmd in self.options:
            # this will take precedence over the default commands
            # below
            goto, callback = self.options[cmd]
            self._callback_goto(callback, goto, raw_string)
        elif cmd in ("look", "l"):
            self._display_nodetext()
        elif cmd in ("help", "h"):
            self._display_helptext()
        elif allow_quit and cmd in ("quit", "q", "exit"):
            self.close_menu()
        elif partial_match(cmd, self.options.keys()):
            key = partial_match(cmd, self.options.keys())
            goto, callback = self.options[key]
            self._callback_goto(callback, goto, raw_string)
        elif self.default:
            goto, callback = self.default
            self._callback_goto(callback, goto, raw_string)
        else:
            caller.msg(_HELP_NO_OPTION_MATCH)

        if not (self.options or self.default):
            # no options - we are at the end of the menu.
            self.close_menu()

    def _format_node(self, nodetext, optionlist, caller=None):
        """
        Format the node text + option section

        Args:
            nodetext (str): The node text
            optionlist (list): List of (key, desc) pairs.

        Returns:
            string (str): The options section, including
                all needed spaces.

        Notes:
            This will adjust the columns of the options, first to use
            a maxiumum of 4 rows (expanding in columns), then gradually
            growing to make use of the screen space.

        """
        if not caller:
            caller = self._caller

        # handle the node text

        nodetext = self._nodetext_formatter(nodetext, len(optionlist), caller)

        # handle the options
        optionstext = self._options_formatter(optionlist, caller)

        # format the entire node
        return self._node_formatter(nodetext, optionstext, caller)

    def goto(self, nodename, raw_string):
        """
        Run a node by name

        Args:
            nodename (str): Name of node.
            raw_string (str): The raw default string entered on the
                previous node (only used if the node accepts it as an
                argument)

        """
        try:
            # execute the node, make use of the returns.
            nodetext, options = self._execute_node(nodename, raw_string)
        except EvMenuError:
            return

        # validation of the node return values
        helptext = ""
        if hasattr(nodetext, "__iter__"):
            if len(nodetext) > 1:
                nodetext, helptext = nodetext[:2]
            else:
                nodetext = nodetext[0]
        nodetext = str(nodetext) or ""
        options = [options] if isinstance(options, dict) else options

        # this will be displayed in the given order
        display_options = []
        # this is used for lookup
        self.options = {}
        self.default = None
        if options:
            for inum, dic in enumerate(options):
                # fix up the option dicts
                keys = make_iter(dic.get("key"))
                if "_default" in keys:
                    keys = [key for key in keys if key != "_default"]
                    desc = dic.get("desc", dic.get("text", _ERR_NO_OPTION_DESC).strip())
                    goto, execute = dic.get("goto", None), dic.get("exec", None)
                    self.default = (goto, execute)
                else:
                    keys = list(make_iter(dic.get("key", str(inum + 1).strip()))) + [str(inum + 1)]
                    desc = dic.get("desc", dic.get("text", _ERR_NO_OPTION_DESC).strip())
                    goto, execute = dic.get("goto", None), dic.get("exec", None)

                if keys:
                    display_options.append((keys[0], desc))
                    for key in keys:
                        if goto or execute:
                            self.options[strip_ansi(key).strip().lower()] = (goto, execute)

        self.nodetext = self._format_node(nodetext, display_options, self._caller)

        # handle the helptext
        if helptext:
            self.helptext = helptext
        elif options:
            self.helptext = _HELP_FULL if self.allow_quit else _HELP_NO_QUIT
        else:
            self.helptext = _HELP_NO_OPTIONS if self.allow_quit else _HELP_NO_OPTIONS_NO_QUIT

        self._display_nodetext()