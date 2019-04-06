from athanor.base.commands import AthCommand
from athanor import AthException


class CmdLook(AthCommand):
    key = 'look'
    aliases = ('dir', 'ls', 'l', 'view', 'login')
    locks = "cmd:all() and not has_account()"

    def _main(self):
        self.msg(self.account.at_look(target=self.account, session=self.session))


class CmdCharCreate(AthCommand):

    key = '@charcreate'
    locks = 'cmd:pperm(Player) and not pperm(Guest) and not has_account()'
    help_category = 'General'

    def _main(self):
        self.account.ath['character'].create(name=self.lhs)


class CmdOptions(AthCommand):
    key = '@options'
    locks = "cmd:pperm(Player) and not pperm(Guest)"

    def _main(self):
        if self.lhs:
            self.change()
        else:
            self.display()

    def change(self):
        if '/' not in self.lhs:
            raise AthException("Must enter a <category>/<setting> combo!")
        sysname, setname = self.lhs.split('/', 1)
        if not sysname:
            raise AthException("Must enter a category name!")
        sys_choices = self.get_handlers()
        system = self.partial(sysname, sys_choices)
        if not system:
            raise AthException("Category not found. Choices are: %s" % ', '.join(sys_choices))
        setting, old_value = system.change_settings(self.session, setname, self.rhs)
        self.sys_msg("Changed Category '%s' Setting '%s' to: %s" % (system, setting, setting.display()))

    def display(self):
        message = list()
        for sys in self.get_handlers():
            message.append(self.header(sys.key.capitalize()))
            columns = (('Name', 20, 'l'), ('Description', 43, 'l'), ('Value', 15, 'l'))
            setting_table = self.table(columns)
            for setting in sorted(sys.settings.values(), key=lambda s: s.key):
                setting_table.add_row(setting.key, '(%s) %s' % (setting.expect_type, setting.description),
                                      setting.display())
            message.append(setting_table)
        message.append(self.footer())
        self.msg_lines(message)

    def get_handlers(self):
        all_handlers = [sys for sys in self.account.ath.ordered_handlers if sys.settings_data]
        for h in all_handlers:
            if not h.loaded_settings:
                h.load_settings()
        return sorted(all_handlers, key=lambda s: s.key)


class CmdConfig(AthCommand):
    key = '@config'
    locks = 'cmd:pperm(Developer)'

    def _main(self):
        if self.lhs:
            self.change()
        else:
            self.display()

    def change(self):
        if '/' not in self.lhs:
            raise AthException("Must enter a <system>/<setting> combo!")
        sysname, setname = self.lhs.split('/', 1)
        if not sysname:
            raise AthException("Must enter a system name!")
        sys_choices = self.get_systems()
        system = self.partial(sysname, sys_choices)
        if not system:
            raise AthException("System not found. Choices are: %s" % ', '.join(sys_choices))
        setting, old_value = system.change_settings(self.session, setname, self.rhs)
        self.sys_msg("Changed System '%s' Setting '%s' to: %s" % (system, setting, setting.display()))

    def display(self):
        message = list()
        for sys in self.get_systems():
            message.append(self.header(sys.key.capitalize()))
            columns = (('Name', 20, 'l'), ('Description', 43, 'l'), ('Value', 15, 'l'))
            setting_table = self.table(columns)
            for setting in sorted(sys.ndb.settings.values(), key=lambda s: s.key):
                setting_table.add_row(setting.key, '(%s) %s' % (setting.expect_type, setting.description), setting.display())
            message.append(setting_table)
        message.append(self.footer())
        self.msg_lines(message)

    def get_systems(self):
        all_systems = [sys for sys in self.systems.values() if sys.load_settings()]
        return sorted(all_systems, key=lambda s: s)


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