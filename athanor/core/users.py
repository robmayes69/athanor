from __future__ import unicode_literals

import pytz
from django.db.models import Q
from athanor.classes.accounts import Account
from athanor.core.command import AthCommand
from athanor.utils.create import account as make_account
from athanor.utils.menu import make_menu
from athanor.utils.time import utcnow, duration_from_string
from athanor.utils.text import normal_string


class CmdAccountConfig(AthCommand):
    """
    Command for setting account-wide options that affect command and system behavior.

    Usage:
        @config - displays all possible options.
        @config <option>=<value> - change an option.

    Options:
        <BOOL> - Boolean. expects 0 (false/off) or 1 (True/On).
        <DURATION> - expects a time string in the format of #d #h #m #s. example: 5d for 5 days, or 1m 30s for 1 minute
                    30 seconds.
        <TIMEZONE> - Takes the name of a timezone. Will attempt to partial match. See @timezone for a proper list.
        <COLOR> - Takes a color code option. Like r for bright red or n for neutral.

    """

    system_name = 'CONFIG'
    key = '@config'
    help_category = 'General'
    player_switches = ['name', 'channel', 'group']

    def _main(self):
        """
        Displays the User-based @config if nothing is entered. Switches to set if something is.

        """
        if not self.args:
            self._display_config()
        else:
            self._set_config()

    def _display_config(self):
        """
        Displays the User @config options.

        """
        self.msg_lines(self.player.config.display(self.player))

    def _set_config(self):
        msg = self.player.config.set(self.lhs, self.rhs)
        self.sys_msg(msg)

    def switch_name(self):
        """
        This is used for assigning a color code to a character name.

        """
        if not self.args:
            return self.display_name()
        found = self.character.search_character(self.lhs)
        msg = self.player.colors.set(target=found, value=self.rhs, mode='characters')
        self.sys_msg(msg)

    def switch_channel(self):
        """
        This is used for assigning a custom color to a channel.

        """
        if not self.args:
            return self.display_channel()
        if not self.lhs:
            raise ValueError("Must enter a channel name.")
        found = self.partial(self.lhs, self.character.channels.visible())
        if not found:
            raise ValueError("Channel not found.")
        msg = self.player.colors.set(target=found, value=self.rhs, mode='channels')
        self.sys_msg(msg)

    def switch_group(self):
        """
        This will be used for assigning a custom color to a group. It's not done yet.

        """
        if not self.args:
            return self.display_group()

class CmdTz(AthCommand):
    """
    Change your Timezone setting.

    Usage:
        @tz <timezone> - change your timezone. Equal to @config timezone=<timezone>
        @tz/list <timezone> - display all timezones. Optionally search for timezones containing entered text.

    Example:
        @tz/list America
        @tz America/Detroit

    """

    key = '@tz'
    aliases = ['@timezone', '+tz']
    help_category = 'General'
    player_switches = ['list']
    sysname = 'TIME'

    def _main(self):

        if not self.args: # Nothing was entered, so we'll remind of current timezone.
            current_tz = self.player.config['timezone']
            now = utcnow().astimezone(current_tz)
            self.sys_msg("Your Current Timezone is '%s'. Is it %s where you are right now?" %
                         (str(current_tz), now.strftime('%c %Z')))
            return

        # Something was entered. Let's change the timezone!
        self.player.player_settings.timezone = self.args
        self.player.player_settings.save(update_fields=['timezone'])
        tz = self.player.player_settings.timezone
        self.sys_msg("Your Current Timezone is now '%s'. Is it %s where you are right now?" %
                     (str(tz), utcnow().astimezone(tz).strftime('%c %Z')))


    def switch_list(self):
        """
        Since Timezones are confusing and there's tons of them, this makes it easy to search for them.

        """
        message = list()
        message.append(self.player.render.header('Available Timezones'))

        # Here's all of the timezones we'll need.
        tz_list = pytz.common_timezones


        if self.args: # Run a search, since the user entered something.
            tz_list = [tz for tz in tz_list if self.args.lower() in tz.lower()]
        if not tz_list:
            raise ValueError("'%s' returned no matches.")

        # All information gained. Render a table and send it off!
        tz_table = self.player.render.make_table(['Name', 'Current Time'], width=[35, 43])
        for zone in tz_list:
            now = utcnow().astimezone(pytz.timezone(zone))
            tz_table.add_row(zone, now.strftime('%c %Z'))
        message.append(tz_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)


