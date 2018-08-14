import athanor
from athanor.base.commands import AthCommand

# Admin and building commands go here.
class CmdDark(AthCommand):
    """
    When you are Dark, other characters won't be able to see you in the room unless you speak up.

    Usage:
        [PREFIX]dark
        reports your current status. To change...

        [PREFIX]dark/on
        [PREFIX]dark/off
    """

    key = 'dark'
    locks = 'cmd:perm(Admin)'
    help_category = 'Admin'
    admin_switches = ['on', 'off']

    def _main(self):
        self.character.ath['core'].console_msg("Current Dark Status: " % self.character.ath['core'].dark)

    def switch_on(self):
        self.character.ath['core'].dark = True

    def switch_off(self):
        self.character.ath['core'].dark = False


class CmdLook(AthCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls", 'dir']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        self.msg(caller.at_look(self.session, target))


class CmdHelp(AthCommand):
    """
    Display the Athanor +help menu tree.

    Usage:
       +help
       +help <filename>
       +help <filename>/<subfile>...
    """
    key = '+help'
    locks = "cmd:all()"
    tree = athanor.HELP_TREES['+help']

    def _main(self):
        if not self.lhs:
            self.msg(text=self.tree.display(self.session))
            return
        self.msg(text=self.tree.traverse_tree(self.session, self.lhs_san))


class CmdShelp(CmdHelp):
    key = '+shelp'
    locks = 'cmd:perm(Admin)'
    tree = athanor.HELP_TREES['+shelp']


class CmdAccount(AthCommand):
    key = '@account'
    locks = 'cmd:perm(Admin)'
    admin_switches = ['list', 'email', 'rename', 'create', 'disable', 'enable', 'ban', 'unban', 'password']
    system_name = 'ACCOUNT'

    def _main(self):
        if self.lhs:
            account = self.systems['account'].search(self.session, self.lhs)
        else:
            account = self.account

    def switch_list(self):
        pass

    def switch_rename(self):
        account = self.systems['account'].search(self.session, self.lhs)
        found_account, old_name = self.systems['account'].rename(self.session, account, self.rhs)
        self.ath['account'].alert("You Renamed Account '%s' to: %s" % (old_name, account))

    def switch_create(self):
        account = self.systems['account'].create(self.session, self.lhs, self.rhs, method="@account/create")
        self.character.ath['core'].alert("You have created Account '%s'" % account, system='ACCOUNT')

    def switch_email(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account, new_email = self.systems['account'].email(self.session, account, self.rhs)
        self.sys_msg("Changed Account '%s' Email to: %s" % (account, new_email))

    def switch_enable(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account = self.systems['account'].enable(self.session, account)
        self.sys_msg("Enabled Account '%s'" % account)

    def switch_disable(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account = self.systems['account'].disable(self.session, account)
        self.sys_msg("Disabled Account '%s'" % account)

    def switch_ban(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account, duration, until = self.systems['account'].ban(self.session, account, self.rhs)
        self.sys_msg("Banned Account '%s' for %s - Until %s" % (account, duration, until))

    def switch_unban(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account = self.systems['account'].unban(self.session, account)
        self.sys_msg("Unbanned Account '%s'" % account)

    def switch_password(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account = self.systems['account'].password(self.session, account, self.rhs)
        self.sys_msg("Password for Account '%s' set! Don't forget it. Remember they are case sensitive." % account)

    def switch_grant(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account, permission = self.systems['account'].grant(self.session, account, self.rhs)
        self.sys_msg("Granted Account '%s' Permission: %s" % (account, permission))

    def switch_revoke(self):
        account = self.systems['account'].search(self.session, self.lhs)
        account, permission = self.systems['account'].revoke(self.session, account, self.rhs)
        self.sys_msg("Revoke Account '%s' Permission: %s" % (account, permission))


class CmdCharacter(AthCommand):
    key = '@character'
    locks = 'cmd:perm(Admin)'
    admin_switches = ['list', 'rename', 'create', 'disable', 'enable', 'ban', 'unban', 'bind', 'unbind']
    system_name = 'CHARACTER'

    def _main(self):
        pass

    def switch_create(self):
        account = self.systems['account'].search(self.session, self.rhs)
        character = self.systems['character'].create(self.session, account, self.lhs)
        self.sys_msg("Character '%s' created for Account '%s'!" % (character, account))

    def switch_list(self):
        pass

    def switch_rename(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character, old_name, new_name = self.systems['character'].rename(self.session, character, self.rhs)
        self.sys_msg("Renamed Character '%s' to: %s" % (old_name, new_name))

    def switch_disable(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character = self.systems['character'].disable(self.session, character)
        self.sys_msg("Disabled Character '%s'" % character)

    def switch_enable(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character = self.systems['character'].enable(self.session, character)
        self.sys_msg("Enabled Character '%s'" % character)

    def switch_ban(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character, duration, until = self.systems['character'].ban(self.session, character, self.rhs)
        self.sys_msg("Banned Character '%s' for %s - Until %s" % (character, duration, until))

    def switch_unban(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character = self.systems['character'].unban(self.session, character)
        self.sys_msg("Un-Banned Character '%s'" % character)

    def switch_bind(self):
        character = self.systems['character'].search(self.session, self.lhs)
        account = self.systems['account'].search(self.session, self.rhs)
        character, account = self.systems['character'].bind(self.session, character, account)
        self.sys_msg("Bound Character '%s' to Account '%s'" % (character, account))

    def switch_unbind(self):
        character = self.systems['character'].search(self.session, self.lhs)
        character, account = self.systems['character'].unbind(self.session, character)
        self.sys_msg("Un-Bound Character '%s' from Account '%s'" % (character, account))


class CmdChannel(AthCommand):
    key = '@channel'
    locks = 'cmd:all()'
    player_switches = ['join', 'leave', 'on', 'off', 'gag', 'ungag', 'who', 'details', 'list', 'color']
    admin_switches = ['create', 'rename', 'lock', 'config']

    def _main(self):
        self.switch_details()

    def switch_join(self):
        channel = self.character.ath['channel'].search(self.lhs)
        channel = self.character.ath['channel'].join(channel)
        self.sys_msg("Turned on Channel '%s'!" % channel)

    def switch_leave(self):
        channel = self.character.ath['channel'].search(self.lhs)
        channel = self.character.ath['channel'].leave(channel)
        self.sys_msg("Left Channel '%s'!" % channel)

    def switch_on(self):
        self.switch_join()

    def switch_off(self):
        self.switch_leave()

    def switch_gag(self):
        if not self.lhs:
            self.character.ath['channel'].gag_all()
            self.sys_msg("Gagged all channels!")
            return
        channel = self.character.ath['channel'].search(self.lhs)
        channel = self.character.ath['channel'].gag(channel)
        self.sys_msg("Gagged Channel '%s'!" % channel)

    def switch_ungag(self):
        if not self.lhs:
            self.character.ath['channel'].ungag_all()
            self.sys_msg("Ungagged all gagged Channels!")
            return
        channel = self.character.ath['channel'].search(self.lhs)
        channel = self.character.ath['channel'].ungag(channel)
        self.sys_msg("Un-Gagged Channel '%s'!" % channel)

    def switch_who(self):
        channel = self.character.ath['channel'].search(self.lhs)

    def switch_details(self):
        channel = self.character.ath['channel'].search(self.lhs)

    def switch_create(self):
        channel = self.systems['channel'].create(self.session, self.lhs)

    def switch_rename(self):
        channel = self.character.ath['channel'].search(self.lhs)

    def switch_lock(self):
        channel = self.character.ath['channel'].search(self.lhs)

    def switch_config(self):
        channel = self.character.ath['channel'].search(self.lhs)


class CmdConfig(AthCommand):
    key = '@config'
    locks = 'cmd:perm(Developer)'

    def _main(self):
        if self.lhs:
            self.change()
        else:
            self.display()

    def change(self):
        pass

    def display(self):
        pass
