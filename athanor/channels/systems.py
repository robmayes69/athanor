from evennia import create_channel
from athanor.base.systems import AthanorSystem
from athanor import AthException
from athanor.channels.classes import PublicChannel


class ChannelSystem(AthanorSystem):

    key = 'channel'
    system_name = 'CHANNEL'
    load_order = -997
    settings_data = (
        ('default_lock', "The lockstring that will be applied to all new Public Channels.", 'lockstring', ''),
        ('stafftag_color', "The color for staff tags shown on channels.", 'color', 'r'),
    )

    def load(self):
        self.channels = PublicChannel.objects.filter_family()
        self.name_map = {chan.key.upper(): chan for chan in self.channels}
        self.id_map = {chan.id: chan for chan in self.channels}

    def find(self, session, channel_name):
        pass

    def create(self, session, name, desc=None):
        name = self.valid['channel_name'](session, name)
        channel = create_channel(name, typeclass=PublicChannel, desc=desc)
        self.load()

    def rename(self, session, channel, new_name):
        channel = self.valid['channel'](session, channel)
        new_name = self.valid['channel_name'](session, channel, new_name)

    def lock(self, session, channel, lock_string):
        channel = self.valid['channel'](session, channel)

    def delete(self, session, channel):
        channel = self.valid['channel'](session, channel)

    def send_alert(self, text, source=None, system=None):
        if not system:
            system = self.system_name
        if source:
            msg = '%s: [%s] %s' % (system, source, text)
        else:
            msg = '%s: %s' % (system, text)
        for chan in self['alert_channels']:
            chan.msg(msg, emit=True)