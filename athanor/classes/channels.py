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

from __future__ import unicode_literals
from evennia import DefaultChannel
from evennia.utils import logger
from evennia.utils.utils import make_iter
from athanor.utils.create import make_speech


class Channel(DefaultChannel):
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
    pass


class AthanorChannel(Channel):
    """
    The AthanorChannel is a nearly complete re-write of the Channel System. It does not rely on
    Msg infrastructure and enables a unified sharing. It accepts the same .msg syntax to ensure
    backwards compatability for external connections.
    """

    def speak(self, speech_obj):
        for entity in self.subscriptions.all():
            try:
                entity.channels.receive(self, speech_obj, emit=False)
            except AttributeError:
                msg = speech_obj.demarkup()
                entity.msg('%s%s' % (self.channel_prefix(msg), msg))

    def emit(self, msg):
        for entity in self.subscriptions.all():
            try:
                entity.channels.receive(self, msg, emit=True)
            except AttributeError:
                entity.msg('%s%s' % (self.channel_prefix(msg), msg))

class PublicChannel(AthanorChannel):

    def __unicode__(self):
        return unicode(self.key)

    def __str__(self):
        return self.key



class RadioChannel(AthanorChannel):

    def init_locks(self):
        lockstring = "control:perm(Wizards);send:all();listen:all()"
        self.locks.add(lockstring)

    def channel_prefix(self, viewer, slot=None):
        try:
            viewer_slot = self.frequency.characters.filter(character=viewer, on=True).first()
            slot_name = viewer_slot.key
            slot_color = viewer_slot.color or 'n'
            display_name = '|%s%s|n' % (slot_color, slot_name)
        except:
            display_name = self.frequency.key
        return '|r-<|n|wRADIO:|n %s|n|r>-|n' % display_name

    def sender_title(self, sender=None, slot=None):
        return slot.title

    def sender_altname(self, sender=None, slot=None):
        return slot.codename


class GroupChannel(AthanorChannel):

    def sender_title(self, sender=None, slot=None):
        title = None
        try:
            options, created = self.group.participants.get_or_create(character=sender)
            if options:
                title = options.title
        except:
            title = None
        return title

    def sender_codename(self, sender=None, slot=None):
        return None

class GroupIC(GroupChannel):

    def init_locks(self, group):
        lockstring = "control:group(##,1);send:gperm(##,ic);listen:gperm(##,ic)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.group
        try:
            personal_color = viewer.settings.get_color_name(group, no_default=True)
        except:
            personal_color = None
        try:
            group_color = group.color
            name = group.key
        except AttributeError:
            name = 'UNKNOWN'
            group_color = 'x'
        color = personal_color or group_color or 'x'
        return '{C<{%s%s{n{C>{n' % (color, name)

class GroupOOC(GroupChannel):

    def init_locks(self, group):
        lockstring = "control:group(##,1);send:gperm(##,ooc);listen:gperm(##,ooc)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.group
        try:
            personal_color = viewer.settings.get_color_name(group, no_default=True)
        except:
            personal_color = None
        try:
            group_color = group.color
            name = group.key
        except AttributeError:
            name = 'UNKNOWN'
            group_color = 'x'
        color = personal_color or group_color or 'x'
        return '{C<{%s%s{n{C-{n{ROOC{n{C>{n' % (color, name)