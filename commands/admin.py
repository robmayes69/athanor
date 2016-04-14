from __future__ import unicode_literals
from evennia import PlayerDB
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string


class CmdPlayers(AthCommand):
    """
    list all registered players

    Usage:
        @players
            List all players.
        @players/bind <character>=<player>
            Bind a character to a given account.

    Lists statistics about the Players registered with the game.
    """
    key = "@players"
    aliases = ["@listplayers"]
    locks = "cmd:perm(listplayers) or perm(Wizards)"
    help_category = "System"
    admin_switches = ['bind']
    system_name = 'ACCOUNT'

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        if 'bind' in switches:
            self.switch_bind(lhs, rhs)
            return
        elif self.args:
            self.switch_display(self.args)
        else:
            self.switch_main(lhs, rhs)


    def switch_bind(self, lhs, rhs):
        pass

    def switch_display(self, args):
        pass

    def switch_main(self, lhs, rhs):
        players = PlayerDB.objects.all().order_by('id')
        message = list()
        message.append(header("Players"))
        player_table = make_table("Dbr", "Name", "Email", "Characters", width=[6, 14, 27, 31], viewer=self.character)
        for player in players:
            characters = ', '.join(str(char) for char in player.get_all_characters())
            if player.email == 'dummy@dummy.com':
                email = 'N/A'
            else:
                email = player.email
            player_table.add_row(player.dbref, player.key, email, characters)
        message.append(player_table)
        message.append(header(viewer=self.character))
        self.msg("\n".join([unicode(line) for line in message]))

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
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        from typeclasses.scripts import AthanorManager
        manager = AthanorManager.objects.filter_family().first()

        if not lhs:
            self.msg(manager.settings.display_categories(viewer=self.character))
            return
        try:
            manager.settings.set_setting(lhs, rhs, exact=False, caller=self.character)
        except ValueError as err:
            self.error(unicode(err))
            return
