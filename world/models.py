import re
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils.validatorfuncs import duration
from evennia.utils import lazy_property, time_format
from world.utils.time import utcnow
from world.utils.online import accounts as online_accounts, puppets as online_puppets


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


class ChannelStub(models.Model):
    channel = models.OneToOneField('comms.ChannelDB', related_name='stub_model', on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255, null=False, blank=False)
    orig_id = models.PositiveIntegerField(null=False)

    def __str__(self):
        if self.channel:
            return str(self.channel)
        return f"{self.key} |X(x {self.orig_id})|n"


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
    account_stub = models.ForeignKey(AccountStub, related_name='+', on_delete=models.CASCADE)
    object_stub = models.ForeignKey(ObjectStub, related_name='+', on_delete=models.CASCADE)
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

    def __str__(self):
        return self.key

    def make_job(self, account, title, opening):
        now = utcnow()
        due = now + self.due
        job = self.jobs.create(title=title, submit_date=now, due_date=due, admin_update=now, public_update=now)
        job.save()
        handler = job.links.create(account_stub=account.stub, link_type=3, check_date=now)
        handler.save()
        handler.make_comment(text=opening, comment_mode=0)
        handler.latest_check()
        return job

    def display(self, account, mode='display', page=1, per_page=30):
        message = list()
        admin = self.access(account, 'admin')
        start = (page - 1) * per_page
        show = list()
        if mode == 'display':
            jobs = self.active()
            show = list(jobs[start:start + per_page])
        elif mode == 'old':
            jobs = self.old()
            show = list(jobs[start:start + per_page])
        elif mode == 'pending':
            jobs = self.pending()
            show = list(jobs[:per_page])
        show.reverse()
        for j in show:
            message.append(j.display_line(account, admin, mode))
        return message

    def active(self):
        Q = models.Q
        interval = utcnow() - duration('7d')
        return self.jobs.filter(Q(status=0, close_date=None) | Q(close_date__gte=interval)).order_by('id').reverse()

    def pending(self):
        return self.jobs.filter(status=0).order_by('id').reverse()

    def old(self):
        return self.jobs.exclude(status=0).order_by('id').reverse()

    def new(self, viewer):
        Q = models.Q
        F = models.F
        interval = utcnow() - duration('14d')
        unseen_ids = self.jobs.exclude(links__account_stub=viewer.stub)
        #updated = Q(submit_date__gte=interval)
        unseen = Q(id__in=unseen_ids)
        if self.locks.check(viewer, 'admin'):
            last = Q(links__account_stub=viewer.stub, admin_update__gt=F('links__check_date'))
        else:
            last = Q(links__account_stub=viewer.stub, public_update__gt=F('links__check_date'))
        jobs = self.jobs.filter(last | unseen).exclude(submit_date__lt=interval)
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
        return ', '.join([str(hand) for hand in self.handlers()])

    def helpers(self):
        return self.links.filter(link_type=1)

    def helper_names(self):
        return ', '.join([str(hand) for hand in self.helpers()])

    def comments(self):
        return JobComment.objects.filter(link__job=self).order_by('date_made')

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
        return self.bucket.locks

    def last_from(self, admin):
        last = self.get_last(admin)
        return last.link_type_name()

    def announce_name(self):
        return f"{self.bucket.key} Job {self.id} '{self.title}'"

    def announce(self, message, only_admin=False):
        online = online_accounts()
        text = f"P{self.announce_name()}: {message}"
        admin = [acc for acc in online if self.bucket.access(acc, 'admin')]
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

    def display_line(self, account, admin, mode=None):
        start = f"{self.unread_star(account, admin)}{self.status_letter()}"
        num = str(self.id).rjust(4).ljust(5)
        owner_link = self.owner
        owner = str(self.owner) if owner_link else ''
        owner = owner[:15].ljust(16)
        title = self.title[:29].ljust(30)
        claimed = self.handler_names()[:12].ljust(13)
        now = utcnow().timestamp()
        last_updated = self.public_update.timestamp()
        if admin:
            last_updated = max(self.admin_update.timestamp(), last_updated)
        due = self.due_date.timestamp() - now
        if due <= 0:
            due = ANSIString("|rOVER|n")
        else:
            due = time_format(due, 1)
        due = due.rjust(6).ljust(7)
        last = time_format(now - last_updated, 1).rjust(4)
        return f"{start} {num}{owner}{title}{claimed}{due}{last}"

    def unread_star(self, account, admin=False):
        link = self.links.filter(account_stub__account=account).first()
        if not link:
            return ANSIString('|r*|n')
        if admin:
            if max(self.admin_update, self.public_update) > link.check_date:
                return ANSIString('|r*|n')
            else:
                return " "
        if self.public_update > link.check_date:
            return ANSIString('|r*|n')
        else:
            return " "

    def get_link(self, account):
        link, created = self.links.get_or_create(account_stub=account.stub)
        if created:
            link.save()
        return link

    def make_comment(self, account, comment_mode=1, text=None, is_private=False):
        link = self.get_link(account)
        return link.make_comment(comment_mode, text, is_private)

    def update_read(self, account):
        link = self.get_link(account)
        link.latest_check()


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
        return self.comments.create(comment_mode=comment_mode, text=text, is_private=is_private, date_made=now)

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
        return self.link.account_stub

    def action_phrase(self):
        kind = {0: 'Opened', 1: 'Replied', 2: '|rSTAFF COMMENTED|n', 3: 'Moved', 4: 'Approved',
                5: 'Denied', 6: 'Canceled', 7: 'Revived', 8: 'Appointed Handler', 9: 'Appointed Helper',
                10: 'Removed Handler', 11: 'Removed Helper', 12: 'Due Date Changed'}
        return kind[self.comment_mode]

    def display(self, viewer, admin=False):
        show_date = viewer.display_time(time_disp=self.date_made)
        message = f"{self.poster()} |w{self.action_phrase()} on {show_date}:|n"
        if self.comment_mode in (3, 8, 9, 10, 11, 12):
            message += " %s" % self.text
        else:
            message += "\n\n%s" % self.text
        return message


