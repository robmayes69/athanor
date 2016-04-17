from __future__ import unicode_literals
from evennia import PlayerDB
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string, partial_match
from world.database.communications.models import StaffEntry


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

    admin_help = """
    @player administration.

    |cCommands|n
        |w@players/bind <character>=<account>|n
            Bind a character to another account and remove them from any existing one. This cannot be used on a character that is currently logged in or has admin permissions.
    """

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
        try:
            char = self.character.search_character(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if char.connection_time:
            self.error("That character is currently online!")
            return
        if self.character.locks.check_lockstring(char, "dummy:perm(wizards)"):
            self.error("Cannot bind a privileged character.")
            return
        player = self.character.search_player(rhs, quiet=True)
        if player:
            player = player[0]
        else:
            self.error("Player not found.")
            return
        player.bind_character(char)
        self.sys_msg("Transferred %s to Account: %s" % (char, player))
        self.sys_report("Transferred %s to Account: %s" % (char, player))

    def switch_display(self, args):
        play = self.character.search_player(args, quiet=True)

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

class CmdAdmin(AthCommand):
    """
    Displays the global staff list!

    Usage:
        staff
    """
    key = 'staff'
    aliases = ['admin', '+admin', 'wizlist', '@wizlist', 'immlist', '+staff']
    locks = 'cmd:all()'
    help_category = 'Community'
    admin_switches = ['add', 'order', 'position', 'duty', 'remove']

    admin_help = """
    Configuring the global staff roster:

    Only immortals may alter the list.

    |cCommands|n
        |wstaff/add <character>[=<order>]|n
            Add a character to the roster. Order is an optional number for sorting.

        |wstaff/remove <character>|n
            Remove someone from the official list. Takes partial matches agaisnt existing entries.

        |wstaff/order <character>=<order>|n
            Re-order staff member positioning.

        |wstaff/position <character>=<position>|n
            Grant title/job position/description to appear in the staff list.

        |wstaff/duty|n
            Toggle whether you appear as on or off duty when online.
    """

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        if not switches:
            self.display_staff()
            return
        switch = switches[0]
        getattr(self, 'switch_%s' % switch)(lhs, rhs)


    def display_staff(self):
        staff = StaffEntry.objects.all().order_by('order')
        if not staff:
            self.error("There are no staff registered!")
            return
        message = list()
        message.append(header("Staff", viewer=self.caller))
        staff_table = make_table("Idl", "Name", "Prm", "Position", "Duty", width=[6, 24, 4, 39, 5], viewer=self.caller)
        for char in staff:
            perms = char.character.permissions.all()
            perm = '|XN/A|n'
            if 'wizards' in perms:
                perm = '|cWiz|n'
            if 'immortals' in perms:
                perm = '|rImm|n'
            if char.duty:
                duty = '|gOn|n'
            else:
                duty = '|xOff|n'
            staff_table.add_row(char.character.off_or_idle_time(viewer=self.caller), char.character.key, perm,
                                char.position, duty)
        message.append(staff_table)
        message.append(header(viewer=self.caller))
        self.msg("\n".join([unicode(line) for line in message]))

    def switch_add(self, lhs, rhs):
        if not self.character.locks.check_lockstring(self.character, "dummy:perm(Immortals)"):
            self.caller.msg("You must be an Immortal or higher to do this!")
            return
        try:
            char = self.character.search_character(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return

        if rhs:
            try:
                order = int(rhs)
            except ValueError:
                self.error("Order numbers must be positive integers.")
                return
        else:
            order = 0
        exist = StaffEntry.objects.filter(character=char).count()
        if exist:
            self.error("%s is already an official staff member!" % char)
            return
        StaffEntry.objects.create(character=char, order=order)
        self.sys_msg("You were added to the official staff roster!", target=char)
        self.sys_msg("%s added to the staff roster!" % char)
        self.sys_report("Added %s to the staff roster!" % char)

    def switch_remove(self, lhs, rhs):
        if not self.character.locks.check_lockstring(self.character, "dummy:perm(Immortals)"):
            self.caller.msg("You must be an Immortal or higher to do this!")
            return
        if not lhs:
            self.error("Who will you remove?")
            return
        exist = StaffEntry.objects.all()
        if not exist:
            self.error("Nobody to remove...")
            return
        find = partial_match(lhs, exist)
        if not find:
            self.error("They are not a staff member!")
            return
        char = find.character
        self.sys_report("Removed %s from the staff roster!" % char)
        self.sys_msg("Removed %s from the staff roster!" % char)
        self.sys_msg("You were removed from the staff roster!", target=char)
        find.delete()

    def switch_order(self, lhs, rhs):
        if not self.character.locks.check_lockstring(self.character, "dummy:perm(Immortals)"):
            self.caller.msg("You must be an Immortal or higher to do this!")
            return
        if not lhs:
            self.error("Who will you reorder?")
            return
        exist = StaffEntry.objects.all()
        if not exist:
            self.error("Nobody to re-order.")
            return
        find = partial_match(lhs, exist)
        if not find:
            self.error("They are not a staff member!")
            return
        try:
            order = int(rhs)
        except ValueError:
            self.error("Order numbers must be positive integers.")
            return
        find.order = order
        find.save(update_fields=['order'])
        self.sys_report("Staff roster for %s is now: %s" % (find, order))
        self.sys_msg("Order altered.")

    def switch_position(self, lhs, rhs):
        if not self.character.locks.check_lockstring(self.character, "dummy:perm(Immortals)"):
            self.caller.msg("You must be an Immortal or higher to do this!")
            return
        if not lhs:
            self.error("Who will you retitle?")
            return
        exist = StaffEntry.objects.all()
        if not exist:
            self.error("Nobody to title.")
            return
        find = partial_match(lhs, exist)
        if not find:
            self.error("They are not a staff member!")
            return
        if not rhs:
            self.error("What position will %s hold?" % find)
            return
        find.position = rhs
        find.save(update_fields=['position'])
        self.sys_report("Staff position for %s is now: %s" % (find, rhs))
        self.sys_msg("Your staff position is now: %s" % rhs, target=find.character)
        self.sys_msg("Position for %s updated." % find)

    def switch_duty(self, lhs, rhs):
        exist = StaffEntry.objects.filter(character=self.caller).first()
        if not exist:
            self.error("You are not on the roster.")
            return
        exist.duty = not(exist.duty)
        duty = exist.duty
        exist.save(update_fields=['duty'])
        if duty:
            self.sys_msg("You are now on duty.")
        else:
            self.sys_msg("You are now off duty.")