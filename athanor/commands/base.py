"""
Commands

Commands describe the input the player can do to the game.

"""

from evennia import default_cmds
import athanor
from athanor.utils.text import partial_match, sanitize_string
from athanor import AthException


class AthCommand(default_cmds.MuxCommand):
    """
    This class is an enhanced version of MuxCommand for the Athanor Command Set.
    """
    player_switches = []
    admin_switches = []
    help_category = 'Athanor'
    system_name = 'SYSTEM'
    admin_help = False

    def valid(self, test, input):
        caller = self.caller
        if self.character:
            caller = self.character
        return athanor.valid[test](caller, input)

    def partial(self, match_text, candidates):
        return partial_match(match_text, candidates)

    def parse(self):
        super(AthCommand, self).parse()
        if self.args:
            self.args = unicode(self.args)
        if self.rhs:
            self.rhs = unicode(self.rhs.strip())
            self.rhs_san = sanitize_string(self.rhs)
        if self.lhs:
            self.lhs = unicode(self.lhs.strip())
            self.lhs_san = sanitize_string(self.lhs)
        if hasattr(self.caller, "account"):
            self.account = self.caller.account
            self.character = self.caller
            self.isic = True
        else:
            self.account = self.caller
            self.isic = False
            self.character = None
        self.is_admin = self.caller.ath['core'].is_admin()
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

    def verify(self, test, checkstr):
        verify_data = self.caller.attributes.get(key='verify', default=dict())
        if not test in verify_data:
            verify_data[test] = checkstr
            self.caller.attributes.add(key='verify', value=verify_data)
            return False
        if checkstr == verify_data[test]:
            return True
        return False


    # When in doubt, use this setup.
    def func(self):
        if not self.final_switches:
            try:
                return self._main()
            except AthException as err:
                return self.caller.msg(unicode(err))
        try:
            switch = getattr(self, 'switch_%s' % self.final_switches[0])
        except:
            return self.caller.msg('Switch Not Implemented for this Command')
        try:
            switch()
        except AthException as err:
            return self.caller.msg(unicode(err))

    def switch_style(self):
        if not self.style:
            self.caller.msg("This command does not support Styles!")
            return
        if not self.lhs_san:
            self.caller.styles[self.style].display(viewer=self.caller)
        if self.rhs_san:
            self.caller.styles[self.style].set(enactor=self.caller, viewer=self.caller, style=self.lhs_san,
                                               value=self.rhs_san)
        else:
            self.caller.styles[self.style].clear(enactor=self.caller, viewer=self.caller, style=self.lhs_san)

    def msg_lines(self, lines):
        self.msg('\n'.join([unicode(line) for line in lines]))