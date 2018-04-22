from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property
from athanor.utils.text import sanitize_string


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)

class WithKey(models.Model):
    """
    abstract model to implement a generic 'key' field that implements case-insensitive renaming.

    Not really that great.
    """
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

    def save_locks(self):
        self.save(update_fields=['lock_storage'])