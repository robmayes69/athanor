import importlib
from django.conf import settings
from athanor.handlers.base import SessionHandler
from athanor.utils.online import characters, accounts
from athanor.validators.funcs import valid_account_name, valid_account_password, valid_account_email
from athanor.utils.create import account as create_account


class SessionSystemHandler(SessionHandler):
    key = 'athanor_system'
    style = 'fallback'
    system_name = 'SYSTEM'
    operations = ('create_account', )

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
        output = response.request.output
        name = params.pop('name', '')
        password = params.pop('password', '')
        email = params.pop('email', None)
        message = {'prefix': False}
        try:
            name = valid_account_name(session, name)
            password = valid_account_password(session, password)
            if email:
                email = valid_account_email(session, email)
            new_account = create_account(name, password, email)
        except Exception as err:
            if 'text' in output:
                message['text'] = unicode(err)
                message['prefix'] = True
            if 'gmcp' in output:
                message['gmcp'] = {'args': (self.key, 'receive_create_account'), 'kwargs': {'error': unicode(err)}}
            message['prefix'] = True
            response.add(session, message)
            return

        if 'text' in output:
            message['text'] = 'Account Created! Remember that password.'
            message['prefix'] = True
        if 'gmcp' in output:
            message['gmcp'] = {'args': (self.key, 'receive_create_account'),
                               'kwargs': {'id': new_account.id, 'key': new_account.key, 'email': new_account.email}}
        response.add(session, message)

    def is_builder(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Builder)")

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Admin)")

    def is_developer(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Developer)")

    def status_name(self):
        if self.is_developer():
            return 'Developer'
        if self.is_admin():
            return 'Admin'
        if self.is_builder():
            return 'Builder'
        return 'Mortal'

    def can_see(self, target):
        return True # ust a basic check for now



class SessionWhoHandler(SessionHandler):
    key = 'athanor_who'
    category = 'athanor_who'
    operations = ('get_who_character', 'get_who_account')

    def online_characters(self):
        return [char for char in characters() if self.can_see(char)]

    def online_accounts(self):
        return [char for char in accounts() if self.can_see(char)]

    def load(self):
        module = importlib.import_module(settings.ATHANOR_CLASSES['who'])
        self.who_character_class = module.WhoCharacter
        self.who_account_class = module.WhoAccount

    def op_get_who_character(self, response):
        online = self.online_characters()
        session = response.request.session
        params = response.request.parameters
        who = self.who_character_class(session, online, params)
        message = dict()
        if 'text' in response.request.output:
            message['text'] = who.render_text()
        if 'gmcp' in response.request.output:
            message['gmcp'] = {'args': (self.key, 'receive_who_character'), 'kwargs': who.render_gmcp()}
        message['prefix'] = False
        response.add(session, message)

    def op_get_who_account(self, response):
        online = self.online_accounts()
        session = response.request.session
        params = response.request.parameters
        who = self.who_account_class(session, online, params)
        message = {'cmdname': ('receive_who_account',), }
        for mode in response.request.output:
            try:
                message[mode] = getattr(who, 'render_%s' % mode)()
            except:
                continue
        message['prefix'] = False
        response.add(session, message)

    def can_see(self, target):
        return True # just passing true for now. will implement visibility later.

ALL = [SessionSystemHandler, SessionWhoHandler]