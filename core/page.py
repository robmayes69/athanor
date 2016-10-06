from __future__ import unicode_literals

from athanor.utils.create import make_speech
from athanor.commands.command import AthCommand

class CmdPage(AthCommand):
    key = 'page'
    aliases = ['tell', 'reply']

    def main(self):
        if self.cmdstring.lower() == 'reply':
            self.reply()
            return
        if not self.args:
            self.error("What will you say?")
        if '=' in self.args:
            if not self.lsargs:
                self.error("Who will you send to?")
                return
            if not self.lsargs:
                self.error("What will you say?")
                return
            targets = list()
            for name in self.lhslist:
                try:
                    found = self.character.search_character(name)
                except ValueError as err:
                    self.error(str(err))
                targets.append(name)
            text = self.rsargs
        else:
            targets = self.character.page.last_to
            text = self.args

        online = [char for char in targets if hasattr(char, 'player')]

        for char in targets:
            if char not in online:
                self.error("%s is offline." % char)

        if not online:
            self.error("Nobody is listening...")

        online.append(self.character)
        online = set(online)

        speech = make_speech(self.character, text, mode='page')
        self.character.page.send(online, speech)

    def reply(self):
        if not self.args:
            self.error("What will you say?")
            return
        targets = self.character.page.last_from
        online = [char for char in targets if hasattr(char, 'player')]
        if not online:
            self.error("Nobody is listening...")
            return

        speech = make_speech(self.character, self.args, mode='page')
        online.append(self.character)
        online = set(online)
        self.character.page.send(online, speech)