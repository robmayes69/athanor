from __future__ import unicode_literals

class ReqException(Exception):
    pass


class Request(object):
    req_character = False
    req_login = False
    req_admin = False
    req_wizard = False
    req_super = False
    character = None
    player = None
    command_name = 'athanor'
    sub_command = 'request'
    cmdid = None

    def __init__(self, session, args=None, kwargs=None):
        if not args:
            args = []
        if not kwargs:
            kwargs = {}
        self.session = session
        self.cmdid = kwargs.get('cmdid', None)
        self.args = args
        self.kwargs = kwargs

    def process(self):
        try:
            self.isLogin()
            self.isIC()
            self.isAdmin()
            self.isWizard()
            self.isSuper()
            self.doRequest()
        except ReqException as err:
            return self.error(str(err))

    def isLogin(self):
        if self.req_login and not self.session.logged_in:
            raise ReqException("Permission denied: operation requires logging in.")
        self.player = self.session.player

    def isIC(self):
        if self.req_character and not hasattr(self.session, 'puppet'):
            raise ReqException("Permission denied: operation requires an @ic character.")
        elif hasattr(self.session, 'puppet'):
            self.character = self.session.puppet

    def isAdmin(self):
        if self.req_admin and not self.character.is_admin():
            raise ReqException("Permission denied: operation requires admin privileges.")

    def isSuper(self):
        if self.req_super and not self.player.is_superuser:
            raise ReqException("Permission denied: Superuser only.")

    def isWizard(self):
        self.isAdmin()

    def error(self, msg):
        self.output('error', {'msg': msg})

    def doRequest(self):
        pass

    def output(self, args, kwargs=None):
        if not kwargs and self.cmdid:
            kwargs = {}
        kwargs['cmdid'] = self.cmdid
        real_kwargs = {self.command_name: (args, kwargs)}
        print real_kwargs
        self.session.msg(**real_kwargs)

class EchoRequest(Request):
    sub_command = 'echo'

    def doRequest(self):
        print 'running dorequest'
        self.output(self.args, self.kwargs)


class GroupRequest(Request):
    pass


class LoginDetails(Request):
    command_name = "login_update"

    def doRequest(self):
        if self.player:
            player_id = self.player.id
            player_key = self.player.key
            superuser = self.player.is_superuser
        else:
            player_id = 0
            player_key = ""
            superuser = False
        if self.character:
            ic = True
            character_id = self.character.id
            character_key = self.character.key
            admin = self.character.is_admin()
        else:
            ic = False
            character_id = 0
            character_key = ""
            admin = False
        self.output([player_id, player_key, character_id, character_key, ic, admin, superuser],{})


class AccountAll(Request):
    command_name = 'account_all'

    def doRequest(self):
        from athanor.classes.accounts import Player
        formatted = []
        for player in Player.objects.filter_family():
            formatted.append({'id': player.id, 'key': player.key, 'email': player.email})
        self.output([], {'data': formatted})


class AccountGet(Request):
    command_name = 'account_get'

    def doRequest(self):
        from athanor.classes.accounts import Player
        play = Player.objects.filter_family(id=self.args[0]).first()
        player = {'id': play.id, 'key': play.key, 'email': play.email}
        self.output([], {'data': player})

class AccountDelete(Request):
    command_name = 'account_delete'

class WhoAll(Request):
    command_name = 'who_all'

    def doRequest(self):
        from athanor.library import connected_characters
        formatted = [{'id': char.id, 'key': char.key} for char in connected_characters()]
        self.output([], {'data': formatted})

class WhoGet(Request):
    command_name = 'who_get'

    def doRequest(self):
        from athanor.library import connected_characters
        conn_map = {char.id: char for char in connected_characters()}
        if conn_map[self.args[0]]:
            char = conn_map[self.args[0]]
            formatted = {'id': char.id, 'key': char.key}
            self.output([], {'data': formatted})

class WhoLogout(Request):
    command_name = 'who_logout'