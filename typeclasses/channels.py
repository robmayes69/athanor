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
from evennia.utils import logger
from evennia.utils.utils import make_iter
from commands.library import Speech

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

    def msg(self, msgobj, header=None, senders=None, sender_strings=None,
            persistent=False, online=False, emit=False, external=False, slot=None):
        """
        Send the given message to all players connected to channel. Note that
        no permission-checking is done here; it is assumed to have been
        done before calling this method. The optional keywords are not used if
        persistent is False.

        Args:
            msgobj (Msg, TempMsg or str): If a Msg/TempMsg, the remaining
                keywords will be ignored (since the Msg/TempMsg object already
                has all the data). If a string, this will either be sent as-is
                (if persistent=False) or it will be used together with `header`
                and `senders` keywords to create a Msg instance on the fly.
            header (str, optional): A header for building the message.
            senders (Object, Player or list, optional): Optional if persistent=False, used
                to build senders for the message.
            sender_strings (list, optional): Name strings of senders. Used for external
                connections where the sender is not a player or object.
                When this is defined, external will be assumed.
            persistent (bool, optional): Ignored if msgobj is a Msg or TempMsg.
                If True, a Msg will be created, using header and senders
                keywords. If False, other keywords will be ignored.
            online (bool, optional) - If this is set true, only messages people who are
                online. Otherwise, messages all players connected. This can
                make things faster, but may not trigger listeners on players
                that are offline.
            emit (bool, optional) - Signals to the message formatter that this message is
                not to be directly associated with a name.
            external (bool, optional): Treat this message as being
                agnostic of its sender.

        Returns:
            success (bool): Returns `True` if message sending was
                successful, `False` otherwise.

        """
        if senders:
            senders = make_iter(senders)
        else:
            senders = []
            emit = True

        self.distribute_message(msgobj, senders=senders, sender_strings=sender_strings, emit=emit, external=external,
                                online=online, slot=None)
        self.post_send_message(msgobj)
        return True


    def distribute_message(self, msg, senders=None, sender_strings=None, emit=False, external=False, online=False,
                           slot=None):
        """
        Method for grabbing all listeners that a message should be
        sent to on this channel, and sending them a message.

        msg (str): Message to distribute.
        online (bool): Only send to receivers who are actually online
            (not currently used):

        """
        # get all players connected to this channel and send to them
        if senders:
            sender = senders[0]
        else:
            sender = None
        title = self.sender_title(sender, slot)
        if sender_strings:
            alt_name = sender_strings[0]
        else:
            alt_name = None
        codename = self.sender_codename(sender, slot)
        speech = Speech(sender, msg, alternate_name=alt_name, title=title, codename=codename)

        for entity in self.subscriptions.all():
            try:
                # note our addition of the from_channel keyword here. This could be checked
                # by a custom player.msg() to treat channel-receives differently.
                display_prefix = self.channel_prefix(entity)
                if self.viewer_monitor(entity):
                    display_main = speech.monitor_display()
                else:
                    display_main = unicode(speech)
                message = display_prefix + display_main
                entity.msg(str(message), from_obj=senders, from_channel=self.id)
            except AttributeError as e:
                logger.log_trace("%s\nCannot send msg to '%s'." % (e, entity))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        return '<%s> ' % self.key

    def sender_title(self, sender=None, slot=None):
        pass

    def sender_codename(self, sender=None, slot=None):
        pass

    def viewer_monitor(self, viewer):
        pass

class PublicChannel(AthanorChannel):

    def at_channel_creation(self):
        super(Channel, self).at_channel_creation()
        self.db.titles = dict()
        self.db.codenames = dict()
        self.db.settings = dict()

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        color = None
        try:
            color = viewer.settings.get_color_name(self, no_default=True)
        except AttributeError:
            pass
        if not color:
            color = self.db.settings.get('color', 'n')
        return '<{%s%s{n> ' % (color, self.key)

    @property
    def color_name(self):
        color = self.db.settings.get('color', 'n')
        return '{%s%s{n' % (color, self.key)

    def sender_title(self, sender=None, slot=None):
        return self.db.titles.get(sender, None)

    def sender_codename(self, sender=None, slot=None):
        return self.db.codenames.get(sender, None)

class RadioChannel(AthanorChannel):
    pass

class GroupChannel(AthanorChannel):

    def sender_title(self, sender=None, slot=None):
        title = None
        try:
            options = sender.group_option.filter(group=self.db.group).first()
            if options:
                title = options.title
        except:
            title = None
        return title

    def sender_codename(self, sender=None, slot=None):
        return None

class GroupIC(GroupChannel):

    def get_group(self):
        return self.group_ic.all().first()

    def init_locks(self):
        group = self.get_group()
        lockstring = "control:perm(Wizards) or group(##,1);send:perm(Wizards) or gperm(##,ic);listen:perm(Wizards) or gperm(##,ic)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.get_group()
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
        return '{C<{%s%s{n{C>{n ' % (color, name)

class GroupOOC(GroupChannel):

    def init_locks(self):
        group = self.get_group()
        lockstring = "control:perm(Wizards) or group(##,1);send:perm(Wizards) or gperm(##,ooc);listen:perm(Wizards) or gperm(##,ooc)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def get_group(self):
        return self.group_ooc.all().first()

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.get_group()
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
        return '{C<{%s%s{n{C-{n{ROOC{n{C>{n ' % (color, name)