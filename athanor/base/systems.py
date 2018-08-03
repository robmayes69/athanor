from athanor.utils.text import partial_match
from athanor.models import SystemSettingModel
from athanor import VALIDATORS, SETTINGS, AthException


class AthanorSystem(object):
    settings_data = tuple()
    category = 'athanor'
    key = 'base'
    system_name = 'SYSTEM'
    load_order = 0
    valid = VALIDATORS
    settings_model = SystemSettingModel

    def __init__(self):
        # Most systems will implement their own Settings.
        self.settings = dict()
        self.load_settings_model()

        self.load_settings()

        # We'll probably be using this a lot.
        import athanor
        self.systems = athanor.SYSTEMS

        # Call easy-extensible loading process.
        self.load()

    def load(self):
        pass

    def load_settings_model(self):
        self.settings_store, created = self.settings_model.objects.get_or_create(key=self.key)

    def __getitem__(self, item):
        return self.settings[item].value

    def load_settings(self):
        saved_data = self.settings_store.value
        for setting_def in self.settings_data:
            try:
                new_setting = SETTINGS[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3], saved_data.get(setting_def[0], None))
                self.settings[new_setting.key] = new_setting
            except Exception:
                pass

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.settings_store.value = save_data

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.settings)
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        return (setting, old_value)

    def alert(self, text, source=None):
        self.systems['channel'].send_alert(text, source)
