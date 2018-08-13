from athanor import AthException
from athanor.utils.text import partial_match


class BaseHandler(object):
    key = 'base'
    cmdsets = ()
    load_order = 0
    settings_data = tuple()

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.loaded_settings = False
        self.settings = dict()
        self.load_cmdsets()
        self.load()

    def load_settings(self):
        saved_data = dict(self.get_db('settings', dict()))
        for setting_def in self.settings_data:
            new_setting = self.base.settings[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3],
                                                             saved_data.get(setting_def[0], None))
            self.settings[new_setting.key] = new_setting
        self.loaded_settings = True

    def __getitem__(self, item):
        if not self.loaded_settings:
            self.load_settings()
        return self.settings[item].value

    def load_cmdsets(self):
        for cmdset in self.cmdsets:
            self.owner.cmdset.add(cmdset)

    def load(self):
        pass

    def set_db(self, name, value):
        return self.owner.attributes.add(name, value, category=self.key)

    def get_db(self, name, default=None):
        return self.owner.attributes.get(name, category=self.key) or default

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.set_db('settings', save_data)

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.settings.values())
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        return setting, old_value


class CharacterBaseHandler(BaseHandler):
    mode = 'character'

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

    def set_db(self, name, value):
        return self.owner.nattributes.add(name, value, category=self.key)

    def get_db(self, name, default=None):
        return self.owner.nattributes.get(name, category=self.key) or default
