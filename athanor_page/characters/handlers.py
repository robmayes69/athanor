from athanor.base.handlers import CharacterHandler


class CharacterPage(CharacterHandler):
    key = 'page'
    style = 'page'
    system_name = 'PAGE'
    cmdsets = ('athanor_page.characters.cmdsets.PageCmdSet',)

    def load(self):
        self.last_to = list()
        self.reply_to = list()
        self.colors = self.owner.render['page']

    def send(self, targets, msg):
        targetnames = ', '.join([str(tar) for tar in targets])
        targets.discard(self.owner)
        self.last_to = targets
        for target in targets:
            target.page.receive(targets, msg, source=self.owner)
        outpage = self.colors['outpage_color']
        self.owner.msg('|%sPAGE|n (%s)|%s:|n %s' % (outpage, targetnames, outpage, msg.render(viewer=self.owner)))


    def receive(self, recipients, msg, source=None):
        color = self.colors['page_color']
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