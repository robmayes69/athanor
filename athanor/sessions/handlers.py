import math
from django.conf import settings
from evennia.utils.ansi import ANSIString
from evennia.utils import evtable
import athanor
from athanor.base.handlers import SessionBaseHandler
from athanor.utils.create import account as create_account, character as create_character
from athanor import AthException


class SessionCoreHandler(SessionBaseHandler):
    key = 'core'
    style = 'fallback'
    system_name = 'SYSTEM'
    operations = ('create_account', 'create_character', 'set_account_disabled', 'set_character_disabled',
                  'set_account_banned', 'set_character_banned', 'set_character_shelved', 'login_account',
                  'puppet_character')
    cmdsets = ('athanor.sessions.unlogged.UnloggedCmdSet',)

    def at_sync(self):
        if not self.owner.logged_in:
            for cmdset in self.cmdsets:
                self.owner.cmdset.add(cmdset)

    def at_login(self, account, **kwargs):
        for cmdset in self.cmdsets:
            self.owner.cmdset.remove(cmdset)

    def is_builder(self):
        if not hasattr(self.owner, 'account'):
            return False
        return self.owner.account.ath['core'].is_builder()

    def is_admin(self):
        if not hasattr(self.owner, 'account'):
            return False
        return self.owner.account.ath['core'].is_admin()

    def is_developer(self):
        if not hasattr(self.owner, 'account'):
            return False
        return self.owner.account.ath['core'].is_developer()

    def op_create_account(self, response):
        """
        required parameters:
            name (str) = The new account's name.
            password (str) = The new account's password.

        optional parameters:
            email (str) = The new account's email.
        """
        session = response.request.session
        params = response.request.parameters
        name = params.pop('name', '')
        password = params.pop('password', '')
        email = params.pop('email', None)
        message = {'prefix': False}
        try:
            name = self.valid['account_name'](session, name)
            password = self.valid['account_password'](session, password)
            if email:
                email = self.valid['account_email'](session, email)
            new_account = create_account(name, password, email)
        except Exception as err:
            message['text'] = unicode(err)
            message['prefix'] = True
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_create_account'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        message['text'] = 'Account Created! Remember that password.'
        message['prefix'] = True
        message['gmcp'] = {'args': (self.mode, self.key, 'receive_create_account'), 'kwargs': {'id': new_account.id, 'key': new_account.key, 'email': new_account.email}}
        response.add(session, message)

    def op_create_character(self, response):
        """
        required parameters:
            name (str) = The new character's name.

        optional parameters:
            account_id (int) = The new character's account ID. If not THIS account...

        """
        session = response.request.session
        params = response.request.parameters
        name = params.pop('name', '')
        account_id = params.pop('account_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            if not account_id:
                account = self.owner.account
            else:
                account = self.valid['account_id'](session, account_id)
            name = self.valid['character_name'](session, name)
            if not session.account.ath['core'].is_admin():
                if session.account != account:
                    raise AthException("Permission denied. Cannot create characters for other accounts!")
                if not settings.ATHANOR_OPEN_CHARACTER_CREATION:
                    raise AthException("Character Creation by non-admin is disabled.")
                if not account.ath['core'].available_character_slots:
                    raise AthException("Account is out of Character Slots!")
            new_character = create_character(name, account)
            session.account.ath['character'].add(new_character)
        except Exception as err:
            message['text'] = unicode(err)
            message['prefix'] = True
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_create_character'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        message['text'] = 'Character Created!'
        message['prefix'] = True
        message['gmcp'] = {'args': (self.mode, self.key, 'receive_create_character'),
                               'kwargs': {'id': new_character.id, 'key': new_character.key, 'account_id': account_id}}
        response.add(session, message)

    def op_set_account_disabled(self, response):
        """
        required parameters:
            disabled (bool): Whether the account should be disabled. Set to 0 to enable again.
            account_id (int): The account to alter.
        """
        session = response.request.session
        params = response.request.parameters
        disabled = params.pop('disabled', '')
        account_id = params.pop('account_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            account = self.valid['account_id'](session, account_id)
            disabled = self.valid['boolean'](session, disabled)
            if not session.account.ath['core'].is_admin():
                raise AthException("Permission denied. Only Admin can alter Account Disable Status.")
            if account.ath['core'].is_admin() and not session.account.is_superuser:
                raise AthException("Permission denied. Only the SuperUser can alter Disables for Admin Accounts.")
            account.ath['core'].set_disabled(disabled)
        except Exception as err:
            message['text'] = unicode(err)
            message['prefix'] = True
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_account_disabled'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        message['text'] = 'Account %s!' % 'disabled' if disabled else 'enabled'
        message['prefix'] = True
        message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_account_disabled'),
                               'kwargs': {'account_id': account_id, 'disabled': disabled}}
        response.add(session, message)

    def op_set_character_disabled(self, response):
        """
        required parameters:
            disabled (bool): Whether the character should be disabled. Set to 0 to enable again.
            character_id (int): The character to alter.
        """
        session = response.request.session
        params = response.request.parameters
        disabled = params.pop('disabled', '')
        character_id = params.pop('character_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            character = self.valid['character_id'](session, character_id)
            disabled = self.valid['boolean'](session, disabled)
            if not session.account.ath['core'].is_admin():
                raise AthException("Permission denied. Only Admin can alter Character Disable Status.")
            if character.ath['core'].account.is_admin() and not session.account.is_superuser:
                raise AthException("Permission denied. Only the SuperUser can alter Disables for Admin Accounts.")
            character.ath['core'].set_disabled(disabled)
        except Exception as err:
            message['text'] = unicode(err)
            message['prefix'] = True
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_character_disabled'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        message['text'] = 'Character %s!' % 'disabled' if disabled else 'enabled'
        message['prefix'] = True
        message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_character_disabled'),
                               'kwargs': {'character_id': character_id, 'disabled': disabled}}
        response.add(session, message)

    def op_set_account_banned(self, response):
        """
        required parameters:
            banned (int): the UNIX_TIMESTAMP (number of seconds since 1970) that the account will be unbanned.
                set to 0 to unban.
            account_id (int): The account to alter.
        """
        session = response.request.session
        params = response.request.parameters
        output = response.request.output
        banned = params.pop('banned', None)
        account_id = params.pop('account_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            account = self.valid['account_id'](session, account_id)
            banned = self.valid['unix_time_future'](session, banned)
            if not session.account.ath['core'].is_admin():
                raise AthException("Permission denied. Only Admin can alter Account Banned Status.")
            if account.ath['core'].is_admin() and not session.account.is_superuser:
                raise AthException("Permission denied. Only the SuperUser can alter Bans for Admin Accounts.")
            account.ath['core'].set_banned(banned)
        except Exception as err:
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_account_banned'),
                                   'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'text' in output:
            message['text'] = 'Account %s!' % 'banned' if banned else 'un-banned'
            message['prefix'] = True
        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_account_banned'),
                               'kwargs': {'account_id': account_id, 'banned': banned}}
        response.add(session, message)


    def op_set_character_banned(self, response):
        """
        required parameters:
            banned (int): the UNIX_TIMESTAMP (number of seconds since 1970) that the character will be unbanned.
                set to 0 to unban.
            character_id (int): The character to alter.
        """
        session = response.request.session
        params = response.request.parameters
        output = response.request.output
        banned = params.pop('banned', None)
        character_id = params.pop('character_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            character = self.valid['character_id'](session, character_id)
            banned = self.valid['unix_time_future'](session, banned)
            if not session.account.ath['core'].is_admin():
                raise AthException("Permission denied. Only Admin can alter Character Banned Status.")
            if character.ath['core'].account.ath['core'].is_admin() and not session.account.is_superuser:
                raise AthException("Permission denied. Only the SuperUser can alter Bans for Admin Accounts.")
            character.ath['core'].set_banned(banned)
        except Exception as err:
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_account_banned'),
                                   'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'text' in output:
            message['text'] = 'Character %s!' % 'banned' if banned else 'un-banned'
            message['prefix'] = True
        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_character_banned'),
                               'kwargs': {'character_id': character_id, 'banned': banned}}
        response.add(session, message)

    def op_set_character_shelved(self, response):
        """
        required parameters:
            shelved (bool): Whether the character should be shelved. Set to 0 to un-shelf again.
            character_id (int): The character to alter.

        optional parameters:
            name (str): A character name that the un-shelved character should be changed to.
                Remember, two characters cannot have the same name!

        :param response: Response object.
        :return:
        """
        session = response.request.session
        params = response.request.parameters
        output = response.request.output
        shelved = params.pop('shelved', '')
        name = params.pop('name', '')
        character_id = params.pop('character_id', None)
        message = {'prefix': False}
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            character = self.valid['character_id'](session, character_id)
            shelved = self.valid['boolean'](session, shelved)
            if not session.account.ath['core'].is_admin():
                raise AthException("Permission denied. Only Admin can alter Character Shelve Status.")
            character.ath['core'].set_shelved(shelved)
        except Exception as err:
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_character_disabled'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'text' in output:
            message['text'] = 'Character %s!' % 'shelved' if shelved else 'un-shelved'
            message['prefix'] = True
        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.mode, self.key, 'receive_set_character_shelved'),
                               'kwargs': {'character_id': character_id, 'shelved': shelved}}
        response.add(session, message)


    def op_login_account(self, response):
        """
        require parameters:
            account_id (int): The account to login to!
            OR
            account_name (str): The account to login to!
            (if both are provided, account_id takes priority)

            password (str): The account password.

        optional parameters:
            dark (bool): Whether the account should login Dark. (Requires Admin. Will be ignored without admin.)
                Default False.
            hidden (bool): Whether the account should login Hidden.
                Default False.
        """
        session = response.request.session
        params = response.request.parameters
        output = response.request.output
        password = params.pop('password', None)
        account_id = params.pop('account_id', None)
        account_name = params.pop('account_name', None)
        dark = params.pop('dark', False)
        hidden = params.pop('hidden', False)
        message = {'prefix': False}
        try:
            if session.account:
                raise AthException("You are already logged in!")
            if not (account_id or account_name):
                raise AthException("Must provide an Account ID or Account Name!")
            if account_id:
                account = self.valid['account_id'](session, account_id)
            else:
                if not account_name:
                    raise AthException("Must at least provide an account name!")
                from athanor.classes.accounts import Account
                account = Account.objects.filter_family(db_key__iexact=account_name).first()
                if not account:
                    raise AthException("Account not found!")
            banned = account.ath['core'].banned
            if banned:
                account.at_failed_login(session)
                raise AthException("That account is banned until %s." % account.ath['core'].display_time(banned))
            if account.ath['core'].disabled:
                account.at_failed_login(session)
                raise AthException("That account is disabled!")
            if not account.check_password(password):
                account.at_failed_login(session)
                raise AthException("Invalid password!")
            if account.ath['core'].is_admin() and dark:
                account.ath['who'].dark = dark
            if hidden:
                account.ath['who'].hidden = hidden
            session.sessionhandler.login(session, account)
        except Exception as err:
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.key, 'receive_login_account'),
                                   'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'text' in output:
            message['text'] = account.return_appearance(session, account)
            message['prefix'] = False
        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.key, 'receive_login_account'),
                               'kwargs': {'account_id': account_id, 'characters': account.ath['character'].login_data()}}
        response.add(session, message)


    def op_puppet_character(self, response):
        """
        required parameters:
            character_id (int): The character to puppet. Set this to 0 to unpuppet an existing character.

        optional parameters:
            dark (bool): Whether the character should materialize Dark. (Requires Admin. Will be ignored without admin.)
                Default False.
            hidden (bool): Whether the character should enter the world who-Hidden.
                Default False.
        """
        session = response.request.session
        params = response.request.parameters
        output = response.request.output
        character_id = params.pop('character_id', None)
        message = {'prefix': False}
        dark = params.pop('dark', False)
        hidden = params.pop('hidden', False)
        try:
            if not session.account:
                raise AthException("You are not logged in!")
            if character_id == 0:
                if not session.puppet:
                    raise AthException("You are already OOC on this session.")
                session.account.unpuppet_object(session)
            else:
                character = self.valid['character_id'](session, character_id)
                if not character.access(session.account, 'puppet'):
                    raise AthException("Permission denied. You cannot puppet that.")
                if character.ath['core'].is_admin() and dark:
                    character.ath['who'].dark = dark
                if hidden:
                    character.ath['who'].hidden = hidden
                session.account.puppet_object(session, character)
        except Exception as err:
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.key, 'receive_puppet_character'),
                                   'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.key, 'receive_puppet_character'),
                               'kwargs': {'character_id': character_id}}
        response.add(session, message)

    def can_see(self, target):
        """
        Simple visibility check.

        Sessions have no permissions unless logged in. In which case, this check is relayed to the Account WhoHandler.
        :param target: Character or Account. A Character shouldn't end up here though.
        :return: Boolean.
        """
        if self.owner.logged_in:
            return self.owner.account.ath['who'].can_see(target)
        return not (target.ath['who'].dark or target.ath['who'].hidden)


