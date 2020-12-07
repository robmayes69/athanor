"""
Contains only Handlers relevant to Accounts.
"""
from django.conf import settings
from athanor.utils.time import utcnow
from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.appearance import AppearanceHandler


class BanHandler:

    def __init__(self, account):
        self.account = account
        self.state = None
        self.load()

    def load(self):
        self.state = self.account.attributes.get(key='ban', category='system', default=dict())

    def get_state(self):
        """

        Returns:
            False if not banned. dict of stuff if yes.
        """
        now = utcnow()
        if (banned_until := self.state.get('until', None)) and banned_until > now:
            return {
                'left': banned_until - now,
                'reason': self.state.get('reason', 'none given'),
                'until': banned_until
            }
        if banned_until and banned_until < now:
            self.clear()
        return False

    def clear(self):
        self.account.attributes.remove(key='ban', category='system')
        self.load()

    def set(self, account, until, reason):
        new_ban = {
            'account': account,
            'until': until,
            'reason': reason,
            'started': utcnow()
        }
        self.account.attributes.add(key='ban', category='system', value=new_ban)
        self.load()


class AccountCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class AccountCmdHandler(CmdHandler):

    def get_cmdobjects(self, session=None):
        if session:
            return session.cmd.get_cmdobjects()
        return {
            'account': self.cmdobj
        }


class AccountAppearanceHandler(AppearanceHandler):
    hooks = ['header', 'details', 'sessions', 'characters', 'commands']

    def details(self, looker, styling, **kwargs):
        return [
            styling.styled_header(f"Account: {self.obj.username}"),
            f"|wEmail:|n {self.obj.email}"
        ]

    def sessions(self, looker, styling, **kwargs):
        message = list()
        if (sessions := self.obj.sessions.all()):
            message.append(styling.styled_separator("Sessions"))
            for sess in sessions:
                message.append(sess.render_character_menu_line(looker))
        return message

    def characters(self, looker, styling, **kwargs):
        message = list()
        if (characters := self.obj.characters()):
            message.append(styling.styled_separator("Characters"))
            for char in characters:
                message.append(char.render_character_menu_line(looker))
        return message

    def commands(self, looker, styling, **kwargs):
        message = list()
        caller_admin = self.obj.check_lock("pperm(Admin)")
        message.append(styling.styled_separator(looker, "Commands"))
        if not settings.RESTRICTED_CHARACTER_CREATION or caller_admin:
            message.append("|w@charcreate <name>|n to create a Character.")
        if not settings.RESTRICTED_CHARACTER_DELETION or caller_admin:
            message.append("|w@chardelete <name>=<verify name>|n to delete a character.")
        if not settings.RESTRICTED_CHARACTER_RENAME or caller_admin:
            message.append("|w@charrename <character>=<new name>|n to rename a character.")
        if not settings.RESTRICTED_ACCOUNT_RENAME or caller_admin:
            message.append("|w@username <name>|n to change your Account username.")
        if not settings.RESTRICTED_ACCOUNT_EMAIL or caller_admin:
            message.append("|w@email <new email>|n to change your Email")
        if not settings.RESTRICTED_ACCOUNT_PASSWORD or caller_admin:
            message.append("|w@password <old>=<new>|n to change your password.")
        message.append("|w@ic <name>|n to enter the game as a Character.")
        message.append("|w@ooc|n to return here again.")
        message.append("|whelp|n for more information.")
        message.append("|wQUIT|n to disconnect.")
        return message
