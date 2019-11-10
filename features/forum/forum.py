import re
from django.db.models import F
from evennia.typeclasses.models import TypeclassBase
from evennia.utils.utils import lazy_property
from evennia.utils.optionhandler import OptionHandler
from evennia.locks.lockhandler import LockException
from evennia.utils.validatorfuncs import lock as validate_lock
from utils.time import utcnow
from utils.online import puppets as online_puppets
from utils.valid import simple_name
from . models import ForumCategoryDB, ForumBoardDB, ForumThreadDB, ForumPostDB, ForumThreadRead


class DefaultForumCategory(ForumCategoryDB, metaclass=TypeclassBase):
    option_dict = {
        'board_locks': ('Default locks for new Boards?', 'Lock', "read:all();post:all();admin:perm(Admin)"),
        'color': ('Color to display Prefix in.', 'Color', 'n'),
        'faction': ('Faction to use for Lock Templates', 'Faction', None)
    }
    prefix_regex = re.compile(r"^[a-zA-Z]{0,3}$")

    @classmethod
    def validate_prefix(cls, prefix_text, rename_target=None):
        if not cls.prefix_regex.match(prefix_text):
            raise ValueError("Prefixes must be 0-3 alphabetical characters.")
        query = cls.objects.filter(db_abbr__iexact=prefix_text)
        if rename_target:
            query = query.exclude(id=rename_target.id)
        if query.count():
            raise ValueError(f"A BoardCategory abbreviated '{prefix_text}' already exists!")
        return prefix_text

    @classmethod
    def validate_key(cls, key_text, rename_target=None):
        if not key_text:
            raise ValueError("A BoardCategory must have a name!")
        key_text = simple_name(key_text, option_key="BBS Category")
        query = cls.objects.filter(db_key__iexact=key_text)
        if rename_target:
            query = query.exclude(id=rename_target.id)
        if query.count():
            raise ValueError(f"A BoardCategory named '{key_text}' already exists!")
        return key_text

    @classmethod
    def validate_order(cls, order_text):
        pass

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})


    def at_board_category_creation(self, *args, **kwargs):
        pass

    def at_first_save(self, *args, **kwargs):
        pass

    @classmethod
    def create(cls, *args, **kwargs):
        key = cls.validate_key(kwargs.get('key', None))
        abbr = cls.validate_prefix(kwargs.get('abbr', None))

        new_category = cls(db_key=key, db_abbr=abbr)
        new_category.save()
        return new_category

    def __str__(self):
        return self.key

    def change_key(self, new_key):
        new_key = self.validate_key(new_key, self)
        self.key = new_key
        return new_key

    def change_prefix(self, new_prefix):
        new_prefix = self.validate_prefix(new_prefix, self)
        self.abbr = new_prefix
        return new_prefix

    def change_locks(self, new_locks):
        if not new_locks:
            raise ValueError("No locks entered!")
        new_locks = validate_lock(new_locks, option_key='BBS Category Locks',
                                        access_options=['see', 'create', 'delete', 'admin'])
        try:
            self.locks.add(new_locks)
        except LockException as e:
            raise ValueError(str(e))
        return new_locks


class DefaultForumBoard(ForumBoardDB, metaclass=TypeclassBase):

    @classmethod
    def validate_key(cls, key_text, category, rename_target=None):
        if not key_text:
            raise ValueError("A BBS Board must have a name!")
        key_text = simple_name(key_text, option_key="BBS Board")
        query = cls.objects.filter(db_key__iexact=key_text, db_category=category)
        if rename_target:
            query = query.exclude(id=rename_target.id)
        if query.count():
            raise ValueError(f"A BBS Board named '{key_text}' already exists in BBS Category '{category}'!")
        return key_text

    @classmethod
    def validate_order(cls, order_input, category, rename_target=None):
        if not order_input:
            raise ValueError("A BBS Board must have an order number!")
        order_input = int(order_input)
        if order_input > 99:
            raise ValueError("The maximum order of a board is 99!")
        if order_input < 1:
            raise ValueError("A BBS Board order may not be lower than 1!")
        query = cls.objects.filter(db_order=order_input, db_category=category)
        if rename_target:
            query.exclude(id=rename_target)
        if query.count():
            raise ValueError(f"A BBS Board already uses Order {order_input} within BBS Category '{category}'!")
        return order_input

    def at_board_creation(self, *args, **kwargs):
        pass

    def at_first_save(self, *args, **kwargs):
        pass

    @classmethod
    def create(cls, *args, **kwargs):
        category = kwargs.get('category', None)
        if not isinstance(category, BoardCategoryDB):
            raise ValueError("Must provide a BoardCategory!")

        key = kwargs.get('key', None)
        order = kwargs.get('order', None)

        key = cls.validate_key(key, category)
        order = cls.validate_order(order, category)

        if not key:
            raise ValueError("Board name is empty!")
        if not order:
            raise ValueError("Board order not provided!")

        new_board = cls(db_key=key, db_order=order, db_category=category)
        new_board.save()
        return new_board

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
    def main_posts(self):
        return self.posts.filter(parent=None)

    def character_join(self, character):
        self.ignore_list.remove(character)

    def character_leave(self, character):
        self.ignore_list.add(character)

    def parse_postnums(self, account, check=None):
        if not check:
            raise ValueError("No posts entered to check.")
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
        posts = self.posts.filter_family(db_order__in=fullnums).order_by('db_order')
        if not posts:
            raise ValueError("Posts not found!")
        return posts

    def check_permission(self, checker=None, mode="read", checkadmin=True):
        if checker.locks.check_lockstring(checker, 'dummy:perm(Admin)'):
            return True
        if self.locks.check(checker.account, "admin") and checkadmin:
            return True
        elif self.locks.check(checker.account, mode):
            return True
        else:
            return False

    def unread_posts(self, account):
        return self.posts.exclude(read__account=account, db_date_modified__lte=F('read__date_read')).order_by('db_order')

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


class DefaultForumThread(ForumThreadDB, metaclass=TypeclassBase):

    def at_first_save(self, *args, **kwargs):
        pass

    @classmethod
    def validate_key(cls, key_text, rename_from=None):
        return key_text

    @classmethod
    def validate_order(cls, order_text, rename_from=None):
        return int(order_text)

    @classmethod
    def create(cls, *args, **kwargs):
        board = kwargs.get('board', None)
        if not isinstance(board, ForumThreadDB):
            raise ValueError("Posts must be linked to a board!")

        owner = kwargs.get('owner', None)
        key = kwargs.get('key', None)
        key = cls.validate_key(key)

        text = kwargs.get('text', None)
        if not text:
            raise ValueError("Post body is empty!")

        order = kwargs.get('order', None)
        if order:
            order = cls.validate_order(order)
        else:
            last_post = board.last_post()
            if last_post:
                order = last_post.order + 1
            else:
                order = 1

        new_post = cls(db_key=key, db_order=order, db_board=board, db_owner=owner, db_text=text)
        new_post.save()
        return new_post

    def __str__(self):
        return self.subject

    def post_alias(self):
        return f"{self.board.alias}/{self.order}"

    def can_edit(self, checker=None):
        if self.owner.account_stub.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.date_modified = utcnow()
        self.text = self.text.replace(find, replace)

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.date_read = utcnow()
        acc_read.save()


class DefaultForumPost(ForumPostDB, metaclass=TypeclassBase):
    pass
