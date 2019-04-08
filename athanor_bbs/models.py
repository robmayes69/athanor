import re
from django.db import models
from athanor.models import WithLocks
from athanor.utils.time import utcnow
from athanor.utils.text import mxp
from athanor.utils.online import accounts as online_accounts


class BoardCategory(WithLocks):
    key = models.CharField(max_length=255, unique=True, blank=False, null=False)
    abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)
    board_locks = models.TextField(null=False, blank=False, default="read:all();post:all();admin:pperm(Admin)")

    def __str__(self):
        return self.key

# Create your models here.


class Board(WithLocks):
    category = models.ForeignKey(BoardCategory, related_name='boards', null=False, on_delete=models.CASCADE)
    key = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    ignore_list = models.ManyToManyField('accounts.AccountDB')
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

    def init_locks(self):
        self.lock_storage = str(self.category.board_locks)
        self.save_locks()

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
        return self.posts.filter(order__in=fullnums).order_by('order')

    def check_permission(self, checker=None, mode="read", checkadmin=True):
        if checker.ath['core'].is_admin():
            return True
        if self.locks.check(checker.account, "admin") and checkadmin:
            return True
        elif self.locks.check(checker.account, mode):
            return True
        else:
            return False

    def unread_posts(self, session):
        return self.posts.exclude(read__account=session.account, modify_date__lte=models.F('read__read_date'))

    def display_permissions(self, checker=None):
        if not checker:
            return " "
        acc = ""
        if self.check_permission(checker=checker, mode="read", checkadmin=False):
            acc += "R"
        else:
            acc += " "
        if self.check_permission(checker=checker, mode="post", checkadmin=False):
            acc += "P"
        else:
            acc += " "
        if self.check_permission(checker=checker, mode="admin", checkadmin=False):
            acc += "A"
        else:
            acc += " "
        return acc

    def listeners(self):
        return [acc for acc in online_accounts() if self.check_permission(checker=acc)
                and acc not in self.ignore_list.all()]

    def squish_posts(self):
        for count, post in enumerate(self.posts.order_by('order')):
            if post.order != count +1:
                post.order = count + 1
                post.save(update_fields=['order'])


class Post(models.Model):
    board = models.ForeignKey('Board', related_name='posts', on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.AccountDB', related_name='+', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    text = models.TextField(blank=True)
    subject = models.CharField(max_length=30)
    order = models.PositiveIntegerField(null=True)
    anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = (('board', 'order'), )

    def __str__(self):
        return self.subject

    def can_edit(self, checker=None):
        if self.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.update_time('modify_date')
        self.text = self.text.replace(find, replace)
        self.save(update_fields=['text'])

    def update_read(self, viewer):
        read, created = self.read.get_or_create(account=viewer)
        read.read_date = utcnow()
        read.save()


class PostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='read', on_delete=models.CASCADE)
    read_date = models.DateTimeField(null=False)

    class Meta:
        unique_together = (('account', 'post'),)
