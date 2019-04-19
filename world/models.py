import re
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property
from world.utils.time import utcnow
from world.utils.online import accounts as online_accounts


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


class WithLocks(models.Model):
    """
    Allows a Model to store Evennia-like Locks.

    Note that whenever you CHANGE locks on this Model you must manually call .save() or .save_locks()
    """
    lock_storage = models.TextField('locks', blank=True)

    class Meta:
        abstract = True

    @lazy_property
    def locks(self):
        return LockHandler(self)

    @property
    def access(self):
        return self.locks.check

    def save_locks(self):
        self.save(update_fields=['lock_storage'])


class StaffCategory(models.Model):
    key = models.CharField(max_length=255, null=False, blank=False, unique=True)
    order = models.PositiveSmallIntegerField(default=0, unique=True)

    def __str__(self):
        return self.key


class StaffEntry(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+', on_delete=models.CASCADE)
    category = models.ForeignKey(StaffCategory, related_name='staffers', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.CharField(max_length=255, default="On", null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    vacation = models.DateTimeField(null=True)

    def __str__(self):
        return self.account.key


class BoardCategory(WithLocks):
    key = models.CharField(max_length=255, unique=True, blank=False, null=False)
    abbr = models.CharField(max_length=5, unique=True, blank=True, null=False)
    board_locks = models.TextField(null=False, blank=False, default="read:all();post:all();admin:pperm(Admin)")

    def __str__(self):
        return self.key


class AccountStub(models.Model):
    """
    This holds 'stubs' of the Accounts meant for display purposes in the event that an Account is deleted.
    """
    account = models.OneToOneField('accounts.AccountDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.account:
            return str(self.account)
        return f"{self.key} |X(x {self.orig_id})|n"


class ObjectStub(models.Model):
    """
    This holds 'stubs' of the Characters meant for display purposes in the event that a Character is deleted.
    """
    obj = models.OneToOneField('objects.ObjectDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.obj:
            return str(self.obj)
        return f"{self.key} |X(x {self.orig_id})|n"


class Board(WithLocks):
    category = models.ForeignKey(BoardCategory, related_name='boards', null=False, on_delete=models.CASCADE)
    key = models.CharField(max_length=80, null=False, blank=False)
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
        return [acc for acc in online_accounts() if self.check_permission(checker=acc)
                and acc not in self.ignore_list.all()]

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
    account_stub = models.ForeignKey(AccountStub, related_name='+', on_delete=models.CASCADE)
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

    def post_alias(self):
        return f"{self.board.alias}/{self.order}"

    def can_edit(self, checker=None):
        if self.account_stub.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.modify_date = utcnow()
        self.text = self.text.replace(find, replace)
        self.save(update_fields=['text', 'modify_date'])

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.read_date = utcnow()
        acc_read.save()


class PostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='read', on_delete=models.CASCADE)
    read_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class JobBucket(WithLocks):
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)
    due = models.DurationField()
    description = models.TextField(blank=True, null=True)

    def make_job(self, account, title, opening):
        now = utcnow()
        due = now + self.due
        job = self.jobs.create(title=title, due_date=due, admin_update=now, public_update=now)
        handler = job.links.create(account_stub=account.stub, link_type=3, check_date=now)
        handler.make_comment(text=opening, comment_mode=0)
        handler.latest_check()
        text = f'Submitted by: {account}'
        job.announce(text)
        job.save()
        handler.save()
        return job

    def display(self, viewer, mode='display', page=1, header_text='', footer=False):
        message = list()
        message.append(viewer.render.header(header_text))
        admin = self.locks.check(viewer, 'admin')
        job_table = viewer.render.make_table(["*", "ID", "From", "Title", "Due", "Handling", "Upd", "LstAct"],
                                             width=[3, 4, 25, 18, 6, 10, 6, 8])
        start = (page - 1) * 30
        show = list()
        if mode == 'display':
            jobs = self.active()
            show = list(jobs[start:start + 30])
        elif mode == 'old':
            jobs = self.old()
            show = list(jobs[start:start + 30])
        elif mode == 'pending':
            jobs = self.pending()
            show = list(jobs[:20])
        else:
            jobs = mode
            show = list(jobs)
        show.reverse()
        for j in show:
            job_table.add_row(j.status_letter(), j.id, j.owner, j.title, j.display_due(viewer),
                              j.handler_names(), j.display_last(viewer, admin), j.last_from(admin))
        message.append(job_table)
        if footer:
            message.append(viewer.render.footer())
        return message

    def active(self):
        Q = models.Q
        interval = utcnow() - duration_from_string('7d')
        return self.jobs.filter(Q(status=0, close_date=None) | Q(close_date__gte=interval)).order_by('id').reverse()

    def pending(self):
        return self.jobs.filter(status=0).order_by('id').reverse()

    def old(self):
        return self.jobs.exclude(status=0).order_by('id').reverse()

    def new(self, viewer):
        Q = models.Q
        F = models.F
        interval = utcnow() - duration_from_string('14d')
        unseen_ids = self.jobs.exclude(characters__character=viewer)
        #updated = Q(submit_date__gte=interval)
        unseen = Q(id__in=unseen_ids)
        if self.locks.check(viewer, 'admin'):
            last = Q(characters__character=viewer, admin_update__gt=F('characters__check_date'))
        else:
            last = Q(characters__character=viewer, public_update__gt=F('characters__check_date'))
        jobs = self.jobs.filter(last | unseen).exclude(submit_date__lt=interval)
        jobs = jobs #.filter(unseen | last).order_by('id').reverse()
        return jobs


class Job(models.Model):
    bucket = models.ForeignKey(JobBucket, related_name='jobs', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    submit_date = models.DateTimeField(null=False)
    due_date = models.DateTimeField(null=False)
    close_date = models.DateTimeField(null=True)
    status = models.SmallIntegerField(default=0)
    # Status: 0 = Pending. 1 = Approved. 2 = Denied. 3 = Canceled
    anonymous = models.BooleanField(default=False)
    public_update = models.DateTimeField(null=True)
    admin_update = models.DateTimeField(null=True)

    def handlers(self):
        return self.links.filter(link_type=2)

    def handler_names(self):
        return ', '.join([hand.account for hand in self.handlers()])

    def helpers(self):
        return self.links.filter(link_type=1)

    def comments(self):
        return JobComment.objects.filter(handler__job=self).order_by('date_made')

    def status_letter(self):
        sta = {0: 'P', 1: 'A', 2: 'D', 3: 'C'}
        return sta[self.status]

    def status_word(self):
        sta = {0: 'Pending', 1: 'Approved', 2: 'Denied', 3: 'Canceled'}
        return sta[self.status]

    def display_due(self, viewer):
        return viewer.time.display(self.due_date, '%m/%d')

    def get_last(self, admin=False):
        if admin:
            return self.comments().last()
        return self.comments().exclude(is_private=1).last()

    def display_last(self, account, admin=False):
        date = self.public_update
        if admin:
            date = self.admin_update
        if not date:
            date = self.submit_date
        return account.display_time(date, '%m/%d')

    def __str__(self):
        return self.title

    @property
    def owner(self):
        return self.links.filter(link_type=3).first()

    @property
    def locks(self):
        return self.category.locks

    def last_from(self, admin):
        last = self.get_last(admin)
        return last.link_type_name()

    def announce_name(self):
        return f"{self.bucket.key} Job {self.id} '{self.title}'"

    def announce(self, message, only_admin=False):
        who = ALL_MANAGERS.who
        online = set(who.ndb.accounts)
        text = f"P{self.announce_name()}: {message}"
        admin = [acc for acc in online if self.access(acc, 'admin')]
        targets = list()
        if only_admin:
            targets += admin
            targets += self.handlers
        else:
            targets += admin
            targets += [char for char in self.links.all()]
        targets = set(targets)
        final_list = targets.intersection(online)

        for acc in final_list:
            acc.msg(text, system_alert='JOBS')

    def appoint_handler(self, enactor, target):
        ehandler, created1 = self.links.get_or_create(character=enactor)
        handler, created = self.links.get_or_create(character=target)
        if handler.is_handler:
            raise ValueError("%s is already handling this job!" % target)
        handler.is_handler = True
        handler.save(update_fields=['is_handler'])
        self.announce('%s added %s to Handlers.' % (enactor, target))
        ehandler.make_comment(comment_mode=8, text='%s' % target)

    def remove_handler(self, enactor, target):
        ehandler, created1 = self.links.get_or_create(character=enactor)
        handler, created = self.links.get_or_create(character=target)
        if not handler.is_handler:
            raise ValueError("%s is not handling this job!" % target)
        handler.is_handler = False
        handler.save(update_fields=['is_handler'])
        self.announce('%s removed %s from Handlers.' % (enactor, target))
        ehandler.make_comment(comment_mode=10, text='%s' % target)

    def appoint_helper(self, enactor, target):
        ehandler, created1 = self.links.get_or_create(character=enactor)
        handler, created = self.links.get_or_create(character=target)
        if handler.is_helper:
            raise ValueError("%s is already helping this job!" % target)
        handler.is_helper = True
        handler.save(update_fields=['is_helper'])
        self.announce('%s added %s to Helpers.' % (enactor, target))
        ehandler.make_comment(comment_mode=8, text='%s' % target)

    def remove_helper(self, enactor, target):
        ehandler, created1 = self.links.get_or_create(character=enactor)
        handler, created = self.links.get_or_create(character=target)
        if not handler.is_helper:
            raise ValueError("%s is not helping this job!" % target)
        handler.is_helper = False
        handler.save(update_fields=['is_helper'])
        self.announce('%s removed %s from Helpers.' % (enactor, target))
        ehandler.make_comment(comment_mode=11, text='%s' % target)

    def change_category(self, account, destination):
        oldcat = self.category
        newcat = destination
        self.announce(f'{account} moved job to: {destination}')
        self.category = newcat
        self.announce(f'{account} moved job from: {oldcat}')
        self.save(update_fields=['category', ])
        handler, created = self.links.get_or_create(account_stub=account.stub)
        handler.make_comment(comment_mode=3, text='%s to %s' % (oldcat, newcat))

    def display(self, viewer):
        admin = False
        if self.locks.check(viewer, 'admin') or self.links.filter(is_handler=True, character=viewer):
            admin = True
        message = list()
        message.append(viewer.render.header('%s Job %s' % (self.category.key, self.id)))
        message.append('important stuff here')
        if admin:
            comments = self.comments()
        else:
            comments = JobComment.objects.exclude(is_private=True).filter(handler__job=self).order_by('date_made')
        for com in comments:
            message.append(viewer.render.separator())
            message.append(com.display(viewer, admin))
        message.append(viewer.render.footer())
        handler, created = self.links.get_or_create(character=viewer)
        handler.check()
        return message

    def make_reply(self, enactor, contents):
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=1)
        name = enactor.key
        if handler.is_owner and self.anonymous:
            name = 'Anonymous'
        self.announce('%s sent a reply.' % name)

    def make_comment(self, enactor, contents):
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=1, is_private=True)
        self.announce('%s added a |rSTAFF COMMENT|n.' % enactor, only_admin=True)

    def set_approved(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be approved.")
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=4)
        self.status = 1
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s approved the job!' % enactor)

    def set_denied(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be denied.")
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=5)
        self.status = 2
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s denied the job!' % enactor)

    def set_canceled(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be canceled.")
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=6)
        self.status = 3
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s canceled the job!' % enactor)

    def set_pending(self, enactor, contents):
        if self.status == 0:
            raise ValueError("Job is not finished, cannot be revived.")
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=7)
        self.status = 0
        self.close_date = None
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s revived the job!' % enactor)

    def set_due(self, enactor, new_date):
        self.due_date = new_date
        self.save(update_fields=['due_date'])
        handler, created = self.links.get_or_create(character=enactor)
        handler.make_comment(comment_mode=12, text='%s' % self.due_date)
        self.announce('%s changed the Due Date to: %s' % (enactor, self.due_date))


class JobLink(models.Model):
    account_stub = models.ForeignKey(AccountStub, related_name='job_handling', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='links', on_delete=models.CASCADE)
    link_type = models.PositiveSmallIntegerField(default=0)
    check_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = (("account_stub", "job"),)

    def __str__(self):
        return str(self.account_stub)

    def latest_check(self):
        self.check_date = utcnow()
        self.save(update_fields=['check_date'])

    def make_comment(self, comment_mode=1, text=None, is_private=False):
        now = utcnow()
        if not is_private:
            self.job.public_update = now
        self.job.admin_update = now
        self.job.save(update_fields=['admin_update', 'public_update'])
        self.comments.create(comment_mode=comment_mode, text=text, is_private=is_private, date_made=now)

    def link_type_name(self):
        return {0: 'Admin', 1: 'Helper', 2: 'Handler', 3: 'Owner'}.get(int(self.link_type))

class JobComment(models.Model):
    link = models.ForeignKey(JobLink, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True, default=None)
    is_private = models.BooleanField(default=False)
    date_made = models.DateTimeField()
    comment_mode = models.PositiveSmallIntegerField(default=1)
    # Comment Mode: 0 = Opening. 1 = Reply. 2 = Staff Comment. 3 = Moved. 4 = Approved.
    # 5 = Denied. 6 = Canceled. 7 = Revived. 8 = Appoint Handler. 9 = Appoint Helper.
    # 10 = Removed Handler. 11 = Removed Helper. 12 = Due Date Changed

    def __str__(self):
        return self.text

    def poster(self):
        if self.link.job.anonymous and self.link.is_owner:
            return 'Anonymous'
        return self.link.character.key

    def display(self, viewer, admin=False):
        kind = {0: 'Opened', 1: 'Replied', 2: '|rSTAFF COMMENTED|n', 3: 'Moved', 4: 'Approved',
                5: 'Denied', 6: 'Canceled', 7: 'Revived', 8: 'Appointed Handler', 9: 'Appointed Helper',
                10: 'Removed Handler', 11: 'Removed Helper', 12: 'Due Date Changed'}
        name = self.poster()
        date = viewer.time.display(self.date_made)
        message = "%s %s on %s:" % (name, kind[self.comment_mode], date)
        if self.comment_mode in (3, 8, 9, 10, 11, 12):
            message += " %s" % self.text
        else:
            message += "\n\n%s" % self.text
        return message


class EquipSlotType(models.Model):
    key = models.CharField(max_length=80, blank=False, null=False, unique=True)


class EquipSlot(models.Model):
    holder = models.ForeignKey('objects.ObjectDB', related_name='equipped', on_delete=models.CASCADE)
    slot = models.ForeignKey('mud.EquipSlotType', related_name='users', on_delete=models.CASCADE)
    layer = models.PositiveIntegerField(default=0, null=False)
    item = models.ForeignKey('objects.ObjectDB', related_name='equipped_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('holder', 'slot', 'layer'), )


class MapRegion(models.Model):
    """
    MapRegions are just names to organize the Maps under.
    """
    key = models.CharField(max_length=255, blank=False, null=False)
    category = models.PositiveSmallIntegerField(default=0, null=False)

    def scan_x(self, x_start, y_start, z_start, x_distance):
        """
        Returns a MapScan along an X coordinate.

        Args:
            x_start (int): The left-most point on the map to begin the scan.
            y_start (int): The upper-most point on the map to begin the scan.
            z_start (int): The z-plane we'll be showing.
            x_distance (int): How many map squares (including the start) to the right to show.
            y_distance (int): How many map squares down (including start) should be shown.

        Returns:
            XArray (list): A List of Rooms and Nones depending on coordinates given.
        """

        plane = self.points.filter(z_coordinate=z_start, y_coordinate=y_start)
        results = list()
        for x in range(0, x_distance):
            find = plane.filter(x_coordinate=x_start + x).first()
            if find:
                results.append(find)
            else:
                results.append(None)
        return results

    def scan(self, x_start, y_start, z_start, x_distance, y_distance):
        """
        Returns a MapScan along an X coordinate.

        Args:
            x_start (int): The left-most point on the map to begin the scan.
            y_start (int): The upper-most point on the map to begin the scan.
            z_start (int): The z-plane we'll be showing.
            x_distance (int): How many map squares (including the start) to the right to show.
            y_distance (int): How many map squares down (including start) should be shown.

        Returns:
            2DMap (list): A two-dimensional list (list of lists) of XArrays.
        """
        results = list()
        for y in range(0, y_distance):
            results.append(self.scan_x(x_start, y_start - y, z_start, x_distance))
        return results


class HasXYZ(models.Model):
    x_coordinate = models.IntegerField(null=False, db_index=True)
    y_coordinate = models.IntegerField(null=False, db_index=True)
    z_coordinate = models.IntegerField(null=False, db_index=True)

    class Meta:
        abstract = True


class MapPoint(HasXYZ):
    """
    Each Room can be a member of a single Map.

    Two Rooms may not inhabit the same coordinates.
    """
    room = models.OneToOneField('objects.ObjectDB', related_name='map_point', on_delete=models.CASCADE)
    region = models.ForeignKey(MapRegion, related_name='points', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('region', 'x_coordinate', 'y_coordinate', 'z_coordinate'), )


class Plot(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    type = models.CharField(max_length=40, blank=True, null=True)

    def display_plot(self, viewer):
        message = list()
        message.append(viewer.render.header('Plot ID %i: %s' % (self.id, self.title)))
        message.append('Runner: %s' % self.owner)
        message.append('Schedule: %s to %s' % (viewer.time.display(date=self.date_start),
                                               viewer.time.display(date=self.date_end)))
        message.append('Status: %s' % ('Running' if not self.status else 'Finished'))
        message.append(self.description)
        message.append(viewer.render.separator('Scenes'))
        scenes_table = viewer.render.make_table(['ID', 'Name', 'Date', 'Description,', 'Participants'],
                                                width=[3, 10, 10, 10, 30])
        for scene in self.scenes.all().order_by('date_created'):
            scenes_table.add_row(scene.id, scene.title, viewer.time.display(date=scene.date_created),
                                 scene.description, '')
        message.append(scenes_table)
        message.append(viewer.render.separator('Events'))
        events_table = viewer.render.make_table('ID', 'Name', 'Date', width=[3, 10, 10])
        for event in self.events.all().order_by('date_schedule'):
            events_table.add_row(event.id, event.title, viewer.time.display(date=event.date_schedule))
        message.append(events_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    @property
    def recipients(self):
        return [char.character for char in self.participants]

    @property
    def participants(self):
        return Participant.objects.filter(event__in=self.events).values_list('character', flat=True)

    @property
    def owner(self):
        found = self.runners.filter(owner=True).first()
        if found:
            return found.character
        return None


class Runner(models.Model):
    plot = models.ForeignKey('scene.Plot', related_name='runners', on_delete=models.CASCADE)
    character = models.ForeignKey(ObjectStub, related_name='plots', on_delete=models.CASCADE)
    runner_type = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (('plot', 'character',),)


class Event(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    pitch = models.TextField(blank=True, null=True, default=None)
    outcome = models.TextField(blank=True, null=True, default=None)
    date_created = models.DateTimeField()
    date_scheduled = models.DateTimeField(null=True)
    date_started = models.DateTimeField(null=True)
    date_finished = models.DateTimeField(null=True)
    plot = models.ForeignKey('Plot', null=True, related_name='scene')
    post = models.OneToOneField('bbs.Post', related_name='event', null=True)
    public = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(default=0, db_index=True)
    log_ooc = models.BooleanField(default=True)
    log_channels = models.ManyToManyField('comms.ChannelDB', related_name='log_events')
    private = models.BooleanField(default=False)
    # Status: 0 = Active. 1 = Paused. 2 = ???. 3 = Finished. 4 = Scheduled. 5 = Canceled.

    def display(self, viewer):
        message = list()
        message.append(viewer.render.header('Scene %i: %s' % (self.id, self.title)))
        message.append('Started: %s' % viewer.time.display(date=self.date_created))
        if self.date_finished:
            message.append('Finished: %s' % viewer.time.display(date=self.date_finished))
        message.append('Description: %s' % self.description)
        message.append('Owner: %s' % self.owner)
        message.append('Status: %s' % self.display_status())
        message.append(viewer.render.separator('Players'))
        player_table = viewer.render.make_table(['Name', 'Status', 'Poses'], width=[35, 30, 13])
        for participant in self.participants.order_by('character'):
            player_table.add_row(participant.character, '', participant.poses.exclude(ignore=True).count())
        message.append(player_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def display_status(self):
        sta = {0: 'Active', 1: 'Paused', 2: '???', 3: 'Finished', 4: 'Scheduled', 5: 'Canceled'}
        return sta[self.status]

    def msg(self, text):
        for character in self.recipients:
            character.msg(text)

    @property
    def recipients(self):
        recip_list = list()
        if self.owner: recip_list.append(self.owner)
        recip_list += [char.character for char in self.participants]
        return set(recip_list)

    @property
    def actions(self):
        return Action.objects.filter(owner__event=self)


class Participant(models.Model):
    character = models.ForeignKey('objects.ObjectDB', related_name='scene')
    event = models.ForeignKey('scene.Event', related_name='participants')
    owner = models.BooleanField(default=False)
    tag = models.BooleanField(default=False)

    class Meta:
        unique_together = (("character", "event"),)


class Source(models.Model):
    key = models.CharField(max_length=255)
    channel = models.ForeignKey('comms.ChannelDB', null=True, related_name='event_logs', on_delete=models.SET_NULL)
    location = models.ForeignKey('objects.ObjectDB', null=True, related_name='poses_here', on_delete=models.SET_NULL)
    mode = models.PositiveSmallIntegerField(default=0)
    # mode: 0 = 'Location Pose'. 1 = Public Channel. 2 = Group IC. 3 = Group OOC. 4 = Radio. 5 = Local OOC. 6 = Combat

    class Meta:
        unique_together = (('key', 'channel', 'location'),)


class Action(models.Model):
    event = models.ForeignKey('scene.Event', related_name='actions')
    owner = models.ForeignKey('scene.Participant', related_name='actions')
    ignore = models.BooleanField(default=False, db_index=True)
    date_made = models.DateTimeField(db_index=True)
    text = models.TextField(blank=True)
    codename = models.CharField(max_length=255, null=True, blank=True, default=None)
    source = models.ForeignKey('scene.Source', related_name='actions')


    def display_pose(self, viewer):
        message = []
        message.append(viewer.render.separator('%s Posed on %s' % (self.owner,
                                                                   viewer.time.display(date=self.date_made))))
        message.append(self.text)
        return "\n".join([unicode(line) for line in message])