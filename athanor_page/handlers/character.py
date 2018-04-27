

class CharacterPage(__CharacterManager):
    style = 'page'
    system_name = 'PAGE'
    key = 'page'

    def __init__(self, owner):
        super(CharacterPage, self).__init__(owner)
        self.last_to = list()
        self.reply_to = list()

    def send(self, targets, msg):
        targetnames = ', '.join([str(tar) for tar in targets])
        targets.discard(self.owner)
        self.last_to = targets
        for target in targets:
            target.page.receive(targets, msg, source=self.owner)
        outpage = self.owner.player_config['outpage_color']
        self.owner.msg('|%sPAGE|n (%s)|%s:|n %s' % (outpage, targetnames, outpage, msg.render(viewer=self.owner)))


    def receive(self, recipients, msg, source=None):
        color = self.owner.player_config['page_color']
        others = set(recipients)
        others.discard(self.owner)
        othernames = ', '.join([str(oth) for oth in others])
        if othernames:
            extra = ', to %s' % othernames
        else:
            extra = ''
        self.owner.msg('|%sPAGE (from %s%s):|n %s' % (color, source, extra, msg.render(viewer=self.owner)))
        reply = set(recipients)
        reply.add(source)
        reply.discard(self.owner)
        self.reply_to = reply