import re
from django.conf import settings
from django.db.models import F
from django.db import transaction

from evennia.utils.logger import log_trace
from evennia.utils.utils import lazy_property, class_from_module
from evennia.utils.optionhandler import OptionHandler
from evennia.locks.lockhandler import LockException
from evennia.utils.validatorfuncs import lock as validate_lock

from athanor.utils.time import utcnow
from athanor.utils.online import puppets as online_puppets
from athanor.utils.valid import simple_name
from athanor.utils.text import partial_match
from athanor.core.scripts import AthanorGlobalScript, AthanorOptionScript

from . models import ForumCategory, ForumBoard, ForumThread, ForumPost, ForumThreadRead


class AthanorForumCategory(AthanorOptionScript):
    option_dict = {
        'board_locks': ('Default locks for new Boards?', 'Lock', "read:all();post:all();admin:perm(Admin)"),
        'color': ('Color to display Prefix in.', 'Color', 'n'),
        'faction': ('Faction to use for Lock Templates', 'Faction', None)
    }
    prefix_regex = re.compile(r"^[a-zA-Z]{0,3}$")


    @classmethod
    def create_forum_category(cls, *args, **kwargs):
        with transaction.atomic():
            script, errors = cls.create(*args, **kwargs)


class AthanorForumBoard(AthanorOptionScript):

    @classmethod
    def create_forum_board(cls, *args, **kwargs):
        with transaction.atomic():
            pass

    def __str__(self):
        return self.key

    def __int__(self):
        return self.order

    @property
    def prefix_order(self):
        if self.category:
            return '%s%s' % (self.category.abbr, self.order)
        return str(self.order)

    @property
    def main_threads(self):
        return self.threads.filter(parent=None)

    def character_join(self, character):
        self.ignore_list.remove(character)

    def character_leave(self, character):
        self.ignore_list.add(character)

    def parse_threadnums(self, account, check=None):
        if not check:
            raise ValueError("No threads entered to check.")
        fullnums = []
        for arg in check.split(','):
            arg = arg.strip()
            if re.match(r"^\d+-\d+$", arg):
                numsplit = arg.split('-')
                numsplit2 = []
                for num in numsplit:
                    numsplit2.append(int(num))
                lo, hi = min(numsplit2), max(numsplit2)
                fullnums += range(lo, hi + 1)
            if re.match(r"^\d+$", arg):
                fullnums.append(int(arg))
            if re.match(r"^U$", arg.upper()):
                fullnums += self.unread_posts(account).values_list('db_order', flat=True)
        threads = self.threads.filter(db_order__in=fullnums).order_by('db_order')
        if not threads:
            raise ValueError("Threads not found!")
        return threads

    def check_permission(self, checker=None, mode="read", checkadmin=True):
        if checker.locks.check_lockstring(checker, 'dummy:perm(Admin)'):
            return True
        if self.locks.check(checker.account, "admin") and checkadmin:
            return True
        elif self.locks.check(checker.account, mode):
            return True
        else:
            return False

    def unread_threads(self, account):
        return self.threads.exclude(read__account=account, db_date_modified__lte=F('read__date_read')).order_by('db_order')

    def display_permissions(self, looker=None):
        if not looker:
            return " "
        acc = ""
        if self.check_permission(checker=looker, mode="read", checkadmin=False):
            acc += "R"
        else:
            acc += " "
        if self.check_permission(checker=looker, mode="post", checkadmin=False):
            acc += "P"
        else:
            acc += " "
        if self.check_permission(checker=looker, mode="admin", checkadmin=False):
            acc += "A"
        else:
            acc += " "
        return acc

    def listeners(self):
        return [char for char in online_puppets() if self.check_permission(checker=char)
                and char not in self.ignore_list.all()]

    def squish_posts(self):
        for count, post in enumerate(self.posts.order_by('db_date_created')):
            if post.order != count + 1:
                post.order = count + 1

    def last_post(self):
        post = self.posts.order_by('db_date_created').first()
        if post:
            return post
        return None

    def change_key(self, new_key):
        new_key = self.validate_key(new_key, self.category, self)
        self.key = new_key
        return new_key

    def change_order(self, new_order):
        pass

    def change_locks(self, new_locks):
        if not new_locks:
            raise ValueError("No locks entered!")
        new_locks = validate_lock(new_locks, option_key='BBS Board Locks',
                                        access_options=['read', 'post', 'admin'])
        try:
            self.locks.add(new_locks)
        except LockException as e:
            raise ValueError(str(e))
        return new_locks


