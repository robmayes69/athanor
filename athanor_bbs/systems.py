from evennia.locks.lockhandler import LockException
from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.utils.text import sanitize_string, partial_match, mxp
from athanor_bbs.models import Board, BoardCategory, Post, PostRead


class BoardManager(AthanorSystem):
    key = 'bbs'
    system_name = 'BBS'
    load_order = -50
    settings_data = (
        ('category_locks', 'Default locks to use for new Board Categories?', 'locks',
         "see:all();create:pperm(Admin);delete:pperm(Admin);admin:pperm(Admin)"),
        ('board_locks', 'Default locks for new Boards?', 'locks', "read:all();post:all();admin:pperm(Admin)"),
    )

    def categories(self):
        return BoardCategory.objects.order_by('key')

    def create_category(self, session, name, abbr=''):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied!")
        name = self.valid['dbname'](name, thing_name='BBS Category')
        if BoardCategory.objects.filter(key__iexact=name).exists():
            raise AthException("Names must be unique!")
        if abbr != '':
            abbr = self.valid['dbname'](abbr, thing_name='BBS Category Prefix')
        if ' ' in abbr:
            raise AthException("Spaces are not allowed in BBS Category Prefixes")
        if len(abbr) > 5:
            raise AthException("BBS Category Prefixes may be no more than 5 characters long.")
        if BoardCategory.objects.filter(abbr__iexact=abbr).exists():
            raise AthException("BBS Category Prefixes must be unique!")
        new_cat, created = BoardCategory.objects.get_or_create(key=name, abbr=abbr)
        self.alert(f"Created BBS Category: {abbr} - {name}", source=session)
        return new_cat

    def find_category(self, session, category=None):
        if not category:
            raise AthException("Must enter a category name!")
        candidates = BoardCategory.objects.all()
        if not session.ath['core'].is_superuser():
            candidates = [c for c in candidates if c.locks.check('see', session.account)]
        if not candidates:
            raise AthException("No Board Categories visible!")
        found = partial_match(category, candidates)
        if not found:
            raise AthException(f"Category '{category}' not found!")
        return found

    def rename_category(self, session, category=None, new_name=None, new_abbr=None):
        if not category:
            raise AthException("Must enter a category name!")
        if not new_name:
            raise AthException("Must enter a new name!")
        if not new_abbr:
            raise AthException("Must enter a new abbr!")
        category = self.find_category(session, category)
        if not category.locks.check('admin', session.account):
            raise AthException("Permission denied!")
        new_name = self.valid['dbname'](new_name, thing_name='BBS Category')
        if BoardCategory.objects.filter(key__iexact=new_name).exclude(id=category).exists():
            raise AthException("Names must be unique!")
        if new_abbr != '':
            new_abbr = self.valid['dbname'](new_abbr, thing_name='BBS Prefix')
        if ' ' in new_abbr:
            raise AthException("BBS Prefixes may not contain spaces.")
        if len(new_abbr) > 5:
            raise AthException("BBS Prefixes may be no more than 5 characters long.")
        if BoardCategory.objects.filter(abbr__iexact=new_abbr).exclude(id=category).exists():
            raise AthException("BBS Prefixes must be unique!")
        old_name = category.key
        old_abbr = category.abbr
        category.key = new_name
        category.abbr = new_abbr
        category.save(update_fields=['key', 'abbr'])
        self.alert(f"BBS Category '{old_abbr} - {old_name}' renamed to: '{new_abbr} - {new_name}'", source=session)

    def delete_category(self, session, category, abbr=None):
        category_found = self.find_category(session, category)
        if not session.account.is_superuser:
            raise AthException("Permission denied! Superuser only!")
        if not category == category_found.key:
            raise AthException("Names must be exact for verification.")
        if not abbr:
            raise AthException("Must provide prefix for verification!")
        if not abbr == category_found.abbr:
            raise AthException("Must provide exact prefix for verification!")
        self.alert(f"|rDELETED|n BBS Category '{category_found.abbr} - {category_found.key}'", source=session)
        category_found.delete()

    def lock_category(self, session, category, new_locks):
        category = self.find_category(session, category)
        if not session.account.is_superuser:
            raise AthException("Permission denied! Superuser only!")
        new_locks = self.valid['locks'](new_locks, thing_name='BBS Category Locks', 
                                        options=['see', 'create', 'delete', 'admin'])
        try:
            category.locks.add(new_locks)
            category.save(update_fields=['lock_storage'])
        except LockException as e:
            raise AthException(str(e))
        self.alert(f"BBS Category '{category.abbr} - {category.key}' lock changed to: {new_locks}", source=session)

    def boards(self):
        return Board.objects.order_by('category__key', 'order')

    def usable_boards(self, session, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(session, mode=mode, checkadmin=check_admin)
                and board.category.locks.check('see', session)]

    def visible_boards(self, session, check_admin=True):
        return [board for board in self.usable_boards(session, mode='read', check_admin=check_admin)
                if session not in board.ignore_list.all() and board.category.locks.check('see', session)]

    def find_board(self, session, find_name=None, visible_only=True):
        if not find_name:
            raise AthException("No board entered to find!")
        if visible_only:
            boards = self.visible_boards(session)
        else:
            boards = self.usable_boards(session)
        if not boards:
            raise AthException("No applicable boards.")

        board_dict = {board.alias.upper(): board for board in boards}

        if find_name.upper() in board_dict:
            return board_dict[find_name.upper()]
        raise AthException("Board '%s' not found!" % find_name)

    def list_boards(self, session):
        message = list()
        message.append(session.render.header(self.name))
        bbtable = session.render.make_table(["ID", "RPA", "Name", "Locks", "On"], width=[4, 4, 25, 43, 4])
        for board in self.usable_boards(session=session):
            if session in board.ignore_list.all():
                member = "No"
            else:
                member = "Yes"
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.alias), board.display_permissions(session),
                            mxp(board, "+bbread %s" % board.alias), board.lock_storage, member)
        message.append(bbtable)
        message.append(session.render.footer())
        return '\n'.join(str(line) for line in message)

    def create_board(self, session, category, name=None, order=None):
        category = self.find_category(session, category)
        if not category.locks.check(session.account, 'create'):
            raise AthException("Permission denied!")
        name = self.valid['dbname'](name, thing_name='BBS Board')
        if category.boards.filter(key__iexact=name).exists():
            raise AthException("Names must be unique!")
        if not order:
            order = max([board.order for board in category.boards.all()]) + 1
        else:
            order = int(order)
            if category.boards.filter(order=order).exists():
                raise AthException("Orders must be unique per group!")
        board = category.objects.create(key=name, order=order, lock_storage=self['board_locks'])
        board.save()
        self.alert(f"BBS Board Created: ({category}) - {board.alias}: {board.key}", source=session)
        return board

    def delete_board(self, session, name=None):
        board = self.find_board(name, session)
        if not name == board.key:
            raise AthException("Entered name must match board name exactly!")
        if not board.category.locks.check('delete', session.account):
            raise AthException("Permission denied!")
        self.alert(f"Deleted BBS Board ({board.category.key}) - {board.alias}: {board.key}", source=session)
        board.delete()

    def rename_board(self, session, name=None, new_name=None):
        board = self.find_board(session, name)
        if not board.category.locks.check('admin', session.account):
            raise AthException("Permission denied!")
        new_name = self.valid['dbname'](new_name, thing_name='BBS Board')
        if board.key == new_name:
            raise AthException("No point... names are the same.")
        if board.category.boards.exclude(id=board).filter(key__iexact=new_name).exists():
            raise AthException("Names must be unique!")
        old_name = board.key
        board.key = new_name
        board.save(update_fields=['key'])
        self.alert(f"Renamed BBS Board ({board.category.key}) - {board.alias}: {old_name} to: {board.key}",
                   source=session)

    def order_board(self, session, name=None, order=None):
        board = self.find_board(session, name)
        if not board.category.locks.check('admin', session.account):
            raise AthException("Permission denied!")
        if not order:
            raise AthException("No order entered!")
        order = self.valid['positive_integer'](order, thing_name='BBS Board Order')
        if board.order == order:
            raise AthException("No point to this operation.")
        if board.category.boards.exclude(id=board.id).filter(order=order).exists():
            raise AthException("Orders must be unique!")
        old_order = board.order
        board.order = order
        board.save(update_fields=['order'])

    def lock_board(self, session, name=None, lock=None):
        board = self.find_board(session, name)
        if not board.category.locks.check('admin', session.account):
            raise AthException("Permission denied!")
        if not lock:
            raise AthException("Must enter a lockstring.")
        lockstring = self.valid['locks'](lock, thing_name='BBS Board Lock')
        try:
            board.locks.add(lockstring)
            board.save(update_fields=['lock_storage'])
        except LockException as e:
            raise AthException(str(e))
        self.alert(f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lockstring}",
                   source=session)