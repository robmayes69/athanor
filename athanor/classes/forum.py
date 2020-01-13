import re
from django.conf import settings
from django.db.models import F, Q

from evennia.utils.logger import log_trace
from evennia.utils.utils import class_from_module
from evennia.locks.lockhandler import LockException
from evennia.utils.validatorfuncs import lock as validate_lock
from evennia.utils.ansi import ANSIString

from athanor.utils.online import puppets as online_puppets
from athanor.utils.text import partial_match
from athanor.utils.time import utcnow
from athanor.core.scripts import AthanorGlobalScript, AthanorOptionScript

from .models import ForumCategoryBridge, ForumBoardBridge, ForumThreadBridge, ForumPost, ForumThreadRead


class AthanorForumCategory(AthanorOptionScript):
    re_name = re.compile(r"^[a-zA-Z]{0,3}$")
    re_abbr = re.compile(r"^[a-zA-Z]{0,3}$")
    lockstring = "see:all();create:perm(Admin);delete:perm(Admin);admin:perm(Admin)"

    def create_bridge(self, key, clean_key, abbr, clean_abbr):
        if hasattr(self, 'forum_category_bridge'):
            return
        ForumCategoryBridge.objects.create(db_script=self, db_name=clean_key, db_cabbr=abbr, db_iname=clean_key.lower(),
                                           db_cname=key, db_abbr=clean_abbr, db_iabbr=clean_abbr.lower())

    def setup_locks(self):
        self.locks.add(self.lockstring)

    def __str__(self):
        return self.key

    @classmethod
    def create_forum_category(cls, key, abbr, **kwargs):
        key = ANSIString(key)
        abbr = ANSIString(abbr)
        clean_key = str(key.clean())
        clean_abbr = str(abbr.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in ForumCategory Name.")
        if not cls.re_abbr.match(clean_abbr):
            raise ValueError("Abbreviations must be between 0-3 alphabetical characters.")
        if ForumCategoryBridge.objects.filter(Q(db_iname=clean_key.lower()) | Q(db_iabbr=clean_abbr.lower())).count():
            raise ValueError("Name or Abbreviation conflicts with another ForumCategory.")
        script, errors = cls.create(clean_key, persistent=True, **kwargs)
        if script:
            script.create_bridge(key.raw(), clean_key, abbr.raw(), clean_abbr)
            script.setup_locks()
        else:
            raise ValueError(errors)
        return script


class AthanorForumBoard(AthanorOptionScript):
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    lockstring = "read:all();post:all();admin:perm(Admin)"

    def setup_locks(self):
        self.locks.add(self.lockstring)

    def create_bridge(self, category, key, clean_key, order):
        if hasattr(self, 'forum_board_bridge'):
            return
        ForumBoardBridge.objects.create(db_script=self, db_name=clean_key, db_category=category.forum_category_bridge,
                                        db_order=order, db_iname=clean_key.lower(), db_cname=key)

    @classmethod
    def create_forum_board(cls, category, key, order, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in ForumCategory Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Forum Board Names must <qualifier>")
        if ForumBoardBridge.objects.filter(db_category=category.forum_category_bridge).filter(
                Q(db_iname=clean_key.lower()) | Q(db_order=order)).count():
            raise ValueError("Name or Order conflicts with another Forum Board in this category.")
        script, errors = cls.create(clean_key, persistent=True, **kwargs)
        if script:
            script.create_bridge(category, key.raw(), clean_key, order)
            script.setup_locks()
        else:
            raise ValueError(errors)
        return script

    def __str__(self):
        return self.key

    @property
    def prefix_order(self):
        bridge = self.forum_board_bridge
        return f'{bridge.category.db_abbr}{bridge.db_order}'

    @property
    def main_threads(self):
        return self.forum_board_bridge.threads.filter(parent=None)

    def character_join(self, character):
        self.forum_board_bridge.ignore_list.remove(character)

    def character_leave(self, character):
        self.forum_board_bridge.ignore_list.add(character)

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
        return self.forum_board_bridge.threads.exclude(read__account=account, db_date_modified__lte=F('read__date_read')).order_by(
            'db_order')

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


class AthanorForumThread(AthanorOptionScript):
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def create_bridge(self, board, key, clean_key, order, account, obj, date_created, date_modified):
        if hasattr(self, 'forum_category_bridge'):
            return
        if not date_created:
            date_created = utcnow()
        if not date_modified:
            date_modified = utcnow()
        ForumThreadBridge.objects.create(db_script=self, db_name=clean_key, db_order=order, db_object=obj, db_cname=key,
                                         db_board=board.forum_board_bridge,  db_iname=clean_key.lower(),
                                         db_date_created=date_created, db_account=account,
                                         db_date_modified=date_modified)

    @classmethod
    def create_forum_thread(cls, board, key, order, account, obj, date_created, date_modified, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Forum Thread Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Forum Thread Names must <qualifier>")
        if ForumThreadBridge.objects.filter(db_board=board.forum_board_bridge).filter(
                Q(db_iname=clean_key.lower()) | Q(db_order=order)).count():
            raise ValueError("Name or Order conflicts with another Forum Thread on this Board.")
        script, errors = cls.create(clean_key, persistent=True, **kwargs)
        if script:
            script.create_bridge(board, key.raw(), clean_key, order, account, obj, date_created, date_modified)
        else:
            raise ValueError(errors)
        return script

    def __str__(self):
        return self.key


class AthanorForumController(AthanorGlobalScript):
    system_name = 'BBS'

    def at_start(self):
        from django.conf import settings

        try:
            self.ndb.category_typeclass = class_from_module(settings.FORUM_CATEGORY_TYPECLASS,
                                                            defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.category_typeclass = AthanorForumCategory

        try:
            self.ndb.board_typeclass = class_from_module(settings.FORUM_BOARD_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.board_typeclass = AthanorForumBoard

        try:
            self.ndb.thread_typeclass = class_from_module(settings.FORUM_THREAD_TYPECLASS,
                                                          defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.thread_typeclass = AthanorForumThread

    def categories(self):
        return AthanorForumCategory.objects.filter_family().order_by('db_key')

    def visible_categories(self, character):
        return [cat for cat in self.categories() if cat.access(character, 'see')]

    def create_category(self, session, name, abbr=''):
        if not self.access(session, 'admin'):
            raise ValueError("Permission denied!")

        new_category = self.ndb.category_typeclass.create_forum_category(key=name, abbr=abbr)
        announce = f"Created BBS Category: {abbr} - {name}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)
        return new_category

    def find_category(self, session, category=None):
        if not category:
            raise ValueError("Must enter a category name!")
        if not (candidates := self.visible_categories(session)):
            raise ValueError("No Board Categories visible!")
        if not (found := partial_match(category, candidates)):
            raise ValueError(f"Category '{category}' not found!")
        return found

    def rename_category(self, session, category=None, new_name=None):
        category = self.find_category(session, category)
        if not category.access(session, 'admin'):
            raise ValueError("Permission denied!")
        old_name = category.key
        old_abbr = category.abbr
        new_name = category.rename(new_name)
        announce = f"BBS Category '{old_abbr} - {old_name}' renamed to: '{old_abbr} - {new_name}'"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def prefix_category(self, session, category=None, new_prefix=None):
        category = self.find_category(session, category)
        if not category.access(session, 'admin'):
            raise ValueError("Permission denied!")
        old_abbr = category.abbr
        new_prefix = category.change_prefix(new_prefix)
        announce = f"BBS Category '{old_abbr} - {category.key}' re-prefixed to: '{new_prefix} - {category.key}'"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def delete_category(self, session, category, abbr=None):
        category_found = self.find_category(session, category)
        if not session.account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        if not category == category_found.key:
            raise ValueError("Names must be exact for verification.")
        if not abbr:
            raise ValueError("Must provide prefix for verification!")
        if not abbr == category_found.abbr:
            raise ValueError("Must provide exact prefix for verification!")
        announce = f"|rDELETED|n BBS Category '{category_found.abbr} - {category_found.key}'"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)
        category_found.delete()

    def lock_category(self, session, category, new_locks):
        category = self.find_category(session, category)
        if not session.account.is_superuser:
            raise ValueError("Permission denied! Superuser only!")
        new_locks = category.change_locks(new_locks)
        announce = f"BBS Category '{category.abbr} - {category.key}' lock changed to: {new_locks}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def boards(self):
        return AthanorForumBoard.objects.filter_family().order_by('forum_board_bridge__db_category__db_name',
                                                                  'forum_board_bridge__db_order')

    def usable_boards(self, character, mode='read', check_admin=True):
        return [board for board in self.boards() if board.check_permission(character, mode=mode, checkadmin=check_admin)
                and board.forum_board_bridge.category.db_script.access(character, 'see')]

    def visible_boards(self, character, check_admin=True):
        return [board for board in self.usable_boards(character, mode='read', check_admin=check_admin)
                if board.forum_board_bridge.category.db_script.access(character, 'see')]

    def find_board(self, session, find_name=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if isinstance(find_name, ForumBoardBridge):
            return find_name.db_script
        if isinstance(find_name, AthanorForumBoard):
            return find_name
        if not (boards := self.visible_boards(session) if visible_only else self.usable_boards(session)):
            raise ValueError("No applicable Forum Boards.")
        board_dict = {board.prefix_order.upper(): board for board in boards}
        if not (found := board_dict.get(find_name.upper(), None)):
            raise ValueError("Board '%s' not found!" % find_name)
        return found

    def create_board(self, session, category, name=None, order=None):
        category = self.find_category(session, category)
        if not category.access(session, 'create'):
            raise ValueError("Permission denied!")
        typeclass = self.ndb.board_typeclass
        new_board = typeclass.create_forum_board(key=name, order=order, category=category)
        announce = f"BBS Board Created: ({category}) - {new_board.prefix_order}: {new_board.key}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)
        return new_board

    def delete_board(self, session, name=None, verify=None):
        board = self.find_board(session, name)
        if not verify == board.key:
            raise ValueError("Entered name must match board name exactly!")
        if not board.forum_board_bridge.category.db_script.access(session, 'delete'):
            raise ValueError("Permission denied!")
        announce = f"Deleted BBS Board ({board.category.key}) - {board.alias}: {board.key}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)
        board.delete()

    def rename_board(self, session, name=None, new_name=None):
        board = self.find_board(session, name)
        if not board.forum_board_bridge.category.db_script.access('admin', session):
            raise ValueError("Permission denied!")
        old_name = board.key
        board.change_key(new_name)
        announce = f"Renamed BBS Board ({board.category.key}) - {board.alias}: {old_name} to: {board.key}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def order_board(self, session, name=None, order=None):
        board = self.find_board(session, name)
        if not board.category.access('admin', session):
            raise ValueError("Permission denied!")
        old_order = board.order
        order = board.change_order(order)
        announce = f"Re-Ordered BBS Board ({board.category.key}) - {board.alias}: {old_order} to: {order}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def lock_board(self, session, name=None, lock=None):
        board = self.find_board(session, name)
        if not board.category.access('admin', session):
            raise ValueError("Permission denied!")
        lock = board.change_locks(lock)
        announce = f"BBS Board ({board.category.key}) - {board.alias}: {board.key} lock changed to: {lock}"
        self.alert(announce, enactor=session)
        self.msg_target(announce, session)

    def create_thread(self, session, board=None, subject=None, text=None, announce=True, date=None, no_post=False):
        board = self.find_board(session, board)
        new_thread = self.ndb.thread_typeclass.create_forum_thread(key=subject, text=text, owner=session.full_stub, board=board, date=date)
        if not no_post:
            new_post = self.create_post(session, board=board, thread=new_thread, subject=subject, text=text,
                                        announce=False, date=date)
        if announce:
            pass  # do something!
        return new_thread

    def rename_thread(self, session, board=None, thread=None, new_name=None):
        board = self.find_board(session, board)
        thread = board.find_thread(session, thread)


    def delete_thread(self, session, board=None, thread=None, name_confirm=None):
        board = self.find_board(session, board)
        thread = board.find_thread(session, thread)


    def create_post(self, session, board=None, thread=None, subject=None, text=None, announce=True, date=None):
        board = self.find_board(session, board)
        thread = board.find_thread(session, thread)
        new_post = thread.create_post(text=text, owner=session, date=date)
        if announce:
            pass  # do something!
        return new_post

    def edit_post(self, session, board=None, thread=None, post=None, seek_text=None, replace_text=None):
        board = self.find_board(session, board)
        thread = board.find_thread(session, thread)
        post = thread.find_post(session, post)
        if not post.can_edit(session):
            raise ValueError("Permission denied.")
        post.edit_post(find=seek_text, replace=replace_text)
        announce = f"Post edited!"
        self.msg_target(announce, session)

    def delete_post(self, session, board=None, thread=None, post=None, verify_string=None):
        board = self.find_board(session, board)
        thread = board.find_thread(session, thread)
        post = thread.find_post(session, post)

    def set_mandatory(self, character, board=None, value=None):
        board = self.find_board(character, board)
