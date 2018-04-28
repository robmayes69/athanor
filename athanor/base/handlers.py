from evennia.utils.ansi import ANSIString
from athanor.utils.text import partial_match


class AthanorRequest(object):
    """
    Instances of TaskRequest store information about a Request. This could come from a Command or an OOB Function.
    """

    def __init__(self, session, handler, operation, parameters=None):
        if not parameters:
            parameters = dict()
        self.handler = handler
        self.session = session
        self.operation = operation
        self.parameters = parameters


class AthanorResponse(object):
    """
    Instances of TaskResponse represent the results of an Atomic Operation on the
    Athanor handler APIs.

    ::param: source is an instance of AthCommand or an object that implements .caller, .player, and .character
    """
    def __init__(self, request):
        self.request = request
        self.messages = list()

    def add(self, target, message):
        self.messages.append((target, message))


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
    category = 'athanor'
    style = 'fallback'
    system_name = 'SYSTEM'
    settings_classes = ()
    load_order = 0
    account_mode = False
    resp_class = AthanorResponse
    cmdsets = ()
    operations = dict()
    mode = None
    django_model = None

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.load_model()
        self.settings = dict()
        self.load_settings()
        self.load_cmdsets()
        self.valid = self.base.valid
        self.load()

    def load_model(self):
        if self.mode and self.django_model:
            kwargs = {self.mode: self.owner}
            self.model, created = self.django_model.objects.get_or_create(**kwargs)

    def accept_request(self, request):
        response = self.respond(request)
        self.process_request(response)
        self.process_response(response)
        return

    def process_request(self, response):
        if response.request.operation not in self.operations:
            response.add(self.owner, "Operation '%s' is not valid for %s" % (response.request.operation, self.__class__.__name__))
            return
        return getattr(self, 'op_%s' % response.request.operation)(response)

    def process_response(self, resp):
        for message in resp.messages:
            if hasattr(message[0], 'ath'): # For now, only gonna worry about messages to Characters and Accounts.
                self.dispatch_message(message)

    def dispatch_message(self, message):
        target, contents = message
        target.ath[self.key].process_message(self.owner, contents)

    def process_message(self, source, contents):
        if 'gmcp' in contents:
            self.gmcp_msg(contents['gmcp'])
        if 'text' in contents:
            self.console_msg(contents['text'], prefix=contents['prefix'])

    def __getitem__(self, item):
        return self.settings[item].value

    def respond(self, request):
        return self.resp_class(request)

    def load_cmdsets(self):
        for cmdset in self.cmdsets:
            self.owner.cmdset.add(cmdset)

    def load_file(self, file):
        return self.base.attributes.get(key=file, category=self.category, default=dict())

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
        self.base.attributes.add(key=file, value=data, category=self.category)

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.save_attribute('settings', save_data)

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

    def console_msg(self, message, error=False, prefix=True):
        if not prefix:
            self.owner.msg(unicode(ANSIString(message)))
            return
        style = self.owner.render[self.style]
        if not style:
            style = self.owner.render.fallback
        if error:
            message = '|rERROR:|n %s' % message
        alert = '|%s-=<|n|%s%s|n|%s>=-|n ' % (style['msg_edge_color'],
                                              style['msg_name_color'],
                                              self.system_name, style['msg_edge_color'])
        send_string = alert + message
        self.owner.msg(unicode(ANSIString(send_string)))

    def gmcp_msg(self, message):
        args = message['args']
        kwargs = message['kwargs']
        self.owner.msg(athanor=(args, kwargs))

    def alert_channel(self):
        pass


class CharacterHandler(__BaseHandler):
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


class AccountHandler(__BaseHandler):
    mode = 'account'
    account_mode = True

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


class ScriptHandler(__BaseHandler):
    mode = 'script'


class SessionHandler(__BaseHandler):
    mode = 'session'

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