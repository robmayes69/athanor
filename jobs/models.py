from __future__ import unicode_literals

from django.db import models

from athanor.core.models import WithKey, WithLocks

# Create your models here.


class JobCategory(WithKey, WithLocks):

    def setup(self):
        self.locks.add('admin:perm(Wizards);post:all()')
        self.save_locks()


class Job(models.Model):
    category = models.ForeignKey('jobs.JobCategory', related_name='jobs')
    title = models.CharField(max_length=255)
    submit_date = models.DateTimeField()
    due_date = models.DateTimeField()
    close_date = models.DateTimeField(null=True)
    status = models.SmallIntegerField(default=0)

    def handlers(self):
        return self.characters.filter(is_handler=True)

    def helpers(self):
        return self.characters.filter(is_helper=True)

    def comments(self):
        return JobComment.objects.filter(handler__job=self)

    def __str__(self):
        return self.title

    @property
    def owner(self):
        return self.characters.filter(is_owner=True).first()

    @property
    def locks(self):
        return self.category.locks


class JobHandler(models.Model):
    character = models.ForeignKey('objects.ObjectDB', related_name='job_handling')
    job = models.ForeignKey('jobs.Job', related_name='characters')
    is_handler = models.BooleanField(default=False)
    is_helper = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    check_date = models.DateTimeField()

    class Meta:
        unique_together = (("character", "job"),)

    def __str__(self):
        return str(self.character)


class JobComment(models.Model):
    handler = models.ForeignKey('jobs.JobHandler', related_name='comments')
    text = models.TextField()
    is_private = models.BooleanField(default=False)
    date_made = models.DateTimeField()

    def __str__(self):
        return self.text