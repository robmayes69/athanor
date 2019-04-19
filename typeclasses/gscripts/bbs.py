import re
from evennia.locks.lockhandler import LockException
from typeclasses.scripts import GlobalScript
from world.utils.text import partial_match
from world.utils.time import utcnow
from world.models import Board, BoardCategory
from evennia.utils.validatorfuncs import simple_name

_RE_PRE = re.compile(r"^[a-zA-Z]{1,3}$")


class BoardManager(GlobalScript):
    system_name = 'BBS'
    option_dict = {
        'category_locks': ('Default locks to use for new Board Categories?', 'Lock',
                           "see:all();create:pperm(Admin);delete:pperm(Admin);admin:pperm(Admin)"),
        'board_locks': ('Default locks for new Boards?', 'Lock', "read:all();post:all();admin:pperm(Admin)"),
    }

    def categories(self):
        return BoardCategory.objects.order_by('key')

    def visible_categories(self, account):
        return [cat for cat in self.categories() if cat.locks.check(account, 'see')]

    def create_category(self, account, name, abbr=None):
        if not abbr:
            abbr = ''
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        name = simple_name(name, option_key='BBS Category')
        if BoardCategory.objects.filter(key__iexact=name).exists():
            raise ValueError("Names must be unique!")
        if not _RE_PRE.match(abbr):
            raise ValueError("Prefixes must be 0-3 alphanumeric characters.")
        if BoardCategory.objects.filter(abbr__iexact=abbr).exists():
            raise ValueError("BBS Category Prefixes must be unique!")
        new_cat, created = BoardCategory.objects.get_or_create(key=name, abbr=abbr)
        announce = f"Created BBS Category: {abbr} - {name}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        return new_cat

    def find_category(self, account, category=None):
        if not category:
            raise ValueError("Must enter a category name!")
        candidates = BoardCategory.objects.all()
        if not account.is_superuser:
            candidates = [c for c in candidates if c.locks.check('see', account)]
        if not candidates:
            raise ValueError("No Board Categories visible!")
        found = partial_match(category, candidates)
        if not found:
            raise ValueError(f"Category '{category}' not found!")
        return found

    def rename_category(self, account, category=None, new_name=None):
        if not category:
            raise ValueError("Must enter a category name!")
        if not new_name:
            raise ValueError("Must enter a new name!")
        category = self.find_category(account, category)
        if not category.locks.check(account, 'admin'):
            raise ValueError("Permission denied!")
        new_name = simple_name(new_name, option_key='BBS Category')
        if BoardCategory.objects.filter(key__iexact=new_name).exclude(id=category.id).exists():
            raise ValueError("Names must be unique!")
        old_name = category.key
        old_abbr = category.abbr
        category.key = new_name
        category.save(update_fields=['key', ])
        announce = f"BBS Category '{old_abbr} - {old_name}' renamed to: '{old_abbr} - {new_name}'"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def prefix_category(self, account, category=None, new_prefix=None):
        if not category:
            raise ValueError("Must enter a category name!")
        category = self.find_category(account, category)
        if not category.locks.check(account, 'admin'):
            raise ValueError("Permission denied!")
        if not _RE_PRE.match(new_prefix):
            raise ValueError("Prefixes must be 0-3 alphanumeric characters.")
        if BoardCategory.objects.filter(abbr__iexact=new_prefix).exclude(id=category.id).exists():
            raise ValueError("BBS Prefixes must be unique!")
        old_abbr = category.abbr
        category.abbr = new_prefix
        category.save(update_fields=['abbr', ])
        announce = f"BBS Category '{old_abbr} - {category.key}' re-prefixed to: '{new_prefix} - {category.key}'"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def delete_category(self, account, category, abbr=None):
        category_found = self.find_category(account, category)
        if not account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        if not category == category_found.key:
            raise ValueError("Names must be exact for verification.")
        if not abbr:
            raise ValueError("Must provide prefix for verification!")
        if not abbr == category_found.abbr:
            raise ValueError("Must provide exact prefix for verification!")
        announce = f"|rDELETED|n BBS Category '{category_found.abbr} - {category_found.key}'"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        category_found.delete()

    def lock_category(self, account, category, new_locks):
        category = self.find_category(account, category)
        if not account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        new_locks = self.valid['locks'](account, new_locks, option_key='BBS Category Locks',
                                        options=['see', 'create', 'delete', 'admin'])
        try:
            category.locks.add(new_locks)
            category.save(update_fields=['lock_storage'])
        except LockException as e:
            raise ValueError(str(e))
        announce = f"BBS Category '{category.abbr} - {category.key}' lock changed to: {new_locks}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def boards(self):
        return Board.objects.order_by('category__key', 'order')

    def usable_boards(self, account, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(account, mode=mode, checkadmin=check_admin)
                and board.category.locks.check(account, 'see')]

    def visible_boards(self, account, check_admin=True):
        return [board for board in self.usable_boards(account, mode='read', check_admin=check_admin)
                if account not in board.ignore_list.all() and board.category.locks.check(account, 'see')]

    def find_board(self, account, find_name=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if visible_only:
            boards = self.visible_boards(account)
        else:
            boards = self.usable_boards(account)
        if not boards:
            raise ValueError("No applicable boards.")

        board_dict = {board.alias.upper(): board for board in boards}

        if find_name.upper() in board_dict:
            return board_dict[find_name.upper()]
        raise ValueError("Board '%s' not found!" % find_name)

    def create_board(self, account, category, name=None, order=None):
        category = self.find_category(account, category)
        if not category.locks.check(account, 'create'):
            raise ValueError("Permission denied!")
        name = simple_name(name, option_key='BBS Board')
        if category.boards.filter(key__iexact=name).exists():
            raise ValueError("Names must be unique!")
        if not order:
            order = max([board.order for board in category.boards.all()]) + 1
        else:
            order = int(order)
            if category.boards.filter(order=order).exists():
                raise ValueError("Orders must be unique per group!")
        if order > 99:
            raise ValueError("The maximum order of a board is 99!")
        board = category.boards.create(key=name, order=order, lock_storage=self.options.board_locks)
        board.save()
        announce = f"BBS Board Created: ({category}) - {board.alias}: {board.key}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        return board

    def delete_board(self, account, name=None):
        board = self.find_board(name, account)
        if not name == board.key:
            raise ValueError("Entered name must match board name exactly!")
        if not board.category.locks.check('delete', account):
            raise ValueError("Permission denied!")
        announce = f"Deleted BBS Board ({board.category.key}) - {board.alias}: {board.key}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        board.delete()

    def rename_board(self, account, name=None, new_name=None):
        board = self.find_board(account, name)
        if not board.category.locks.check('admin', account):
            raise ValueError("Permission denied!")
        new_name = simple_name(new_name, option_key='BBS Board')
        if board.key == new_name:
            raise ValueError("No point... names are the same.")
        if board.category.boards.exclude(id=board).filter(key__iexact=new_name).exists():
            raise ValueError("Names must be unique!")
        old_name = board.key
        board.key = new_name
        board.save(update_fields=['key'])
        announce = f"Renamed BBS Board ({board.category.key}) - {board.alias}: {old_name} to: {board.key}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def order_board(self, account, name=None, order=None):
        board = self.find_board(account, name)
        if not board.category.locks.check('admin', account):
            raise ValueError("Permission denied!")
        if not order:
            raise ValueError("No order entered!")
        order = self.valid['positive_integer'](account, order, option_key='BBS Board Order')
        if board.order == order:
            raise ValueError("No point to this operation.")
        if board.category.boards.exclude(id=board.id).filter(order=order).exists():
            raise ValueError("Orders must be unique!")
        if order > 99:
            raise ValueError("Board order may not exceed 99.")
        old_order = board.order
        board.order = order
        board.save(update_fields=['order'])
        announce = f"Re-Ordered BBS Board ({board.category.key}) - {board.alias}: {old_order} to: {order}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def lock_board(self, account, name=None, lock=None):
        board = self.find_board(account, name)
        if not board.category.locks.check('admin', account):
            raise ValueError("Permission denied!")
        if not lock:
            raise ValueError("Must enter a lockstring.")
        lockstring = self.valid['locks'](account, lock, option_key='BBS Board Lock')
        try:
            board.locks.add(lockstring)
            board.save_locks()
        except LockException as e:
            raise ValueError(str(e))
        announce = f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lockstring}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def create_post(self, account, board=None, subject=None, text=None, announce=True, date=None):
        board = self.find_board(account, board)
        if not text:
            raise ValueError("Text field empty.")
        if not subject:
            raise ValueError("Subject field empty.")
        if not date:
            date = utcnow()
        order = board.posts.all().count() + 1
        post = board.posts.create(account_stub=account.stub, subject=subject, text=text, creation_date=date,
                                  modify_date=date, order=order)
        return post

    def edit_post(self, account, board=None, post=None, seek_text=None, replace_text=None):
        board = self.find_board(account, board)
        posts = board.parse_postnums(account, post)
        if not posts:
            raise ValueError("Post not found!")
        if len(posts) > 1:
            raise ValueError("Cannot edit multiple posts at once.")
        p = posts[0]
        if not p.can_edit(account):
            raise ValueError("Permission denied.")
        p.edit_post(find=seek_text, replace=replace_text)
        announce = f"Post edited!"
        self.msg_target(announce, account)

    def delete_post(self, account, board=None, post=None):
        board = self.find_board(account, board)
        posts = board.parse_postnums(account, post)
        if not posts:
            raise ValueError("Post not found!")
        errors = set()
        for p in posts:
            if p.can_edit(account):
                self.msg_target(f"Post {p.order} deleted!", account)
                p.delete()
            else:
                errors.add(p.order)
        if errors:
            pass

    def set_mandatory(self, account, board=None, value=None):
        board = self.find_board(account, board)
