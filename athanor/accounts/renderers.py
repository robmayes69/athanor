from athanor.base.renderers import BaseRenderer
from athanor.models import AccountRenderModel

class AccountRenderer(BaseRenderer):
    mode = 'account'

    def load_model(self):
        self.model, created = AccountRenderModel.objects.get_or_create(account=self.owner)