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
    run_interval = 0
    valid = VALIDATORS
    systems = SYSTEMS

    def at_start(self):
        # Most systems will implement their own Settings.
        self.ndb.loaded_settings = False
        self.ndb.gagged = set()
        self.ndb.settings = dict()
        # We'll probably be using this a lot.

        # Call easy-extensible loading process.
        self.load()

    def at_server_reload(self):
        self.load()

    def __getitem__(self, item):
        if not self.ndb.loaded_settings:
            self.load_settings()
        return self.ndb.settings[item].value

    def load_settings(self):
        if self.ndb.loaded_settings:
            return bool(self.ndb.settings)
        saved_data = dict(self.attributes.get('settings', dict()))
        for setting_def in self.settings_data:
            try:
                new_setting = SETTINGS[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3], saved_data.get(setting_def[0], None))
                print "save for %s: %s" % (setting_def[0], saved_data.get(setting_def[0], None))
                self.ndb.settings[new_setting.key] = new_setting
            except Exception as e:
                pass
        self.ndb.loaded_settings = True
        return bool(self.ndb.settings)

    def save_settings(self):
        save_data = dict()
        for setting in self.ndb.settings.values():
            if setting.customized():
                save_data[setting.key] = setting.export()
        self.db.settings = save_data
        print self.db.settings

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.ndb.settings.values())
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        self.alert("Setting '%s' changed to: %s (previously: %s)" % (setting, setting.display(), old_value),
                   source=session)
        return setting, old_value

    def listeners(self):
        return admin() - self.ndb.gagged

    def alert(self, text, source=None):
        if source:
            msg = '|r>>>|n |w[|n%s|w]|n |w%s:|n %s' % (source, self.system_name, text)
        else:
            msg = '|r>>>|n |w%s:|n %s' % (self.system_name, text)
        msg = self.systems['character'].render(msg)
        for char in self.listeners():
            char.msg(text=msg)
