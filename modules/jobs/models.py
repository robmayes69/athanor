from django.db import models
from modules.core.models import WithLocks
from utils.time import utcnow
from utils.online import accounts as online_accounts
from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
from evennia.utils.validatorfuncs import duration


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
    owner = models.ForeignKey('core.AccountCharacterStub', related_name='job_handling', on_delete=models.DO_NOTHING)
    job = models.ForeignKey(Job, related_name='links', on_delete=models.CASCADE)
    link_type = models.PositiveSmallIntegerField(default=0)
    check_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = (("owner", "job"),)

    def __str__(self):
        return str(self.owner)

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

    @property
    def is_owner(self):
        return self.link_type == 3


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
        return self.link.owner

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