import re
from django.db import models
from modules.core.models import WithLocks
from utils.time import utcnow
from utils.online import puppets as online_puppets


class BoardCategory(WithLocks):
    key = models.CharField(max_length=255, unique=True, blank=False, null=False)
    abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)
    board_locks = models.TextField(null=False, blank=False, default="read:all();post:all();admin:pperm(Admin)")

    def __str__(self):
        return self.key


class Board(WithLocks):
    category = models.ForeignKey(BoardCategory, related_name='boards', null=False, on_delete=models.CASCADE)
    key = models.CharField(max_length=80, null=False, blank=False)
    order = models.PositiveIntegerField(default=0)
    ignore_list = models.ManyToManyField('objects.ObjectDB')
    mandatory = models.BooleanField(default=False)

    def __str__(self):
        return self.key

    def __int__(self):
        return self.order

    @property
    def alias(self):
        if self.category:
            return '%s%s' % (self.category.abbr, self.order)
        return str(self.order)

    class Meta:
        unique_together = (('category', 'key'), ('category', 'order'))

    @property
    def main_posts(self):
        return self.posts.filter(parent=None)

    def character_join(self, account):
        self.ignore_list.remove(account)

    def character_leave(self, account):
        self.ignore_list.add(account)

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
                fullnums += self.unread_posts(account).values_list('order', flat=True)
        posts = self.posts.filter(order__in=fullnums).order_by('order')
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
        return self.posts.exclude(read__account=account, modify_date__lte=models.F('read__read_date')).order_by('order')

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
        for count, post in enumerate(self.posts.order_by('order')):
            if post.order != count + 1:
                post.order = count + 1
                post.save(update_fields=['order'])

    def last_post(self):
        post = self.posts.order_by('creation_date').first()
        if post:
            return post
        return None


class Post(models.Model):
    board = models.ForeignKey('Board', related_name='posts', on_delete=models.CASCADE)
    owner = models.ForeignKey('core.AccountCharacter', related_name='+', on_delete=models.CASCADE)
    date_created = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(null=True)
    text = models.TextField(blank=False, null=False)
    subject = models.CharField(max_length=30)
    order = models.PositiveIntegerField(null=True)
    anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = (('board', 'order'), )

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
        self.save(update_fields=['text', 'date_modified'])

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.date_read = utcnow()
        acc_read.save()


class PostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class PostComment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    owner = models.ForeignKey('core.AccountCharacter', related_name='+', on_delete=models.CASCADE)
    date_created = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(null=True)
    text = models.TextField(blank=False, null=False)
    order = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = (('post', 'order'), )
