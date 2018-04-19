
from athanor.core.scripts import WhoManager
from athanor.groups.scripts import GroupManager
from athanor.bbs.scripts import BoardManager
from evennia import create_script

class Manager(object):
    id = 0

    def __init__(self, id):
        self.id = id
        self.who = self.get_who()
        self.group = self.get_group()
        self.board = self.get_board()

    def get_who(self):
        found = WhoManager.objects.filter_family(db_key='Who Manager').first()
        if found:
            return found
        return create_script(WhoManager, persistent=False, obj=None)

    def get_group(self):
        found = GroupManager.objects.filter_family(db_key='Group Manager').first()
        if found:
            return found
        return create_script(GroupManager, persistent=False, obj=None)

    def get_board(self):
        found = BoardManager.objects.filter_family(db_key='BBS Manager').first()
        if found:
            return found
        return create_script(BoardManager, persistent=False, obj=None)

ALL_MANAGERS = Manager(1)