class SessionRendererHandler(SessionBaseHandler):
    key = 'render'

    def width(self):
        return self.owner.protocol_flags['SCREENWIDTH'][0]

    def load_settings(self):
        for k, v in athanor.STYLES_DATA.iteritems():
            try:
                new_setting = athanor.SETTINGS[v[0]](self, k, v[1], v[2], None)
                self.settings[new_setting.key] = new_setting
            except Exception:
                pass

    def get_settings(self):
        if hasattr(self.owner, 'account'):
            return self.owner.account.ath['color'].get_settings()
        if not self.loaded_settings:
            self.load_settings()
        return self.settings

    def table(self, columns, border='cols', header=True, width=None, **kwargs):
        colors = self.get_settings()
        border_color = colors['border_color'].value
        column_color = colors['table_column_header_text_color'].value

        colornames = ['|%s%s|n' % (column_color, col[0]) for col in columns]
        header_line_char = ANSIString('|%s-|n' % border_color)
        corner_char = ANSIString('|%s+|n' % border_color)
        border_left_char = ANSIString('|%s|||n' % border_color)
        border_right_char = ANSIString('|%s|||n' % border_color)
        border_bottom_char = ANSIString('|%s-|n' % border_color)
        border_top_char = ANSIString('|%s-|n' % border_color)

        if not width:
            width = self.width()

        table = evtable.EvTable(*colornames, border=border, pad_width=0, valign='t', header_line_char=header_line_char,
                                corner_char=corner_char, border_left_char=border_left_char,
                                border_right_char=border_right_char, border_bottom_char=border_bottom_char,
                                border_top_char=border_top_char, header=header, width=width, maxwidth=width)

        # Tables always have the borders on each side, so let's subtract two characters.
        for count, column in enumerate(columns):
            if column[1]:
                table.reformat_column(count, width=column[1], align=column[2])
            else:
                table.reformat_column(count, align=column[2])
        return table

    def header(self, header_text=None, fill_character=None, edge_character=None, mode='header', color_header=True):
        styles = self.get_settings()
        colors = {}
        colors['border'] = styles['%s_fill_color' % mode].value
        colors['headertext'] = styles['%s_text_color' % mode].value
        colors['headerstar'] = styles['%s_star_color' % mode].value

        width = self.width()
        if edge_character:
            width -= 2

        if header_text:
            if color_header:
                header_text = ANSIString(header_text).clean()
                header_text = ANSIString('|n|%s%s|n' % (colors['headertext'], header_text))
            if mode == 'header':
                begin_center = ANSIString("|n|%s<|%s* |n" % (colors['border'], colors['headerstar']))
                end_center = ANSIString("|n |%s*|%s>|n" % (colors['headerstar'], colors['border']))
                center_string = ANSIString(begin_center + header_text + end_center)
            else:
                center_string = ANSIString('|n |%s%s |n' % (colors['headertext'], header_text))
        else:
            center_string = ''

        fill_character = styles['%s_fill' % mode].value

        remain_fill = width - len(center_string)
        if remain_fill % 2 == 0:
            right_width = remain_fill / 2
            left_width = remain_fill / 2
        else:
            right_width = math.floor(remain_fill / 2)
            left_width = math.ceil(remain_fill / 2) + 1

        right_fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character * int(right_width)))
        left_fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character * int(left_width)))

        if edge_character:
            edge_fill = ANSIString('|n|%s%s|n' % (colors['border'], edge_character))
            main_string = ANSIString(center_string)
            final_send = ANSIString(edge_fill) + left_fill + main_string + right_fill + ANSIString(edge_fill)
        else:
            final_send = left_fill + ANSIString(center_string) + right_fill
        return final_send

    def subheader(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'subheader'
        return self.header(*args, **kwargs)

    def separator(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'separator'
        return self.header(*args, **kwargs)

    def footer(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'footer'
        return self.header(*args, **kwargs)
