from athanor.classes.scripts import AthanorScript

class AthanorManager(AthanorScript):

    def at_script_creation(self):
        self.key = 'Athanor Manager'
        self.desc = 'Handles Athanor system settings.'
        self.persistent = False


class WhoManager(AthanorScript):

    def at_script_creation(self):
        self.ndb.characters = list()
        self.key = 'Who Manager'
        self.desc = 'Maintains the Who List for webclients.'
        self.interval = 30

    def at_start(self):
        from athanor.utils.online import characters as _char
        self.ndb.characters = _char()

    def add(self, character):
        if character in self.ndb.characters:
            return
        self.ndb.characters.append(character)

    def rem(self, character):
        if character not in self.ndb.characters:
            return
        self.ndb.characters.remove(character)

    def visible_characters(self, character):
        return [chr for chr in self.ndb.characters if character.time.can_see(chr)]