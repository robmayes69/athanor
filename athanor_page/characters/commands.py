from athanor.base.commands import AthCommand
from athanor.utils.create import make_speech
from athanor import AthException

class CmdPage(AthCommand):
    key = 'page'
    aliases = ['tell', 'reply']
    player_switches = ['reply',]

    def _main(self):
        if self.cmdstring.lower() == 'reply':
            self.switch_reply()
            return
        if not self.args:
            raise AthException("What will you say?")
        if '=' in self.args:
            if not self.lhs:
                raise AthException("Who will you send to?")
            if not self.lhs:
                raise AthException("What will you say?")
            targets = set()
            for name in self.lhslist:
                found = self.character.search_character(name)
                targets.add(found)
            text = self.rhs
        else:
            targets = self.character.page.last_to
            text = self.args

        online = set([char for char in targets if hasattr(char, 'account')])
        offline = targets - online

        for char in offline:
            self.error("%s is offline." % char)

        if not online:
            self.error("Nobody is listening...")

        speech = make_speech(self.character, text, mode='page', targets=online)
        self.character.ath['page'].send(online, speech)

    def switch_reply(self):
        if not self.args:
            raise AthException("What will you say?")
        targets = self.character.page.last_from
        online = set([char for char in targets if hasattr(char, 'player')])
        if not online:
            raise AthException("Nobody is listening...")

        speech = make_speech(self.character, self.args, mode='page', targets=online)
        online = set(online)
        self.character.ath['page'].send(online, speech)