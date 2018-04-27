from __future__ import unicode_literals

from athanor.core.command import AthCommand
from athanor.core.models import StaffEntry


class CmdGameConfig(AthCommand):
    """
    Used to configure global options.

    Usage:
        @gameconfig
        @gameconfig <setting>=<value>

    Without arguments it displays the global settings and information on how they can be used.
    Any admin can view the settings, but only an Immortal can change them.

    Types:

    Bool - Enter the value 0 or 1 for Off/On.
    List - Enter a comma-separated list. Example: @gameconfig <setting>=Thing1,Thing2,Thing3
    Number - Enter a whole number.
    Email - Enter a valid email.
    Color - Enter a simple foreground color code.
    Channels - As a List, but a List of Channels.
    BBS - The name of a BBS Board.
    Duration - w for weeks, d for days, h for hours, m for minutes. Example: @gameconfig <setting>=3d 5m - this will
        result in 3 days and 5 minutes.
    """
    key = '+gameconfig'
    locks = 'cmd:perm(Admin) or perm(Gameconfig)'
    help_category = 'System'

    def switch_main(self):
        if not self.args:
            return self.msg_lines(self.settings.display(self.player))
        if not self.player.account.is_immortal():
            raise AthException("Permission denied.")
        op = self.lhs
        val = self.rhs
        msg = self.settings.set(op, val, self.rhslist)
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