from athanor.base.handlers import CharacterHandler


class CharacterOOC(CharacterHandler):
    key = 'ooc'
    style = 'ooc'
    system_name = 'OOC'
    operations = ('send',)

    def op_send(self, resp):
        pass

    def send(self, message):
        pass

    def receive(self, message):
        pass