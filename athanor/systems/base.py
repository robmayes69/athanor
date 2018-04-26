from athanor.classes.scripts import AthanorScript
from athanor.utils.text import partial_match
from athanor.handlers.base import AthanorResponse


class SystemScript(AthanorScript):
    settings_classes = tuple()
    category = 'athanor'
    key = 'base'
    system_name = 'SYSTEM'
    django_model = None
    operations = ()
    resp_class = AthanorResponse
    interval = 60
    repeats = 0

    def at_start(self):
        # Most systems will implement their own Settings.
        self.settings = dict()
        self.load_settings()

        # And some will need Django Save files!
        if self.django_model:
            self.model, created = self.django_model.objects.get_or_create(script=self)

        # We'll probably be using this a lot.
        import athanor
        self.systems = athanor.SYSTEMS

        # Call easy-extensible loading process.
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        return self.settings[item].value

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

    def respond(self, request):
        return self.resp_class(request)

    def load_file(self, file):
        return self.attributes.get(key=file, category=self.category, default=dict())

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

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.save_attribute('settings', save_data)

    def save_attribute(self, file, data):
        self.attributes.add(key=file, value=data, category=self.category)

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
