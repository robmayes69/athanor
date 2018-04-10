"""
Commands

Commands describe the input the player can do to the game.

"""
from __future__ import unicode_literals
import re

from evennia import Command as BaseCommand
from evennia import default_cmds, CmdSet
from evennia.utils.ansi import ANSIString
from athanor.groups.models import find_group
from athanor.utils.text import partial_match
from athanor.utils.time import utc_from_string, duration_from_string
from athanor.core.config import GLOBAL_SETTINGS


_VAL_ISNUM = re.compile(r'\D+')


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own
    command styles. Note that Evennia's default commands
    use MuxCommand instead (next in this module).

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order:
        - at_pre_command(): If this returns True, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_command(): Extra actions, often things done after
            every command, like prompts.

    """
    # these need to be specified

    key = "MyCommand"
    aliases = []
    locks = "cmd:all()"
    help_category = "General"

    # optional
    # auto_help = False      # uncomment to deactive auto-help for this command.
    # arg_regex = r"\s.*?|$" # optional regex detailing how the part after
                             # the cmdname must look to match this command.

    # (we don't implement hook method access() here, you don't need to
    #  modify that unless you want to change how the lock system works
    #  (in that case see evennia.commands.command.Command))

    def at_pre_cmd(self):
        """
        This hook is called before `self.parse()` on all commands.
        """
        pass

    def parse(self):
        """
        This method is called by the `cmdhandler` once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from `self.func()` (see below).

        The following variables are available to us:
           # class variables:

           self.key - the name of this command ('mycommand')
           self.aliases - the aliases of this cmd ('mycmd','myc')
           self.locks - lock string for this command ("cmd:all()")
           self.help_category - overall category of command ("General")

           # added at run-time by `cmdhandler`:

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following `self.cmdstring`.
           self.cmdset - the `cmdset` from which this command was picked. Not
                         often used (useful for commands like `help` or to
                         list all available commands etc).
           self.obj - the object on which this command was defined. It is often
                         the same as `self.caller`.
        """
        pass

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        self.caller.msg("Command called!")

    def at_post_cmd(self):
        """
        This hook is called after `self.func()`.
        """
        pass


class MuxCommand(default_cmds.MuxCommand):
    """
    This sets up the basis for Evennia's 'MUX-like' command style.
    The idea is that most other Mux-related commands should
    just inherit from this and don't have to implement parsing of
    their own unless they do something particularly advanced.

    A MUXCommand command understands the following possible syntax:

        name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

    The `name[ with several words]` part is already dealt with by the
    `cmdhandler` at this point, and stored in `self.cmdname`. The rest is stored
    in `self.args`.

    The MuxCommand parser breaks `self.args` into its constituents and stores them
    in the following variables:
        self.switches = optional list of /switches (without the /).
        self.raw = This is the raw argument input, including switches.
        self.args = This is re-defined to be everything *except* the switches.
        self.lhs = Everything to the left of `=` (lhs:'left-hand side'). If
                     no `=` is found, this is identical to `self.args`.
        self.rhs: Everything to the right of `=` (rhs:'right-hand side').
                    If no `=` is found, this is `None`.
        self.lhslist - `self.lhs` split into a list by comma.
        self.rhslist - list of `self.rhs` split into a list by comma.
        self.arglist = list of space-separated args (including `=` if it exists).

    All args and list members are stripped of excess whitespace around the
    strings, but case is preserved.
    """

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        # this can be removed in your child class, it's just
        # printing the ingoing variables as a demo.
        super(MuxCommand, self).func()


class AthCommand(MuxCommand):
    """
    This class is an enhanced version of MuxCommand for the Athanor Command Set.
    """
    player_switches = []
    admin_switches = []
    help_category = 'Athanor'
    system_name = 'SYSTEM'
    admin_help = False

    def partial(self, match_text, candidates):
        return partial_match(match_text, candidates)

    def sys_msg(self, message, target=None, error=False):
        if not target:
            target = self.caller
        target.sys_msg(message, self.system_name, error=error)

    def sys_report(self, message, system_name=None, sender=None):
        if not system_name:
            system_name = self.system_name
        if not sender:
            sender = self.caller
        channels = GLOBAL_SETTINGS['alerts_channels']
        alert_string = '|w[%s]|n |C%s|n: %s' % (sender, system_name, message)
        for chan in channels:
            chan.emit(alert_string)

    def error(self, message, target=None):
        if not target:
            target = self.caller
        self.sys_msg(message, target=target, error=True)

    def parse(self):
        super(AthCommand, self).parse()
        if self.args:
            self.args = unicode(self.args)
        if self.rhs:
            self.rhs = unicode(self.rhs.strip())
        if self.lhs:
            self.lhs = unicode(self.lhs.strip())
        if hasattr(self.caller, "account"):
            self.account = self.caller.account
            self.character = self.caller
            self.isic = True
        else:
            self.account = self.caller
            self.isic = False
            self.character = None
        self.is_admin = self.caller.account.is_admin()
        self.parse_switches()

    def parse_switches(self):
        self.final_switches = []
        total_switches = []
        if self.is_admin and self.admin_switches:
            total_switches += self.admin_switches
        total_switches += self.player_switches
        for switch in self.switches:
            found_switches = partial_match(switch, total_switches)
            if found_switches:
                self.final_switches.append(found_switches)

    def verify(self, checkstr):
        if checkstr == str(self.account.db.verify):
            del self.account.db.verify
            return True
        else:
            self.account.db.verify = checkstr
            return False

    def msg_lines(self, message=None):
        lines = '\n'.join(unicode(line) for line in message)
        self.caller.msg(lines)

    @property
    def settings(self):
        return GLOBAL_SETTINGS

    # When in doubt, use this setup.
    def func(self):
        try:
            if not self.final_switches:
                return self._main()
            return getattr(self, 'switch_%s' % self.final_switches[0])()
        except ValueError as err:
            return self.error(str(err))

    def valid_color(self, entry=None):
        if not entry:
            raise ValueError("Nothing entered for a color!")
        test_str = ANSIString('|%s|n' % entry)
        if len(test_str):
            raise ValueError("'%s' is not a valid color." % entry)
        return entry

    def valid_duration(self, entry=None):
        if not entry:
            raise ValueError("Nothing entered for a duration!")
        return duration_from_string(entry)

    def valid_date(self, entry=None, player=None):
        if not player:
            player = self.player
        tz = player.config['timezone']
        return utc_from_string(entry, tz)

    def valid_int(self, entry=None):
        if not entry:
            raise ValueError("Must enter a valid integer!")
        try:
            num = int(entry)
        except ValueError:
            raise ValueError("Could not convert that to a number.")
        return num

    def valid_bool(self, entry=None):
        if not entry:
            raise ValueError("Must enter 0 (false) or 1 (true).")
        if entry not in ('0', '1'):
            raise ValueError("Must enter 0 (false) or 1 (true).")
        if entry == '0':
            return False
        return True

    def valid_posint(self, entry=None, allow_zero=False):
        num = self.valid_int(entry)
        beyond = 0
        if not allow_zero:
            beyond = 1
        if not num >= beyond:
            raise ValueError("Must enter a whole number greater than %s!" % beyond)
        return num

    def valid_group(self, entry=None):
        group = find_group(search_name=entry, exact=False)


class ModeCmdSet(CmdSet):
    """
    This Class is used as the parent of CmdSets assigned by the @mode command.
    """
    key = "BaseModeCmdSet"
    priority = 30
    locks = 'cmd:any()'

    def at_cmdset_creation(self):
        self.add(Finish)
        self.add(Menu)

class ModeCommand(AthCommand):
    """
    This Command is used as at least the parent for all Commands put in a ModeCmdSet.
    It has nothing to do with EvMode.
    """
    mode_key = 'ModeCommand'
    display_post = True
    help_category = 'Current Menu'
    mode_syntax = ''
    mode_explanation = ''
    mode_sort = 0
    mode_parent = None
    mode_manager = None
    mode_default = dict()
    mode_target = None

    def parse(self):
        super(ModeCommand, self).parse()
        self.mode_manager = self.character.mode.get(self.mode_key, self.mode_default)
        self.mode_target = self.character.mode.target(self.mode_key)

    def all_mode_commands(self):
        all_cmds = [cmd for cmd in self.cmdset if cmd.access(self.caller)]
        all_cmds = [cmd for cmd in all_cmds if hasattr(cmd, 'mode_sort')]
        return sorted(all_cmds, key=lambda cmd2: cmd2.mode_sort)

    def at_post_cmd(self):
        super(ModeCommand, self).at_post_cmd()
        if not self.display_post:
            return
        self.mode_display()

    def mode_display(self):
        cmds = self.all_mode_commands()
        message = list()
        message.append(self.player.render.header(self.mode_key))
        mode_table = self.player.render.make_table(['Cmd', 'Syntax', 'Explanation'], width=[16, 25, 37])
        for cmd in cmds:
            mode_table.add_row(cmd.key, cmd.mode_syntax, cmd.mode_explanation)
        message.append(mode_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)

    def mode_exit(self, final=True):
        if final:
            self.character.sys_msg("Left Mode: %s" % self.mode_key)
        self.character.mode.leave()

    def mode_can_parent(self):
        if self.mode_parent:
            return self.character.locks.check_lockstring(self.character, self.mode_parent.locks)
        return False

    def mode_back(self):
        if not self.mode_parent:
            raise ValueError("Mode has no parent mode.")
        if not self.mode_can_parent():
            raise ValueError("Permission denied. Cannot return to parent mode.")
        self.mode_exit()
        self.character.cmdset.add(self.mode_parent)
        self.character.execute_cmd('menu')

class Finish(ModeCommand):
    key = 'finish'
    mode_syntax = 'finish'
    mode_explanation = 'Return to normal command mode.'
    display_post = False
    mode_sort = 1000

    def func(self):
        self.mode_exit()


class Menu(ModeCommand):
    key = 'menu'
    mode_syntax = 'menu'
    mode_explanation = 'Display this help table.'
    display_post = False
    mode_sort = 999

    def func(self):
        self.mode_display()