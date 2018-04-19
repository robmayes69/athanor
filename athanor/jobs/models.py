from __future__ import unicode_literals
from django.db import models
from athanor.core.models import WithKey, WithLocks
from athanor.utils.time import utcnow, duration_from_string


class JobBucket(WithKey, WithLocks):
    anonymous = models.BooleanField(default=False)
    due = models.DurationField()
    description = models.TextField(blank=True, null=True, default=None)

    def setup(self):
        self.locks.add('admin:perm(Wizards);post:all()')
        self.save_locks()

    def make_job(self, source, title, opening):
        now = utcnow()
        due = now + self.due
        job = self.jobs.create(title=title, due_date=due, anonymous=self.anonymous, admin_update=now, public_update=now)
        handler = job.characters.create(character=source, is_owner=True, check_date=now)
        handler.make_comment(text=opening, comment_mode=0)
        handler.check()
        text = 'Submitted by: %s'
        if self.anonymous:
            msg = text % 'Anonymous'
        else:
            msg = text % source.key
        job.announce(msg)

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
    bucket = models.ForeignKey('jobs.JobBucket', related_name='jobs')
    title = models.CharField(max_length=255)
    submit_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    close_date = models.DateTimeField(null=True)
    status = models.SmallIntegerField(default=0)
    # Status: 0 = Pending. 1 = Approved. 2 = Denied. 3 = Canceled
    anonymous = models.BooleanField(default=False)
    public_update = models.DateTimeField(null=True)
    admin_update = models.DateTimeField(null=True)

    def handlers(self):
        return self.characters.filter(is_handler=True)

    def handler_names(self):
        return ', '.join([hand.character.key for hand in self.handlers()])

    def helpers(self):
        return self.characters.filter(is_helper=True)

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

    def display_last(self, viewer, admin=False):
        date = self.public_update
        if admin:
            date = self.admin_update
        if not date:
            date = self.submit_date
        return viewer.time.display(date, '%m/%d')

    def __str__(self):
        return self.title

    @property
    def owner(self):
        return self.characters.filter(is_owner=True).first()

    @property
    def locks(self):
        return self.category.locks

    def last_from(self, admin):
        last = self.get_last(admin)
        handler = last.handler
        if handler.is_owner:
            return 'Owner'
        if handler.is_handler:
            return 'Handler'
        if handler.is_helper:
            return 'Helper'
        return 'Admin'

    def announce_name(self):
        return "%s Job %s '%s'" % (self.category.key, self.id, self.title)

    def announce(self, message, only_admin=False):
        from athanor.managers import ALL_MANAGERS
        who = ALL_MANAGERS.who
        online = set(who.ndb.characters)
        text = ("%s: %s" % (self.announce_name(), message))
        admin = [char for char in online if self.locks.check(char, 'admin')]
        targets = list()
        if only_admin:
            targets += admin
            targets += self.handlers
        else:
            targets += admin
            targets += [char for char in self.characters.all()]
        targets = set(targets)
        final_list = targets.intersection(online)

        for char in final_list:
            char.sys_msg(text, sys_name='JOBS')

    def appoint_handler(self, enactor, target):
        ehandler, created1 = self.characters.get_or_create(character=enactor)
        handler, created = self.characters.get_or_create(character=target)
        if handler.is_handler:
            raise ValueError("%s is already handling this job!" % target)
        handler.is_handler = True
        handler.save(update_fields=['is_handler'])
        self.announce('%s added %s to Handlers.' % (enactor, target))
        ehandler.make_comment(comment_mode=8, text='%s' % target)

    def remove_handler(self, enactor, target):
        ehandler, created1 = self.characters.get_or_create(character=enactor)
        handler, created = self.characters.get_or_create(character=target)
        if not handler.is_handler:
            raise ValueError("%s is not handling this job!" % target)
        handler.is_handler = False
        handler.save(update_fields=['is_handler'])
        self.announce('%s removed %s from Handlers.' % (enactor, target))
        ehandler.make_comment(comment_mode=10, text='%s' % target)

    def appoint_helper(self, enactor, target):
        ehandler, created1 = self.characters.get_or_create(character=enactor)
        handler, created = self.characters.get_or_create(character=target)
        if handler.is_helper:
            raise ValueError("%s is already helping this job!" % target)
        handler.is_helper = True
        handler.save(update_fields=['is_helper'])
        self.announce('%s added %s to Helpers.' % (enactor, target))
        ehandler.make_comment(comment_mode=8, text='%s' % target)

    def remove_helper(self, enactor, target):
        ehandler, created1 = self.characters.get_or_create(character=enactor)
        handler, created = self.characters.get_or_create(character=target)
        if not handler.is_helper:
            raise ValueError("%s is not helping this job!" % target)
        handler.is_helper = False
        handler.save(update_fields=['is_helper'])
        self.announce('%s removed %s from Helpers.' % (enactor, target))
        ehandler.make_comment(comment_mode=11, text='%s' % target)

    def change_category(self, enactor, destination):
        oldcat = self.category
        newcat = destination
        self.announce('%s moved job to: %s' % (enactor, destination))
        self.category = newcat
        self.announce('%s moved job from: %s' % (enactor, oldcat))
        self.save(update_fields=['category'])
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(comment_mode=3, text='%s to %s' % (oldcat, newcat))

    def display(self, viewer):
        admin = False
        if self.locks.check(viewer, 'admin') or self.characters.filter(is_handler=True, character=viewer):
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
        handler, created = self.characters.get_or_create(character=viewer)
        handler.check()
        return message

    def make_reply(self, enactor, contents):
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=1)
        name = enactor.key
        if handler.is_owner and self.anonymous:
            name = 'Anonymous'
        self.announce('%s sent a reply.' % name)

    def make_comment(self, enactor, contents):
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=1, is_private=True)
        self.announce('%s added a |rSTAFF COMMENT|n.' % enactor, only_admin=True)

    def set_approved(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be approved.")
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=4)
        self.status = 1
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s approved the job!' % enactor)

    def set_denied(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be denied.")
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=5)
        self.status = 2
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s denied the job!' % enactor)

    def set_canceled(self, enactor, contents):
        if not self.status == 0:
            raise ValueError("Job is not pending, cannot be canceled.")
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=6)
        self.status = 3
        self.close_date = utcnow()
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s canceled the job!' % enactor)

    def set_pending(self, enactor, contents):
        if self.status == 0:
            raise ValueError("Job is not finished, cannot be revived.")
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(text=contents, comment_mode=7)
        self.status = 0
        self.close_date = None
        self.save(update_fields=['status', 'close_date'])
        self.announce('%s revived the job!' % enactor)

    def set_due(self, enactor, new_date):
        self.due_date = new_date
        self.save(update_fields=['due_date'])
        handler, created = self.characters.get_or_create(character=enactor)
        handler.make_comment(comment_mode=12, text='%s' % self.due_date)
        self.announce('%s changed the Due Date to: %s' % (enactor, self.due_date))


class JobHandler(models.Model):
    character = models.ForeignKey('objects.ObjectDB', related_name='job_handling')
    job = models.ForeignKey('jobs.Job', related_name='characters')
    is_handler = models.BooleanField(default=False)
    is_helper = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    check_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = (("character", "job"),)

    def __str__(self):
        return str(self.character)

    def check(self):
        self.check_date = utcnow()
        self.save(update_fields=['check_date'])

    def make_comment(self, comment_mode=1, text=None, is_private=False):
        now = utcnow()
        if not is_private:
            self.job.public_update = now
        self.job.admin_update = now
        self.job.save(update_fields=['admin_update', 'public_update'])
        self.comments.create(comment_mode=comment_mode, text=text, is_private=is_private, date_made=now)

class JobComment(models.Model):
    handler = models.ForeignKey('jobs.JobHandler', related_name='comments')
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
        if self.handler.job.anonymous and self.handler.is_owner:
            return 'Anonymous'
        return self.handler.character.key

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