class CmdFriend(AthCommand):
    """
    The Friend system alerts you when characters log on or off.

    Usage:
    @friend
    @friend/list

    Used to display all friends on your @watch list. /list includes offline friends.

    Management:
    @friend/add <character>
        Add a character to your friends list.

    @friend/remove <character>
        Remove a character from your friends list.

    @friend/hide
        No longer trigger other people's friend alerts. Use again to disable.

    @friend/mute
        No longer hear when others connect. Use again to disable.

    """
    key = '@friend'
    aliases = ['@watch', '+wf', 'wf', '+watch']
    system_name = 'FRIEND'
    help_category = 'Community'
    player_switches = ['list', 'add', 'remove', 'hide', 'mute']

    def _main(self):
        """
        Used to display online friends.

        """
        msg = self.player.config.model.display_friends(viewer=self.character, connected_only=True)
        self.character.msg(msg)

    def switch_list(self):
        """
        Display all friends, even offline ones.

        """
        msg = self.player.config.model.display_friends(viewer=self.character, connected_only=False)
        self.character.msg(msg)

    def switch_add(self):
        """
        Add a character to your friend list.

        """
        found = self.character.search_character(self.args)
        self.player.config.model.friends.add(found)
        self.sys_msg("Added '%s' to your Friend list." % found)

    def switch_remove(self):
        """
        Remove character from your friend list.

        """
        found = self.character.search_character(self.args)
        if found not in self.player.player_settings.watch_list.all():
            raise ValueError("They are not a friend!")
        self.player.config.model.friends.remove(found)
        self.sys_msg("Removed '%s' from your Friend list." % found)

    def switch_hide(self):
        """
        Toggle your Hide status.

        """
        self.player.db._friend_hide = not self.player.db._friend_hide
        self.sys_msg("Your connections will %s alert others." % ('now' if self.player.db._friend_hide else 'no longer'))

    def switch_mute(self):
        """
        Toggle your mute status.

        """
        self.player.db._friend_mute = not self.player.db._friend_mute
        self.sys_msg("You will %s hear friends connecting." % ('now' if self.player.db._friend_mute else 'no longer'))



