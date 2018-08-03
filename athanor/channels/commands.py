import evennia

from athanor.classes.channels import PublicChannel
from athanor.core.command import AthCommand
from athanor.utils.create import make_speech


class CmdChannels(AthCommand):
    """
    General command used to administrate the channel system.

    Usage:
        @channel - List all channels.

    Switches:
        /on or /off <channel> - turn reception of a channel on or off.
        /gag or /ungag <channel> - temporarily stop receiving messages from a channel, resets on logoff.

    """
    key = "@channel"
    system_name = 'CHANNEL'
    aliases = ['comlist', 'channels', '@clist', 'chanlist', '@channels']
    locks = 'cmd:all()'
    player_switches = ['on', 'off', 'gag', 'ungag']
    admin_switches = ['edit', 'create']

    def switch_edit(self):
        self.menu(self.character, 'athanor.core.menus.channel')

    def main(self):
        channels = PublicChannel.objects.filter_family().order_by('db_key')
        message = list()
        permissions = ['control', 'send', 'listen']
        message.append(self.player.render.header("Public Channels"))
        online = set(self.character.who.visible_characters(self.character))
        channel_table = self.player.render.make_table(["Sta", "Name", "Aliases", "Perms", "Members", "Description"],
                                                       width=[5, 22, 8, 7, 8, 28])
        for chan in channels:
            perms = [perm[0].upper() for perm in permissions if chan.access(self.character, perm)]
            status = self.character.channels.status(chan)
            members = set(chan.subscriptions.all())
            visible = len(members.intersection(online))
            channel_table.add_row(status, chan.key, ', '.join(chan.aliases.all()), ' '.join(perms),
                                  '%s/%s' % (visible, len(members)), chan.db.desc)
        message.append(channel_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)


class CmdSend(AthCommand):
    key = evennia.syscmdkeys.CMD_CHANNEL
    system_name = 'CHANNEL'

    def parse(self):
        channelname, msg = self.args.split(':', 1)
        self.args = channelname.strip(), msg.strip()

    def func(self):
        """
        Create a new message and send it to channel, using
        the already formatted input.
        """
        caller = self.caller
        self.character = self.caller
        self.player = self.caller.player
        channelkey, msg = self.args
        if not msg:
            self.sys_msg("Say what?")
            return
        channel = evennia.ChannelDB.objects.get_channel(channelkey)
        if not channel:
            self.error("Channel '%s' not found." % channelkey)
            return
        if not channel.has_connection(caller):
            string = "You are not connected to channel '%s'."
            self.error(string % channelkey)
            return
        if not channel.access(caller, 'send'):
            string = "You are not permitted to send to channel '%s'."
            self.error(string % channelkey)
            return
        speech = make_speech(self.character, msg, mode='channel')
        channel.speak(speech)