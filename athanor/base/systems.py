from evennia import DefaultScript
from athanor.utils.text import partial_match
from athanor import VALIDATORS, SETTINGS, AthException, SYSTEMS
from athanor.utils.online import admin


class AthanorSystem(DefaultScript):
    settings_data = tuple()
    category = 'athanor'
    key = 'base'
    system_name = 'SYSTEM'
    load_order = 0
    interval = 0
    valid = VALIDATORS
    systems = SYSTEMS

    def at_start(self):
        # Most systems will implement their own Settings.
        self.ndb.loaded_settings = False
        self.ndb.gagged = list()
        # We'll probably be using this a lot.

        # Call easy-extensible loading process.
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        if not self.ndb.loaded_settings:
            self.load_settings()
        return self.ndb.settings[item].value

    def load_settings(self):
        saved_data = dict(self.attributes.get('settings', dict()))
        for setting_def in self.settings_data:
            try:
                new_setting = SETTINGS[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3], saved_data.get(setting_def[0], None))
                self.ndb.settings[new_setting.key] = new_setting
            except Exception:
                pass
        self.ndb.loaded_settings = True

    def save_settings(self):
        save_data = dict()
        for setting in self.ndb.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.db.settings = save_data

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.ndb.settings.values())
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        return setting, old_value

    def listeners(self):
        online = set(admin())
        return online - set(self.ndb.gagged)

    def alert(self, text, source=None):
        if source:
            msg = '|r>>>|n |w[|n%s|w]|n |w%s:|n %s' % (source, self.system_name, text)
        else:
            msg = '|r>>>|n |w%s:|n %s' % (self.system_name, text)
        msg = self.systems['character'].render(msg)
        for char in self.listeners():
            char.msg(text=msg)
