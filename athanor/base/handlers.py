from evennia.utils.ansi import ANSIString
from athanor.base.systems import AthanorSystem
from athanor.models import AccountSettingModel, CharacterSettingModel

class BaseHandler(AthanorSystem):
    cmdsets = ()
    handler_model = None

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        super(BaseHandler, self).__init__()
        self.load_model()
        self.load_cmdsets()

    def load_model(self):
        pass

    def __getitem__(self, item):
        return self.settings[item].value


    def load_cmdsets(self):
        for cmdset in self.cmdsets:
            self.owner.cmdset.add(cmdset)

    def load(self):
        pass


class CharacterBaseHandler(BaseHandler):
    mode = 'character'

    def load_model(self):
        if self.handler_model:
            self.model, created = self.handler_model.objects.get_or_create(character=self.owner)

    def at_init(self):
        pass

    def at_object_creation(self):
        pass

    def at_post_unpuppet(self, account, session, **kwargs):
        pass

    def at_true_logout(self, account, session, **kwargs):
        pass

    def at_true_login(self, **kwargs):
        pass

    def at_post_puppet(self, **kwargs):
        pass


class AccountBaseHandler(BaseHandler):

    def load_model(self):
        if self.handler_model:
            self.model, created = self.handler_model.objects.get_or_create(account=self.owner)

    def at_account_creation(self):
        pass

    def at_post_login(self, session, **kwargs):
        pass

    def at_true_login(self, session, **kwargs):
        pass

    def at_failed_login(self, session, **kwargs):
        pass

    def at_init(self):
        pass

    def at_disconnect(self, reason, **kwargs):
        pass

    def at_true_logout(self, **kwargs):
        pass

    def render_login(self, session, viewer):
        pass


class ScriptBaseHandler(BaseHandler):
    pass


class SessionBaseHandler(BaseHandler):

    def at_sync(self):
        pass

    def at_login(self, account, **kwargs):
        pass

    def at_disconnect(self, reason, **kwargs):
        pass

    def load_file(self, file):
        pass

    def save_file(self, file):
        pass

    def save(self):
        pass