class CmdUser(AthCommand):
    """
    General admin tool for managing Users. (Users are known in Evennia lingo as
    Players. They are the Accounts used to login to the game.)

    Usage:
        @user <user>
        @user/logins <user>

    Displays information about a specific user, or your own User if no User is
    provided. Only admin can view other User data. The /logins switch shows
    login records.

    Staff:

    @user/list <name>
        List all active users beginning with <name>. If <name> is empty it
        displays them all.

    @user/inactive <name>
        List inactive users, as with /list. Inactive users are Disabled ones
        or those who have not logged in within 90 days.

    @user/create <name>=<password>
        Create a new user.

    @user/email <name>=<new email>
        Change a user's email.

    @user/rename <name>=<new name>
        Rename a user.

    @user/password <name>=<new password>
        Change a user's password.

    @user/newcharacter <name>=<character name>
        Create a new character for a user.

    @user/super <user>
        Grant Superuser power to a user. Only Superusers can use this, and not on
        themselves.

    @user/disable <user>
        Disable a user. They will not appear in the normal list and cannot login.
        This is how you 'delete' a User. Or for a soft-ban/suspension.

    @user/enable <user>
        Re-enable a disabled User account.

    @user/mothballed <user>
        Special version of /list for showing Disabled Users.

    """
    key = '@user'
    system_name = 'USER'
    help_category = 'System'
    player_switches = []
    admin_switches = ['list', 'create', 'password', 'inactive', 'disable', 'enable', 'email',
                      'newcharacter', 'super', 'rename', 'mothballed']

    def _target(self, must_enter=False, enabled=True, authority=False):
        """
        Internal method used for the various switches. Uses command arguments to target a player.

        Args:
            must_enter (bool): If false, no entry means return the caller's Player object.
            enabled (bool): Return only Enabled Players.
            authority (bool): Run authority check.

        Returns:
            (PlayerDB): The targeted User.

        """
        if must_enter and not self.lhs:
            raise ValueError("Must enter a User!")
        target = None
        if not self.args or not self.is_admin:
            target = self.player
        elif self.lhs and self.is_admin:
            target = Account.objects.filter_family(username__iexact=self.lhs, player_settings__enabled=enabled).first()
        if not target:
            raise ValueError("User not found.")
        if authority:
            if not target.authority(self.player):
                raise ValueError("Permission denied. %s is a %s!" % (target, target.account.status_name()))
        return target

    def func(self):
        """
        If no switches, call the main() method for display. Otherwise, run the specific switch_ method.

        """
        try:
            if not self.final_switches:
                return self.main()
            return getattr(self, 'switch_%s' % self.final_switches[0])()
        except ValueError as err:
            return self.error(str(err))

    def main(self):
        """
        Display the User account information.

        """
        target = self._target()
        self.msg(target.account.display(self.player))

    def switch_create(self):
        """
        Creates a new User using the given name and password.

        """
        name, password = self.lhs, self.rhs
        if not name:
            raise ValueError("No name entered.")
        if not password:
            raise ValueError("No password entered.")
        target = make_account(name, password)
        self.sys_msg("User created! Don't forget to set its email with @user/email.")
        self.sys_report("Created New User: %s" % target)

    def switch_list(self, enabled=True, inactive=False):
        """
        Switch method used for /list, /inactive, and /mothballed. Generates an EvTable and spits it out.

        Args:
            enabled (bool): Displays enabled users. used for showing mothballed Users when false.
            inactive (bool): Display inactive users. If false, displays active users. Active = logged on within last
                90 days.

        """
        message = list()
        message.append(self.caller.render.header('Users'))
        if self.args: # If you entered a name... filter by it!
            found = Account.objects.filter_family(username__istartswith=self.args,
                                                 player_settings__enabled=enabled).order_by('player_settings__last_played')
        else: # And if not...
            found = Account.objects.filter_family().order_by('player_settings__last_played')

        # Prepare time cutoff for active/inactive check.
        cutoff = duration_from_string('90d')
        final_cutoff = utcnow() - cutoff

        # Alter filtering for the different display modes.
        if inactive and enabled:
            found = found.filter(Q(player_settings__last_played__lt=final_cutoff) | Q(player_settings__last_played=None))
        else:
            found = found.filter(player_settings__last_played__gte=final_cutoff)

        # Now to create the
        acc_table = self.caller.render.make_table(['Name', 'Last', 'Characters'], width=[36, 7, 37])
        for acc in found:
            login = acc.player_settings.last_played
            if login:
                login = self.caller.time.display(acc.player_settings.last_played,format='%b %d')
            else:
                login = 'N/A'
            acc_table.add_row('%s%s' % (acc.key, ' (Disabled)' if not acc.config.model.enabled else ''), login,
                              ', '.join(char.key for char in acc.account.characters()))
        message.append(acc_table)
        message.append(self.caller.render.footer())
        self.msg_lines(message)

    def switch_inactive(self):
        """
        Call self.switch_list to display all inactive users.

        """
        self.switch_list(inactive=True)

    def switch_mothballed(self):
        """
        Call self.switch_list to display all Disabled users.

        """
        self.switch_list(enabled=False)

    def switch_password(self):
        """
        Change a User's password.

        """
        target = self._target(must_enter=True, authority=True)
        if not self.rhs:
            raise ValueError("No password entered!")
        target.set_password(self.rhs)
        if not self.verify('%s %s' % (target.id, self.rhs)):
            return self.sys_msg("WARNING: This will change their password. Enter this again to verify!")
        msg = "Changed Password for: %s (%s)" % (target, target.account.status_name())
        self.sys_report(msg)
        self.sys_msg(msg)

    def switch_super(self):
        """
        Grants or revokes Superuser privileges. It just flips the existing value.

        """
        if not self.player.is_superuser:
            raise ValueError("Permission denied.")
        target = self._target(must_enter=True)
        if not target:
            raise ValueError("Must target a User!")
        if target == self.player:
            raise ValueError("Cannot alter yourself.")
        target.is_superuser = not target.is_superuser
        target.save()
        msg = "Superuser privileges for %s: %s." % (target, 'Granted' if target.is_superuser else 'Revoked')
        self.sys_report(msg)
        self.sys_msg(msg)

    def switch_rename(self):
        """
        Renames a user.

        """
        target = self._target(must_enter=True, authority=True)
        name = normal_string(self.rhs)
        if not name:
            raise ValueError("Must enter a new name!")
        if Account.objects.filter_family(username__iexact=name).exclude(id=target.id).count():
            raise ValueError("Usernames must be unique.")
        oldname = target.username
        target.username = name
        target.save()
        msg = "User Renamed from %s to: %s" % (oldname, name)
        self.sys_msg(msg)
        self.sys_report(msg)

    def switch_enable(self):
        """
        Enable a disabled user. I haven't written it yet.

        """
        target = self._target(must_enter=True, authority=True)


    def switch_disable(self):
        """
        Disables a User. I haven't written it yet.

        """
        pass