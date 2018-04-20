import importlib
from django.conf import settings
from evennia.utils.ansi import ANSIString
from athanor.utils.text import partial_match



class TaskResponse(object):
    """
    Instances of TaskResponse represent the results of an Atomic Operation on the
    Athanor handler APIs.

    ::param: source is an instance of AthCommand or an object that implements .caller, .player, and .character
    """
    def __init__(self, source):
        self.error = list()
        self.error_json = list()
        self.success = list()
        self.success_json = list()
        self.alert = list()
        self.alert_json = list()

    def json(self, name, **kwargs):
        my_list = getattr(self, '%s_json')
        my_list.append(kwargs)



class __BaseTypeHandler(object):
    """
    The base used for the Athanor Handlers that are loaded onto all Athanor Accounts and Characters.

    Not meant to be used directly.
    """
    mode = None

    def get_handlers(self):
        pass

    def __init__(self, owner):
        """

        :param owner: An instance of a TypeClass'd object.
        """
        self.owner = owner
        self.attributes = owner.attributes
        self.get_handlers()
        self.handlers = dict()

        hook_list = [item.key for item in self.handlers_dict.values() if item.use_hooks]
        hook_list.sort(key=lambda h: h.hook_order)

        self.hook_handlers = tuple(hook_list)

        # Process the 'always load' handlers:
        load_handlers = [item for item in self.handlers_dict.values() if item.always_load]
        load_handlers.sort(key=lambda h: h.load_order)

        for handler in load_handlers:
            self.handlers[handler.key] = handler(self)

        # Call an extensible Load function for simplicity if need be.
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        if item in self.handlers:
            return self.handlers[item]
        if item not in self.handlers_dict:
            raise ImportError("Improper Athanor Managers Data. Cannot Find: %s" % item)

        # If it doesn't exist, then we'll load it here.
        new_item = self.handlers_dict[item](self)
        self.handlers[item] = new_item
        return new_item


class CharacterTypeHandler(__BaseTypeHandler):
    mode = 'character'

    def get_handlers(self):
        handlers_classes = list()
        for handler in settings.ATHANOR_HANDLERS_CHARACTER:
            module = importlib.import_module(handler)
            handlers_classes += module.ALL

        self.handlers_dict = {handler.key: handler for handler in handlers_classes}
        self.always_loads = [item for item in handlers_classes if item.always_load]
        self.always_loads.sort(key=lambda i: i.load_order)
        self.hook_list = [item for item in handlers_classes if item.use_hooks]
        self.hook_list.sort(key=lambda i: i.hook_order)

    def at_post_unpuppet(self, account, session):
        pass

    def at_true_logout(self, account, session):
        pass

    def at_true_login(self):
        pass

    def at_post_puppet(self):
        pass


class AccountTypeHandler(__BaseTypeHandler):
    mode = 'account'

    def get_handlers(self):
        handlers_classes = list()
        for handler in settings.ATHANOR_HANDLERS_ACCOUNT:
            module = importlib.import_module(handler)
            handlers_classes += module.ALL

        self.handlers_dict = {handler.key: handler for handler in handlers_classes}
        self.always_loads = [item for item in handlers_classes if item.always_load]
        self.always_loads.sort(key=lambda i: i.load_order)
        self.hook_list = [item for item in handlers_classes if item.use_hooks]
        self.hook_list.sort(key=lambda i: i.hook_order)

    def at_account_creation(self):
        for handler in self.hook_list:
            handler.at_account_creation()

    def at_post_login(self, session):
        for handler in self.hook_list:
            handler.at_post_login(session)

    def at_true_login(self, session):
        for handler in self.hook_list:
            handler.at_true_login(session)

    def at_failed_login(self, session):
        for handler in self.hook_list:
            handler.at_failed_login(session)


class ScriptTypeHandler(__BaseTypeHandler):
    mode = 'script'


class __BaseHandler(object):
    """
    Base class for each kind of Handler implemented by Athanor modules.

    file_names and category are used for saving to an Attribute. they must be unique together.
    "settings" is a reservd file name.

    Key is also unique per BaseTypeHandler. So, don't re-use them.

    The default is for each to save and load a bunch of dictionaries.

    style is the style colors that this system should use for rendering data, if any. Use 'fallback' as a failsafe.

    system_name will affect system message headers prefix.

    settings_classes must be a tuple or list of all classes used for this system's per-typeclass settings.

    use_hooks will enable the hooks system on Accounts and Characters to propogate to this Handler.

    hook_order will affect in what order those hooks are called.

    always_load will cause this handler to be loaded during initialization of the base Handler.

    load_order will ensure that it happens in a specific order.
    """
    key = 'base'
    file_names = ()
    category = 'base'
    style = 'fallback'
    system_name = 'SYSTEM'
    settings_classes = ()
    use_hooks = False
    hook_order = 0
    always_load = False
    load_order = 0
    account_mode = False
    resp_class = TaskResponse

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.settings = dict()
        self.load_settings()
        self.load()

    def __getitem__(self, item):
        return self.settings[item].value

    def respond(self, source):
        return self.resp_class(source)

    def load_file(self, file):
        return self.base.attributes.get(key=file, default=dict(), category=self.category)

    def load_settings(self):
        resp = self.respond(self)
        saved_data = self.load_file('settings')
        for setting_class in self.settings_classes:
            try:
                new_setting = setting_class(self, saved_data)
                self.settings[new_setting.key] = new_setting
            except Exception as err:
                resp.error.append("Could not Load %s Setting: %s. Reason: %s. (Setting restored to defaults.)")
                resp.json('error', message="Cannot load Setting", reason=unicode(err))
                new_setting = setting_class(self)
                self.settings[new_setting.key] = new_setting

    def load(self):
        pass

    def save_attribute(self, file, data):
        self.base.attributes.get(key=file, value=data, category=self.category)

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.save_attribute('settings', save_data)

    def process_response(self, resp):
        for error in resp.errors:
            self.console_msg(error, error=True)
        for success in resp.success:
            self.console_msg(success)
        # Put JSON stuff here later.

    def change_settings(self, source, key, value):
        resp = self.respond(source)
        setting = partial_match(key, self.settings)
        if not setting:
            resp.error.append("Setting '%s' not found!" % key)
            resp.json('error', message='Setting not found', key=key)
            return self.process_response(resp)
        results = setting.set(value, str(value).split(','), source)
        resp.success.append("Setting '%s' Changed to: %s" % results)
        resp.json('success', message='Setting Changed!', key=key, value=results)
        self.save_settings()
        return self.process_response(resp)

    def export(self, file):
        return None

    def save_file(self, file):
        data = self.export(file)
        if data:
            self.save_attribute(file, data)

    def save(self):
        for file in self.file_names:
            self.save_file(file)

    def console_msg_lines(self, message=None):
        lines = '\n'.join(unicode(line) for line in message)
        self.owner.msg(lines)

    def console_msg(self, message, error=False):
        style = self.owner.styles[self.style]
        if not style:
            style = self.owner.styles.fallback
        if error:
            message = '|rERROR:|n %s' % message
        alert = '|%s-=<|n|%s%s|n|%s>=-|n ' % (style['msg_edge_color'],
                                              style['msg_name_color'],
                                              self.system_name, style['msg_edge_color'])
        send_string = alert + message
        self.owner.msg(unicode(ANSIString(send_string)))

    def json_msg(self, message):
        pass

    def alert_channel(self):
        pass


class CharacterHandler(__BaseHandler):

    def at_post_unpuppet(self, account, session):
        pass


class AccountHandler(__BaseHandler):
    account_mode = True


class ScriptHandler(__BaseHandler):
    pass