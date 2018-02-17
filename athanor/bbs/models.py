from __future__ import unicode_literals
import re
from django.db import models
from django.conf import settings
from athanor.core.models import WithTimestamp, WithLocks
from athanor.utils.time import utcnow
from athanor.utils.text import mxp, sanitize_string, partial_match
from athanor.utils.online import characters

# Create your models here.


class BoardGroup(models.Model):
    group = models.OneToOneField('groups.Group', null=True, related_name='board')
    main = models.BooleanField(default=1)

    class Meta:
        unique_together = (('group', 'main'),)

    @property
    def list(self):
        return self.boards.all().order_by('order')

    @property
    def timeout(self):
        pass

    @property
    def posts(self):
        return Post.objects.filter(board__category=self)

    @property
    def name(self):
        if self.group:
            return "(GBS) %s Boards" % self.group
        return "(BBS) %s Boards" % settings.SERVERNAME

    def usable_boards(self, checker, checkadmin=True):
        return [board for board in self.list if board.check_permission(checker, checkadmin=checkadmin)]

    def visible_boards(self, checker, checkadmin=True):
        return [board for board in self.usable_boards(checker, checkadmin) if checker not in board.ignore_list.all()]

    def boards_list(self, checker, viewer):
        message = list()
        message.append(viewer.player.render.header(self.name))
        bbtable = viewer.player.render.make_table(["ID", "RWA", "Name", "Locks", "On"], width=[4, 4, 25, 43, 4])
        for board in self.usable_boards(checker=checker):
            if checker in board.ignore_list.all():
                member = "No"
            else:
                member = "Yes"
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.order), board.display_permissions(checker),
                            mxp(board, "+bbread %s" % board.order), board.lock_storage, member)
        message.append(bbtable)
        message.append(viewer.player.render.footer())
        return '\n'.join(unicode(line) for line in message)

    def find_board(self, find_name=None, checker=None, visible_only=True):
        if not find_name:
            raise ValueError("No board entered to find!")
        if checker:
            if visible_only:
                boards = self.visible_boards(checker)
            else:
                boards = self.usable_boards(checker)
        else:
            boards = self.list
        if not boards:
            raise ValueError("No applicable boards.")
        try:
            find_num = int(find_name)
        except ValueError:
            find_board = partial_match(find_name, boards)
            if not find_board:
                raise ValueError("Board '%s' not found." % find_name)
            return find_board
        else:
            if find_num not in [board.order for board in boards]:
                raise ValueError("Board '%s' not found." % find_name)
            return [board for board in boards if board.order == find_num][0]

    def process_timeout(self):
        if self.timeout:
            for board in self.boards.all():
                board.process_timeout()

    def make_board(self, key=None):
        if not key:
            raise ValueError("Board requires a name.")
        new_name = sanitize_string(key, strip_ansi=True)
        try:
            new_num = max([board.order for board in self.boards.all()]) + 1
        except ValueError:
            new_num = 1
        board = self.boards.create(key=new_name, order=new_num)
        board.init_locks()
        return board

    def display_boards(self, checker, viewer):
        message = list()
        message.append(viewer.render.header(self.name))
        bbtable = viewer.render.make_table(["ID", "RWA", "Name", "Last Post", "#", "U"], width=[4, 4, 37, 25, 5, 5])
        for board in self.visible_boards(checker=checker):
            bbtable.add_row(mxp(board.order, "+bbread %s" % board.order),
                            board.display_permissions(checker), mxp(board, "+bbread %s" % board.order),
                            board.last_post(checker), board.posts.all().count(),
                            board.posts.exclude(read=viewer).count())
        message.append(bbtable)
        message.append(viewer.render.footer())
        return '\n'.join(unicode(line) for line in message)


class Board(WithLocks):
    category = models.ForeignKey('bbs.BoardGroup', related_name='boards')
    key = models.CharField(max_length=40)
    order = models.PositiveSmallIntegerField(default=0)
    ignore_list = models.ManyToManyField('objects.ObjectDB')
    anonymous = models.CharField(max_length=80, null=True)
    timeout = models.DurationField(null=True)
    mandatory = models.BooleanField(default=False)

    def __unicode__(self):
        return self.key

    def __int__(self):
        return self.order

    class Meta:
        unique_together = (('category', 'key'), ('category', 'order'))

    def init_locks(self):
        if self.category.group:
            group_id = self.category.group.id
            locks = 'read:group(%i);write:group(%i);admin:gbadmin(%i)' % (group_id, group_id, group_id)
        else:
            locks = 'read:all();write:all();admin:perm(Wizards)'
        self.lock_storage = locks
        self.save_locks()

    @property
    def group(self):
        return self.category.group

    def parse_postnums(self, player, check=None):
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
                fullnums += self.posts.exclude(read__contains=player).values_list('order', flat=True)
        return self.posts.filter(order__in=fullnums).order_by('order')

    def check_permission(self, checker=None, mode="read", checkadmin=True):
        if checker.account.is_admin():
            return True
        if self.group:
            if self.group.check_permission(checker, 'gbadmin'):
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
        if self.check_permission(checker=checker, mode="write", checkadmin=False):
            acc += "W"
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
                                 modify_date=date, timeout=self.timeout, order=order)
        if announce:
            self.announce_post(post)
        return post

    def announce_post(self, post):
        postid = '%s/%s' % (self.order, post.order)
        if self.group:
            clickable = mxp(text=postid, command='+gbread %s=%s' % (postid, self.group.name))
            text_message = "{cM<GROUP BB>{n New GB Message (%s) posted to '%s' '%s' by %s: %s"
            message = text_message % (clickable, self.group, self, post.owner if not self.anonymous else self.anonymous,
                                                                                             post.subject)
            for character in self.listeners():
                character.msg(message)
        else:
            clickable = mxp(text=postid, command='+bbread %s' % postid)
            text_message = "(New BB Message (%s) posted to '%s' by %s: %s)"
            message = text_message % (clickable, self, post.owner if not self.anonymous else self.anonymous,
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

    def process_timeout(self):
        if not self.timeout:
            return
        check_list = [post.process_timeout() for post in self.posts.all()]
        if True in check_list:
            self.squish_posts()


class Post(WithTimestamp):
    board = models.ForeignKey('Board', related_name='posts')
    owner = models.ForeignKey('objects.ObjectDB', related_name='posts')
    creation_date = models.DateTimeField(null=True)
    timeout_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    text = models.TextField(blank=True)
    subject = models.CharField(max_length=30)
    timeout = models.DurationField(null=True)
    remaining_timeout = models.FloatField(null=True)
    read = models.ManyToManyField('accounts.AccountDB')
    order = models.PositiveSmallIntegerField(null=True)

    def __unicode__(self):
        return unicode(self.subject)

    def __str__(self):
        return self.subject

    def remaining_time(self):
        if not self.timeout:
            return '(No Timeout)'
        rem_time = (self.timeout_date or self.creation_date) + self.timeout
        if rem_time > utcnow():
            rem_time = 'Timed out!'
        if not self.board.timeout:
            return '(Board Timeouts Disabled - %s)' % rem_time
        if not self.board.category.timeout:
            return '(Timeouts Disabled - %s)' % rem_time
        else:
            return '(Time Left: %s)' % rem_time

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

    def process_timeout(self):
        if not self.timeout:
            return
        start_date = self.timeout_date or self.creation_date
        check_date = start_date + self.timeout
        if check_date < utcnow():
            self.delete()
            return True

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