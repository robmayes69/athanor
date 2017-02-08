from __future__ import unicode_literals

import pytz

from athanor.classes.players import Player
from athanor.core.command import AthCommand
from athanor.utils.create import player as make_player
from athanor.utils.menu import make_menu
from athanor.utils.time import utcnow


class CmdPlayerConfig(AthCommand):
    """
    Command for setting account-wide options that affect command and system behavior.

    Usage:
        +config - displays all possible options.
        +config <option>=<value> - change an option.

    Options:
        <BOOL> - Boolean. expects 0 (false/off) or 1 (True/On).
        <DURATION> - expects a time string in the format of #d #h #m #s. example: 5d for 5 days, or 1m 30s for 1 minute
                    30 seconds.
        <TIMEZONE> - Takes the name of a timezone. Will attempt to partial match. See @timezone for a proper list.
        <COLOR> - Takes a color code option. Like r for bright red or n for neutral.
    """

    system_name = 'CONFIG'
    key = '+config'
    help_category = 'General'
    player_switches = ['name', 'channel', 'group']

    def main(self):
        if not self.args:
            self.display_config()
        else:
            self.set_config()

    def display_config(self):
        self.msg_lines(self.player.config.display(self.player))

    def set_config(self):
        try:
            msg = self.player.config.set(self.lhs, self.rhs)
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg(msg)


    def switch_name(self):
        if not self.args:
            self.display_name()
            return
        try:
            found = self.character.search_character(self.lhs)
            msg = self.player.colors.set(target=found, value=self.rhs, mode='characters')
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg(msg)


    def switch_channel(self):
        if not self.args:
            self.display_channel()
            return
        if not self.lhs:
            self.error("Must enter a channel name.")
            return
        found = self.partial(self.lhs, self.character.channels.visible())
        if not found:
            self.error("Channel not found.")
            return
        try:
            msg = self.player.colors.set(target=found, value=self.rhs, mode='channels')
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg(msg)

    def switch_group(self):
        if not self.args:
            self.display_group()
            return

class CmdTz(AthCommand):
    """
    Change your Timezone setting.

    Usage:
        @tz <timezone> - change your timezone. Equal to +config system/timezone=<timezone>
        @tz/list [<timezone>] - display all timezones. Optionally search for timezones beginning with entered text.

    Example:
        @tz/list America
        @tz America/Detroit
    """

    key = '@tz'
    aliases = ['@timezone', '+tz']
    help_category = 'General'
    player_switches = ['list']
    sysname = 'TIME'

    def func(self):

        switches = self.final_switches

        if 'list' in switches:
            self.switch_list()
            return
        else:
            self.switch_none()
            return

    def switch_none(self):
        if not self.args:
            current_tz = self.player.player_settings.timezone
            now = utcnow().astimezone(current_tz)

            self.sys_msg("Your Current Timezone is '%s'. Is it %s where you are right now?" % (str(current_tz),
                                                                                               now.strftime('%c %Z')))
            return
        self.player.player_settings.timezone = self.args
        self.player.player_settings.save(update_fields=['timezone'])
        tz = self.player.player_settings.timezone
        self.sys_msg("Your Current Timezone is now '%s'. Is it %s where you are right now?" % (str(tz),
                                                                                               utcnow().astimezone(tz).strftime('%c %Z')))


    def switch_list(self):
        message = []
        message.append(self.player.render.header('Available Timezones'))
        tz_list = pytz.common_timezones
        if self.args:
            tz_list = [tz for tz in tz_list if tz.lower().startswith(self.args.lower())]
        if not tz_list:
            self.error("'%s' returned no matches.")
            return
        tz_table = self.player.render.make_table(['Name', 'Current Time'], width=[35, 43])
        for zone in tz_list:
            now = utcnow().astimezone(pytz.timezone(zone))
            tz_table.add_row(zone, now.strftime('%c %Z'))
        message.append(tz_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)


