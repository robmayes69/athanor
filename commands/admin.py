from __future__ import unicode_literals
from athanor.commands.command import AthCommand
from athanor.utils.text import partial_match
from athanor.core.models import StaffEntry
from athanor.core.config import GLOBAL_SETTINGS

class CmdGameConfig(AthCommand):
    """
    Used to configure global options.
    """
    key = '+gameconfig'
    aliases = ['+gconf']
    locks = 'cmd:perm(Wizards) or perm(gameconfig)'
    help_category = 'System'
    admin_switches = []

    def func(self):
        if not self.final_switches:
            self.main()
        else:
            getattr(self, 'switch_%s' % self.final_switches[0])()

    def main(self):
        if not self.args:
            self.msg_lines(GLOBAL_SETTINGS.display(self.player))
            return
        op = self.lhs
        val = self.rhs
        try:
            msg = GLOBAL_SETTINGS.set(op, val, self.rhslist)
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg(msg)
        self.sys_report(msg)


class CmdAdmin(AthCommand):
    """
    Displays the global staff list!

    Usage:
        @admin
    """
    key = '@admin'
    aliases = ['admin', '+admin', 'wizlist', '@wizlist', 'immlist', '+staff']
    locks = 'cmd:all()'
    help_category = 'Community'
    admin_switches = ['edit', 'duty']

    admin_help = """
    Configuring the global staff roster:

    Only immortals may alter the list.

    |cCommands|n
        |w@admin/edit|n
            Launch the editor menu.
    """

    def switch_edit(self):
        if not self.character.locks.check_lockstring(self.character, 'dummy:perm(Immortals)'):
            self.error("Permission denied! Immortals only!")
            return
        self.menu(self.character, 'athanor.core.menus.admin')

    def switch_duty(self, boo=None):
        chk = StaffEntry.objects.filter(character=self.character).first()
        if not chk:
            self.error("You are not on the @admin list!")
            return
        chk.duty = not(chk.duty)
        chk.save(update_fields=['duty'])
        status = 'on' if chk.duty else 'off'
        self.sys_msg("You are now %s duty!" % status)

    def main(self):
        staff = StaffEntry.objects.all().order_by('order')
        if not staff:
            self.error("There are no staff registered!")
            return
        message = list()
        message.append(self.player.render.header("Staff"))
        staff_table = self.player.render.make_table(["Idl", "Name", "Prm", "Position", "Duty"],
                                                    width=[6, 24, 4, 39, 5])
        for char in staff:
            perms = char.character.permissions.all()
            perm = '|xN/A|n'
            if 'wizards' in perms:
                perm = '|cWiz|n'
            if 'immortals' in perms:
                perm = '|rImm|n'
            if char.duty:
                duty = '|gOn|n'
            else:
                duty = '|xOff|n'
            staff_table.add_row(char.character.time.off_or_idle_time(viewer=self.player),
                                char.character.key, perm,
                                char.position, duty)
        message.append(staff_table)
        message.append(self.player.render.footer())
        self.msg("\n".join([unicode(line) for line in message]))