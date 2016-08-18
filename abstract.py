from django.db import models
from athanor.library import sanitize_string, utcnow
from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property

class WithKey(models.Model):
    key = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.key

    def __str__(self):
        return self.key

    def rename(self, new_name):
        if not new_name:
            raise ValueError("No new name entered!")
        clean_name = sanitize_string(new_name, strip_ansi=True)
        if self.__class__.objects.filter(key__iexact=clean_name).exclude(id=self.id).count():
            raise ValueError("Names must be unique, case insensitive.")
        else:
            if self.key == clean_name:
                return
            self.key = clean_name
            self.save(update_fields=['key'])

class WithTimestamp(models.Model):

    class Meta:
        abstract = True

    def update_time(self, fields):
        timestamp = utcnow()
        if isinstance(fields, basestring):
            setattr(self, fields, timestamp)
            self.save(update_fields=[fields])
            return
        for field in fields:
            setattr(self, field, timestamp)
        self.save(update_fields=fields)

class WithLocks(models.Model):
    lock_storage = models.TextField('locks', blank=True)

    class Meta:
        abstract = True

    @lazy_property
    def locks(self):
        return LockHandler(self)

    def save_locks(self):
        self.save(update_fields=['lock_storage'])