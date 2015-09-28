from django.db import models
from django.conf import settings
from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property
from commands.library import utcnow, mxp_send, connected_characters, AthanorError, header, separator, make_table

# Create your models here.
class Board(models.Model):
    key = models.CharField(max_length=40)
    order = models.IntegerField()
    main = models.BooleanField(default=True)
    group = models.ForeignKey('groups.Group', null=True, related_name='boards')
    lock_storage = models.TextField('locks', blank=True)
    ignore_list = models.ManyToManyField('objects.ObjectDB')
    anonymous = models.CharField(max_length=40, null=True)
    timeout = models.FloatField(default=0.0, null=True)
    mandatory = models.BooleanField(default=False)

    def __unicode__(self):
        return self.key

    def __int__(self):
        return self.order

    @lazy_property
    def locks(self):
        return LockHandler(self)

    def display_name(self):
        if self.group:
            return "(GBS) %s Boards - %s" % (self.group, self)
        return "(BBS) %s Boards - %s" % (settings.SERVERNAME, self)

    def check_permission(self, checker=None, type="read", checkadmin=True):
        if checker.is_admin():
            return True
        if self.group:
            if self.group.check_permission(checker, 'gbadmin'):
                return True
            else:
                return False
        elif self.locks.check(checker, "admin") and checkadmin:
            return True
        elif self.locks.check(checker, type):
            return True
        else:
            return False

    def display_permissions(self, checker=None):
        if not checker:
            return " "
        acc = ""
        if self.perm_check(checker=checker, type="read", checkadmin=False):
            acc += "R"
        else:
            acc += " "
        if self.perm_check(checker=checker, type="write", checkadmin=False):
            acc += "W"
        else:
            acc += " "
        if self.perm_check(checker=checker, type="admin", checkadmin=False):
            acc += "A"
        else:
            acc += " "
        return acc

    def listeners(self):
        return [char for char in connected_characters() if self.perm_check(checker=char)
                and not self.ignore_list.filter(id=char.id)]

    def make_post(self, actor=None, subject=None, text=None, announce=True, date=utcnow()):
        if not actor:
            raise AthanorError("No player data to use.")
        if not text:
            raise AthanorError("Text field empty.")
        if not subject:
            raise AthanorError("Subject field empty.")
        post = self.posts.create(actor=actor, post_subject=subject, post_text=text, post_date=date,
                                 modify_date=date, setting_timeout=self.setting_timeout,
                                 remaining_timeout=self.setting_timeout)
        self.squish_posts()
        if announce: self.announce_post(post)

    def announce_post(self, post):
        postid = '%s/%s' % (self.order, post.order)
        if self.group:
            clickable = mxp_send(text=postid, command='+gbread %s=%s' % (postid, self.group.name))
            text_message = "{cM<GROUP BB>{n New GB Message (%s) posted to '%s' '%s' by %s: %s"
            message = text_message % (clickable, self.group, self, post.actor if not self.anonymous else self.anonymous,
                                                                                             post.post_subject)
            for character in self.listeners():
                character.msg(message)
        else:
            clickable = mxp_send(text=postid, command='+bbread %s' % postid)
            text_message = "(New BB Message (%s) posted to '%s' by %s: %s)"
            message = text_message % (clickable, self, post.actor if not self.anonymous else self.anonymous,
                                      post.post_subject)
            for character in self.listeners():
                character.msg(message)

    def squish_posts(self):
        for count, post in enumerate(self.posts.order_by('post_date')):
            if not post.order == count +1:
                post.order = count + 1
                post.save()

    def show_board(self, viewer):
        """
        Viewer is meant to be a PlayerDB instance in this case! Since it needs to pull from Player read/unread.
        """
        message = []
        message.append(header(self.display_name()))
        board_table = make_table("ID", "Subject", "Date", "Poster", width=[6, 29, 22, 21])
        for post in self.posts.all().order_by('post_date'):
            board_table.add_row(post.order, post.post_subject,
                                viewer.display_local_time(date=post.date_posted, format='%X %x %Z'),
                                post.display_poster(viewer))
        message.append(board_table)
        message.append(header)
        return "\n".join([unicode(line) for line in message])

class Post(models.Model):
    board = models.ForeignKey('Board', related_name='posts')
    actor = models.ForeignKey('communications.ObjectActor')
    post_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    post_text = models.TextField()
    post_subject = models.CharField(max_length=30)
    setting_timeout = models.FloatField(null=True)
    remaining_timeout = models.FloatField(null=True)
    read = models.ManyToManyField('players.PlayerDB')
    order = models.IntegerField(null=True)

    def __unicode__(self):
        return unicode("Post %s: %s" % (self.order, self.post_subject))

    def can_edit(self, checker=None):
        if self.actor.object == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise AthanorError("No text entered to find.")
        if not replace:
            replace = ''
        self.modify_date = utcnow()
        self.post_text = self.post_text.replace(find, replace)
        self.save()

    def display_poster(self, viewer):
        anon = self.board.anonymous
        if anon and viewer.is_admin():
            return "(%s)" % self.actor
        return anon or self.actor

    def show_post(self, viewer):
        message = []
        message.append(header(self.board.display_name()))
        message.append('testing stuff here')
        message.append(separator())
        message.append(self.post_text)
        message.append(header())
        self.read.add(viewer)
        return "\n".join([unicode(line) for line in message])