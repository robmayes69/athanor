

class CharacterChannel(__CharacterManager):

    def __init__(self, owner):
        super(CharacterChannel, self).__init__(owner)
        self.gagging = list()
        self.monitor = False

    def receive(self, channel, speech, emit=False):
        if channel in self.gagging:
            return
        if not hasattr(self.owner, 'player'):
            return
        prefix = self.prefix(channel)
        if emit:
            self.owner.msg('%s %s' % (prefix, speech))
            return
        if self.monitor:
            render = speech.monitor_display(self.owner)
        else:
            render = speech.render(self.owner)
        self.owner.msg('%s %s' % (prefix, render))

    def color_name(self, channel):
        color = self.owner.player.colors.channels.get(channel, None)
        if not color:
            color = channel.db.color
        if not color:
            color = 'n'
        return '|%s%s|n' % (color, channel.key)

    def prefix(self, channel):
        return '<%s>' % self.color_name(channel)

    def status(self, channel):
        if not channel.has_connection(self.owner):
            return 'Off'
        if channel in self.gagging:
            return 'Gag'
        return 'On'

    def visible(self):
        channels = PublicChannel.objects.all().order_by('db_key')
        return [chan for chan in channels if chan.locks.check(self.owner, 'listen')]