class CmdWatch(AthCommand):
    """
    The WatchFor system maintains a friends list and alerts you when characters log on or off.

    Usage:
        +watch
            Display all connected friends.
        +watch/list
            Display all friends, connected or not.
        +watch/add <character>
            Add a character to your friends list.
        +watch/delete <character>
            Remove a character from your friends list.
        +watch/hide
            No longer trigger other people's friends alerts. Use again to disable.
        +watch/mute
            No longer hear when friends connect. Use again to disable.
    """
    key = '+watch'
    aliases = ['+friend', '+wf', 'wf']
    system_name = 'WATCH'
    help_category = 'Community'
    player_switches = ['list', 'add', 'delete', 'hide', 'mute']

    def func(self):
        if not self.final_switches:
            self.display_list()
            return
        else:
            exec 'self.switch_%s()' % self.final_switches[0]
            return

    def display_list(self):
        msg = self.player.config.model.display_watch(viewer=self.character, connected_only=True)
        self.character.msg(msg)

    def switch_list(self):
        msg = self.player.config.model.display_watch(viewer=self.character, connected_only=False)
        self.character.msg(msg)

    def switch_add(self):
        try:
            found = self.character.search_character(self.args)
        except ValueError as err:
            self.error(str(err))
            return
        self.player.config.model.watch_list.add(found)
        self.sys_msg("Added '%s' to your Watch list." % found)

    def switch_delete(self):
        try:
            found = self.character.search_character(self.args)
        except ValueError as err:
            self.error(str(err))
            return
        if found not in self.player.player_settings.watch_list.all():
            self.error("They are not a friend!")
        self.player.config.model.watch_list.remove(found)
        self.sys_msg("Removed '%s' from your Watch list." % found)

    def switch_hide(self):
        toggle = bool(self.player.db._watch_hide)
        self.sys_msg("Your connections will %s alert others." % ('now' if toggle else 'no longer'))
        self.player.db._watch_hide = toggle

    def switch_mute(self):
        toggle = bool(self.player.db._watch_mute)
        self.sys_msg("You will %s hear friends connecting." % ('now' if toggle else 'no longer'))
        self.player.db._watch_mute = toggle



class CmdAccount(AthCommand):
    """

    """
    key = '@account'
    system_name = 'ACCOUNT'
    help_category = 'System'
    player_switches = ['edit']
    admin_switches = ['list', 'create']

    def target(self):
        if not self.args or not self.is_admin:
            target = self.player
        elif self.args and self.is_admin:
            target = Player.objects.filter_family(username__iexact=self.args).first()
        else:
            target = None
        return target

    def func(self):
        if not self.final_switches:
            self.main()
        else:
            getattr(self, 'switch_%s' % self.final_switches[0])()

    def main(self):
        target = self.target()
        self.msg(target.account.display(self.player))

    def switch_create(self):
        name, password = self.lsargs, self.rsargs
        if not name:
            self.error("No name entered.")
            return
        if not password:
            self.error("No password entered.")
            return
        try:
            target = make_player(name, password)
        except ValueError as err:
            self.error(str(err))
            return
        self.sys_msg("Account created!")
        #make_menu(self.character, 'athanor.core.menus.account', player=target)

    def switch_edit(self):
        target = self.target()
        if not target:
            self.error("Nobody found!")
            return
        make_menu(self.character, 'athanor.core.menus.account', player=target)

    def switch_list(self):
        message = list()
        message.append(self.player.render.header('Accounts'))
        if self.args:
            found = Player.objects.filter_family(username__istartswith=self.args).order_by('id')
        else:
            found = Player.objects.filter_family().order_by('id')
        acc_table = self.player.render.make_table(['ID', 'Name', 'Email', 'Characters'], width=[6, 17, 25, 30])
        for acc in found:
            acc_table.add_row(acc.id, '%s%s' % (acc.key, ' (Disabled)' if not acc.config.model.enabled else ''),
                              acc.email, ', '.join(char.key for char in acc.account.characters()))
        message.append(acc_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)




ACCOUNT_COMMANDS = [CmdPlayerConfig, CmdTz, CmdWatch, CmdAccount]