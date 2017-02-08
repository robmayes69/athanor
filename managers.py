from athanor.classes.scripts import WhoManager
from evennia import create_script

class Manager(object):
    id = 0

    def __init__(self, id):
        self.id = id
        self.who = self.get_who()

    def get_who(self):
        found = WhoManager.objects.filter_family(db_key='Who Manager').first()
        if found:
            return found
        return create_script(WhoManager, persistent=False, obj=None)


ALL_MANAGERS = Manager(1)