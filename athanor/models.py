from __future__ import unicode_literals
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


class __AbstractAccountSystem(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField()
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)
    timezone = TimeZoneField(default=UTC)
    
    class Meta:
        abstract = True
        

class AccountSettings(__AbstractAccountSystem):
    pass
    
    
class __AbstractAccountWho(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)

    class Meta:
        abstract = True


class AccountWho(__AbstractAccountWho):
    pass


class __AbstractAccountCharacter(models.Model):
    account = models.OneToOneField('accounts.AccountDB', related_name='+')
    last_character = models.ForeignKey('objects.ObjectDB', on_delete=models.SET_NULL, null=True)
    extra_character_slots = models.SmallIntegerField(default=0)
    characters = models.ManyToManyField('objects.ObjectDB', related_name='+')

    class Meta:
        abstract = True


class AccountCharacter(__AbstractAccountCharacter):
    pass


class __AbstractCharacterSystem(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    account = models.ForeignKey('accounts.AccountDB', related_name='+', null=True, on_delete=models.SET_NULL)
    banned = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    playtime = models.DurationField()
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    shelved = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class CharacterSystem(__AbstractCharacterSystem):
    pass


class __AbstractCharacterWho(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)

    class Meta:
        abstract = True


class CharacterWho(__AbstractAccountWho):
    pass


class __AbstractCharacterCharacter(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')


    class Meta:
        abstract = True


class CharacterCharacter(__AbstractCharacterCharacter):
    pass


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