class AthanorForumController(AthanorGlobalScript):
    system_name = 'BBS'
    option_dict = {
        'category_locks': ('Default locks to use for new Board Categories?', 'Lock',
                           "see:all();create:perm(Admin);delete:perm(Admin);admin:perm(Admin)"),
    }

    def at_start(self):
        from django.conf import settings

        try:
            self.ndb.category_typeclass = class_from_module(settings.BASE_FORUM_CATEGORY_TYPECLASS,
                                                     defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.category_typeclass = AthanorForumCategory

        try:
            self.ndb.board_typeclass = class_from_module(settings.BASE_FORUM_BOARD_TYPECLASS,
                                                     defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.board_typeclass = AthanorForumBoard

    def categories(self):
        return AthanorForumCategory.objects.filter_family().order_by('db_key')

    def visible_categories(self, character):
        return [cat for cat in self.categories() if cat.access(character, 'see')]

    def create_category(self, account, name, abbr=None):
        if not abbr:
            abbr = ''
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        typeclass = class_from_module(settings.BASE_FORUM_CATEGORY_TYPECLASS)
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
        return DefaultForumBoard.objects.filter_family().order_by('db_category__db_key', 'db_order')

    def usable_boards(self, character, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(character, mode=mode, checkadmin=check_admin)
                and board.category.access(character, 'see')]

    def visible_boards(self, character, check_admin=True):
        return [board for board in self.usable_boards(character, mode='read', check_admin=check_admin)
                if board.category.access(character, 'see')]

    def find_board(self, character, find_name=None, visible_only=True):
        if isinstance(find_name, DefaultForumBoard):
            return find_name
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
        typeclass = class_from_module(settings.BASE_FORUM_BOARD_TYPECLASS)
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
        announce = f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lock}"
        self.alert(announce, enactor=character)
        self.msg_target(announce, character)

    def create_thread(self, character, board=None, subject=None, text=None, announce=True, date=None, no_post=False):
        board = self.find_board(character, board)
        typeclass = class_from_module(settings.BASE_FORUM_THREAD_TYPECLASS)
        new_thread = typeclass.create(key=subject, text=text, owner=character.full_stub, board=board, date=date)
        if not no_post:
            new_post = self.create_post(character, board=board, thread=new_thread, subject=subject, text=text,
                                        announce=False, date=date)
        if announce:
            pass  # do something!
        return new_thread

    def rename_thread(self, character, board=None, thread=None, new_name=None):
        pass

    def delete_thread(self, character, board=None, thread=None, name_confirm=None):
        pass

    def create_post(self, character, board=None, thread=None, subject=None, text=None, announce=True, date=None):
        if not isinstance(board, DefaultForumBoard):
            board = self.find_board(character, board)
        if not isinstance(thread, DefaultForumThread):
            thread = board.parse_threadnums(character, thread)
            if len(thread) > 1:
                raise ValueError("Can only create posts on a single thread at a time!")
            thread = thread[0]
        typeclass = class_from_module(settings.BASE_FORUM_POST_TYPECLASS)
        new_post = typeclass.create(key=subject, text=text, owner=character, thread=thread, date=date)
        if announce:
            pass  # do something!
        return new_post

    def edit_post(self, character, board=None, post=None, seek_text=None, replace_text=None):
        board = self.find_board(character, board)
        posts = board.parse_threadnums(character, post)
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
        posts = board.parse_threadnums(character, post)
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
