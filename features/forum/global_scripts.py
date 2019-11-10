from django.conf import settings
from evennia.utils.utils import class_from_module
from typeclasses.scripts import GlobalScript
from utils.text import partial_match
from features.forum.models import ForumCategoryDB, ForumBoardDB


class DefaultForumManager(GlobalScript):
    system_name = 'BBS'
    option_dict = {
        'category_locks': ('Default locks to use for new Board Categories?', 'Lock',
                           "see:all();create:perm(Admin);delete:perm(Admin);admin:perm(Admin)"),
    }

    def categories(self):
        return ForumCategoryDB.objects.filter_family().order_by('db_key')

    def visible_categories(self, character):
        return [cat for cat in self.categories() if cat.access(character, 'see')]

    def create_category(self, account, name, abbr=None):
        if not abbr:
            abbr = ''
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        typeclass = class_from_module(settings.BASE_BOARDCATEGORY_TYPECLASS)
        new_category = typeclass.create(key=name, abbr=abbr)
        announce = f"Created BBS Category: {abbr} - {name}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        return new_category

    def find_category(self, character, category=None):
        if not category:
            raise ValueError("Must enter a category name!")
        candidates = self.categories()
        if not character.account.is_superuser:
            candidates = [c for c in candidates if c.access(character, 'see')]
        if not candidates:
            raise ValueError("No Board Categories visible!")
        found = partial_match(category, candidates)
        if not found:
            raise ValueError(f"Category '{category}' not found!")
        return found

    def rename_category(self, character, category=None, new_name=None):
        if not category:
            raise ValueError("Must enter a category name!")
        category = self.find_category(character, category)
        if not category.access(character, 'admin'):
            raise ValueError("Permission denied!")
        old_name = category.key
        old_abbr = category.abbr
        new_name = category.change_key(new_name)
        announce = f"BBS Category '{old_abbr} - {old_name}' renamed to: '{old_abbr} - {new_name}'"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def prefix_category(self, character, category=None, new_prefix=None):
        if not category:
            raise ValueError("Must enter a category name!")
        category = self.find_category(character, category)
        if not category.access(character, 'admin'):
            raise ValueError("Permission denied!")
        old_abbr = category.abbr
        category.abbr = new_prefix
        new_prefix = category.change_prefix(new_prefix)
        announce = f"BBS Category '{old_abbr} - {category.key}' re-prefixed to: '{new_prefix} - {category.key}'"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def delete_category(self, character, category, abbr=None):
        category_found = self.find_category(character, category)
        if not character.account.is_superuser:
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
        new_locks = category.change_locks(new_locks)
        announce = f"BBS Category '{category.abbr} - {category.key}' lock changed to: {new_locks}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def boards(self):
        return ForumBoardDB.objects.filter_family().order_by('db_category__db_key', 'db_order')

    def usable_boards(self, character, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(character, mode=mode, checkadmin=check_admin)
                and board.category.access(character, 'see')]

    def visible_boards(self, character, check_admin=True):
        return [board for board in self.usable_boards(character, mode='read', check_admin=check_admin)
                if character not in board.db_ignore_list.all() and board.category.access(character, 'see')]

    def find_board(self, character, find_name=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if visible_only:
            boards = self.visible_boards(character)
        else:
            boards = self.usable_boards(character)
        if not boards:
            raise ValueError("No applicable forum.")

        board_dict = {board.prefix_order.upper(): board for board in boards}

        if find_name.upper() in board_dict:
            return board_dict[find_name.upper()]
        raise ValueError("Board '%s' not found!" % find_name)

    def create_board(self, character, category, name=None, order=None):
        category = self.find_category(character, category)
        if not category.access(character, 'create'):
            raise ValueError("Permission denied!")
        typeclass = class_from_module(settings.BASE_BOARD_TYPECLASS)
        new_board = typeclass.create(key=name, order=order, category=category)
        announce = f"BBS Board Created: ({category}) - {new_board.prefix_order}: {new_board.key}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)
        return new_board

    def delete_board(self, character, name=None):
        board = self.find_board(name, character)
        if not name == board.key:
            raise ValueError("Entered name must match board name exactly!")
        if not board.category.access(character, 'delete'):
            raise ValueError("Permission denied!")
        announce = f"Deleted BBS Board ({board.category.key}) - {board.alias}: {board.key}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)
        board.delete()

    def rename_board(self, character, name=None, new_name=None):
        board = self.find_board(character, name)
        if not board.category.access('admin', character):
            raise ValueError("Permission denied!")
        old_name = board.key
        board.change_key(new_name)
        announce = f"Renamed BBS Board ({board.category.key}) - {board.alias}: {old_name} to: {board.key}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def order_board(self, character, name=None, order=None):
        board = self.find_board(character, name)
        if not board.category.access('admin', character):
            raise ValueError("Permission denied!")
        old_order = board.order
        order = board.change_order(order)
        announce = f"Re-Ordered BBS Board ({board.category.key}) - {board.alias}: {old_order} to: {order}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def lock_board(self, character, name=None, lock=None):
        board = self.find_board(character, name)
        if not board.category.access('admin', character):
            raise ValueError("Permission denied!")
        lock = board.change_locks(lock)
        announce = f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lockstring}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def create_post(self, character, board=None, subject=None, text=None, announce=True, date=None):
        board = self.find_board(character, board)
        typeclass = class_from_module(settings.BASE_POST_TYPECLASS)
        new_post = typeclass.create(key=subject, text=text, owner=character.full_stub, board=board, date=date)
        if announce:
            pass  # do something!
        return new_post

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
