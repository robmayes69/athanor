from __future__ import unicode_literals
from evennia.locks.lockhandler import LockException
from athanor.classes.scripts import AthanorScript
from athanor.utils.text import sanitize_string, partial_match, mxp, sanitize_board_name
from athanor.bbs.models import Board


class BoardManager(AthanorScript):

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

    def list_boards(self, viewer):
        message = list()
        message.append(viewer.render.header(self.name))
        bbtable = viewer.render.make_table(["ID", "RPA", "Name", "Locks", "On"], width=[4, 4, 25, 43, 4])
        for board in self.usable_boards(checker=viewer):
            if viewer in board.ignore_list.all():
                member = "No"
            else:
                member = "Yes"
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.order), board.display_permissions(viewer),
                            mxp(board, "+bbread %s" % board.order), board.lock_storage, member)
        message.append(bbtable)
        message.append(viewer.render.footer())
        return '\n'.join(unicode(line) for line in message)

    def create_board(self, enactor, name=None, group=None, order=None):
        name = sanitize_board_name(name)
        if group:
            group.check_permission_error(enactor, 'bbadmin')
        else:
            if not enactor.accountsub.is_admin():
                raise ValueError("Permission denied!")
        if Board.objects.filter(key__iexact=name, group=group).exist():
            raise ValueError("Names must be unique!")
        if not order:
            order = max([board.order for board in self.boards() if board.group == group]) + 1
        else:
            order = int(order)
            if Board.objects.filter(group=group,order=order).count():
                raise ValueError("Orders must be unique per group!")
        board = self.boards.create(key=name, group=group, order=order)
        board.init_locks()
        return board

    def delete_board(self, enactor, name, verify):
        name = sanitize_board_name(name)
        board = self.find_board(name, enactor, visible_only=False)
        if board.group:
            board.group.check_permission_error(enactor, 'bbadmin')
        else:
            if not enactor.accountsub.is_admin():
                raise ValueError("Permission denied!")
        if not sanitize_string(verify).lower() == board.key.lower():
            raise ValueError("Verify field does not match Board name!")
        board.delete()
        
    def rename_board(self, enactor, name=None, new_name=None):
        name = sanitize_board_name(name)
        board = self.find_board(name, enactor, visible_only=False)
        if board.group:
            board.group.check_permission_error(enactor, 'bbadmin')
        else:
            if not enactor.accountsub.is_admin():
                raise ValueError("Permission denied!")
        new_name = sanitize_board_name(new_name)
        if name == new_name:
            raise ValueError("No point... names are the same.")
        if Board.objects.exclude(id=board.id).filter(key__iexact=new_name, group=board.group).exist():
            raise ValueError("Names must be unique!")
        old_name = board.key
        board.key = new_name
        board.save(update_fields=['key'])

    def order_board(self, enactor, name=None, order=None):
        name = sanitize_board_name(name)
        board = self.find_board(name, enactor, visible_only=False)
        if board.group:
            board.group.check_permission_error(enactor, 'bbadmin')
        else:
            if not enactor.accountsub.is_admin():
                raise ValueError("Permission denied!")
        if not order:
            raise ValueError("No order entered!")
        try:
            order = int(order)
        except:
            raise ValueError("Entered order must be an integer!")
        if board.order == order:
            raise ValueError("No point to this operation.")
        if Board.objects.exclude(id=board.id).filter(group=board.group, order=order).exist():
            raise ValueError("Orders must be unique!")
        old_order = board.order
        board.order = order
        board.save(update_fields=['order'])
        
    def lock_board(self, enactor, name=None, lock=None):
        name = sanitize_board_name(name)
        board = self.find_board(name, enactor, visible_only=False)
        if board.group:
            board.group.check_permission_error(enactor, 'bbadmin')
        else:
            if not enactor.accountsub.is_admin():
                raise ValueError("Permission denied!")
        
        if not lock:
            raise ValueError("Must enter a lockstring.")

        for locksetting in lock.split(';'):
            access_type, lockfunc = locksetting.split(':', 1)
            if not access_type:
                raise ValueError("Must enter an access type: read, write, or admin.")
            accmatch = partial_match(access_type, ['read', 'write', 'admin'])
            if not accmatch:
                raise ValueError("Access type must be read, write, or admin.")
            if not lockfunc:
                raise ValueError("Lock func not entered.")
            ok = False
            try:
                ok = board.locks.add(lock)
                board.save(update_fields=['lock_storage'])
            except LockException as e:
                raise ValueError(unicode(e))


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