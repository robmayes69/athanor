from __future__ import unicode_literals
import re
from evennia.utils.utils import time_format
from athanor.jobs.models import JobCategory, Job, JobHandler, JobComment
from athanor.core.command import AthCommand
from athanor.utils.text import normal_string
from athanor.utils.time import utcnow

class CmdJob(AthCommand):
    key = '+job'
    system_name = 'JOBS'
    player_switches = ['reply', 'old', 'approve', 'deny', 'cancel', 'revive', 'comment', 'due', 'claim', 'unclaim',
                       'attn', 'scan', 'next', 'pending', 'addplayer', 'remplayer', 'brief', 'search']
    admin_switches = ['newcategory', 'delcategory', 'rencategory', 'lock', 'move', 'config']
    page = 1

    def func(self):
        pages = [int(swi) for swi in self.switches if swi.isdigit()]
        if pages:
            self.page = pages[0]

        rhs = self.rhs
        lhs = self.lhs
        switches = [swi for swi in self.final_switches if not isinstance(swi, int)]

        if switches:
            switch = switches[0]
            getattr(self, 'switch_%s' % switch)(lhs, rhs)
            return
        if self.args:
            self.switch_display(lhs, rhs)
            return
        else:
            self.list_categories(lhs, rhs)

    def list_categories(self, lhs, rhs):
        message = list()
        message.append(self.player.render.header('Job Categories'))
        cat_table = self.player.render.make_table(['Name', 'Description', 'Pen', 'App', 'Dny', 'Cnc', 'Over', 'Due', 'Anon'],
                                                    width=[10, 35, 5, 5, 5, 5, 5, 5, 5])
        for cat in JobCategory.objects.all().order_by('key'):
            pending = cat.jobs.filter(status=0).count()
            approved = cat.jobs.filter(status=1).count()
            denied = cat.jobs.filter(status=2).count()
            canceled = cat.jobs.filter(status=3).count()
            anon = 'Yes' if cat.anonymous else 'No'
            now = utcnow()
            overdue = cat.jobs.filter(status=0, due_date__lt=now).count()
            due = time_format(cat.due.total_seconds(), style=1)
            cat_table.add_row(cat.key, cat.description, pending, approved, denied, canceled, overdue, due, anon)
        message.append(cat_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)


    def switch_newcategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            return self.error("Permission denied!")
        name = normal_string(lhs)
        if not name:
            return self.error("Nothing entered to create.")
        found = JobCategory.objects.filter(key__iexact=name).count()
        if found:
            return self.error("Category already exists. Use /rencategory to rename it.")
        due = self.valid_duration('1w')
        cat, created = JobCategory.objects.get_or_create(key=name, due=due)
        msg = "Created New Job Category: %s" % name
        self.sys_report(msg)
        self.sys_msg(msg)

    def valid_jobcategory(self, entry=None):
        if not entry:
            raise ValueError("Job category name field empty.")
        found = JobCategory.objects.filter(key__istartswith=entry).order_by('key').first()
        if not found:
            raise ValueError("Job Category not found.")
        return found

    def switch_rencategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            self.error("Permission denied!")
            return
        try:
            cat = self.valid_jobcategory(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        name = normal_string(rhs)
        if not name:
            return self.error("Job category new name field empty.")
        found = JobCategory.objects.exclude(id=cat.id).filter(key__iexact=name).first()
        if found:
            return self.error("That would conflict with an existing category.")
        msg = "Renamed Job Category '%s' to '%s'!" % (cat.key, name)
        cat.key = name
        cat.save(update_fields=['key'])
        self.sys_msg(msg)
        self.sys_report(msg)

    def switch_delcategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            self.error("Permission denied!")
            return
        try:
            cat = self.valid_jobcategory(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        if not self.verify('delete job category %s' % cat.id):
            self.sys_msg("This will delete the Job Category '%s' and ALL ASSOCIATED JOBS. This cannot be undone."
                         "Enter the same command again in ten seconds to verify!")

    def switch_lock(self, lhs, rhs):
        pass


    def switch_move(self, lhs, rhs):
        pass


    def switch_config(self, lhs, rhs):
        pass