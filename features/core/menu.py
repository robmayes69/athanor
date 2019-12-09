from evennia.utils.ansi import ANSIString
from evennia.utils.evmenu import EvMenu, EvMenuError, _HELP_FULL, _HELP_NO_QUIT, _HELP_NO_OPTIONS_NO_QUIT, _HELP_NO_OPTIONS
from evennia.utils.evmenu import _ERR_GENERAL, _ERR_NOT_IMPLEMENTED
from evennia.utils.evtable import EvTable
import re, math
from evennia.utils import logger
from inspect import isfunction, getargspec
from evennia.utils.utils import mod_import, make_iter, pad, to_str, m_len, is_iter, dedent, crop
from evennia.utils.ansi import strip_ansi
from evennia import GLOBAL_SCRIPTS

_RE_ARGS = re.compile(r"(?s)(?i)^(?P<prefix>[@+?$&%-]+)?(?P<cmd>\w+)(?P<switches>(\/\S+)+?)?(?:\s+(?P<args>(?P<lhs>[^=]+)(?:=(?P<rhs>.*))?)?)?")


class AthanorMenu(EvMenu):
    global_scripts = GLOBAL_SCRIPTS

    def __init__(self, *args, **kwargs):
        self.args = kwargs.pop('args', None)
        self.menu_name = kwargs.pop('menu_name', 'Unknown')
        self.session = kwargs.pop('session', None)
        self.caller = args[0]
        self.db = self.caller.db if self.caller.db else None
        self.ndb = self.session.ndb if self.session else self.caller.ndb
        self.account = self.session.get_account() if self.session else None
        self.character = self.session.get_puppet() if self.session else None
        EvMenu.__init__(self, *args, **kwargs)

    def error(self, *args, **kwargs):
        self.msg(f"|rERROR:|n {args[0]}", *args[1:], **kwargs)

    def msg(self, *args, **kwargs):
        return self.caller.msg(*args, **kwargs)

    def parse_input(self, raw_string):
        match_dict = _RE_ARGS.match(raw_string.strip()).groupdict()
        self.cmd = match_dict.get('cmd', '')
        self.prefix = match_dict.get('prefix', '')
        switches = match_dict.get('switches', '')
        self.args = match_dict.get('args', '')
        self.switches = [swi.strip() for swi in match_dict.get('switches').split('/') if swi.strip()] if switches else list()
        self.lhs = match_dict.get('lhs', '')
        self.lhslist = [lh.strip() for lh in self.lhs.split(',') if lh.strip()] if self.lhs else list()
        self.rhs = match_dict.get('rhs', '')
        self.rhslist = [rh.strip() for rh in self.rhs.split(',') if rh.strip()] if self.rhs else list()
        return EvMenu.parse_input(self, self.cmd)

    def client_width(self):
        """
        Get the client screenwidth for the session using this command.

        Returns:
            client width (int or None): The width (in characters) of the client window. None
                if this command is run without a Session (such as by an NPC).

        """
        if self._session:
            return self._session.protocol_flags["SCREENWIDTH"][0]
        return 78

    def styled_table(self, *args, **kwargs):
        """
        Create an EvTable styled by on user preferences.

        Args:
            *args (str): Column headers. If not colored explicitly, these will get colors
                from user options.
        Kwargs:
            any (str, int or dict): EvTable options, including, optionally a `table` dict
                detailing the contents of the table.
        Returns:
            table (EvTable): An initialized evtable entity, either complete (if using `table` kwarg)
                or incomplete and ready for use with `.add_row` or `.add_collumn`.

        """
        account = self.account
        border_color = account.options.get("border_color") if account else 'n'
        column_color = account.options.get("column_names_color") if account else 'n'

        colornames = ["|%s%s|n" % (column_color, col) for col in args]

        h_line_char = kwargs.pop("header_line_char", "~")
        header_line_char = ANSIString(f"|{border_color}{h_line_char}|n")
        c_char = kwargs.pop("corner_char", "+")
        corner_char = ANSIString(f"|{border_color}{c_char}|n")

        b_left_char = kwargs.pop("border_left_char", "||")
        border_left_char = ANSIString(f"|{border_color}{b_left_char}|n")

        b_right_char = kwargs.pop("border_right_char", "||")
        border_right_char = ANSIString(f"|{border_color}{b_right_char}|n")

        b_bottom_char = kwargs.pop("border_bottom_char", "-")
        border_bottom_char = ANSIString(f"|{border_color}{b_bottom_char}|n")

        b_top_char = kwargs.pop("border_top_char", "-")
        border_top_char = ANSIString(f"|{border_color}{b_top_char}|n")

        table = EvTable(
            *colornames,
            header_line_char=header_line_char,
            corner_char=corner_char,
            border_left_char=border_left_char,
            border_right_char=border_right_char,
            border_top_char=border_top_char,
            **kwargs,
        )
        return table

    def _render_decoration(
        self,
        header_text=None,
        fill_character=None,
        edge_character=None,
        mode="header",
        color_header=True,
        width=None,
    ):
        """
        Helper for formatting a string into a pretty display, for a header, separator or footer.

        Kwargs:
            header_text (str): Text to include in header.
            fill_character (str): This single character will be used to fill the width of the
                display.
            edge_character (str): This character caps the edges of the display.
            mode(str): One of 'header', 'separator' or 'footer'.
            color_header (bool): If the header should be colorized based on user options.
            width (int): If not given, the client's width will be used if available.

        Returns:
            string (str): The decorated and formatted text.

        """
        colors = dict()
        account = self.account
        colors["border"] = account.options.get("border_color") if account else 'n'
        colors["headertext"] = account.options.get("%s_text_color" % mode) if account else 'n'
        colors["headerstar"] = account.options.get("%s_star_color" % mode) if account else 'n'

        width = width or self.client_width()
        if edge_character:
            width -= 2

        if header_text:
            if color_header:
                header_text = ANSIString(header_text).clean()
                header_text = ANSIString("|n|%s%s|n" % (colors["headertext"], header_text))
            if mode == "header":
                begin_center = ANSIString(
                    "|n|%s<|%s* |n" % (colors["border"], colors["headerstar"])
                )
                end_center = ANSIString("|n |%s*|%s>|n" % (colors["headerstar"], colors["border"]))
                center_string = ANSIString(begin_center + header_text + end_center)
            else:
                center_string = ANSIString("|n |%s%s |n" % (colors["headertext"], header_text))
        else:
            center_string = ""

        fill_character = account.options.get("%s_fill" % mode) if account else '='

        remain_fill = width - len(center_string)
        if remain_fill % 2 == 0:
            right_width = remain_fill / 2
            left_width = remain_fill / 2
        else:
            right_width = math.floor(remain_fill / 2)
            left_width = math.ceil(remain_fill / 2)

        right_fill = ANSIString("|n|%s%s|n" % (colors["border"], fill_character * int(right_width)))
        left_fill = ANSIString("|n|%s%s|n" % (colors["border"], fill_character * int(left_width)))

        if edge_character:
            edge_fill = ANSIString("|n|%s%s|n" % (colors["border"], edge_character))
            main_string = ANSIString(center_string)
            final_send = (
                ANSIString(edge_fill) + left_fill + main_string + right_fill + ANSIString(edge_fill)
            )
        else:
            final_send = left_fill + ANSIString(center_string) + right_fill
        return final_send

    def styled_header(self, *args, **kwargs):
        """
        Create a pretty header.
        """

        if "mode" not in kwargs:
            kwargs["mode"] = "header"
        return self._render_decoration(*args, **kwargs)

    def styled_separator(self, *args, **kwargs):
        """
        Create a separator.

        """
        if "mode" not in kwargs:
            kwargs["mode"] = "separator"
        return self._render_decoration(*args, **kwargs)

    def styled_footer(self, *args, **kwargs):
        """
        Create a pretty footer.

        """
        if "mode" not in kwargs:
            kwargs["mode"] = "footer"
        return self._render_decoration(*args, **kwargs)

    def node_formatter(self, nodetext, optionstext):
        """
        Formats the entirety of the node.

        Args:
            nodetext (str): The node text as returned by `self.nodetext_formatter`.
            optionstext (str): The options display as returned by `self.options_formatter`.
            caller (Object, Account or None, optional): The caller of the node.

        Returns:
            node (str): The formatted node to display.

        """
        sep = self.node_border_char

        message = list()
        message.append(self.styled_header(f"Menu: {self.menu_name if self.menu_name else 'Unknown'}"))
        message.append(nodetext)
        message.append(self.styled_separator('Options'))
        message.append(optionstext)
        if self.auto_quit:
            message.append(self.styled_footer(f"|nType |wquit|n to exit menu", color_header=False))
        else:
            message.append(self.styled_footer())
        return '\n'.join([str(l) for l in message])

    def options_formatter(self, optionlist):
        """
        Formats the option block.

        Args:
            optionlist (list): List of (key, description) tuples for every
                option related to this node.
            caller (Object, Account or None, optional): The caller of the node.

        Returns:
            options (str): The formatted option display.

        """
        table = self.styled_table('Cmd', 'Desc', width=self.client_width())
        for op in optionlist:
            cmd = op[2].get('syntax', op[0])
            table.add_row(f"|w{cmd}|n", f"{op[1]}")
        return str(table)

    def goto(self, nodename, raw_string, **kwargs):
        """
        Run a node by name, optionally dynamically generating that name first.

        Args:
            nodename (str or callable): Name of node or a callable
                to be called as `function(caller, raw_string, **kwargs)` or
                `function(caller, **kwargs)` to return the actual goto string or
                a ("nodename", kwargs) tuple.
            raw_string (str): The raw default string entered on the
                previous node (only used if the node accepts it as an
                argument)
        Kwargs:
            any: Extra arguments to goto callables.

        """

        if callable(nodename):
            # run the "goto" callable, if possible
            inp_nodename = nodename
            nodename = self._safe_call(nodename, raw_string, **kwargs)
            if isinstance(nodename, (tuple, list)):
                if not len(nodename) > 1 or not isinstance(nodename[1], dict):
                    raise EvMenuError(
                        "{}: goto callable must return str or (str, dict)".format(inp_nodename)
                    )
                nodename, kwargs = nodename[:2]
            if not nodename:
                # no nodename return. Re-run current node
                nodename = self.nodename
        try:
            # execute the found node, make use of the returns.
            nodetext, options = self._execute_node(nodename, raw_string, **kwargs)
        except EvMenuError:
            return

        if self._persistent:
            self.caller.attributes.add(
                "_menutree_saved_startnode", (nodename, (raw_string, kwargs))
            )

        # validation of the node return values
        helptext = ""
        if is_iter(nodetext):
            if len(nodetext) > 1:
                nodetext, helptext = nodetext[:2]
            else:
                nodetext = nodetext[0]
        nodetext = "" if nodetext is None else str(nodetext)
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
                desc = dic.get("desc", dic.get("text", None))
                if "_default" in keys:
                    keys = [key for key in keys if key != "_default"]
                    goto, goto_kwargs, execute, exec_kwargs = self.extract_goto_exec(nodename, dic)
                    self.default = (goto, goto_kwargs, execute, exec_kwargs)
                else:
                    # use the key (only) if set, otherwise use the running number
                    keys = list(make_iter(dic.get("key", str(inum + 1).strip())))
                    goto, goto_kwargs, execute, exec_kwargs = self.extract_goto_exec(nodename, dic)
                if keys:
                    display_options.append((keys[0], desc, dic))
                    for key in keys:
                        if goto or execute:
                            self.options[strip_ansi(key).strip().lower()] = (
                                goto,
                                goto_kwargs,
                                execute,
                                exec_kwargs,
                            )

        self.nodetext = self._format_node(nodetext, display_options)
        self.node_kwargs = kwargs
        self.nodename = nodename

        # handle the helptext
        if helptext:
            self.helptext = self.helptext_formatter(helptext)
        elif options:
            self.helptext = _HELP_FULL if self.auto_quit else _HELP_NO_QUIT
        else:
            self.helptext = _HELP_NO_OPTIONS if self.auto_quit else _HELP_NO_OPTIONS_NO_QUIT

        self.display_nodetext()
        if not options:
            self.close_menu()

    def _safe_call(self, callback, raw_string, **kwargs):
        """
        Call a node-like callable, with a variable number of raw_string, *args, **kwargs, all of
        which should work also if not present (only `caller` is always required). Return its result.

        """
        try:
            try:
                nargs = len(getargspec(callback).args)
            except TypeError:
                raise EvMenuError("Callable {} doesn't accept any arguments!".format(callback))
            supports_kwargs = bool(getargspec(callback).keywords)
            if nargs <= 0:
                raise EvMenuError("Callable {} doesn't accept any arguments!".format(callback))

            if supports_kwargs:
                if nargs > 1:
                    ret = callback(self, raw_string, **kwargs)
                    # callback accepting raw_string, **kwargs
                else:
                    # callback accepting **kwargs
                    ret = callback(self, **kwargs)
            elif nargs > 1:
                # callback accepting raw_string
                ret = callback(self, raw_string)
            else:
                # normal callback, only the caller as arg
                ret = callback(self)
        except EvMenuError:
            errmsg = _ERR_GENERAL.format(nodename=callback)
            self.caller.msg(errmsg, self._session)
            logger.log_trace()
            raise

        return ret