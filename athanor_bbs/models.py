import re
from django.db import models
from django.conf import settings
from athanor.core.models import WithTimestamp, WithLocks
from athanor.utils.time import utcnow
from athanor.utils.text import mxp, sanitize_string, partial_match
from athanor.utils.online import characters

# Create your models here.
class Board(WithLocks):
    group = models.ForeignKey('groups.Group', related_name='boards', null=True)
    key = models.CharField(max_length=40)
    order = models.PositiveIntegerField(default=0)
    ignore_list = models.ManyToManyField('objects.ObjectDB')
    anonymous = models.CharField(max_length=80, null=True)
    mandatory = models.BooleanField(default=False)

    def __unicode__(self):
        return self.key

    def __int__(self):
        return self.order

    @property
    def alias(self):
        if self.group:
            return '%s%s' % (self.group.get_abbr(), self.order)
        return str(self.order)

    class Meta:
        unique_together = (('group', 'key'), ('group', 'order'))

    @property
    def main_posts(self):
        return self.posts.filter(parent=None)

    def character_join(self, character):
        self.ignore_list.remove(character)

    def character_leave(self, character):
        self.ignore_list.add(character)

    def init_locks(self):
        if self.category.group:
            group_id = self.category.group.id
            locks = 'read:group(%i);post:group(%i);admin:gperm(%i, bbadmin)' % (group_id, group_id, group_id)
        else:
            locks = 'read:all();post:all();admin:perm(Admin)'
        self.lock_storage = locks
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
                fullnums += self.main_posts.exclude(read__account=account, modify_date__lte=models.F('read__read_date')).values_list('order', flat=True)
        return self.posts.filter(order__in=fullnums).order_by('order')

    def check_permission(self, checker=None, mode="read", checkadmin=True):
        if checker.account.is_admin():
            return True
        if self.group:
            if self.group.check_permission(checker, 'bbadmin'):
                return True
            else:
                return False
        elif self.locks.check(checker, "admin") and checkadmin:
            return True
        elif self.locks.check(checker, mode):
            return True
        else:
            return False

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
        from athanor.managers import ALL_MANAGERS
        return [char for char in ALL_MANAGERS.who.ndb.characters if self.check_permission(checker=char)
                and not char in self.ignore_list.all()]

    def make_post(self, character=None, subject=None, text=None, announce=True, date=None):
        if not character:
            raise ValueError("No player data to use.")
        if not text:
            raise ValueError("Text field empty.")
        if not subject:
            raise ValueError("Subject field empty.")
        if not date:
            date = utcnow()
        order = self.posts.all().count() + 1
        post = self.posts.create(owner=character, subject=subject, text=text, creation_date=date,
                                 modify_date=date, order=order)
        if announce:
            self.announce_post(post)
        return post

    def announce_post(self, post):

        post_data = {
            'board': self,
            'number': post.order,
            'source': post.owner,
            'anonymous': self.anonymous,
            'alias': self.alias,
            'group': self.group,
            'command': '+bbread'
        }

        postid = '%s/%s' % (self.alias, post.order)
        if self.group:
            board_name = '%s/%s' % (self.group.key, self.key)
        else:
            board_name = self.key
        clickable = mxp(text=postid, command='+bbread %s' % postid)
        text_message = "(New BB Message (%s) posted to '%s' by %s: %s)"
        message = text_message % (clickable, board_name, post.owner if not self.anonymous else self.anonymous,
                                  post.subject)
        for character in self.listeners():
            character.msg(message)


    def squish_posts(self):
        for count, post in enumerate(self.posts.order_by('order')):
            if post.order != count +1:
                post.order = count + 1
                post.save(update_fields=['order'])

    def display_board(self, viewer):
        """
        Viewer is meant to be a PlayerDB instance in this case! Since it needs to pull from Player read/unread.
        """
        message = list()
        message.append(viewer.render.header('%s - %s' % (self.category.name, self.key)))
        board_table = viewer.render.make_table(["ID", 'S', "Subject", "Date", "Poster"], width=[7, 2, 35, 9, 27])
        for post in self.posts.all().order_by('creation_date'):
            board_table.add_row("%s/%s" % (self.order, post.order), 'U' if viewer not in post.read.all() else '',
                                post.subject, viewer.time.display(date=post.creation_date, format='%x'),
                                post.display_poster(viewer))
        message.append(board_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def last_post(self, viewer):
        find = self.posts.all().order_by('creation_date').first()
        if find:
            return viewer.time.display(date=find.creation_date, format='%X %x %Z')
        else:
            return "None"

class Post(WithTimestamp):
    board = models.ForeignKey('Board', related_name='posts')
    owner = models.ForeignKey('objects.ObjectDB', related_name='posts')
    creation_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    text = models.TextField(blank=True)
    subject = models.CharField(max_length=30)
    order = models.PositiveIntegerField(null=True)
    anonymous = models.BooleanField(default=False)
    parent = models.ForeignKey('athanor-bbs.Post', related_name='comments', null=True)

    class Meta:
        unique_together = (('board', 'order'), ('parent', 'order'))

    def __unicode__(self):
        return unicode(self.subject)

    def __str__(self):
        return self.subject

    def can_edit(self, checker=None):
        if self.owner.object == checker:
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

    def display_poster(self, viewer):
        anon = self.board.anonymous
        if anon and viewer.is_admin():
            return "(%s)" % self.owner
        return anon or str(self.owner)

    def display_post(self, viewer):
        message = list()
        message.append(viewer.render.header(self.board.category.name))
        message.append("Message: %s/%s - By %s on %s" % (self.board.order, self.order, self.display_poster(viewer),
                                                         viewer.time.display(date=self.creation_date,format='%X %x %Z')))
        message.append(viewer.render.separator())
        message.append(self.text)
        message.append(viewer.render.footer())
        self.read.add(viewer)
        return "\n".join([unicode(line) for line in message])

class PostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read')
    post = models.ForeignKey('athanor-bbs.Post', related_name='read')
    read_date = models.DateTimeField(null=False)

    class Meta:
        unique_together = (('account', 'post'),)