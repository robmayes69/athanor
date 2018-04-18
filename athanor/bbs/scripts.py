from __future__ import unicode_literals
from athanor.classes.scripts import AthanorScript
from athanor.utils.text import sanitize_string, partial_match, mxp
from athanor.bbs.models import Board


def sanitize_board_name(name):
    name = sanitize_string(name)
    if not name:
        raise ValueError("Board names must not be empty!")
    for char in ['/','|','=']:
        if char in name:
            raise ValueError("%s is not allowed in Board names!" % char)
    return name


class BBSManager(AthanorScript):

    def at_script_creation(self):
        self.key = "BBS Manager"
        self.desc = "Organizes BBS"

    def boards(self):
        return Board.objects.order_by('group__key', 'order')

    def usable_boards(self, checker, mode='read', checkadmin=True):
        return [board for board in self.boards() if board.check_permission(checker, mode=mode, checkadmin=checkadmin)]

    def visible_boards(self, checker, checkadmin=True):
        return [board for board in self.usable_boards(checker, mode='read', checkadmin=checkadmin) if checker not in board.ignore_list.all()]

    def find_board(self, find_name=None, checker=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if checker:
            if visible_only:
                boards = self.visible_boards(checker)
            else:
                boards = self.usable_boards(checker)
        else:
            boards = self.boards()
        if not boards:
            raise ValueError("No applicable boards.")

        board_dict = {board.key.upper(): board for board in boards}

        if find_name.upper() in board_dict:
            return board_dict[find_name.upper()]
        raise ValueError("Board '%s' not found!" % find_name)

    def boards_list(self, checker, viewer):
        message = list()
        message.append(viewer.player.render.header(self.name))
        bbtable = viewer.player.render.make_table(["ID", "RPA", "Name", "Locks", "On"], width=[4, 4, 25, 43, 4])
        for board in self.usable_boards(checker=checker):
            if checker in board.ignore_list.all():
                member = "No"
            else:
                member = "Yes"
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.order), board.display_permissions(checker),
                            mxp(board, "+bbread %s" % board.order), board.lock_storage, member)
        message.append(bbtable)
        message.append(viewer.account.render.footer())
        return '\n'.join(unicode(line) for line in message)

    def create_board(self, name=None, group=None, order=None):
        name = sanitize_board_name(name)
        if not order:
            order = max([board.order for board in self.boards() if board.group == group]) + 1
        else:
            if Board.objects.filter(group=group,order=order).count():
                raise ValueError("Orders must be unique per group!")
        board = self.boards.create(key=name, group=group, order=order)
        board.init_locks()
        return board

    def delete_board(self, enactor, name, verify):
        name = sanitize_board_name(name)
        board = self.find_board(name, enactor, visible_only=False)
        if not board.check_permission(enactor, mode='admin'):
            raise ValueError("Permission Denied.")
        if not sanitize_string(verify).lower() == board.key.lower():
            raise ValueError("Verify field does not match Board name!")
        board.delete()

    def display_boards(self, checker, viewer):
        message = list()
        message.append(viewer.render.header(self.name))
        bbtable = viewer.render.make_table(["ID", "RPA", "Name", "Last Post", "#", "U"], width=[4, 4, 37, 25, 5, 5])
        for board in self.visible_boards(checker=checker):
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.order),
                            board.display_permissions(checker), mxp(board, "+bbread %s" % board.order),
                            board.last_post(checker), board.posts.all().count(),
                            board.posts.exclude(read=viewer).count())
        message.append(bbtable)
        message.append(viewer.render.footer())
        return '\n'.join(unicode(line) for line in message)