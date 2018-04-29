from athanor.base.handlers import CharacterHandler
from athanor_cwho.models import CharacterWho


class CWhoHandler(CharacterHandler):
    key = 'cwho'
    category = 'cwho'
    system_name = 'WHO'
    django_model = CharacterWho
    cmdsets = ('athanor_cwho.characters.cmdsets.WhoCmdSet',)


    def at_true_logout(self, account, session, **kwargs):
        self.model.hidden = False
        self.model.save(update_fields=['hidden'])

    @property
    def hidden(self):
        return self.model.hidden

    @hidden.setter
    def hidden(self, value):
        self.model.hidden = value
        self.model.save(update_fields=['hidden', ])
