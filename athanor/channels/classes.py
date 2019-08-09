"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

from evennia import DefaultChannel
from athanor import SETTINGS, AthException
from athanor import SYSTEMS
from athanor.modules.core.models import PublicChannelMessage
from athanor.utils.text import partial_match, Speech
from athanor.utils.time import utcnow


class AthanorChannel(DefaultChannel):
    """
    Working methods:
        at_channel_creation() - called once, when the channel is created
        has_connection(player) - check if the given player listens to this channel
        connect(player) - connect player to this channel
        disconnect(player) - disconnect player from channel
        access(access_obj, access_type='listen', default=False) - check the
                    access on this channel (default access_type is listen)
        delete() - delete this channel
        message_transform(msg, emit=False, prefix=True,
                          sender_strings=None, external=False) - called by
                          the comm system and triggers the hooks below
        msg(msgobj, header=None, senders=None, sender_strings=None,
            persistent=None, online=False, emit=False, external=False) - main
                send method, builds and sends a new message to channel.
        tempmsg(msg, header=None, senders=None) - wrapper for sending non-persistent
                messages.
        distribute_message(msg, online=False) - send a message to all
                connected players on channel, optionally sending only
                to players that are currently online (optimized for very large sends)

    Useful hooks:
        channel_prefix(msg, emit=False) - how the channel should be
                  prefixed when returning to user. Returns a string
        format_senders(senders) - should return how to display multiple
                senders to a channel
        pose_transform(msg, sender_string) - should detect if the
                sender is posing, and if so, modify the string
        format_external(msg, senders, emit=False) - format messages sent
                from outside the game, like from IRC
        format_message(msg, emit=False) - format the message body before
                displaying it to the user. 'emit' generally means that the
                message should not be displayed with the sender's name.

        pre_join_channel(joiner) - if returning False, abort join
        post_join_channel(joiner) - called right after successful join
        pre_leave_channel(leaver) - if returning False, abort leave
        post_leave_channel(leaver) - called right after successful leave
        pre_send_message(msg) - runs just before a message is sent to channel
        post_send_message(msg) - called just after message was sent to channel

    """
    settings_data = (

    )
    helper = None

    def at_channel_creation(self):
        if not self.db.titles:
            self.db.titles = dict()
        if not self.db.settings:
            self.db.settings = dict()

    def load_settings(self):
        saved_data = dict(self.attributes.get('settings', dict()))
        self.ndb.settings = dict()
        for setting_def in self.settings_data:
            try:
                new_setting = SETTINGS[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3], saved_data.get(setting_def[0], None))
                self.ndb.settings[new_setting.key] = new_setting
            except Exception as e:
                print(e)
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

    def __getitem__(self, item):
        if not self.ndb.loaded_settings:
            self.load_settings()
        return self.ndb.settings[item].value

    def online_characters(self):
        return set(self.subscriptions.all()).intersection(SYSTEMS['character'].ndb.online_characters)


class PublicChannel(AthanorChannel):
    settings_data = (
        ('titles_enabled', "Allow the use of Channel Titles?", 'boolean', 1),
        ('titles_max_length', "How many characters long can titles be?", 'positive_integer', 80),
        ('color', 'What channel should the color be?', 'color', ''),
    )
    helper = 'channel'

    def emit(self, source, text):
        text = self.systems['character'].render(text)
        for recip in self.online_characters():
            recip.ath[self.helper].receive(channel=self, message=text, source=source)
        PublicChannelMessage.objects.create(channel=self, speaker=source, markup_text=text, date_created=utcnow())

    def speech(self, source, text):
        title = ''
        if self['titles_enabled'] and source:
            title = self.db.titles.get(source, '')[:self['titles_max_length']]
        msg = Speech(speaker=source, speech_text=text, title=title, mode='channel')
        for recip in self.online_characters():
            recip.ath[self.helper].receive(channel=self, message=msg, source=source)
        PublicChannelMessage.objects.create(channel=self, speaker=source, markup_text=msg.log(), date_created=utcnow())

    def msg(self, message, senders=None, online=True, *args, **kwargs):
        self.speech(senders, message)