from athanor.base.helpers import AccountHandler
from athanor.athanor_awho.models import AccountWho

class AWhoHandler(AccountHandler):
    key = 'awho'
    style = 'awho'
    category = 'athanor'
    system_name = 'WHO'
    django_model = AccountWho
    cmdsets = ('athanor_awho.accounts.cmdsets.AWhoCmdSet',)


    def at_true_logout(self, **kwargs):
        self.model.hidden = False
        self.model.save(update_fields=['hidden'])

    @property
    def hidden(self):
        return self.model.hidden

    @hidden.setter
    def hidden(self, value):
        self.model.hidden = value
        self.model.save(update_fields=['hidden', ])