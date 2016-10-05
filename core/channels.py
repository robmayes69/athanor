from __future__ import unicode_literals
from evennia import PlayerDB
from evennia.utils.create import create_channel
from athanor.classes.channels import PublicChannel
from athanor.commands.command import AthCommand
from athanor.utils.time import utcnow
from athanor.utils.text import sanitize_string

class CmdChannels(AthCommand):
    """
    Used to list all channels available to you.
    """
    key = "@channels"
    aliases = ['comlist', 'channellist', 'all channels', 'channels', '@clist', 'chanlist']
    locks = 'cmd:all()'

    def func(self):
        channels = PublicChannel.objects.filter_family().order_by('db_key')
        message = list()
        message.append(self.player.render.header("Public Channels"))
        channel_table = self.player.render.make_table(["Sta", "Name", "Aliases", "Perms", "Members", "Description"],
                                                       width=[5, 22, 8, 7, 8, 28])
        for chan in channels:
            channel_table.add_row('##', chan.key, 'test', 'test2', '0', 'test3')
        message.append(channel_table)
        message.append(self.player.render.footer())
        self.msg("\n".join([unicode(line) for line in message]))