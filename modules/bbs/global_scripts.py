import re
from evennia.locks.lockhandler import LockException
from typeclasses.scripts import GlobalScript
from utils.text import partial_match
from utils.time import utcnow
from . models import Board, BoardCategory
from utils.valid import simple_name

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

    def visible_categories(self, character):
        return [cat for cat in self.categories() if cat.locks.check(character, 'see')]

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

    def find_category(self, character, category=None):
        if not category:
            raise ValueError("Must enter a category name!")
        candidates = BoardCategory.objects.all()
        if not character.account.is_superuser:
            candidates = [c for c in candidates if c.locks.check('see', character)]
        if not candidates:
            raise ValueError("No Board Categories visible!")
        found = partial_match(category, candidates)
        if not found:
            raise ValueError(f"Category '{category}' not found!")
        return found

    def rename_category(self, character, category=None, new_name=None):
        if not category:
            raise ValueError("Must enter a category name!")
        if not new_name:
            raise ValueError("Must enter a new name!")
        category = self.find_category(character, category)
        if not category.locks.check(character, 'admin'):
            raise ValueError("Permission denied!")
        new_name = simple_name(new_name, option_key='BBS Category')
        if BoardCategory.objects.filter(key__iexact=new_name).exclude(id=category.id).exists():
            raise ValueError("Names must be unique!")
        old_name = category.key
        old_abbr = category.abbr
        category.key = new_name
        category.save(update_fields=['key', ])
        announce = f"BBS Category '{old_abbr} - {old_name}' renamed to: '{old_abbr} - {new_name}'"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def prefix_category(self, character, category=None, new_prefix=None):
        if not category:
            raise ValueError("Must enter a category name!")
        category = self.find_category(character, category)
        if not category.locks.check(character, 'admin'):
            raise ValueError("Permission denied!")
        if not _RE_PRE.match(new_prefix):
            raise ValueError("Prefixes must be 0-3 alphanumeric characters.")
        if BoardCategory.objects.filter(abbr__iexact=new_prefix).exclude(id=category.id).exists():
            raise ValueError("BBS Prefixes must be unique!")
        old_abbr = category.abbr
        category.abbr = new_prefix
        category.save(update_fields=['abbr', ])
        announce = f"BBS Category '{old_abbr} - {category.key}' re-prefixed to: '{new_prefix} - {category.key}'"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def delete_category(self, character, category, abbr=None):
        category_found = self.find_category(character, category)
        if not account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        if not category == category_found.key:
            raise ValueError("Names must be exact for verification.")
        if not abbr:
            raise ValueError("Must provide prefix for verification!")
        if not abbr == category_found.abbr:
            raise ValueError("Must provide exact prefix for verification!")
        announce = f"|rDELETED|n BBS Category '{category_found.abbr} - {category_found.key}'"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)
        category_found.delete()

    def lock_category(self, character, category, new_locks):
        category = self.find_category(character, category)
        if not character.account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        new_locks = self.valid['locks'](character, new_locks, option_key='BBS Category Locks',
                                        options=['see', 'create', 'delete', 'admin'])
        try:
            category.locks.add(new_locks)
            category.save(update_fields=['lock_storage'])
        except LockException as e:
            raise ValueError(str(e))
        announce = f"BBS Category '{category.abbr} - {category.key}' lock changed to: {new_locks}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def boards(self):
        return Board.objects.order_by('category__key', 'order')

    def usable_boards(self, character, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(character, mode=mode, checkadmin=check_admin)
                and board.category.locks.check(character, 'see')]

    def visible_boards(self, character, check_admin=True):
        return [board for board in self.usable_boards(character, mode='read', check_admin=check_admin)
                if character not in board.ignore_list.all() and board.category.locks.check(character, 'see')]

    def find_board(self, character, find_name=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if visible_only:
            boards = self.visible_boards(character)
        else:
            boards = self.usable_boards(character)
        if not boards:
            raise ValueError("No applicable boards.")

        board_dict = {board.alias.upper(): board for board in boards}

        if find_name.upper() in board_dict:
            return board_dict[find_name.upper()]
        raise ValueError("Board '%s' not found!" % find_name)

    def create_board(self, character, category, name=None, order=None):
        category = self.find_category(character, category)
        if not category.locks.check(character, 'create'):
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
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)
        return board

    def delete_board(self, character, name=None):
        board = self.find_board(name, character)
        if not name == board.key:
            raise ValueError("Entered name must match board name exactly!")
        if not board.category.locks.check(character, 'delete'):
            raise ValueError("Permission denied!")
        announce = f"Deleted BBS Board ({board.category.key}) - {board.alias}: {board.key}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)
        board.delete()

    def rename_board(self, character, name=None, new_name=None):
        board = self.find_board(character, name)
        if not board.category.locks.check('admin', character):
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
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def order_board(self, character, name=None, order=None):
        board = self.find_board(character, name)
        if not board.category.locks.check('admin', character):
            raise ValueError("Permission denied!")
        if not order:
            raise ValueError("No order entered!")
        order = self.valid['positive_integer'](character, order, option_key='BBS Board Order')
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
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def lock_board(self, character, name=None, lock=None):
        board = self.find_board(character, name)
        if not board.category.locks.check('admin', character):
            raise ValueError("Permission denied!")
        if not lock:
            raise ValueError("Must enter a lockstring.")
        lockstring = self.valid['locks'](character, lock, option_key='BBS Board Lock')
        try:
            board.locks.add(lockstring)
            board.save_locks()
        except LockException as e:
            raise ValueError(str(e))
        announce = f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lockstring}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def create_post(self, character, board=None, subject=None, text=None, announce=True, date=None):
        board = self.find_board(character, board)
        if not text:
            raise ValueError("Text field empty.")
        if not subject:
            raise ValueError("Subject field empty.")
        if not date:
            date = utcnow()
        order = board.posts.all().count() + 1
        post = board.posts.create(account_stub=character.account.stub, object_stub=character.stub, subject=subject, text=text, creation_date=date,
                                  modify_date=date, order=order)
        return post

    def edit_post(self, character, board=None, post=None, seek_text=None, replace_text=None):
        board = self.find_board(character, board)
        posts = board.parse_postnums(character, post)
        if not posts:
            raise ValueError("Post not found!")
        if len(posts) > 1:
            raise ValueError("Cannot edit multiple posts at once.")
        p = posts[0]
        if not p.can_edit(character):
            raise ValueError("Permission denied.")
        p.edit_post(find=seek_text, replace=replace_text)
        announce = f"Post edited!"
        self.msg_target(announce, character)

    def delete_post(self, character, board=None, post=None):
        board = self.find_board(character, board)
        posts = board.parse_postnums(character, post)
        if not posts:
            raise ValueError("Post not found!")
        errors = set()
        for p in posts:
            if p.can_edit(character):
                self.msg_target(f"Post {p.order} deleted!", character)
                p.delete()
            else:
                errors.add(p.order)
        if errors:
            pass

    def set_mandatory(self, character, board=None, value=None):
        board = self.find_board(character, board)
