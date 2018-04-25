from __future__ import unicode_literals
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from evennia.locks.lockhandler import LockHandler
from evennia.utils.ansi import ANSIString
from evennia.utils import lazy_property
from timezone_field import TimeZoneField
from pytz import UTC


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


class AccountCore(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField(default=timedelta(0))
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)
    timezone = TimeZoneField(default='UTC')
    

class AccountWho(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)



class AccountCharacter(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    last_character = models.ForeignKey('objects.ObjectDB', on_delete=models.SET_NULL, null=True)
    extra_character_slots = models.SmallIntegerField(default=0)
    characters = models.ManyToManyField('objects.ObjectDB', related_name='+')


class CharacterCore(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    account = models.ForeignKey('accounts.AccountDB', related_name='+', null=True, on_delete=models.SET_NULL)
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField(default=timedelta(0))
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)


class CharacterWho(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)


class CharacterCharacter(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')


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