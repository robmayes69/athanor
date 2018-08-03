import athanor
from athanor.base.systems import AthanorSystem

class BaseRenderer(AthanorSystem):

    def __init__(self, base):
        self.base = base
        self.owner = base
        super(BaseRenderer, self).__init__()
        self.load()

    def load_settings(self):
        saved_data = self.model.value
        for k, v in athanor.STYLES_DATA.iteritems():
            try:
                new_setting = athanor.SETTINGS[v[0]](self, k, v[1], v[2], saved_data.get(k, None))
                self.settings[new_setting.key] = new_setting
            except Exception:
                pass