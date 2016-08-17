from __future__ import unicode_literals
from evennia import PlayerDB
from evennia.utils.create import create_channel
from typeclasses.channels import PublicChannel
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string

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
        message.append(header("Public Channels"))
        channel_table = make_table("Sta", "Name", "Aliases", "Perms", "Members", "Description", width=[5, 22, 8, 7, 8, 28], viewer=self.character)
        for chan in channels:
            channel_table.add_row('##', chan.key, 'test', 'test2', '0', 'test3')
        message.append(channel_table)
        message.append(header(viewer=self.character))
        self.msg("\n".join([unicode(line) for line in message]))