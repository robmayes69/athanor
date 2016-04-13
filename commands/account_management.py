import pytz
from evennia import PlayerDB
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string
from world.database.communications.models import WatchFor

class CmdPlayerConfig(AthCommand):
    """
    Command for setting account-wide options that affect command and system behavior.

    Usage:
        +config - displays all possible options.
        +config <option>=<value> - change an option.
        +config/defaults - restore default settings.

    Options:
        <BOOL> - Boolean. expects 0 (false) or 1 (True).
        <DURATION> - expects a time string in the format of #d #h #m #s. example: 5d for 5 days, or 1m 30s for 1 minute
                    30 seconds.
        <TIMEZONE> - Takes the name of a timezone. Will attempt to partial match. See @timezone for a proper list.
        <COLOR> - Takes a color code option.
    """

    system_name = 'CONFIG'
    key = '+config'
    help_category = 'General'
    player_switches = ['defaults']

    def func(self):
        if 'defaults' in self.final_switches:
            self.reset_defaults()
            return

        if not self.args:
            self.display_config()
        else:
            self.set_config()

    def reset_defaults(self):
        if not self.verify('settings defaults'):
            self.sys_msg("WARNING: This will clear your default settings."
                         "Are you sure? Enter the command again to confirm.")
            return
        self.player.settings.restore_defaults()
        self.sys_msg("Your settings were restored to defaults.")

    def display_config(self):
        self.caller.msg(self.player.settings.display_categories(self.caller))

    def set_config(self):
        try:
            self.player.settings.set_setting(self.lhs, self.rhs, exact=False)
        except ValueError as err:
            self.error(str(err))
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
            current_tz = self.player.settings.get('timezone')
            now = utcnow().astimezone(current_tz)

            self.sys_msg("Your Current Timezone is '%s'. Is it %s where you are right now?" % (str(current_tz),
                                                                                               now.strftime('%c %Z')))
            return
        tz = self.player.settings.set_setting('timezone', self.args)
        self.sys_msg("Your Current Timezone is now '%s'. Is it %s where you are right now?" % (str(tz),
                                                                                               utcnow().astimezone(tz).strftime('%c %Z')))


    def switch_list(self):
        message = []
        message.append(header('Available Timezones', viewer=self.caller))
        tz_list = pytz.common_timezones
        if self.args:
            tz_list = [tz for tz in tz_list if tz.lower().startswith(self.args.lower())]
        if not tz_list:
            self.error("'%s' returned no matches.")
            return
        tz_table = make_table('Name', 'Current Time', width=[35, 43], viewer=self.caller)
        for zone in tz_list:
            now = utcnow().astimezone(pytz.timezone(zone))
            tz_table.add_row(zone, now.strftime('%c %Z'))
        message.append(tz_table)
        message.append(subheader(viewer=self.caller))
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

    def find_watch(self):
        watch, created = WatchFor.objects.get_or_create(player=self.player)
        return watch

    def display_list(self):
        watch = self.find_watch()
        self.character.msg(watch.display_list(viewer=self.character, connected_only=True))

    def switch_list(self):
        watch = self.find_watch()
        self.character.msg(watch.display_list(viewer=self.character, connected_only=False))

    def switch_add(self):
        try:
            found = self.character.search_character(self.args)
        except ValueError as err:
            self.error(str(err))
            return
        watch = self.find_watch()
        watch.watch_list.add(found)
        self.sys_msg("Added '%s' to your Watch list." % found)

    def switch_delete(self):
        try:
            found = self.character.search_character(self.args)
        except ValueError as err:
            self.error(str(err))
            return
        watch = self.find_watch()
        if found not in watch.watch_list.all():
            self.error("They are not a friend!")
            return
        watch.watch_list.remove(found)
        self.sys_msg("Removed '%s' from your Watch list." % found)

    def switch_hide(self):
        toggle = bool(self.player.db._watch_hide)
        self.sys_msg("Your connections will %s alert others." % ('now' if toggle else 'no longer'))
        self.player.db._watch_hide = toggle

    def switch_mute(self):
        toggle = bool(self.player.db._watch_mute)
        self.sys_msg("You will %s hear friends connecting." % ('now' if toggle else 'no longer'))
        self.player.db._watch_mute = toggle

class CmdUsername(AthCommand):
    """
    This command is used to change your account's username.

    Usage:
        @username <new name>
    """
    key = '@username'
    aliases = []
    system_name = 'ACCOUNT'
    help_category = 'System'
    player_switches = []

    def func(self):
        if not self.args:
            self.error("Nothing entered for a username!")
            return
        new_name = sanitize_string(self.args)
        if PlayerDB.objects.filter(username__iexact=new_name).exclude(id=self.player.id).count():
            self.error("Cannot rename to %s. That name is already taken." % new_name)
            return
        self.player.key = new_name
        self.player.save()
        del self.player.db._reset_username
        self.sys_msg("Your new username is: %s - Remember this for your next login!" % new_name)

class CmdEmail(AthCommand):
    """
    This command is used to change your account's email.

    Usage:
        @email <new address>
    """
    key = '@email'
    aliases = []
    system_name = 'ACCOUNT'
    help_category = 'System'
    player_switches = []

    def func(self):
        if not self.args:
            self.error("Nothing entered for an address!")
            return
        new_address = PlayerDB.objects.normalize_email(sanitize_string(self.args))
        self.player.email = new_address
        self.sys_msg("Your new email is: %s" % new_address)
        del self.player.db._reset_email
        self.player.save()

ACCOUNT_COMMANDS = [CmdPlayerConfig, CmdTz, CmdWatch, CmdUsername, CmdEmail]