class EquipSlotType(models.Model):
    key = models.CharField(max_length=80, blank=False, null=False, unique=True)


class EquipSlot(models.Model):
    holder = models.ForeignKey('objects.ObjectDB', related_name='equipped', on_delete=models.CASCADE)
    slot = models.ForeignKey(EquipSlotType, related_name='users', on_delete=models.CASCADE)
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
    plot = models.ForeignKey(Plot, related_name='runners', on_delete=models.CASCADE)
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
    plot = models.ForeignKey('Plot', null=True, related_name='scene', on_delete=models.SET_NULL)
    post = models.OneToOneField(Post, related_name='event', null=True, on_delete=models.SET_NULL)
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
    character = models.ForeignKey(ObjectStub, related_name='scene', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='participants', on_delete=models.CASCADE)
    participant_type = models.PositiveSmallIntegerField(default=0)
    action_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("character", "event"),)


class Source(models.Model):
    key = models.CharField(max_length=255)
    channel = models.ForeignKey('comms.ChannelDB', null=True, related_name='event_logs', on_delete=models.SET_NULL)
    location = models.ForeignKey(ObjectStub, null=True, related_name='poses_here', on_delete=models.SET_NULL)
    mode = models.PositiveSmallIntegerField(default=0)
    # mode: 0 = 'Location Pose'. 1 = Public Channel. 2 = Group IC. 3 = Group OOC. 4 = Radio. 5 = Local OOC. 6 = Combat

    class Meta:
        unique_together = (('key', 'channel', 'location'),)


class Action(models.Model):
    event = models.ForeignKey(Event, related_name='actions', on_delete=models.CASCADE)
    owner = models.ForeignKey(Participant, related_name='actions', on_delete=models.CASCADE)
    ignore = models.BooleanField(default=False, db_index=True)
    date_made = models.DateTimeField(db_index=True)
    text = models.TextField(blank=True)
    codename = models.CharField(max_length=255, null=True, blank=True, default=None)
    location = models.ForeignKey(ObjectStub, related_name='actions_here', null=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey(ChannelStub, related_name='actions_logged', null=True, on_delete=models.SET_NULL)


    def display_pose(self, viewer):
        message = []
        message.append(viewer.render.separator('%s Posed on %s' % (self.owner,
                                                                   viewer.time.display(date=self.date_made))))
        message.append(self.text)
        return "\n".join([unicode(line) for line in message])